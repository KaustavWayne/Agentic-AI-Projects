# Implementation Roadmap: Dental Appointment Management System

This roadmap provides a logical, step-by-step guide to building the **Dental Appointment Management System** using **LangGraph**, **Groq**, **FastAPI**, and **Streamlit**.

---

## phase 1: Environment & Dependency Management 🛠️

We use `uv` for lightning-fast dependency management and reproducible environments.

### 1. Install `uv`
If you haven't installed `uv` yet, run the following command in your terminal:
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **macOS/Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Initialize Project & Sync
Navigate to your project root and run:
```bash
# Initialize a new project (if starting from scratch)
uv init

# Install dependencies defined in pyproject.toml
uv sync
```
> [!TIP]
> **When to use `uv sync`?**
> Run `uv sync` every time you add a new dependency to [pyproject.toml](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/pyproject.toml) or when you first clone the project. It ensures your `.venv` is perfectly aligned with your [uv.lock](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/uv.lock) file.

---

## Phase 2: Core Agent Logic (The "Brain") 🧠

The project follows a modular architecture within the `dental_agent/` directory.

### Step 1: Data & Utilities
- **File:** [doctor_availability.csv](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/doctor_availability.csv)
  - Populate this with mock data for doctors, slots, and patient records.
- **File:** [dental_agent/utils.py](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/dental_agent/utils.py)
  - Implement helper functions for CSV reading/writing and date parsing.

### Step 2: Define State & Tools
- **File:** [dental_agent/models/state.py](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/dental_agent/models/state.py)
  - Define the `AgentState` using TypedDict to track message history and context.
- **File:** `dental_agent/tools/appointment_tools.py`
  - Create Python functions for `search_slots`, `book_appointment`, and `cancel_appointment`. 
  - Use the `@tool` decorator from `langchain-core`.

### Step 3: Individual Agents
- **Files:** [dental_agent/agents/booking_agent.py](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/dental_agent/agents/booking_agent.py), `rescheduling_agent.py`, etc.
  - Define specialized prompts for each agent.
  - Initialize the LLM (Groq) and bind tools to it.

### Step 4: Orchestration (LangGraph)
- **File:** [dental_agent/workflows/graph.py](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/dental_agent/workflows/graph.py)
  - Define the `StateGraph`.
  - Add nodes (Agents, ToolNode).
  - Define edges (Conditional routing based on tool calls).
  - Compile the graph into `dental_graph`.

---

## Phase 3: Interface Layers 🌐

### Step 5: Backend API (FastAPI)
- **File:** [api.py](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/api.py)
  - Design endpoints (`/chat`, `/slots`) to expose the agent's functionality.
  - Integrate `dental_graph.invoke()` or `.stream()` within the API routes.

### Step 6: Premium Frontend (Streamlit)
- **File:** [streamlit_ui.py](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/streamlit_ui.py)
  - Create a modern, interactive UI.
  - Use `st.chat_message` for the conversation.
  - Add a sidebar for doctor availability visualization.

---

## Phase 4: Execution & Testing 🚀

### Running the Project
Add these scripts to your workflow:

1. **CLI Mode (Direct Testing):**
   ```bash
   uv run main.py
   ```

2. **Backend Mode:**
   ```bash
   uv run uvicorn api:app --reload
   ```

3. **Frontend Mode:**
   ```bash
   uv run streamlit run streamlit_ui.py
   ```

---

## Summary of Key Files
| File Path | Responsibility |
| :--- | :--- |
| [pyproject.toml](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/pyproject.toml) | Dependencies & Project Metadata |
| [.env](file:///e:/Projects-Agentic-AI/Doctor-Appointment-Project/.env) | API Keys (GROQ_API_KEY) |
| `dental_agent/tools/` | Operations on the hardware/data (CSV) |
| `dental_agent/workflows/graph.py` | The main logic flow and routing |
| `api.py` | FastAPI server connecting UI to Agent |
| `streamlit_ui.py` | The user interface |

> [!IMPORTANT]
> Always ensure your `.env` contains a valid `GROQ_API_KEY` before running the agents!
