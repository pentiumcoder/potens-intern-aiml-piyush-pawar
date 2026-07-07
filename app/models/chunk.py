from pydantic import BaseModel


class ChunkMetadata(BaseModel):
    document_id: str
    title: str
    heading: str
    section: str
    chunk_id: str
    chunk_index: int
    page: int | None = None
    embedding_version: str | None = None


class Chunk(BaseModel):
    content: str
    metadata: ChunkMetadata
