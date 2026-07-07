from app.providers.llm.base import LLMProvider
from app.providers.translator.base import TranslatorProvider
from app.utils.prompt_loader import PromptLoader


class GeminiTranslatorProvider(TranslatorProvider):
    def __init__(self, llm_provider: LLMProvider, prompt_loader: PromptLoader | None = None) -> None:
        self.llm_provider = llm_provider
        self.prompt_loader = prompt_loader or PromptLoader()

    def translate(self, text: str, target_language: str, source_language: str | None = None) -> str:
        prompt = self.prompt_loader.render(
            "translation.txt",
            text=text,
            target_language=target_language,
            source_language=source_language or "auto",
        )
        return self.llm_provider.generate(prompt).strip()
