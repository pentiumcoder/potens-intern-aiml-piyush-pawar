# Potens AI/ML Internship Assignment

## Project

Document Question Answering (RAG) with Citations

---

## Goal

Build a multilingual Retrieval-Augmented Generation (RAG) system over FastAPI documentation.

The system must:

- Answer questions grounded only in the provided documents
- Return citations
- Detect contradictions between documents
- Refuse to answer when evidence is insufficient
- Support multilingual queries
- Provide REST APIs and a Streamlit UI

---

# Tech Stack

Backend
- FastAPI

LLM
- Gemini 2.5 Flash

Embedding Model
- intfloat/multilingual-e5-base

Vector Database
- ChromaDB

Document Parsing
- PyMuPDF

Language Detection
- lingua-language-detector

UI
- Streamlit

Testing
- pytest

Deployment
- Docker

---

# Architecture

Streamlit

↓

FastAPI

↓

RAG Service

↓

Language Detection

↓

Translation

↓

Embedding

↓

Retriever

↓

Confidence Gate

↓

Gemini

↓

Citation Builder

↓

Response

---

# Project Structure

app/

api/

providers/

services/

schemas/

models/

utils/

prompts/

documents/

tests/

ui/

---

# Provider Layer

The provider layer contains wrappers around external systems.

Providers:

- EmbeddingProvider
- LLMProvider
- TranslatorProvider
- VectorStoreProvider

Business logic must never call external SDKs directly.

---

# Service Layer

Services orchestrate providers.

Services:

- IngestionService
- RetrievalService
- CitationService
- ContradictionService

---

# Chunking Strategy

Use section-aware chunking.

Rules:

- Preserve headings
- Preserve sections
- Recursive chunking for long sections
- Chunk size approximately 500 tokens
- 80-token overlap

Metadata:

- document_id
- title
- page
- section
- chunk_id
- embedding_version

---

# Retrieval Pipeline

Detect language

↓

Translate query if needed

↓

Embed

↓

Retrieve Top 10

↓

(Optional rerank)

↓

Confidence check

↓

Generate answer

↓

Attach citations

↓

Translate response

---

# Hallucination Policy

The LLM must never answer without supporting evidence.

If retrieval confidence is below threshold:

"I couldn't find sufficient information in the provided documentation."

---

# Citation Format

Every citation must contain:

- source file
- page
- section
- chunk id
- supporting snippet

---

# API Endpoints

POST /ask

POST /contradict

---

# Streamlit

Show:

Question

Answer

Confidence

Retrieved chunks

Sources

Debug mode

---

# Code Standards

- Type hints everywhere
- Pydantic models
- Dependency Injection
- SOLID principles
- Small modules
- No business logic in routes
- No LangChain

---

# Git Strategy

Commit after every milestone.

No massive commits.

---

# Stretch Goals

- Reranker
- Confidence score
- Evaluation dataset