from google import genai

from app.providers.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text or ""
