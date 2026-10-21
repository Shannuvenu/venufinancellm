import csv
import hashlib
import io
from pathlib import Path

from pypdf import PdfReader


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract(filename: str, data: bytes) -> list[tuple[int | None, str]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        pages = []
        for number, page in enumerate(PdfReader(io.BytesIO(data)).pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((number, text))
        return pages
    text = data.decode("utf-8-sig", errors="replace")
    if suffix in {".txt", ".md", ".markdown"}:
        return [(None, text)]
    if suffix in {".html", ".htm"}:
        from html.parser import HTMLParser
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__(); self.parts = []
            def handle_data(self, value): self.parts.append(value)
        parser = TextExtractor(); parser.feed(text)
        return [(None, " ".join(parser.parts))]
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
        return [(None, "\n".join(" | ".join(row) for row in rows))]
    raise ValueError("Supported formats: PDF, TXT, Markdown, HTML, CSV and TSV.")


def chunk_pages(pages: list[tuple[int | None, str]], size: int = 1100, overlap: int = 160):
    chunks = []
    for page, text in pages:
        clean = " ".join(text.split())
        if not clean:
            continue
        start = 0
        while start < len(clean):
            end = min(start + size, len(clean))
            if end < len(clean):
                boundary = clean.rfind(" ", start + size // 2, end)
                if boundary > start:
                    end = boundary
            chunks.append((page, clean[start:end]))
            if end >= len(clean):
                break
            start = max(start + 1, end - overlap)
    return chunks
