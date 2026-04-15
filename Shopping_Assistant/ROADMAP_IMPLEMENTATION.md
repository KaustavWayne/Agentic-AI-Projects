# 🛍️ Agentic Shopping Assistant: Implementation Roadmap

This document outlines the step-by-step implementation sequence for the **ShopMind AI** project. Each stage builds upon the previous one to create a modular, multi-agent pipeline using **LangGraph**, **Groq**, and **Tavily**.

---

## 🏗️ Phase 1: Environment & Foundation
Set up the workspace and core configuration.

1. **Initialise Project**
   - Create project directory structure: `agents/`, `graph/`, `tools/`.
   - Create `requirements.txt` with dependencies: `langchain-groq`, `langgraph`, `tavily-python`, `streamlit`, `pydantic`, `python-dotenv`.
   - Setup `.env` for `GROQ_API_KEY` and `TAVILY_API_KEY`.

2. **Core LLM Configuration (`agents/llm.py`)**
   - Initialise the Groq LLM instance (e.g., `llama-3.3-70b-versatile`).
   - Configure parameters like temperature and model name.

3. **Shared Schemas (`agents/schemas.py`)**
   - Define **Pydantic** models for every agent's output (Query, Product, Comparison, Budget, etc.).
   - This ensures strict JSON structure across the entire pipeline.

---

## 🛠️ Phase 2: Tools & Utilities
Implement the external capabilities.

4. **Search Tools (`tools/search_tools.py`)**
   - Integrate **Tavily API** for real-time web searching.
   - Implement logic to fetch and parse product details from search results.

---

## 🤖 Phase 3: Agent Nodes (Brain of the System)
Implement each agent as a standalone function that returns structured data.

5. **Query Agent (`agents/query_agent.py`)**
   - Parses the user's natural language input into a structured query (Product Type, Budget, Features).

6. **Search Agent (`agents/search_agent.py`)**
   - Uses the search tools to find relevant products.

7. **Comparison Agent (`agents/comparison_agent.py`)**
   - Processes found products to extract Pros/Cons and compute a "Value Score".

8. **Budget Agent (`agents/budget_agent.py`)**
   - Filters products based on the user's max budget and suggests alternatives if needed.

9. **Review Agent (`agents/review_agent.py`)**
   - (Optional/Enhancement) Fetches and summarises customer reviews for the top product.

10. **Recommendation Agent (`agents/recommendation_agent.py`)**
    - Picks the "Best Choice" based on all gathered data and provides a justification.

11. **Aggregator Agent (`agents/aggregator_agent.py`)**
    - Combines all previous findings into a single, clean `ShoppingAssistantOutput` object.

---

## 🕸️ Phase 4: Graph Orchestration
Connect the agents into a workflow.

12. **Define State (`graph/shopping_graph.py`)**
    - Create a `TypedDict` to hold the conversational state (the "memory" of the pipeline).

13. **Build the Graph**
    - Add all nodes to the `StateGraph`.
    - Define edges (the flow) from Query → Search → Comparison → Budget → Reviews → Recommendation → Aggregator.
    - Compile the graph into an executable runner.

---

## 🎨 Phase 5: User Interface
Create a premium frontend to interact with the graph.

14. **Streamlit UI (`streamlit_app.py`)**
    - Build the sidebar for settings and API keys.
    - Build the main search bar and hero section.
    - Implement the **Pipeline Runner**:
        - Show progress bars and status updates as the graph executes.
        - Render results using custom HTML/CSS (Hero cards, Comparison tables, Review badges).

---

## ✅ Phase 6: Testing & Polishing
15. **Integration Testing**
    - Run edge cases (e.g., "Phone under ₹1,000" which might have no results).
    - Ensure error handling is robust (e.g., invalid API keys).

16. **Performance**
    - Implement caching for search results to save on API usage.
