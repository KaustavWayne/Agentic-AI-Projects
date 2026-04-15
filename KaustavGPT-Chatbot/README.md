<div align="center">
  <img src="https://og-image.vercel.app/KaustavGPT.png?theme=dark&md=1&fontSize=100px&images=https%3A%2F%2Fassets.vercel.com%2Fimage%2Fupload%2Ffront%2Fassets%2Fdesign%2Fvercel-triangle-white.svg" alt="KaustavGPT Banner" width="100%" />

  # KaustavGPT (LangGraph Chatbot)

  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
  [![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

  A ChatGPT/Claude-style AI chat application built with LangGraph, Groq, and Streamlit.
</div>


## Features

- 🧠 **LangGraph** agent with tool-use loop
- 🔍 **RAG** — upload a PDF and chat with it per thread
- 🌐 **Web search** via DuckDuckGo
- 📈 **Stock prices** via Alpha Vantage
- 🔢 **Calculator** tool
- 💾 **Persistent memory** — SQLite checkpointing per thread
- 🎨 **ChatGPT-style UI** — named chats, ordered history, dark theme

---

## Project Structure

```text
📂 langgraph-chatbot
├── 📄 run.py                # Main Application Entry Point
├── 📄 requirements.txt      # Project Dependencies
├── 📄 .env.example          # Environment Variables Template
├── 📄 chatbot.db            # Persistent SQLite Database (Auto-generated)
└── 📂 app                   # Core Logic
    ├── 📂 database          # Database connection & Checkpointing
    │   └── 📄 sqlite.py
    ├── 📂 frontend          # Streamlit UI Components
    │   ├── 📄 app.py        # Main Loop & Page Layout
    │   ├── 📄 styles.py     # Custom CSS Styling
    │   └── 📂 components    # Reusable UI widgets
    │       ├── 📄 chat.py
    │       └── 📄 sidebar.py
    ├── 📂 graph             # LangGraph Workflow Definition
    │   └── 📄 chatbot.py
    ├── 📂 llm               # AI Models Configuration
    │   └── 📄 config.py
    ├── 📂 rag               # Retrieval Augmented Generation logic
    │   └── 📄 retriever.py
    └── 📂 tools             # Agent Tool Definitions
        └── 📄 definitions.py
```

---

## Setup

```bash
# 1. Clone / unzip the project
cd langgraph-chatbot

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run
streamlit run run.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | **Required.** Get free at https://console.groq.com |

---

## Models Used

| Component | Model |
|---|---|
| LLM | `llama-3.1-8b-instant` via Groq |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace |

---

## Usage Tips

- **New Chat** — click the button in the sidebar to start a fresh conversation
- **Chat History** — previous chats are listed by name (most recent on top); click to restore
- **PDF Upload** — upload a PDF in the sidebar; the RAG tool is automatically available in that thread
- **Rate limits** — if Groq rate limits are hit, the app retries automatically with back-off

---

## Author

**Kaustav Roy Chowdhury**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/KaustavWayne)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kaustavroychowdhury)
