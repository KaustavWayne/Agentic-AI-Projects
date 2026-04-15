# 🗺️ Implementation Roadmap: Agentic AI Trip Planner

This document outlines the step-by-step architectural approach to building the **Voyage AI Trip Planner**. Follow these phases to build a robust, production-ready multi-agent system.

---

## 🏗️ Phase 1: Environment & Foundation
*Goal: Set up a high-performance development environment.*

1.  **Install `uv`**: Use the `uv` package manager for lightning-fast dependency management.
2.  **Initialize Project**: Run `uv init` and `uv venv`.
3.  **Dependency Management**: Add core libraries:
    - `langgraph`, `langchain-groq`, `tavily-python` (The AI Engine)
    - `pydantic` (Data Validation)
    - `streamlit`, `plotly` (The Dashboard)
    - `tenacity`, `diskcache` (Robustness & Speed)
4.  **Secrets Management**: Create a [.env](file:///d:/CAMPUSX/Claude%20Projects/Voyage-Trip-Planner/.env) file for API keys (`GROQ`, `TAVILY`, etc.).

---

## 📦 Phase 2: Structural Data Models (Pydantic)
*Goal: Define the "Contract" between AI agents.*

1.  **Atomic Models**: Define structures for `Money`, `Hotel`, `Activity`, and `TransportOption`.
2.  **State Model**: Define [TripState](file:///d:/CAMPUSX/Claude%20Projects/Voyage-Trip-Planner/graph/trip_graph.py#10-27) (TypedDict) to track the graph's memory (destination, budget, nodes, errors).
3.  **The TripPlan**: Create a monolithic `TripPlan` Pydantic model for final structured output validation.

---

## 🛠️ Phase 3: Service Wrappers (The Tools)
*Goal: Create clean interfaces for external APIs.*

1.  **Tavily Tool**: Specialized search for hotels, attractions, and local travel data.
2.  **Currency Tool**: ExchangeRate-API integration with hardcoded fallback rates.
3.  **Weather Tool**: OpenWeatherMap integration for forecasts and travel conditions.

---

## 🔗 Phase 4: Agentic Nodes (The Workers)
*Goal: Build specialized LLM "Workers" for each planning task.*

1.  **Node 1: Destination Research**: Identifies country, currency, and highlights.
2.  **Node 2: Currency Converter**: Sets up rates for multi-currency output.
3.  **Node 3: Weather Scout**: Fetches current and 5-day forecasts.
4.  **Node 4: Smart Budgeter**: Allocates INR budget across flights/hotels using rules & LLM.
5.  **Node 6: Hotel & Transport Nodes**: Researches and extracts real booking options.
6.  **Node 7: Itinerary Architect**: Builds day-wise plans with clickable Google Maps links.

---

## 🧠 Phase 5: Graph Orchestration (The Brain)
*Goal: Chain the workers together using LangGraph.*

1.  **Define StateGraph**: Initialize `StateGraph(TripState)`.
2.  **Edge Mapping**: Connect nodes in a linear flow: `START -> Research -> Currency -> Weather -> Budget -> Hotels -> Itinerary -> Transport -> Aggregator -> END`.
3.  **Compilation**: Compile the graph into a runnable executable.

---

## 🎨 Phase 6: Elite Streamlit UI
*Goal: Build a premium "Glassmorphism" dashboard.*

1.  **Layout**: Multi-column main area with a sleek sidebar for user inputs.
2.  **Styling**: Inject custom CSS for dark gradients, glass effects, and custom fonts.
3.  **Visualization**: Use Plotly for budget donut charts and custom cards for hotels/weather.

---

## 🛡️ Phase 7: Robustness & Optimization
1.  **Retries**: Use `tenacity` for exponential backoff on API calls.
2.  **Caching**: Use `diskcache` to speed up repeated queries.
3.  **Sanity Checks**: Implement an Aggregator node to handle missing data and errors gracefully.
