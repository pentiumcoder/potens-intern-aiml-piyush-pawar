from pydantic import BaseModel

from app.models.chunk import ChunkMetadata


class Citation(BaseModel):
    document_id: str
    title: str
    heading: str
    section: str
    chunk_id: str
    chunk_index: int
    page: int | None = None
    embedding_version: str | None = None
    supporting_snippet: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    refused: bool
    retrieved_metadata: list[ChunkMetadata]
