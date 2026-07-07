"""
api.py

Thin HTTP client for the FastAPI backend.

The Streamlit UI must never talk to Chroma or Gemini directly, and must never
import backend services. This module is the ONLY place that makes network
calls to the backend.
"""

from typing import Any, Dict, Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BACKEND_URL = "http://localhost:8000"

DEFAULT_TIMEOUT = 30  # seconds


class BackendUnavailableError(Exception):
    """Raised when the FastAPI backend cannot be reached."""


class APIClient:
    """Small wrapper around the FastAPI backend HTTP API."""

    def __init__(self, base_url: str = BACKEND_URL, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -- internal helper ----------------------------------------------------

    def _get(self, path: str) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}{path}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise BackendUnavailableError(str(exc)) from exc

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}{path}", json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise BackendUnavailableError(str(exc)) from exc

    # -- public API -----------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Check backend health. Raises BackendUnavailableError if unreachable."""
        return self._get("/health")

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question against the document corpus.

        Returns the /ask response payload:
        {
            "answer": str,
            "confidence": float,
            "refused": bool,
            "citations": [...],
            "retrieved_metadata": [...]
        }
        """
        return self._post("/ask", {"question": question})

    def contradict(self, question: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call the /contradict endpoint.

        Extra keyword arguments are passed through in the request body,
        since the exact contradiction-check payload is defined by the
        already-implemented backend endpoint.
        """
        payload: Dict[str, Any] = {"question": question}
        payload.update(kwargs)
        return self._post("/contradict", payload)

    def is_online(self) -> bool:
        """Convenience helper for sidebar status - never raises."""
        try:
            self.health()
            return True
        except BackendUnavailableError:
            return False

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        Fetch backend/index stats for the sidebar from /health.

        Expects (new, extended) /health schema:
        {
            "status": "ok",
            "llm_model": "gemini-2.5-flash",
            "embedding_model": "multilingual-e5-base",
            "indexed_documents": 7,
            "indexed_chunks": 85,
            "collection_size": 85
        }

        Returns None if the backend is unreachable. Missing individual
        fields are tolerated - callers should treat them as unknown ("—")
        rather than assume old hardcoded values.
        """
        try:
            return self.health()
        except BackendUnavailableError:
            return None