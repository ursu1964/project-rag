from app.rag.chunking import chunk_text


def test_chunk_text_returns_multiple_chunks():
    chunks = chunk_text("abcdef", chunk_size=3, overlap=1)
    assert len(chunks) > 1
