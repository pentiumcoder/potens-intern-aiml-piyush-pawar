from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import settings
from app.models.chunk import Chunk
from app.providers.vectorstore.chroma import ChromaVectorStore
from app.services.ingestion.index_service import IndexService
from app.services.ingestion.service import IngestionService


DEFAULT_DOCUMENTS_DIR = PROJECT_ROOT / "documents" / "raw"


@dataclass(frozen=True)
class IndexingSummary:
    document_count: int
    chunk_count: int
    stored_count: int
    collection_count: int


def load_chunks(documents_dir: Path) -> tuple[int, list[Chunk]]:
    ingestion_service = IngestionService(documents_dir=documents_dir)
    documents = ingestion_service.load_documents()
    chunks: list[Chunk] = []

    for document in documents:
        chunks.extend(ingestion_service.chunker.chunk_document(document))

    return len(documents), chunks


def build_index_service() -> tuple[IndexService, ChromaVectorStore]:
    from app.providers.embeddings.sentence_transformer import SentenceTransformerEmbeddingProvider

    embedding_provider = SentenceTransformerEmbeddingProvider(settings.embedding_model)
    vector_store = ChromaVectorStore(PROJECT_ROOT / settings.vector_db_path)
    return IndexService(embedding_provider, vector_store), vector_store


def run_indexing(
    documents_dir: Path = DEFAULT_DOCUMENTS_DIR,
    index_service: IndexService | None = None,
    vector_store: ChromaVectorStore | None = None,
) -> IndexingSummary:
    document_count, chunks = load_chunks(documents_dir)

    if index_service is None or vector_store is None:
        index_service, vector_store = build_index_service()

    stored_count = index_service.index_chunks(chunks)
    collection_count = vector_store.collection.count()

    return IndexingSummary(
        document_count=document_count,
        chunk_count=len(chunks),
        stored_count=stored_count,
        collection_count=collection_count,
    )


def main() -> None:
    summary = run_indexing()
    print(f"Loaded {summary.document_count} markdown files")
    print(f"Created {summary.chunk_count} chunks")
    print("Generated embeddings")
    print(f"Stored {summary.stored_count} vectors")
    print(f"Collection count: {summary.collection_count}")
    print("Indexing complete")


if __name__ == "__main__":
    main()
