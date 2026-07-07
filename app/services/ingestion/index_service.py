from app.models.chunk import Chunk
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vectorstore.base import VectorStoreProvider


class IndexService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_chunks(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0

        embeddings = self.embedding_provider.embed_texts([chunk.content for chunk in chunks])
        self.vector_store.add_chunks(chunks, embeddings)
        return len(chunks)
