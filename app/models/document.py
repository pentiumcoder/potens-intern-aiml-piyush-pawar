from pathlib import Path

from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    heading: str
    section: str
    level: int
    content: str
    page: int | None = None


class Document(BaseModel):
    document_id: str
    title: str
    source_path: Path
    sections: list[DocumentSection] = Field(default_factory=list)
