from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings
from app.services.guardrails import RetrievedChunk


@lru_cache
def get_chroma_client() -> chromadb.PersistentClient:
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_collection() -> Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def collection_count() -> int:
    return get_collection().count()


def upsert_chunks(
    *,
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    if not ids:
        return

    collection = get_collection()
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query_similar(
    embedding: list[float],
    *,
    top_k: int,
) -> list[RetrievedChunk]:
    if top_k <= 0:
        return []

    collection = get_collection()
    if collection.count() == 0:
        return []

    result = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    ids = (result.get("ids") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    chunks: list[RetrievedChunk] = []
    for doc_id, text, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
        strict=True,
    ):
        meta = metadata or {}
        chunks.append(
            RetrievedChunk(
                id=doc_id,
                text=text or "",
                source=str(meta.get("source", "unknown")),
                page=int(meta.get("page", 0)),
                chunk_index=int(meta.get("chunk_index", 0)),
                distance=float(distance),
            ),
        )

    return chunks
