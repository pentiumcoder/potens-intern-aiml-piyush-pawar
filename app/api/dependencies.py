from functools import lru_cache
from pathlib import Path

from app.models.answer import AnswerResponse
from app.models.retrieval import RetrievalResult
from app.config.settings import settings
from app.providers.llm.base import LLMProvider
from app.services.citation.builder import CitationBuilder
from app.services.contradiction.service import ContradictionService
from app.services.retrieval.answer_service import AnswerService
from app.services.retrieval.hallucination_guard import HallucinationGuard
from app.services.retrieval.service import RetrievalService


class LazyRetrievalService:
    def __init__(self) -> None:
        self._service: RetrievalService | None = None

    def retrieve(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        return self._get_service().retrieve(query, top_k=top_k)

    def _get_service(self) -> RetrievalService:
        if self._service is None:
            self._service = _build_retrieval_service()
        return self._service


class LazyAnswerService:
    def __init__(self) -> None:
        self._service: AnswerService | None = None

    def answer(
        self,
        question: str,
        retrieved_results: list[RetrievalResult],
        response_language: str | None = None,
    ) -> AnswerResponse:
        return self._get_service().answer(
            question=question,
            retrieved_results=retrieved_results,
            response_language=response_language,
        )

    def _get_service(self) -> AnswerService:
        if self._service is None:
            self._service = _build_answer_service()
        return self._service


def _build_retrieval_service() -> RetrievalService:
    from app.providers.embeddings.sentence_transformer import SentenceTransformerEmbeddingProvider
    from app.providers.vectorstore.chroma import ChromaVectorStore

    embedding_provider = SentenceTransformerEmbeddingProvider(settings.embedding_model)
    vector_store = ChromaVectorStore(Path(settings.vector_db_path))
    return RetrievalService(embedding_provider, vector_store)


def _build_llm_provider() -> LLMProvider:
    from app.providers.llm.gemini import GeminiProvider

    return GeminiProvider(api_key=settings.gemini_api_key, model_name=settings.gemini_model)


def _build_answer_service() -> AnswerService:
    return AnswerService(
        llm_provider=_build_llm_provider(),
        hallucination_guard=get_hallucination_guard(),
        citation_builder=get_citation_builder(),
    )


@lru_cache
def get_retrieval_service() -> LazyRetrievalService:
    return LazyRetrievalService()


@lru_cache
def get_hallucination_guard() -> HallucinationGuard:
    return HallucinationGuard()


@lru_cache
def get_citation_builder() -> CitationBuilder:
    return CitationBuilder()


@lru_cache
def get_answer_service() -> LazyAnswerService:
    return LazyAnswerService()


@lru_cache
def get_contradiction_service() -> ContradictionService:
    return ContradictionService(
        retrieval_service=get_retrieval_service(),
        answer_service=get_answer_service(),
    )
