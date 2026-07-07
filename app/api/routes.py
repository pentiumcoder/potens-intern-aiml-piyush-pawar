from fastapi import APIRouter, Depends, status

from app.schemas.api import (
    AnswerApiResponse,
    AskRequest,
    ContradictRequest,
    ContradictionApiResponse,
    HealthResponse,
)
from app.services.contradiction.service import ContradictionService
from app.services.retrieval.answer_service import AnswerService
from app.services.retrieval.service import RetrievalService
from app.api.dependencies import get_answer_service, get_contradiction_service, get_retrieval_service


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["health"],
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post(
    "/ask",
    response_model=AnswerApiResponse,
    status_code=status.HTTP_200_OK,
    tags=["qa"],
)
def ask(
    request: AskRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    answer_service: AnswerService = Depends(get_answer_service),
) -> AnswerApiResponse:
    retrieved_results = retrieval_service.retrieve(request.question, top_k=request.top_k)
    answer = answer_service.answer(
        question=request.question,
        retrieved_results=retrieved_results,
        response_language=request.response_language,
    )
    return AnswerApiResponse(**answer.model_dump())


@router.post(
    "/contradict",
    response_model=ContradictionApiResponse,
    status_code=status.HTTP_200_OK,
    tags=["qa"],
)
def contradict(
    request: ContradictRequest,
    contradiction_service: ContradictionService = Depends(get_contradiction_service),
) -> ContradictionApiResponse:
    answer = contradiction_service.evaluate(
        statement_a=request.statement_a,
        statement_b=request.statement_b,
        top_k=request.top_k,
        response_language=request.response_language,
    )
    return ContradictionApiResponse(**answer.model_dump())
