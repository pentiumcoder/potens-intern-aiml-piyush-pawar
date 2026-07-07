from app.models.retrieval import RetrievalResult
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vectorstore.base import VectorStoreProvider


class RetrievalService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        query_embedding = self.embedding_provider.embed_query(query)
        return self.vector_store.similarity_search(query_embedding, top_k=top_k)
