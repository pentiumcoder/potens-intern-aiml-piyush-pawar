from app.models.chunk import Chunk, ChunkMetadata
from app.models.retrieval import RetrievalResult
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vectorstore.base import VectorStoreProvider
from app.services.ingestion.index_service import IndexService
from app.services.retrieval.service import RetrievalService


class FakeEmbeddingProvider(EmbeddingProvider):
    @property
    def embedding_version(self) -> str:
        return "fake-v1"

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), 1.0] for text in texts]

    def embed_query(self, query: str) -> list[float]:
        return [float(len(query)), 1.0]


class FakeVectorStore(VectorStoreProvider):
    def __init__(self) -> None:
        self.added_chunks: list[Chunk] = []
        self.added_embeddings: list[list[float]] = []
        self.query_embedding: list[float] | None = None
        self.top_k: int | None = None

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.added_chunks = chunks
        self.added_embeddings = embeddings

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[RetrievalResult]:
        self.query_embedding = query_embedding
        self.top_k = top_k
        chunk = self.added_chunks[0]
        return [
            RetrievalResult(
                chunk=chunk,
                metadata=chunk.metadata,
                similarity_score=0.87,
            )
        ]


def test_index_service_embeds_and_stores_chunks_with_metadata() -> None:
    chunk = _chunk()
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    service = IndexService(embedding_provider, vector_store)

    indexed_count = service.index_chunks([chunk])

    assert indexed_count == 1
    assert vector_store.added_chunks == [chunk]
    assert vector_store.added_embeddings == [[float(len(chunk.content)), 1.0]]
    assert vector_store.added_chunks[0].metadata == chunk.metadata


def test_index_service_skips_empty_chunk_list() -> None:
    vector_store = FakeVectorStore()
    service = IndexService(FakeEmbeddingProvider(), vector_store)

    indexed_count = service.index_chunks([])

    assert indexed_count == 0
    assert vector_store.added_chunks == []
    assert vector_store.added_embeddings == []


def test_retrieval_service_returns_chunk_metadata_and_similarity_score() -> None:
    chunk = _chunk()
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    vector_store.add_chunks([chunk], [[1.0, 1.0]])
    service = RetrievalService(embedding_provider, vector_store)

    results = service.retrieve("security", top_k=3)

    assert vector_store.query_embedding == [8.0, 1.0]
    assert vector_store.top_k == 3
    assert len(results) == 1
    assert results[0].chunk == chunk
    assert results[0].metadata == chunk.metadata
    assert results[0].similarity_score == 0.87


def _chunk() -> Chunk:
    return Chunk(
        content="# FastAPI\n\nFastAPI security content.",
        metadata=ChunkMetadata(
            document_id="security",
            title="FastAPI Security",
            heading="Security",
            section="FastAPI Security > Security",
            chunk_id="security:0",
            chunk_index=0,
            page=None,
            embedding_version=None,
        ),
    )
