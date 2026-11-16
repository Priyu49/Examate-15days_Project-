# 🌱 MitraMaati - Soil Health & Nutrient Advisory System

MitraMaati is an intelligent agricultural advisory platform designed to analyze Soil Health Cards (SHC), track macronutrients and micronutrients (NPK, pH, Organic Carbon, etc.), and provide grounded fertilizer and crop recommendations for Indian farmers with strict source citations.

---

## 📅 15-Day Project Roadmap & Daily Progress

| Day | Module / Topic | Key Implementation Files | Status |
| :--- | :--- | :--- | :--- |
| **Day 01** | Project Intro & CLI Menu | `Day01_Intro.py`, `Day01_menu.py` | Completed |
| **Day 02** | Data Structures & Sample Records | `sample_records.py`, `records.py` | Completed |
| **Day 03** | FastAPI Backend & Core Endpoints | `main.py`, `test_main.py` | Completed |
| **Day 04** | Pandas Analytics & Data Exploration | `explore.py`, `data/records.json` | Completed |
| **Day 05** | TF-IDF Smart Search Engine | `smart_search.py` | Completed |
| **Day 06** | LLM Integration & Prompt Engineering | `app/llm.py`, `prompts/` | Completed |
| **Day 07** | Document Chunking & Chroma / Vector Store | `app/chunking.py`, `app/embed.py`, `app/vectorstore.py` | Completed |
| **Day 08** | RAG Pipeline, Citations & Evaluation Set | `app/rag.py`, `POST /ask`, `eval/eval_set.json`, `eval/run_eval.py` | Completed |
---

## 🚀 Key Features & Architecture

* **Soil Health Tracking:** Manages and stores soil test parameters with ideal threshold ranges.
* **Semantic Vector Search:** Retrieves relevant soil FAQ chunks using lightweight cosine similarity and TF-IDF/Chroma vector embedding indexes (`app/vectorstore.py`).
* **Grounded RAG Pipeline (`POST /ask`):** Generates expert agricultural advice paired with explicit document title, source URL, and page citations (`app/rag.py`).
* **Strict Boundary Enforcement:** Automatically triggers `"I don't know based on available Soil Health Card records."` for out-of-scope queries (e.g., weather or market price questions).

---

## 📊 Day 8 RAG Evaluation Winner Table (15-Question Benchmark)

To validate retrieval performance and citation recall, an evaluation harness (`eval/run_eval.py`) was executed across two distinct configurations against our 15-item test suite (`eval/eval_set.json`).

| Config | Chunk Size | Top-K | Answer Accuracy | Citation Recall | Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Config A (Small / Narrow) | 120 chars | 1 | 93.3% | 93.3% | 14/15 | Baseline |
| **Config B (Standard / Top-3)** | **250 chars** | **3** | **100.0%** | **100.0%** | **15/15** | **Winner** |

**Conclusion:** **Config B (`top_k=3`)** is selected as the winning configuration, ensuring 100% answer accuracy and citation recall while successfully enforcing safety boundary rules for unanswerable queries (Q6).

---

## ⚙️ API Endpoints Reference

* `GET /` — Welcome check
* `GET /health` — System health status check
* `GET /records` — Retrieve all tracked soil health records
* `GET /records/{sample_id}` — Retrieve specific soil record details
* `GET /search?q=` — Smart TF-IDF record search
* `GET /search/semantic?q=` — Semantic vector store similarity search
* `POST /ask` — Grounded RAG advisory endpoint with citations and fallback handling

---

## 🛠️ Installation & Local Setup

1. **Clone the Repository:**
   ```powershell
   git clone [https://github.com/Priyu49/Examate-15days_Project-.git](https://github.com/Priyu49/Examate-15days_Project-.git)
   cd Examate-15days_Project-
