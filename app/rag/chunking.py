"""Text chunking helpers."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    value = str(text or "")
    if not value:
        return []
    size = max(1, int(chunk_size))
    step = max(1, size - max(0, int(overlap)))
    chunks: list[str] = []
    for start in range(0, len(value), step):
        chunk = value[start : start + size].strip()
        if chunk:
            chunks.append(chunk)
        if start + size >= len(value):
            break
    return chunks
