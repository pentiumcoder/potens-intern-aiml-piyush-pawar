from pydantic import BaseModel

from app.models.chunk import Chunk, ChunkMetadata


class RetrievalResult(BaseModel):
    chunk: Chunk
    metadata: ChunkMetadata
    similarity_score: float
