# 🚀 KaustavGPT: Implementation Roadmap

This roadmap outlines the step-by-step approach to building the **KaustavGPT** LangGraph chatbot. Follow these phases to ensure a modular and robust development process.

---

## 🛠️ Phase 1: Foundation & Environment
**Goal:** Set up the development environment and core LLM configurations.

1.  **Environment Setup**:
    - [ ] Create [.env](file:///e:/Chatbot%20Project/langgraph-chatbot/.env) and configure `GROQ_API_KEY`.
    - [ ] Initialize [requirements.txt](file:///e:/Chatbot%20Project/langgraph-chatbot/requirements.txt) with LangChain, LangGraph, Groq, and Streamlit.
2.  **LLM Configuration** ([app/llm/config.py](file:///e:/Chatbot%20Project/langgraph-chatbot/app/llm/config.py)):
    - [ ] Initialize the `ChatGroq` model.
    - [ ] Set up HuggingFace embeddings for RAG.

---

## 🧰 Phase 2: Tools & RAG Engine
**Goal:** Build the capabilities the agent will use to answer questions.

1.  **Basic Tools** ([app/tools/definitions.py](file:///e:/Chatbot%20Project/langgraph-chatbot/app/tools/definitions.py)):
    - [ ] Implement DuckDuckGo Search.
    - [ ] Implement Calculator and Stock Price tools.
2.  **RAG Implementation** ([app/rag/retriever.py](file:///e:/Chatbot%20Project/langgraph-chatbot/app/rag/retriever.py)):
    - [ ] Build the PDF processing logic (PyPDF).
    - [ ] Set up the FAISS vector store retriever.
    - [ ] Wrap the retriever as a LangChain tool.

---

## 🧠 Phase 3: The LangGraph Brain
**Goal:** Define the logic, state, and decision-making flow of the agent.

1.  **Graph Definition** ([app/graph/chatbot.py](file:///e:/Chatbot%20Project/langgraph-chatbot/app/graph/chatbot.py)):
    - [ ] Define the `AgentState` typed dictionary.
    - [ ] Create the `call_model` node (decision point).
    - [ ] Create the `tool_node` (action execution).
    - [ ] Compile the graph with a `SqliteSaver` checkpointer.

---

## 💾 Phase 4: Persistence & Database
**Goal:** Ensure the chatbot remembers conversation history across sessions.

1.  **Database Setup** ([app/database/sqlite.py](file:///e:/Chatbot%20Project/langgraph-chatbot/app/database/sqlite.py)):
    - [ ] Configure the `SqliteSaver` for LangGraph.
    - [ ] Ensure [chatbot.db](file:///e:/Chatbot%20Project/langgraph-chatbot/chatbot.db) is initialized on startup.

---

## 🎨 Phase 5: Frontend & User Experience
**Goal:** Create a clean, ChatGPT-style interface using Streamlit.

1.  **Styling** ([app/frontend/styles.py](file:///e:/Chatbot%20Project/langgraph-chatbot/app/frontend/styles.py)):
    - [ ] Define the dark-mode theme and custom CSS.
2.  **Components** (`app/frontend/components/`):
    - [ ] `sidebar.py`: Handle chat history management and PDF uploads.
    - [ ] `chat.py`: Render user/assistant message bubbles.
3.  **State Management** (`app/frontend/session.py`):
    - [ ] Manage thread IDs and chat history strings.
4.  **Main Application** (`app/frontend/app.py`):
    - [ ] Orchestrate the input loop and graph execution.
5.  **Entry Point** (`run.py`):
    - [ ] Create a simple script to trigger `streamlit run app/frontend/app.py`.

---

## 🧪 Phase 6: Testing & Optimization
1.  **Test Tool-Calling**: Ensure the agent can choose between Search and RAG correctly.
2.  **Verify Memory**: Restart the app and check if past threads are restored.
3.  **Performance**: Optimize PDF ingestion time and tool execution.

---

## 📜 Files Summary Checklist
| File | Responsibility |
| :--- | :--- |
| `app/llm/config.py` | LLM & Embedding models |
| `app/tools/definitions.py` | External search, calculator tools |
| `app/rag/retriever.py` | PDF ingestion & FAISS retrieval |
| `app/graph/chatbot.py` | LangGraph nodes & edges |
| `app/database/sqlite.py` | Persistent checkpointing |
| `app/frontend/app.py` | Main Streamlit interface |
| `run.py` | Application entry point |
