from app.models.chunk import Chunk, ChunkMetadata
from app.models.retrieval import RetrievalResult
from app.providers.llm.base import LLMProvider
from app.providers.translator.base import TranslatorProvider
from app.services.citation.builder import CitationBuilder
from app.services.retrieval.answer_service import AnswerService
from app.services.retrieval.hallucination_guard import HallucinationGuard, REFUSAL_MESSAGE


class FakeLLMProvider(LLMProvider):
    def __init__(self, response: str = "FastAPI supports dependency injection.") -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


class FakeTranslatorProvider(TranslatorProvider):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str | None]] = []

    def translate(self, text: str, target_language: str, source_language: str | None = None) -> str:
        self.calls.append((text, target_language, source_language))
        return f"[{target_language}] {text}"


def test_answer_service_refuses_without_evidence_and_does_not_call_llm() -> None:
    llm = FakeLLMProvider()
    service = AnswerService(
        llm_provider=llm,
        hallucination_guard=HallucinationGuard(minimum_similarity_score=0.5),
    )

    response = service.answer("What is FastAPI?", [])

    assert response.refused is True
    assert response.answer == REFUSAL_MESSAGE
    assert response.citations == []
    assert response.confidence == 0.0
    assert llm.prompts == []


def test_answer_service_refuses_below_threshold_without_fabricating_citations() -> None:
    llm = FakeLLMProvider()
    service = AnswerService(
        llm_provider=llm,
        hallucination_guard=HallucinationGuard(minimum_similarity_score=0.8),
    )

    response = service.answer("What is FastAPI?", [_result(score=0.79)])

    assert response.refused is True
    assert response.answer == REFUSAL_MESSAGE
    assert response.citations == []
    assert response.confidence == 0.79
    assert response.retrieved_metadata == [_metadata()]
    assert llm.prompts == []


def test_answer_service_generates_answer_from_evidence_and_builds_citations() -> None:
    llm = FakeLLMProvider(response="Use dependencies to share reusable logic.")
    service = AnswerService(
        llm_provider=llm,
        hallucination_guard=HallucinationGuard(minimum_similarity_score=0.5),
    )

    response = service.answer("How do dependencies work?", [_result(score=0.91)])

    assert response.refused is False
    assert response.answer == "Use dependencies to share reusable logic."
    assert response.confidence == 0.91
    assert len(response.citations) == 1
    assert response.citations[0].chunk_id == "dependencies:0"
    assert response.citations[0].supporting_snippet.startswith("# Dependencies")
    assert "How do dependencies work?" in llm.prompts[0]
    assert "chunk_id: dependencies:0" in llm.prompts[0]
    assert "FastAPI dependencies are reusable callables." in llm.prompts[0]


def test_answer_service_translates_response_when_translator_is_available() -> None:
    translator = FakeTranslatorProvider()
    service = AnswerService(
        llm_provider=FakeLLMProvider(response="Dependencies are reusable."),
        hallucination_guard=HallucinationGuard(minimum_similarity_score=0.5),
        translator_provider=translator,
    )

    response = service.answer("Explain dependencies.", [_result(score=0.9)], response_language="Hindi")

    assert response.answer == "[Hindi] Dependencies are reusable."
    assert translator.calls == [("Dependencies are reusable.", "Hindi", None)]


def test_citation_builder_deduplicates_chunks_and_uses_existing_metadata() -> None:
    result = _result(score=0.9)
    citations = CitationBuilder(snippet_length=20).build([result, result])

    assert len(citations) == 1
    citation = citations[0]
    assert citation.document_id == result.metadata.document_id
    assert citation.title == result.metadata.title
    assert citation.heading == result.metadata.heading
    assert citation.section == result.metadata.section
    assert citation.chunk_id == result.metadata.chunk_id
    assert citation.chunk_index == result.metadata.chunk_index
    assert citation.page is None
    assert citation.embedding_version is None
    assert citation.supporting_snippet == "# Dependencies FastA"


def _result(score: float) -> RetrievalResult:
    chunk = Chunk(
        content="# Dependencies\n\nFastAPI dependencies are reusable callables.",
        metadata=_metadata(),
    )
    return RetrievalResult(chunk=chunk, metadata=chunk.metadata, similarity_score=score)


def _metadata() -> ChunkMetadata:
    return ChunkMetadata(
        document_id="dependencies",
        title="Dependencies",
        heading="Dependencies",
        section="Dependencies",
        chunk_id="dependencies:0",
        chunk_index=0,
        page=None,
        embedding_version=None,
    )
