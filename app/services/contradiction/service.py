from app.models.answer import AnswerResponse
from app.services.retrieval.answer_service import AnswerService
from app.services.retrieval.service import RetrievalService
from app.utils.prompt_loader import PromptLoader


class ContradictionService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        answer_service: AnswerService,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.answer_service = answer_service
        self.prompt_loader = prompt_loader or PromptLoader()

    def evaluate(
        self,
        statement_a: str,
        statement_b: str,
        top_k: int = 10,
        response_language: str | None = None,
    ) -> AnswerResponse:
        query = f"{statement_a}\n{statement_b}"
        retrieved_results = self.retrieval_service.retrieve(query, top_k=top_k)
        question = self.prompt_loader.render(
            "contradiction_question.txt",
            statement_a=statement_a,
            statement_b=statement_b,
        )
        return self.answer_service.answer(
            question=question,
            retrieved_results=retrieved_results,
            response_language=response_language,
        )
