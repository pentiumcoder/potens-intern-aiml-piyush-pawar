from app.models.answer import Citation
from app.models.retrieval import RetrievalResult


class CitationBuilder:
    def __init__(self, snippet_length: int = 320) -> None:
        self.snippet_length = snippet_length

    def build(self, retrieved_results: list[RetrievalResult]) -> list[Citation]:
        citations: list[Citation] = []
        seen_chunk_ids: set[str] = set()

        for result in retrieved_results:
            metadata = result.metadata
            if metadata.chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(metadata.chunk_id)
            citations.append(
                Citation(
                    document_id=metadata.document_id,
                    title=metadata.title,
                    heading=metadata.heading,
                    section=metadata.section,
                    chunk_id=metadata.chunk_id,
                    chunk_index=metadata.chunk_index,
                    page=metadata.page,
                    embedding_version=metadata.embedding_version,
                    supporting_snippet=self._snippet(result.chunk.content),
                )
            )

        return citations

    def _snippet(self, content: str) -> str:
        normalized = " ".join(content.split())
        return normalized[: self.snippet_length]
