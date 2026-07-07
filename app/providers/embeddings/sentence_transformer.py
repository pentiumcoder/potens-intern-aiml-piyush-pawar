from sentence_transformers import SentenceTransformer

from app.providers.embeddings.base import EmbeddingProvider


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "intfloat/multilingual-e5-base") -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    @property
    def embedding_version(self) -> str:
        return self.model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        passages = [self._format_passage(text) for text in texts]
        return self.model.encode(
            passages,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode(
            self._format_query(query),
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

    @staticmethod
    def _format_passage(text: str) -> str:
        return f"passage: {text}"

    @staticmethod
    def _format_query(query: str) -> str:
        return f"query: {query}"
