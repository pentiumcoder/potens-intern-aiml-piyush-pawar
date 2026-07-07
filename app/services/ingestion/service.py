from pathlib import Path

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.ingestion.chunker import SectionAwareChunker
from app.services.ingestion.markdown_parser import MarkdownParser


class IngestionService:
    def __init__(
        self,
        documents_dir: Path,
        parser: MarkdownParser | None = None,
        chunker: SectionAwareChunker | None = None,
    ) -> None:
        self.documents_dir = documents_dir
        self.parser = parser or MarkdownParser()
        self.chunker = chunker or SectionAwareChunker()

    def load_documents(self) -> list[Document]:
        markdown_paths = sorted(self.documents_dir.rglob("*.md"))
        return [self.parser.parse_file(path) for path in markdown_paths]

    def build_chunks(self) -> list[Chunk]:
        chunks: list[Chunk] = []
        for document in self.load_documents():
            chunks.extend(self.chunker.chunk_document(document))
        return chunks
