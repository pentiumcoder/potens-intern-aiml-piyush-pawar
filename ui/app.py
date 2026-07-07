"""
app.py

Single-page Streamlit frontend for the Document Q&A with Citations RAG system.

This UI talks ONLY to the FastAPI backend via APIClient (api.py).
It never calls Gemini or Chroma directly, and never imports backend services.

All HTTP calls: api.py
All rendering: components.py
All formatting helpers: utils.py
This file only orchestrates page flow and session state.
"""

import streamlit as st

from api import APIClient, BackendUnavailableError
from components import (
    render_answer,
    render_backend_unavailable,
    render_citations,
    render_retrieved_evidence,
    render_sample_questions,
    render_sidebar,
)
from utils import EMPTY_QUESTION_MESSAGE, SAMPLE_QUESTIONS

st.set_page_config(
    page_title="Document Q&A with Citations",
    page_icon="📄",
    layout="wide",
)

client = APIClient()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "auto_submit" not in st.session_state:
    st.session_state.auto_submit = False

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------

st.title("📄 Document Q&A with Citations")
st.caption("Ask grounded questions over the indexed documentation. Answers are cited and refuse to guess.")

# ---------------------------------------------------------------------------
# Sidebar (backend status + dynamic index stats)
# ---------------------------------------------------------------------------

backend_online = client.is_online()
backend_stats = client.get_stats() if backend_online else None
render_sidebar(is_online=backend_online, stats=backend_stats)

# ---------------------------------------------------------------------------
# Sample questions (auto-submit on click)
# ---------------------------------------------------------------------------

st.subheader("Ask a Question")
st.caption("Try a sample question:")

clicked_question = render_sample_questions(SAMPLE_QUESTIONS)
if clicked_question:
    st.session_state.question_input = clicked_question
    st.session_state.auto_submit = True
    st.rerun()

# ---------------------------------------------------------------------------
# Question input
# ---------------------------------------------------------------------------

with st.container(border=True):
    question = st.text_area(
        "Your question",
        height=100,
        key="question_input",
        placeholder=EMPTY_QUESTION_MESSAGE,
    )

    ask_clicked = st.button("Ask", type="primary")

# A sample-question click counts as an implicit "Ask" on this rerun.
should_ask = ask_clicked or st.session_state.auto_submit
st.session_state.auto_submit = False

# ---------------------------------------------------------------------------
# Handle submission
# ---------------------------------------------------------------------------

if should_ask:
    if not question.strip():
        st.info(EMPTY_QUESTION_MESSAGE)
    elif not backend_online:
        render_backend_unavailable()
    else:
        with st.spinner("Searching documentation..."):
            try:
                result = client.ask(question)
            except BackendUnavailableError:
                result = None
                render_backend_unavailable()

        if result is not None:
            st.divider()
            with st.container(border=True):
                render_answer(result)
            st.divider()
            render_citations(result.get("citations", []))
            render_retrieved_evidence(result.get("retrieved_metadata", []))