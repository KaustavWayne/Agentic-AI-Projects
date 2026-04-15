# 🦷 Dental Appointment Management System (Agentic AI)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-orange?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama--3.1--8B-black?style=for-the-badge)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Built with uv](https://img.shields.io/badge/Built%20with-uv-purple?style=for-the-badge)](https://github.com/astral-sh/uv)

An advanced Agentic AI system for managing dental appointments, powered by **LangGraph** and **Groq (Llama-3.1-8B-Instant)**. This project leverages a multi-agent architecture to handle complex appointment tasks like booking, rescheduling, and cancellation with human-like precision.

---

## 🚀 Overview

This system provides a seamless experience for patients and staff through three interfaces (CLI, API, and UI):
- **Smart Routing**: A Supervisor Agent classifies user intent and routes to specialized sub-agents.
- **Appointment Lifecycle**: Check availability, Book, Reschedule, or Cancel in natural language.
- **Specialized Agents**: Modular agents for Info, Booking, Cancellation, and Rescheduling.
- **RAG-Lite**: Uses CSV-based data management for real-time doctor availability.

---

## 🏗️ Project Structure

```bash
├── dental_agent/               # Core Package
│   ├── agents/                 # Specialized Agent Logic (Supervisor, Booking, etc.)
│   ├── config/                 # Environment & Config Settings
│   ├── models/                 # Pydantic state & data models
│   ├── tools/                  # CSV operations & Appointment tools
│   ├── workflows/              # LangGraph orchestration (graph.py)
│   └── utils.py                # Helper utilities
├── api.py                      # FastAPI Backend Service
├── streamlit_ui.py             # Premium Streamlit Frontend
├── main.py                     # CLI Entry Point
├── doctor_availability.csv      # Local Data Store (Database)
├── pyproject.toml              # Modern Python dependencies (UV)
└── .env                        # API Keys & Secrets
```

---

## 🛠️ Installation & Setup

We use `uv` for optimized package management.

### 1. Clone & Enter
```bash
git clone https://github.com/KaustavWayne/Doctor-Appointment-Project.git
cd Doctor-Appointment-Project
```

### 2. Install Dependencies
```bash
# Ensure you have 'uv' installed
# If not: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
uv sync
```

### 3. Environment Config
Create a `.env` file and add your Groq API Key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🚦 Running the Project

### Choice 1: Interactive CLI
Fastest way to test the agent logic directly.
```bash
uv run main.py
```

### Choice 2: Premium UI (Streamlit) + API
The full experience with a modern dashboard.
```bash
# Terminal 1: Start Backend
uv run uvicorn api:app --reload

# Terminal 2: Start UI
uv run streamlit run streamlit_ui.py
```

---

## 🧠 Architectural Highlights

- **Multi-Agent Orchestration**: Used `LangGraph` to build a stateful, cyclical graph where agents communicate and share state.
- **Tool Binding**: Agents dynamically decide when to call Python functions for data mutation.
- **Intent Classification**: Uses `llama-3.1-8b-instant` for zero-shot intent detection and routing.

---

## 🧠 Deep Dive: How the Flow Works

Understanding this system helps demonstrate several key AI engineering concepts:

### 1. Multi-Agent Architecture
The system follows a supervisor pattern where a central coordinator analyzes user messages and routes them to the most appropriate specialized agent:

```text
                    ┌──────────────┐
                    │   Supervisor │ ← Intent classification & routing
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   ┌─────────────┐ ┌─────────────┐ ┌───────────────┐
   │ Info Agent  │ │   Booking   │ │  Cancellation │
   │             │ │    Agent    │ │    Agent      │
   └─────────────┘ └─────────────┘ └───────────────┘
          │
          ▼
   ┌───────────────┐
   │   Reschedule  │
   │    Agent      │
   └───────────────┘
```

### 2. Intent Classification
When a user sends a message, the **Supervisor agent** analyzes the text to determine what action the user wants. This is done using structured output parsing (Pydantic), where the LLM returns:
- `intent`: The type of request (get_info, book, cancel, reschedule, end)
- `next_agent`: Which specialized agent should handle it
- `reasoning`: Explanation of the decision

### 3. Tool Use in Agents
Each specialized agent has access to specific tools. For example, the **Info Agent** can query available slots but cannot book appointments. This demonstrates the **principle of least privilege** in agent design.

### 4. State Management
**LangGraph** maintains conversation state across all agents. The state includes:
- Message history (for context)
- Current intent and routing decision
- Parameters collected during booking (patient_id, doctor, date)
- Tool execution results

### 5. Conditional Routing
The graph uses conditional edges to determine flow:
- **After supervisor**: Route based on classified intent.
- **After agent**: Continue to tools if needed, or end if the response is complete.

### 6. Data Layer Abstraction
Tools provide an abstraction layer over the CSV data, making it easy to change the data source (e.g., to a real database) without changing agent logic.

---

## ⚙️ Configuration

Environment variables can be set in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| GROQ_API_KEY | Your Groq API key | Required |
| MODEL_NAME | LLM model to use | llama-3.1-8b-instant |
| TEMPERATURE | LLM creativity (0=deterministic) | 0 |


---

## 👤 Developer & Credits

**Developed by: Kaustav Roy Chowdhury**

> "The best way to predict the future is to create it." – Peter Drucker
> "Agentic AI is not just about LLMs; it's about giving them the tools and the plan to execute."

🔗 **Connect with me:**
- **LinkedIn**: [Kaustav Roy Chowdhury](https://www.linkedin.com/in/kaustavroychowdhury)
- **GitHub**: [@KaustavWayne](https://github.com/KaustavWayne)

---

## ⚖️ License
This project is open-source and intended for educational and professional demonstration purposes.


