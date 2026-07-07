from app.models.retrieval import RetrievalResult


REFUSAL_MESSAGE = "I couldn't find sufficient information in the provided documentation."


class HallucinationGuard:
    def __init__(self, minimum_similarity_score: float = 0.5) -> None:
        self.minimum_similarity_score = minimum_similarity_score

    def has_sufficient_evidence(self, retrieved_results: list[RetrievalResult]) -> bool:
        if not retrieved_results:
            return False
        return max(result.similarity_score for result in retrieved_results) >= self.minimum_similarity_score

    def confidence(self, retrieved_results: list[RetrievalResult]) -> float:
        if not retrieved_results:
            return 0.0
        return max(result.similarity_score for result in retrieved_results)
