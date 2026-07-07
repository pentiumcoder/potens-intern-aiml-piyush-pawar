from fastapi.testclient import TestClient

from app.api.dependencies import get_answer_service, get_contradiction_service, get_retrieval_service
from app.main import app
from app.models.answer import AnswerResponse
from app.models.chunk import Chunk, ChunkMetadata
from app.models.retrieval import RetrievalResult


client = TestClient(app)


class FakeRetrievalService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def retrieve(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        self.calls.append((query, top_k))
        return [_retrieval_result()]


class FakeAnswerService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[RetrievalResult], str | None]] = []

    def answer(
        self,
        question: str,
        retrieved_results: list[RetrievalResult],
        response_language: str | None = None,
    ) -> AnswerResponse:
        self.calls.append((question, retrieved_results, response_language))
        return _answer_response(refused=False)


class FakeContradictionService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int, str | None]] = []

    def evaluate(
        self,
        statement_a: str,
        statement_b: str,
        top_k: int = 10,
        response_language: str | None = None,
    ) -> AnswerResponse:
        self.calls.append((statement_a, statement_b, top_k, response_language))
        return _answer_response(refused=False, answer="No contradiction found.")


def setup_function() -> None:
    app.dependency_overrides.clear()


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint_orchestrates_retrieval_and_answer_services() -> None:
    retrieval_service = FakeRetrievalService()
    answer_service = FakeAnswerService()
    app.dependency_overrides[get_retrieval_service] = lambda: retrieval_service
    app.dependency_overrides[get_answer_service] = lambda: answer_service

    response = client.post(
        "/ask",
        json={"question": " What is FastAPI? ", "top_k": 3, "response_language": "English"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "FastAPI is a Python web framework."
    assert payload["refused"] is False
    assert payload["confidence"] == 0.9
    assert payload["citations"][0]["chunk_id"] == "intro:0"
    assert retrieval_service.calls == [("What is FastAPI?", 3)]
    assert answer_service.calls[0][0] == "What is FastAPI?"
    assert answer_service.calls[0][1][0].metadata.chunk_id == "intro:0"
    assert answer_service.calls[0][2] == "English"


def test_ask_endpoint_rejects_blank_question() -> None:
    response = client.post("/ask", json={"question": "   "})

    assert response.status_code == 422


def test_contradict_endpoint_orchestrates_contradiction_service() -> None:
    contradiction_service = FakeContradictionService()
    app.dependency_overrides[get_contradiction_service] = lambda: contradiction_service

    response = client.post(
        "/contradict",
        json={
            "statement_a": "FastAPI supports dependencies.",
            "statement_b": "FastAPI does not support dependencies.",
            "top_k": 4,
            "response_language": "English",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "No contradiction found."
    assert payload["citations"][0]["section"] == "Introduction"
    assert contradiction_service.calls == [
        (
            "FastAPI supports dependencies.",
            "FastAPI does not support dependencies.",
            4,
            "English",
        )
    ]


def test_contradict_endpoint_rejects_blank_statement() -> None:
    response = client.post(
        "/contradict",
        json={"statement_a": "FastAPI supports dependencies.", "statement_b": " "},
    )

    assert response.status_code == 422


def _answer_response(refused: bool, answer: str = "FastAPI is a Python web framework.") -> AnswerResponse:
    metadata = _metadata()
    return AnswerResponse(
        answer=answer,
        citations=[
            {
                "document_id": metadata.document_id,
                "title": metadata.title,
                "heading": metadata.heading,
                "section": metadata.section,
                "chunk_id": metadata.chunk_id,
                "chunk_index": metadata.chunk_index,
                "page": metadata.page,
                "embedding_version": metadata.embedding_version,
                "supporting_snippet": "FastAPI is a modern Python web framework.",
            }
        ],
        confidence=0.9,
        refused=refused,
        retrieved_metadata=[metadata],
    )


def _retrieval_result() -> RetrievalResult:
    chunk = Chunk(
        content="# FastAPI\n\nFastAPI is a modern Python web framework.",
        metadata=_metadata(),
    )
    return RetrievalResult(chunk=chunk, metadata=chunk.metadata, similarity_score=0.9)


def _metadata() -> ChunkMetadata:
    return ChunkMetadata(
        document_id="intro",
        title="FastAPI",
        heading="FastAPI",
        section="Introduction",
        chunk_id="intro:0",
        chunk_index=0,
        page=None,
        embedding_version=None,
    )
