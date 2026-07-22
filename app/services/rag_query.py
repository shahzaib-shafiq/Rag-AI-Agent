from dataclasses import dataclass

from app.core.config import settings
from app.services.embeddings import embed_texts
from app.services.guardrails import (
    RetrievedChunk,
    filter_by_distance,
    refusal_answer,
    validate_query,
)
from app.services.llm import generate_answer
from app.services.vectorstore import collection_count, query_similar


@dataclass(frozen=True)
class RagQueryResult:
    answer: str
    refused: bool
    refusal_reason: str | None
    sources: list[RetrievedChunk]


def _format_context_chunk(chunk: RetrievedChunk) -> str:
    return f"(page {chunk.page})\n{chunk.text}"


def _refused(reason: str) -> RagQueryResult:
    return RagQueryResult(
        answer=refusal_answer(reason),
        refused=True,
        refusal_reason=reason,
        sources=[],
    )


async def answer_query(
    query: str,
    *,
    top_k: int | None = None,
) -> RagQueryResult:
    validation = validate_query(query)
    if not validation.ok:
        reason = validation.refusal_reason or "invalid_query"
        return _refused(reason)

    if collection_count() == 0:
        return _refused("no_documents")

    k = settings.rag_top_k if top_k is None else top_k
    if k < 1:
        k = settings.rag_top_k

    embeddings = await embed_texts([validation.cleaned_query])
    retrieved = query_similar(embeddings[0], top_k=k)
    relevant = filter_by_distance(retrieved)

    if not relevant:
        return _refused("no_relevant_context")

    context_chunks = [_format_context_chunk(chunk) for chunk in relevant]
    answer = await generate_answer(
        query=validation.cleaned_query,
        context_chunks=context_chunks,
    )

    return RagQueryResult(
        answer=answer,
        refused=False,
        refusal_reason=None,
        sources=relevant,
    )
