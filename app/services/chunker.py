from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    page: int
    chunk_index: int
    text: str


def chunk_text(
    text: str,
    *,
    page: int,
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    if not text:
        return []

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0
    step = chunk_size - chunk_overlap

    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                TextChunk(page=page, chunk_index=chunk_index, text=piece),
            )
            chunk_index += 1
        if end >= len(text):
            break
        start += step

    return chunks


def chunk_pages(
    pages: list[tuple[int, str]],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    all_chunks: list[TextChunk] = []
    for page, text in pages:
        all_chunks.extend(
            chunk_text(
                text,
                page=page,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
        )
    return all_chunks
