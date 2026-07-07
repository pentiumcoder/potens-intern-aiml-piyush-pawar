from app.models.answer import AnswerResponse
from app.models.retrieval import RetrievalResult
from app.providers.llm.base import LLMProvider
from app.providers.translator.base import TranslatorProvider
from app.services.citation.builder import CitationBuilder
from app.services.retrieval.hallucination_guard import HallucinationGuard, REFUSAL_MESSAGE
from app.utils.prompt_loader import PromptLoader


class AnswerService:
    def __init__(
        self,
        llm_provider: LLMProvider,
        hallucination_guard: HallucinationGuard | None = None,
        citation_builder: CitationBuilder | None = None,
        prompt_loader: PromptLoader | None = None,
        translator_provider: TranslatorProvider | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.hallucination_guard = hallucination_guard or HallucinationGuard()
        self.citation_builder = citation_builder or CitationBuilder()
        self.prompt_loader = prompt_loader or PromptLoader()
        self.translator_provider = translator_provider

    def answer(
        self,
        question: str,
        retrieved_results: list[RetrievalResult],
        response_language: str | None = None,
    ) -> AnswerResponse:
        confidence = self.hallucination_guard.confidence(retrieved_results)
        metadata = [result.metadata for result in retrieved_results]

        if not self.hallucination_guard.has_sufficient_evidence(retrieved_results):
            refusal = self._translate_if_needed(REFUSAL_MESSAGE, response_language)
            return AnswerResponse(
                answer=refusal,
                citations=[],
                confidence=confidence,
                refused=True,
                retrieved_metadata=metadata,
            )

        prompt = self.prompt_loader.render(
            "grounded_answer.txt",
            question=question,
            evidence=self._format_evidence(retrieved_results),
        )
        answer = self.llm_provider.generate(prompt).strip()
        answer = self._translate_if_needed(answer, response_language)

        return AnswerResponse(
            answer=answer,
            citations=self.citation_builder.build(retrieved_results),
            confidence=confidence,
            refused=False,
            retrieved_metadata=metadata,
        )

    def _translate_if_needed(self, text: str, response_language: str | None) -> str:
        if not response_language or response_language.lower() in {"en", "english"}:
            return text
        if self.translator_provider is None:
            return text
        return self.translator_provider.translate(text, target_language=response_language)

    @staticmethod
    def _format_evidence(retrieved_results: list[RetrievalResult]) -> str:
        evidence_blocks: list[str] = []
        for index, result in enumerate(retrieved_results, start=1):
            metadata = result.metadata
            evidence_blocks.append(
                "\n".join(
                    [
                        f"[Evidence {index}]",
                        f"chunk_id: {metadata.chunk_id}",
                        f"title: {metadata.title}",
                        f"heading: {metadata.heading}",
                        f"section: {metadata.section}",
                        f"page: {metadata.page}",
                        f"similarity_score: {result.similarity_score:.4f}",
                        "content:",
                        result.chunk.content,
                    ]
                )
            )
        return "\n\n".join(evidence_blocks)
