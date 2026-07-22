from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    pdf_path: str = Field(
        min_length=1,
        examples=["./docs/manual.pdf"],
        description="Local filesystem path to a PDF file",
    )


class DocumentIngestResponse(BaseModel):
    source: str
    chunks_indexed: int
    collection: str


class QueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
        examples=["What does the document say about setup?"],
        description="User question to answer from indexed documents",
    )
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
        description="Optional override for number of chunks to retrieve",
    )


class SourceChunk(BaseModel):
    source: str
    page: int
    chunk_index: int
    distance: float


class QueryResponse(BaseModel):
    answer: str
    refused: bool
    refusal_reason: str | None = None
    sources: list[SourceChunk] = Field(default_factory=list)
