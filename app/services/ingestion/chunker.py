import re

from app.models.chunk import Chunk, ChunkMetadata
from app.models.document import Document, DocumentSection


class SectionAwareChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 80) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []
        for section in document.sections:
            section_chunks = self._chunk_section(section)
            for section_chunk in section_chunks:
                chunk_index = len(chunks)
                chunk_id = f"{document.document_id}:{chunk_index}"
                chunks.append(
                    Chunk(
                        content=section_chunk,
                        metadata=ChunkMetadata(
                            document_id=document.document_id,
                            title=document.title,
                            heading=section.heading,
                            section=section.section,
                            chunk_id=chunk_id,
                            chunk_index=chunk_index,
                            page=section.page,
                            embedding_version=None,
                        ),
                    )
                )
        return chunks

    def _chunk_section(self, section: DocumentSection) -> list[str]:
        heading_prefix = self._heading_prefix(section)
        body = section.content.strip()
        if not body:
            return []

        if self._word_count(f"{heading_prefix}\n\n{body}") <= self.chunk_size:
            return [f"{heading_prefix}\n\n{body}".strip()]

        body_chunks = self._split_text(body)
        return [f"{heading_prefix}\n\n{chunk}".strip() for chunk in body_chunks]

    def _split_text(self, text: str) -> list[str]:
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
        grouped = self._pack_units(paragraphs)
        if grouped:
            return grouped

        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
        grouped = self._pack_units(sentences)
        if grouped:
            return grouped

        return self._split_words(text)

    def _pack_units(self, units: list[str]) -> list[str]:
        chunks: list[str] = []
        current_units: list[str] = []
        current_size = 0

        for unit in units:
            unit_size = self._word_count(unit)
            if unit_size > self.chunk_size:
                return None

            if current_units and current_size + unit_size > self.chunk_size:
                chunks.append("\n\n".join(current_units))
                overlap_units = self._overlap_units(current_units)
                current_units = overlap_units + [unit]
                current_size = sum(self._word_count(item) for item in current_units)
            else:
                current_units.append(unit)
                current_size += unit_size

        if current_units:
            chunks.append("\n\n".join(current_units))

        return chunks

    def _overlap_units(self, units: list[str]) -> list[str]:
        selected: list[str] = []
        selected_size = 0
        for unit in reversed(units):
            unit_size = self._word_count(unit)
            if selected and selected_size + unit_size > self.overlap:
                break
            selected.insert(0, unit)
            selected_size += unit_size
            if selected_size >= self.overlap:
                break
        return selected

    def _split_words(self, text: str) -> list[str]:
        words = text.split()
        chunks: list[str] = []
        start = 0
        step = self.chunk_size - self.overlap

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start += step

        return chunks

    @staticmethod
    def _heading_prefix(section: DocumentSection) -> str:
        headings = section.section.split(" > ")
        return "\n".join(f"{'#' * min(index + 1, 6)} {heading}" for index, heading in enumerate(headings))

    @staticmethod
    def _word_count(text: str) -> int:
        return len(text.split())
