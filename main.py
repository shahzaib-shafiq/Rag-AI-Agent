import os
from pathlib import Path

import chromadb
import httpx
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

PDF_PATH = Path(__file__).parent / "User_Manual.pdf"
CHUNK_SIZE = int(os.getenv("PDF_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("PDF_CHUNK_OVERLAP", "200"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", "storage/chroma"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "pdf_chunks")


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"[Page {i}]\n{text}")
    return "\n\n".join(pages)


def create_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    chunks: list[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = end - chunk_overlap

    return chunks


def embed_texts(texts: list[str], batch_size: int = 16) -> list[list[float]]:
    embeddings: list[list[float]] = []
    with httpx.Client(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/embed",
                json={"model": OLLAMA_EMBEDDING_MODEL, "input": batch},
            )
            response.raise_for_status()
            batch_embeddings = response.json().get("embeddings") or []
            if len(batch_embeddings) != len(batch):
                raise RuntimeError(
                    f"Expected {len(batch)} embeddings, got {len(batch_embeddings)}"
                )
            embeddings.extend(batch_embeddings)
            done = min(start + batch_size, len(texts))
            print(f"Embedded chunks {done}/{len(texts)}")
    return embeddings


def store_chunks(chunks: list[str], embeddings: list[list[float]], source: str) -> int:
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

    try:
        client.delete_collection(CHROMA_COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"{source}::chunk-{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": source, "chunk_index": i, "char_count": len(chunk)}
        for i, chunk in enumerate(chunks)
    ]

    batch_size = 32
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.upsert(
            ids=ids[start:end],
            documents=chunks[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    return collection.count()


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    text = extract_text(PDF_PATH)
    chunks = create_chunks(text, CHUNK_SIZE, CHUNK_OVERLAP)

    print(f"PDF: {PDF_PATH.name}")
    print(f"Characters: {len(text)}")
    print(f"Chunks: {len(chunks)} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"Embedding model: {OLLAMA_EMBEDDING_MODEL}")
    print("-" * 60)

    embeddings = embed_texts(chunks)
    count = store_chunks(chunks, embeddings, source=PDF_PATH.name)

    print("-" * 60)
    print(f"Stored {count} vectors in Chroma")
    print(f"Persist dir: {CHROMA_PERSIST_DIR.resolve()}")
    print(f"Collection: {CHROMA_COLLECTION_NAME}")


if __name__ == "__main__":
    main()
