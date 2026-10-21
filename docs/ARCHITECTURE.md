# Architecture

```text
Next.js workspace (127.0.0.1:3000)
   | JSON API / multipart upload
FastAPI (127.0.0.1:8000)
   |-- SQLAlchemy persistence: PostgreSQL configured, SQLite local fallback
   |-- Document extraction -> chunks -> local embeddings -> NumPy cosine retrieval
   |-- Anthropic provider interface (optional)
   |-- SEC EDGAR and configured RSS connectors with stored snapshots and deduplication
   |-- Deterministic calculators
```

The API is separated from the presentation layer. Providers are kept behind Python modules so supported sources and reasoning backends can be replaced. Retrieval is exact application-level cosine similarity; no vector database is used. Local semantic embeddings use `all-MiniLM-L6-v2` if the optional dependency/model is available. The fallback uses deterministic token hashing and lexical ranking and is explicitly marked as lower-quality.

The schema stores document metadata, extracted chunks with serialized embedding arrays, deduplicated news snapshots, and answer feedback. Alembic manages schema changes; the Windows startup script runs `alembic upgrade head` before services start. SQLite is used for local setup and PostgreSQL is supported by the SQLAlchemy driver.

Configured RSS sources are refreshed at startup and every 15 minutes, with a manual refresh endpoint and URL deduplication. Keyword categories and a relevance estimate are heuristics, not measured market impact. User answer feedback is stored locally for review and is not converted into facts. Feedback export/review tools, authentication, and licensed quote APIs remain follow-on work.
