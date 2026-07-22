from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.schemas.rag import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    QueryRequest,
    QueryResponse,
    SourceChunk,
)
from app.services.embeddings import OllamaEmbeddingError
from app.services.ingest import ingest_pdf
from app.services.llm import OllamaChatError
from app.services.rag_query import answer_query

router = APIRouter()


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_document(
    body: DocumentIngestRequest,
) -> DocumentIngestResponse:
    pdf_path = Path(body.pdf_path).expanduser().resolve()

    if pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path must point to a .pdf file",
        )

    if not pdf_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF not found: {pdf_path}",
        )

    try:
        result = await ingest_pdf(pdf_path)
    except OllamaEmbeddingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest PDF: {exc}",
        ) from exc

    return DocumentIngestResponse(**result)


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_documents(body: QueryRequest) -> QueryResponse:
    try:
        result = await answer_query(body.query, top_k=body.top_k)
    except OllamaEmbeddingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except OllamaChatError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer query: {exc}",
        ) from exc

    return QueryResponse(
        answer=result.answer,
        refused=result.refused,
        refusal_reason=result.refusal_reason,
        sources=[
            SourceChunk(
                source=chunk.source,
                page=chunk.page,
                chunk_index=chunk.chunk_index,
                distance=chunk.distance,
            )
            for chunk in result.sources
        ],
    )
