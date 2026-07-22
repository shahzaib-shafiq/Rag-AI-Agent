from dataclasses import dataclass

from app.core.config import settings

BLOCKED_PHRASES = (
    "ignore previous instructions",
    "system prompt",
    "jailbreak",
    "dan mode",
)

MIN_QUERY_LENGTH = 3

REFUSAL_MESSAGES = {
    "blocked_query": (
        "I cannot process that request because it violates safety rules."
    ),
    "no_documents": (
        "No documents have been indexed yet. Please ingest a PDF first."
    ),
    "no_relevant_context": (
        "I could not find relevant information in the indexed documents "
        "to answer that question."
    ),
    "invalid_query": (
        "Please provide a valid question between "
        f"{MIN_QUERY_LENGTH} and {settings.rag_max_query_length} characters."
    ),
}


@dataclass(frozen=True)
class QueryValidationResult:
    ok: bool
    cleaned_query: str
    refusal_reason: str | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str
    source: str
    page: int
    chunk_index: int
    distance: float


def validate_query(query: str) -> QueryValidationResult:
    cleaned = " ".join(query.split()).strip()

    if len(cleaned) < MIN_QUERY_LENGTH:
        return QueryValidationResult(
            ok=False,
            cleaned_query=cleaned,
            refusal_reason="invalid_query",
        )

    if len(cleaned) > settings.rag_max_query_length:
        return QueryValidationResult(
            ok=False,
            cleaned_query=cleaned,
            refusal_reason="invalid_query",
        )

    lowered = cleaned.lower()
    if any(phrase in lowered for phrase in BLOCKED_PHRASES):
        return QueryValidationResult(
            ok=False,
            cleaned_query=cleaned,
            refusal_reason="blocked_query",
        )

    return QueryValidationResult(ok=True, cleaned_query=cleaned)


def filter_by_distance(
    chunks: list[RetrievedChunk],
    *,
    max_distance: float | None = None,
) -> list[RetrievedChunk]:
    threshold = (
        settings.rag_max_distance if max_distance is None else max_distance
    )
    return [chunk for chunk in chunks if chunk.distance <= threshold]


def refusal_answer(reason: str) -> str:
    return REFUSAL_MESSAGES.get(
        reason,
        "I cannot answer that request.",
    )
