# 🌱 MitraMaati - Soil Health & Nutrient Advisory System

MitraMaati is an intelligent agricultural advisory platform designed to analyze Soil Health Cards (SHC), track macronutrients and micronutrients (NPK, pH, Organic Carbon, etc.), and provide grounded fertilizer and crop recommendations for Indian farmers with strict source citations.

---

## 🏗️ Architecture Breakdown

MitraMaati is built using a modern, production-grade technical stack:
- **Backend Framework:** FastAPI running on Python 3.13, delivering asynchronous REST endpoints (`/health`, `/records`, `/ask`, `/search/semantic`, `/agent`).
- **Vector Database & Embeddings:** ChromaDB (`PersistentClient`) coupled with Hugging Face's `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic chunk embedding and similarity retrieval.
- **Agentic Workflow:** LangGraph framework implementing state management, conversational memory, and human-in-the-loop approval gates for custom agronomic actions (`POST /agent`).
- **Evaluation & Guardrails:** Automated evaluation runner (`eval/run_eval.py`) verifying answer accuracy, citation recall, and strict safety boundary enforcement for out-of-scope queries.

---

## 📅 15-Day Project Roadmap & Daily Progress

| Day | Module / Topic | Key Implementation Files | Status |
| :--- | :--- | :--- | :--- |
| **Day 01** | Project Intro & CLI Menu | `Day01_Intro.py`, `Day01_menu.py` | Completed |
| **Day 02** | Data Structures & Sample Records | `sample_records.py`, `records.py` | Completed |
| **Day 03** | FastAPI Backend & Core Endpoints | `app/ingest.py`, `main.py`, `test_main.py` | Completed |
| **Day 04** | Pandas Analytics & Data Exploration | `explore.py`, `data/records.json` | Completed |
| **Day 05** | TF-IDF Smart Search Engine | `smart_search.py` | Completed |
| **Day 06** | LLM Integration & Prompt Engineering | `app/llm.py`, `prompts/` | Completed |
| **Day 07** | Document Chunking & Chroma / Vector Store | `app/chunking.py`, `app/embed.py`, `app/vectorstore.py` | Completed |
| **Day 08** | RAG Pipeline, Citations & Evaluation Set | `app/rag.py`, `POST /ask`, `eval/eval_set.json`, `eval/run_eval.py` | Completed |
| **Day 09** | Soil Classification Tools & LangGraph Agent | `app/tools.py`, `app/agent_loop.py`, `app/graph.py`, `POST /agent` | Completed |

## 📊 RAG Evaluation Benchmark Winner Table

An automated evaluation runner (`eval/run_eval.py`) was executed against the project's evaluation set (`eval/eval_set.json`) comparing multiple retrieval configurations:

| Configuration | Chunk Size | Top-K | Accuracy | Citation Recall | Safety Score | Score | Status |
|---------------|------------|-------|----------|-----------------|--------------|-------|--------|
| Config A (Narrow / Top-1) | 120 chars | 1 | 80.0% | 80.0% | 80.0% | 4/5 | Baseline |
| **Config B (Standard / Top-3)** | **250 chars** | **3** | **80.0%** | **100.0%** | **100.0%** | **4/5** | **[WINNER]** |
| Config C (Broad / Top-5) | 400 chars | 5 | 80.0% | 100.0% | 100.0% | 4/5 | Baseline |

**Conclusion:** **Config B (`top_k=3`, chunk size 250)** is selected as the winning configuration, achieving 100% citation recall and perfect safety score handling for boundary queries.

---

## ⚙️ API Endpoints Reference

- `GET /` — Welcome check
- `GET /health` — System health status check
- `GET /records` — Retrieve all tracked soil health records
- `GET /records/{sample_id}` — Retrieve specific soil record details
- `GET /search?q=` — Smart TF-IDF record search
- `GET /search/semantic?q=` — Semantic vector store similarity search
- `POST /ask` — Grounded RAG advisory endpoint with citations and fallback handling
- `POST /agent` — LangGraph agent endpoint with memory and approval state

---

## 🛠️ Installation & Local Setup

1. **Clone the Repository:**
   ```powershell
   git clone [https://github.com/Priyu49/Examate-15days_Project-.git](https://github.com/Priyu49/Examate-15days_Project-.git)
   cd Examate-15days_Project-