"""
components.py

Streamlit rendering helpers. Each function renders one piece of the UI.
Keeping these separate from app.py keeps the main page flow readable.
"""

from typing import Any, Dict, List, Optional

import streamlit as st

from utils import confidence_level, truncate


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar(is_online: bool, stats: Optional[Dict[str, Any]] = None) -> None:
    """
    Render the sidebar using dynamic stats fetched from the backend
    (APIClient.get_stats(), i.e. the extended /health payload).

    `stats` may be None (backend offline) or missing individual keys
    (older backend not yet extended) - both are shown as "—" rather
    than a hardcoded guess.
    """
    stats = stats or {}

    with st.sidebar:
        st.header("Backend Status")

        if is_online:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Offline")

        st.divider()

        st.markdown("**LLM Model**")
        st.caption(stats.get("llm_model", "—"))

        st.markdown("**Embedding Model**")
        st.caption(stats.get("embedding_model", "—"))

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Indexed Documents", stats.get("indexed_documents", "—"))
        with col2:
            st.metric("Indexed Chunks", stats.get("indexed_chunks", "—"))

        st.metric("Collection Size", stats.get("collection_size", "—"))


# ---------------------------------------------------------------------------
# Sample question buttons
# ---------------------------------------------------------------------------

def render_sample_questions(questions: List[str]) -> Optional[str]:
    """
    Renders sample question buttons in a row.
    Returns the clicked question text, or None if nothing was clicked.
    """
    clicked: Optional[str] = None
    cols = st.columns(len(questions))

    for col, question in zip(cols, questions):
        with col:
            if st.button(question, use_container_width=True):
                clicked = question

    return clicked


# ---------------------------------------------------------------------------
# Answer + confidence
# ---------------------------------------------------------------------------

def render_answer(result: Dict[str, Any]) -> None:
    answer = result.get("answer", "")
    confidence = result.get("confidence", 0.0)
    refused = result.get("refused", False)

    st.subheader("Answer")

    if refused:
        st.warning(answer or "The system could not find enough evidence to answer confidently.")
    else:
        st.markdown(answer)

    pct, level = confidence_level(confidence)
    st.metric(label="Confidence", value=pct, delta=level, delta_color="off")


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------

def render_citations(citations: List[Dict[str, Any]]) -> None:
    st.subheader("Citations")

    if not citations:
        st.caption("No citations returned for this answer.")
        return

    for citation in citations:
        title = citation.get("title") or citation.get("document_id", "Unknown document")
        section = citation.get("section", "")
        heading = citation.get("heading", "")
        snippet = citation.get("supporting_snippet", "")
        chunk_id = citation.get("chunk_id", "")

        with st.container(border=True):
            st.markdown(f"📄 **{title}**")
            if section:
                st.caption(f"Section: {section}")
            if heading:
                st.markdown(f"**Heading:** {heading}")
            if snippet:
                st.markdown(f"> {truncate(snippet)}")
            if chunk_id:
                st.caption(f"chunk_id: {chunk_id}")


# ---------------------------------------------------------------------------
# Retrieved evidence (debug panel)
# ---------------------------------------------------------------------------

def render_retrieved_evidence(retrieved_metadata: List[Dict[str, Any]]) -> None:
    with st.expander("Retrieved Evidence"):
        if not retrieved_metadata:
            st.caption("No retrieved evidence available.")
            return

        for item in retrieved_metadata:
            similarity = item.get("similarity")
            chunk_id = item.get("chunk_id", "")
            document_id = item.get("document_id", "")
            heading = item.get("heading", "")
            section = item.get("section", "")
            snippet = item.get("supporting_snippet", item.get("snippet", ""))

            st.markdown(f"**Chunk:** `{chunk_id}`")
            if similarity is not None:
                st.caption(f"Similarity: {similarity:.3f}")
            st.caption(f"Document: {document_id}")
            if heading:
                st.caption(f"Heading: {heading}")
            if section:
                st.caption(f"Section: {section}")
            if snippet:
                st.markdown(f"> {truncate(snippet, 220)}")
            st.divider()


# ---------------------------------------------------------------------------
# Error state
# ---------------------------------------------------------------------------

def render_backend_unavailable() -> None:
    st.error("Backend unavailable.\n\nPlease start the FastAPI server and try again.")