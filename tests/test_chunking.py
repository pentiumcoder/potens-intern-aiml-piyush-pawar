from pathlib import Path

from app.models.document import Document, DocumentSection
from app.services.ingestion.chunker import SectionAwareChunker
from app.services.ingestion.markdown_parser import MarkdownParser


def test_markdown_parser_preserves_heading_hierarchy() -> None:
    markdown = """# FastAPI

Intro text.

## Security

Security overview.

### OAuth2

OAuth2 details.
"""

    document = MarkdownParser().parse(markdown, Path("documents/raw/security.md"))

    assert document.document_id == "security"
    assert document.title == "FastAPI"
    assert [section.heading for section in document.sections] == [
        "FastAPI",
        "Security",
        "OAuth2",
    ]
    assert [section.section for section in document.sections] == [
        "FastAPI",
        "FastAPI > Security",
        "FastAPI > Security > OAuth2",
    ]


def test_chunker_outputs_required_metadata() -> None:
    document = Document(
        document_id="intro",
        title="FastAPI Introduction",
        source_path=Path("documents/raw/introduction.md"),
        sections=[
            DocumentSection(
                heading="Features",
                section="FastAPI Introduction > Features",
                level=2,
                content="FastAPI is fast and easy to use.",
            )
        ],
    )

    chunks = SectionAwareChunker(chunk_size=20, overlap=4).chunk_document(document)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert "# FastAPI Introduction" in chunk.content
    assert "## Features" in chunk.content
    assert chunk.metadata.document_id == "intro"
    assert chunk.metadata.title == "FastAPI Introduction"
    assert chunk.metadata.heading == "Features"
    assert chunk.metadata.section == "FastAPI Introduction > Features"
    assert chunk.metadata.chunk_id == "intro:0"
    assert chunk.metadata.chunk_index == 0
    assert chunk.metadata.page is None
    assert chunk.metadata.embedding_version is None


def test_chunker_splits_long_sections_with_word_overlap() -> None:
    words = [f"word{i}" for i in range(25)]
    document = Document(
        document_id="long-doc",
        title="Long Doc",
        source_path=Path("documents/raw/long-doc.md"),
        sections=[
            DocumentSection(
                heading="Long Section",
                section="Long Doc > Long Section",
                level=2,
                content=" ".join(words),
            )
        ],
    )

    chunks = SectionAwareChunker(chunk_size=10, overlap=3).chunk_document(document)

    assert len(chunks) == 4
    assert chunks[0].metadata.chunk_id == "long-doc:0"
    assert chunks[1].metadata.chunk_id == "long-doc:1"
    assert chunks[0].metadata.section == chunks[1].metadata.section
    assert "word7 word8 word9" in chunks[1].content
    assert "word14 word15 word16" in chunks[2].content


def test_chunker_does_not_mix_sections() -> None:
    document = Document(
        document_id="multi",
        title="Multi",
        source_path=Path("documents/raw/multi.md"),
        sections=[
            DocumentSection(
                heading="First",
                section="Multi > First",
                level=2,
                content="alpha beta gamma",
            ),
            DocumentSection(
                heading="Second",
                section="Multi > Second",
                level=2,
                content="delta epsilon zeta",
            ),
        ],
    )

    chunks = SectionAwareChunker(chunk_size=12, overlap=2).chunk_document(document)

    assert len(chunks) == 2
    assert chunks[0].metadata.section == "Multi > First"
    assert chunks[1].metadata.section == "Multi > Second"
    assert "delta" not in chunks[0].content
    assert "alpha" not in chunks[1].content
