from pathlib import Path

from app.core.config import settings
from app.services.chunker import chunk_pages
from app.services.embeddings import embed_texts
from app.services.pdf_loader import load_pdf_pages
from app.services.vectorstore import upsert_chunks


async def ingest_pdf(pdf_path: Path) -> dict[str, str | int]:
    pages = load_pdf_pages(pdf_path)
    chunks = chunk_pages(
        [(page.page, page.text) for page in pages],
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    if not chunks:
        return {
            "source": str(pdf_path),
            "chunks_indexed": 0,
            "collection": settings.chroma_collection,
        }

    source_name = pdf_path.name
    ids = [
        f"{source_name}:{chunk.page}:{chunk.chunk_index}" for chunk in chunks
    ]
    documents = [chunk.text for chunk in chunks]
    metadatas = [
        {
            "source": source_name,
            "page": chunk.page,
            "chunk_index": chunk.chunk_index,
        }
        for chunk in chunks
    ]

    embeddings = await embed_texts(documents)
    upsert_chunks(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {
        "source": str(pdf_path),
        "chunks_indexed": len(chunks),
        "collection": settings.chroma_collection,
    }
