import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import STORAGE, settings
from .database import Base, SessionLocal, engine, get_db
from .models import AnswerFeedback, Chunk, Document, NewsArticle
from .providers.llm import get_provider
from .providers.sources import market_quote, news_items, sec_company_search, sec_submissions, web_search
from .services.calculations import calculate
from .services.documents import chunk_pages, digest_bytes, extract
from .services.embeddings import embed, encode, model_status, similarity

Base.metadata.create_all(bind=engine)
logger = logging.getLogger("venufin")


async def refresh_news(db: Session) -> int:
    inserted = 0
    for item in await news_items():
        if db.query(NewsArticle).filter_by(url=item["url"]).first():
            continue
        db.add(NewsArticle(url=item["url"], title=item["title"][:1000], publisher=item["publisher"][:300],
                           published_at=item.get("published_at"), summary=item.get("summary"),
                           category=item.get("category", "General"), relevance_estimate=item.get("relevance_estimate", 0)))
        inserted += 1
    if inserted: db.commit()
    return inserted


async def news_scheduler():
    while True:
        try:
            if settings.rss_urls:
                with SessionLocal() as db:
                    await refresh_news(db)
        except Exception:
            logger.exception("Scheduled RSS refresh failed")
        await asyncio.sleep(900)


@asynccontextmanager
async def lifespan(_app):
    task = asyncio.create_task(news_scheduler())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="VenuFin AI API", version="0.1.0", description="Source-aware personal financial research. Research only; no trading endpoint.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"], allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])
_requests: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def local_rate_limit(request: Request, call_next):
    now = time.monotonic(); key = request.client.host if request.client else "local"
    bucket = _requests[key]
    while bucket and now - bucket[0] > 60: bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_minute:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Local request limit reached; retry shortly."}, status_code=429)
    bucket.append(now)
    return await call_next(request)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    document_ids: list[int] = []


class CalculationRequest(BaseModel):
    kind: str
    inputs: dict


class FeedbackRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    answer_excerpt: str = Field(min_length=1, max_length=8000)
    rating: str
    comment: str | None = Field(default=None, max_length=2000)


def retrieve(question: str, db: Session, document_ids: list[int] | None = None, limit: int = 5):
    chunks = db.query(Chunk).join(Document).filter(Document.status == "indexed")
    if document_ids:
        chunks = chunks.filter(Chunk.document_id.in_(document_ids))
    rows = chunks.all()
    if not rows:
        return [], "none"
    qvecs, mode = embed([question])
    scored = []
    for row in rows:
        vec = json.loads(row.embedding) if row.embedding else []
        score = similarity(qvecs[0], vec) if vec else 0
        if mode == "lexical-fallback":
            qterms = set(question.lower().split()); terms = set(row.text.lower().split())
            score = len(qterms & terms) / max(1, len(qterms))
        scored.append((score, row))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    output = []
    for score, row in scored[:limit]:
        if score <= 0: continue
        output.append({"score": round(score, 4), "filename": row.document.filename, "document_id": row.document_id, "page": row.page, "text": row.text})
    return output, mode


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")); database_ok = True
    except Exception:
        database_ok = False
    return {"status": "ok" if database_ok else "degraded", "database": database_ok,
            "database_mode": "sqlite-local" if settings.database_url.startswith("sqlite") else "postgresql",
            "llm": {"provider": "google-gemini" if settings.gemini_api_key else "anthropic",
                    "configured": bool(settings.gemini_api_key or settings.anthropic_api_key),
                    "model": settings.gemini_model if settings.gemini_api_key else settings.anthropic_model},
            "embeddings": model_status(), "news_feeds_configured": len(settings.rss_urls),
            "web_search": {"provider": "Brave Search", "configured": bool(settings.brave_search_api_key)},
            "market_data": {"provider": "Alpha Vantage", "configured": bool(settings.alphavantage_api_key), "entitlement": settings.market_data_entitlement or "end-of-day"},
            "sec_edgar": "available-on-request", "trading": "not-supported"}


@app.get("/api/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "status": d.status, "error": d.error,
             "created_at": d.created_at.isoformat(), "chunks": len(d.chunks)} for d in docs]


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed = {".pdf", ".txt", ".md", ".markdown", ".html", ".htm", ".csv", ".tsv"}
    filename = Path(file.filename or "upload").name
    if Path(filename).suffix.lower() not in allowed:
        raise HTTPException(415, "Unsupported file type.")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit.")
    digest = digest_bytes(data)
    existing = db.query(Document).filter_by(digest=digest).first()
    if existing:
        return {"id": existing.id, "status": "duplicate", "filename": existing.filename}
    doc = Document(filename=filename, digest=digest, content_type=file.content_type or "application/octet-stream", status="processing")
    db.add(doc); db.flush()
    (STORAGE / f"{doc.id}_{filename}").write_bytes(data)
    try:
        parts = chunk_pages(extract(filename, data))
        if not parts:
            raise ValueError("No extractable text was found in this file.")
        vectors, _mode = embed([part for _, part in parts])
        for ordinal, ((page, content), vector) in enumerate(zip(parts, vectors)):
            db.add(Chunk(document_id=doc.id, ordinal=ordinal, page=page, text=content, embedding=encode(vector)))
        doc.status = "indexed"; db.commit()
        return {"id": doc.id, "status": doc.status, "chunks": len(parts), "embedding_mode": _mode}
    except Exception as exc:
        doc.status = "failed"; doc.error = str(exc)[:500]; db.commit()
        raise HTTPException(422, f"Document extraction failed: {doc.error}")


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc: raise HTTPException(404, "Document not found.")
    for file in STORAGE.glob(f"{document_id}_*"):
        file.unlink(missing_ok=True)
    db.delete(doc); db.commit()
    return {"deleted": document_id}


@app.post("/api/chat")
async def chat(body: ChatRequest, db: Session = Depends(get_db)):
    evidence, retrieval_mode = retrieve(body.question, db, body.document_ids or None)
    web_sources = []
    search_error = None
    if settings.brave_search_api_key:
        try:
            web_sources = await web_search(body.question)
        except Exception as exc:
            logger.warning("Web search failed: %s", type(exc).__name__)
            search_error = "Web search provider is temporarily unavailable."
    try:
        provider = get_provider()
        answer = await provider.answer(body.question, evidence, web_sources)
        mode = "google-gemini" if settings.gemini_api_key else "anthropic"
    except Exception as exc:
        if web_sources:
            answer = "I searched the live web and found the sources below. AI synthesis is not connected yet, so these are search excerpts rather than a verified answer. Open the original pages to confirm details."
        elif evidence:
            answer = "I found these relevant passages, but answer synthesis is unavailable because the reasoning provider is not configured or reachable. Review the excerpts below; no unsupported conclusion has been inferred."
        else:
            answer = "I couldn't retrieve live web sources or document evidence. Connect Brave Search in the local .env file to enable current web research; I will not invent current facts."
        mode = "limited"
        provider_error = str(exc)[:220]
    result = {"answer": answer, "evidence": evidence, "web_sources": web_sources, "retrieval_mode": retrieval_mode, "answer_mode": mode,
              "freshness": "Live web search · retrieved just now" if web_sources else ("Retrieved from uploaded documents" if evidence else "No current external source retrieved"),
              "disclaimer": "Research and education only; not investment advice."}
    if search_error: result["search_status"] = search_error
    if mode == "limited": result["provider_status"] = provider_error
    return result


@app.get("/api/market/quote")
async def market_quote_endpoint(symbol: str):
    symbol = symbol.strip()
    if not symbol or len(symbol) > 24 or not all(c.isalnum() or c in ".-_^" for c in symbol):
        raise HTTPException(422, "Enter a valid ticker symbol.")
    try:
        return await market_quote(symbol)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        logger.warning("Market quote request failed: %s", type(exc).__name__)
        raise HTTPException(503, "Market data provider is temporarily unavailable.")


@app.post("/api/calculate")
def calculate_endpoint(body: CalculationRequest):
    try: return calculate(body.kind, body.inputs)
    except (ValueError, KeyError, TypeError, OverflowError) as exc: raise HTTPException(422, str(exc))


@app.get("/api/news")
def get_news(db: Session = Depends(get_db)):
    rows = db.query(NewsArticle).order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.retrieved_at.desc()).limit(200).all()
    return {"items": [{"title": n.title, "url": n.url, "publisher": n.publisher, "published_at": n.published_at,
                        "retrieved_at": n.retrieved_at.isoformat(), "summary": n.summary, "category": n.category,
                        "relevance_estimate": n.relevance_estimate} for n in rows],
            "feeds_configured": len(settings.rss_urls), "coverage": "configured feeds only", "scheduler_interval_minutes": 15}


@app.post("/api/news/refresh")
async def refresh_news_endpoint(db: Session = Depends(get_db)):
    return {"inserted": await refresh_news(db), "feeds_configured": len(settings.rss_urls), "coverage": "configured feeds only"}


@app.post("/api/feedback")
def save_feedback(body: FeedbackRequest, db: Session = Depends(get_db)):
    allowed = {"correct", "incorrect", "incomplete", "outdated", "poorly_sourced", "misleading", "needs_research"}
    if body.rating not in allowed: raise HTTPException(422, f"Rating must be one of: {', '.join(sorted(allowed))}.")
    row = AnswerFeedback(question=body.question, answer_excerpt=body.answer_excerpt, rating=body.rating, comment=body.comment)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "saved": True, "created_at": row.created_at.isoformat()}


@app.get("/api/feedback/summary")
def feedback_summary(db: Session = Depends(get_db)):
    rows = db.query(AnswerFeedback.rating).all()
    counts = {}
    for (rating,) in rows: counts[rating] = counts.get(rating, 0) + 1
    return {"total": len(rows), "ratings": counts, "review_required": True}


@app.get("/api/company/search")
async def company_search(q: str):
    if len(q.strip()) < 1: raise HTTPException(422, "Search query is required.")
    try: return {"results": await sec_company_search(q.strip()), "source": "SEC EDGAR", "retrieved_at": time.time()}
    except Exception as exc: raise HTTPException(503, f"SEC EDGAR unavailable: {type(exc).__name__}")


@app.get("/api/company/{cik}/filings")
async def company_filings(cik: str):
    if not cik.isdigit() or len(cik) > 10: raise HTTPException(422, "CIK must contain up to 10 digits.")
    try: return await sec_submissions(cik)
    except Exception as exc: raise HTTPException(503, f"SEC EDGAR unavailable: {type(exc).__name__}")


@app.get("/api/sources")
def sources():
    return {"items": [
        {"name": "SEC EDGAR", "status": "on request", "type": "official filing data", "coverage": "US filings; not price quotes"},
        {"name": "Configured RSS", "status": "connected" if settings.rss_urls else "not configured", "type": "news", "coverage": "user-configured feeds only"},
        {"name": "Brave Search", "status": "connected" if settings.brave_search_api_key else "not configured", "type": "live web search", "coverage": "web search results; provider limits apply"},
        {"name": "Alpha Vantage", "status": "connected" if settings.alphavantage_api_key else "not configured", "type": "market quotes", "coverage": "global quote; end-of-day by default"},
        {"name": "Anthropic", "status": "connected" if settings.anthropic_api_key else "not configured", "type": "reasoning", "coverage": "optional synthesis"},
    ]}


@app.get("/{path:path}")
def frontend_fallback(path: str):
    # API runs separately from Next.js; this endpoint gives a helpful root health message.
    if path.startswith("api/"): raise HTTPException(404, "API route not found")
    return {"message": "VenuFin API is running. Start the Next.js frontend on port 3000.", "docs": "/docs", "health": "/api/health"}
