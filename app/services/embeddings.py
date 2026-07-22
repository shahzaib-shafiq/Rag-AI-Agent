import httpx

from app.core.config import settings


class OllamaEmbeddingError(Exception):
    pass


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings: list[list[float]] = []
    url = f"{settings.ollama_base_url.rstrip('/')}/api/embeddings"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            for text in texts:
                response = await client.post(
                    url,
                    json={
                        "model": settings.ollama_embed_model,
                        "prompt": text,
                    },
                )
                if response.status_code != 200:
                    raise OllamaEmbeddingError(
                        f"Ollama embeddings failed ({response.status_code}): "
                        f"{response.text}",
                    )

                payload = response.json()
                embedding = payload.get("embedding")
                if not embedding:
                    raise OllamaEmbeddingError(
                        "Ollama response missing 'embedding' field",
                    )
                embeddings.append(embedding)
    except httpx.HTTPError as exc:
        raise OllamaEmbeddingError(
            f"Ollama embeddings request failed: {exc}",
        ) from exc

    return embeddings
