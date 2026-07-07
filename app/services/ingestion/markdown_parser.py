import re
from pathlib import Path

from app.models.document import Document, DocumentSection


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


class MarkdownParser:
    def parse_file(self, path: Path) -> Document:
        content = path.read_text(encoding="utf-8")
        return self.parse(content=content, source_path=path)

    def parse(self, content: str, source_path: Path) -> Document:
        document_id = source_path.stem
        title = source_path.stem.replace("-", " ").title()
        sections: list[DocumentSection] = []
        heading_stack: list[tuple[int, str]] = []
        current_heading = title
        current_level = 1
        current_lines: list[str] = []

        def flush_section() -> None:
            text = "\n".join(current_lines).strip()
            if not text:
                return
            section_path = self._format_section(heading_stack) or current_heading
            sections.append(
                DocumentSection(
                    heading=current_heading,
                    section=section_path,
                    level=current_level,
                    content=text,
                )
            )

        for line in content.splitlines():
            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                flush_section()
                current_lines = []
                level = len(heading_match.group(1))
                heading = heading_match.group(2).strip()
                heading_stack = [
                    (existing_level, existing_heading)
                    for existing_level, existing_heading in heading_stack
                    if existing_level < level
                ]
                heading_stack.append((level, heading))
                current_heading = heading
                current_level = level
                if level == 1:
                    title = heading
                continue

            current_lines.append(line)

        flush_section()

        if not sections and content.strip():
            sections.append(
                DocumentSection(
                    heading=title,
                    section=title,
                    level=1,
                    content=content.strip(),
                )
            )

        return Document(
            document_id=document_id,
            title=title,
            source_path=source_path,
            sections=sections,
        )

    @staticmethod
    def _format_section(heading_stack: list[tuple[int, str]]) -> str:
        return " > ".join(heading for _, heading in heading_stack)
