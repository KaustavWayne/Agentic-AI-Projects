<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=60&pause=1000&color=3670A0&center=true&vCenter=true&width=1000&height=200&lines=%E2%9A%A1+QuizForge;%F0%9F%9A%80+AI+MCQ+Generator;%F0%9F%93%9D+PDF+to+Knowledge" alt="QuizForge Banner" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=langgraph&logoColor=white" alt="LangGraph">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
</p>

---

## 🌟 Introduction

**QuizForge** is a sophisticated AI-powered MCQ generator designed to transform study notes and PDF documents into high-quality, context-aware multiple-choice questions. By leveraging **LangGraph** for workflow orchestration and **Groq** for high-speed LLM inference, it ensures that generated questions test deep conceptual understanding rather than simple surface-level recall.

> Transform notes into razor-sharp MCQs that test deep understanding, not surface recall.

---

## 🏷️ Product Name Suggestions

| Name | Why it works |
|------|-------------|
| **QuizForge** | "Forging" implies crafting with precision; implies strength & quality |
| **NeuralQuiz** | Signals AI-native origin; clean, modern |
| **DeepDrill** | Implies going beneath surface-level recall |
| **ContextCraft** | Emphasises context-aware, non-pattern questions |
| **MindSieve** | The system *sifts* understanding from mere memorisation |

---

## 📁 Project Structure

```
mcq_generator/
├── app/
│   └── streamlit_app.py       # Streamlit UI (entry point)
├── core/
│   ├── graph.py               # LangGraph workflow (Generator → Validator → Formatter)
│   └── llm_client.py          # Groq LLM init + tool binding
├── models/
│   └── schemas.py             # Pydantic: MCQ, MCQSet, GraphState
├── prompts/
│   └── mcq_prompts.py         # Generation + repair prompts
├── tools/
│   └── validation_tool.py     # MCQ validation tool (bound to LLM)
├── services/
│   └── mcq_service.py         # Public service API
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📄 PDF Upload Support

No RAG required. The system extracts text directly from the PDF and passes it to the LLM.

**How it works:**
1. User uploads a PDF via the UI
2. `pdf_service.py` extracts text using **PyMuPDF** (fast, primary) with **pdfplumber** as fallback
3. Text is cleaned (removes page numbers, junk chars, excess whitespace)
4. If > 12,000 characters, smart-truncated at a sentence boundary
5. Extracted text is passed directly to the same MCQ generation pipeline

**Limitations:**
- Scanned / image-only PDFs (no text layer) are **not supported** — OCR is not included
- Very large PDFs (100+ pages) will be truncated to the first ~12,000 chars
- Password-protected PDFs will fail gracefully with a clear error message

**When would you need RAG + Pinecone?**
Only if you need to handle entire textbooks (300+ pages) without truncation, or build a persistent question bank that searches across many uploaded documents.

---

## 🚀 Quick Start

```bash
# 1. Clone / create the project folder
cd mcq_generator

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key
cp .env.example .env
# Edit .env → add your GROQ_API_KEY
# Get a free key: https://console.groq.com

# 5. Run the app
streamlit run app/streamlit_app.py
```

---

## 🔑 Environment Variables

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

---

## 🏗️ Architecture

```
User Notes
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                    LangGraph Workflow                │
│                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────┐ │
│  │  Generator  │───▶│  Validator  │───▶│Formatter│ │
│  │   Node      │◀───│   Node      │    │  Node   │ │
│  │             │    │             │    │         │ │
│  │ Groq LLM    │    │ Pydantic    │    │ MCQSet  │ │
│  │ + Tool      │    │ + Tool Call │    │ output  │ │
│  └─────────────┘    └─────────────┘    └─────────┘ │
│         │                                           │
│         ▼                                           │
│   validate_mcqs (Tool)                              │
│   • Checks labels A/B/C/D                           │
│   • No duplicate options                            │
│   • correct_answer in options                       │
│   • No duplicate questions                          │
└─────────────────────────────────────────────────────┘
    │
    ▼
Streamlit UI (Card-based MCQ display)
```

---

## ❓ RAG / Pinecone — Do You Need It?

### For this use case: **No, RAG is NOT required.**

**Why?**
- The user's notes ARE the context. They fit comfortably in Groq's 8192-token window.
- There is no retrieval step — we generate FROM the notes, not search a knowledge base.

### When WOULD you use Pinecone?

| Scenario | Use Pinecone? |
|----------|--------------|
| Notes < 8000 tokens, single session | ❌ Not needed |
| Large document sets (textbooks, PDFs) | ✅ Yes — chunk + embed + retrieve |
| Question bank deduplication across sessions | ✅ Yes — store past Q embeddings |
| Multi-user platform with shared question bank | ✅ Yes |

### Does Pinecone auto-create the database?

**No.** You must:
1. Create an account at pinecone.io
2. Create an **Index** (choose dimensions matching your embedding model, e.g. 1536 for OpenAI)
3. Pinecone creates the vector store; you populate it via `pinecone.upsert()`

---

## 🧠 Key Design Decisions

1. **No ChatPromptTemplate** — Direct f-string prompts for full control and debuggability
2. **Tool binding** — LLM self-validates before returning; repair loop for failures
3. **Pydantic v2** — Strict validation at every layer (not just the final output)
4. **Retry logic** — Up to 3 attempts with targeted repair prompts
5. **Service layer** — Streamlit never imports LangGraph directly; testable in isolation
6. **`@lru_cache`** — LLM client cached; no re-init on every user request

---

## 📊 Rate Limit Awareness (Free Tier)

| API | Free Tier Limit | Mitigation |
|-----|----------------|-----------|
| Groq (llama3-8b-8192) | 30 RPM / 14400 RPD | `@lru_cache` on LLM; avoid retries on non-validation errors |
| Tavily (if added) | 1000 req/month | Not used in this system |

---

---

## 👨‍💻 Author

**Kaustav Roy Chowdhury**

<a href="https://github.com/KaustavWayne">
  <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>
<a href="https://www.linkedin.com/in/kaustavroychowdhury">
  <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
</a>

*© 2024 Kaustav Roy Chowdhury*
