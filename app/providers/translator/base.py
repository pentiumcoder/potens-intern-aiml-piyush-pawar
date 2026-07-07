from abc import ABC, abstractmethod


class TranslatorProvider(ABC):
    @abstractmethod
    def translate(self, text: str, target_language: str, source_language: str | None = None) -> str:
        raise NotImplementedError
