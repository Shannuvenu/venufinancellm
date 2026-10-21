from app.services.documents import chunk_pages, digest_bytes, extract
from app.services.embeddings import embed, similarity


def test_text_extraction_and_chunking_preserve_page_metadata():
    page = "Quarterly revenue was 100. " * 100
    chunks = chunk_pages([(3, page)], size=350, overlap=30)
    assert len(chunks) > 1
    assert all(number == 3 for number, _ in chunks)
    assert all(text for _, text in chunks)


def test_csv_extraction_keeps_table_rows():
    extracted = extract("statement.csv", b"Item,Value\nRevenue,125\n")
    assert "Revenue | 125" in extracted[0][1]


def test_digest_is_stable():
    assert digest_bytes(b"data") == digest_bytes(b"data")


def test_embedding_similarity_is_bounded_for_local_fallback(monkeypatch):
    from app.services import embeddings
    monkeypatch.setattr(embeddings.settings, "embeddings_enabled", False)
    vecs, mode = embed(["operating profit rose", "operating profit rose"])
    assert mode == "lexical-fallback"
    assert similarity(vecs[0], vecs[1]) > 0.99
