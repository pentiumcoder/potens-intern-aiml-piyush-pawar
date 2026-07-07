from abc import ABC, abstractmethod

from app.models.chunk import Chunk
from app.models.retrieval import RetrievalResult


class VectorStoreProvider(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[RetrievalResult]:
        raise NotImplementedError
