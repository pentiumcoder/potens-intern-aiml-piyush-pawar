from pydantic import BaseModel, Field, field_validator

from app.models.answer import Citation
from app.models.chunk import ChunkMetadata


class HealthResponse(BaseModel):
    status: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=20)
    response_language: str | None = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("question must not be blank")
        return stripped


class ContradictRequest(BaseModel):
    statement_a: str = Field(..., min_length=1)
    statement_b: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=20)
    response_language: str | None = None

    @field_validator("statement_a", "statement_b")
    @classmethod
    def statement_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("statements must not be blank")
        return stripped


class AnswerApiResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    refused: bool
    retrieved_metadata: list[ChunkMetadata]


class ContradictionApiResponse(AnswerApiResponse):
    pass
