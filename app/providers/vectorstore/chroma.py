from pathlib import Path
from typing import Any

import chromadb

from app.models.chunk import Chunk, ChunkMetadata
from app.models.retrieval import RetrievalResult
from app.providers.vectorstore.base import VectorStoreProvider


class ChromaVectorStore(VectorStoreProvider):
    def __init__(
        self,
        persist_directory: str | Path = "./chroma_db",
        collection_name: str = "document_chunks",
    ) -> None:
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        if not chunks:
            return

        self.collection.upsert(
            ids=[chunk.metadata.chunk_id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.content for chunk in chunks],
            metadatas=[self._metadata_to_chroma(chunk.metadata) for chunk in chunks],
        )

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[RetrievalResult]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieval_results: list[RetrievalResult] = []
        for document, metadata, distance in zip(documents, metadatas, distances):
            chunk_metadata = self._metadata_from_chroma(metadata)
            chunk = Chunk(content=document, metadata=chunk_metadata)
            retrieval_results.append(
                RetrievalResult(
                    chunk=chunk,
                    metadata=chunk_metadata,
                    similarity_score=self._distance_to_similarity(float(distance)),
                )
            )

        return retrieval_results

    @staticmethod
    def _metadata_to_chroma(metadata: ChunkMetadata) -> dict[str, str | int]:
        return {
            "document_id": metadata.document_id,
            "title": metadata.title,
            "heading": metadata.heading,
            "section": metadata.section,
            "chunk_id": metadata.chunk_id,
            "chunk_index": metadata.chunk_index,
            "page": "" if metadata.page is None else metadata.page,
            "embedding_version": metadata.embedding_version or "",
        }

    @staticmethod
    def _metadata_from_chroma(metadata: dict[str, Any]) -> ChunkMetadata:
        page = metadata.get("page")
        embedding_version = metadata.get("embedding_version")
        return ChunkMetadata(
            document_id=str(metadata["document_id"]),
            title=str(metadata["title"]),
            heading=str(metadata["heading"]),
            section=str(metadata["section"]),
            chunk_id=str(metadata["chunk_id"]),
            chunk_index=int(metadata["chunk_index"]),
            page=None if page == "" else int(page),
            embedding_version=None if embedding_version == "" else str(embedding_version),
        )

    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        return max(0.0, min(1.0, 1.0 - distance))
