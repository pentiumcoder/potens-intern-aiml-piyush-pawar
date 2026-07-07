"""
utils.py

Small formatting / presentation helpers used by app.py and components.py.
No network calls and no business logic live here.
"""

from typing import Tuple


def confidence_badge(confidence: float) -> Tuple[str, str]:
    """
    Map a confidence score (0.0-1.0) to a colored label and percentage string.

    Returns (label, percentage_str), e.g. ("🟢 High", "91%")
    Kept for any callers that still want the emoji-combined form.
    """
    pct = round(confidence * 100)

    if confidence >= 0.75:
        label = "🟢 High"
    elif confidence >= 0.45:
        label = "🟡 Medium"
    else:
        label = "🔴 Low"

    return label, f"{pct}%"


def confidence_level(confidence: float) -> Tuple[str, str]:
    """
    Same thresholds as confidence_badge, split for use with st.metric().

    Returns (percentage_str, level_str), e.g. ("91%", "High")
    """
    pct = round(confidence * 100)

    if confidence >= 0.75:
        level = "High"
    elif confidence >= 0.45:
        level = "Medium"
    else:
        level = "Low"

    return f"{pct}%", level


def truncate(text: str, max_chars: int = 280) -> str:
    """Truncate long snippets for display, adding an ellipsis if cut."""
    if text is None:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


EMPTY_QUESTION_MESSAGE = "Ask a question about the indexed documentation."


SAMPLE_QUESTIONS = [
    "What are dependencies in FastAPI?",
    "How do response models work?",
    "Explain background tasks.",
    "How is security implemented?",
]