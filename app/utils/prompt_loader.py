from pathlib import Path


class PromptLoader:
    def __init__(self, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or Path(__file__).resolve().parents[1] / "prompts"

    def render(self, template_name: str, **values: str) -> str:
        template = (self.prompts_dir / template_name).read_text(encoding="utf-8")
        return template.format(**values)
