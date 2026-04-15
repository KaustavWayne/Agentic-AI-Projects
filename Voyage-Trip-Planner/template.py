import os
from pathlib import Path

def create_trip_planner_structure():
    project_root = "trip_planner"

    # Define the file structure and initial contents
    files = {
        "main.py": "# Entry point for the CLI application",
        "streamlit_app.py": "# Streamlit UI for the trip planner",
        "requirements.txt": "langchain\nlanggraph\ngroq\nstreamlit\npython-dotenv\ntavily-python",
        ".env.example": "GROQ_API_KEY=\nTAVILY_API_KEY=\nOPENAI_API_KEY=",
        
        # Agents & Nodes
        "agents/__init__.py": "",
        "nodes/__init__.py": "",
        "nodes/destination_research.py": "# Research destinations using search tools",
        "nodes/budget_planner.py": "# Calculate estimated costs",
        "nodes/hotel_finder.py": "# Locate accommodations",
        "nodes/itinerary_planner.py": "# Generate day-by-day plans",
        "nodes/transport_node.py": "# Flight and transit logic",
        "nodes/currency_conversion.py": "# Handle currency calculations",
        "nodes/aggregator.py": "# Compile all results into final response",

        # Graph Orchestration
        "graph/__init__.py": "",
        "graph/trip_graph.py": "# LangGraph state machine definition",

        # LLM Client
        "llm/__init__.py": "",
        "llm/groq_client.py": "# Groq / Llama 3 initialization",

        # Tools
        "tools/__init__.py": "",
        "tools/tavily_search.py": "# Web search tool integration",
        "tools/currency_converter.py": "# Currency API tool",

        # Data Models
        "models/__init__.py": "",
        "models/trip_models.py": "# Pydantic models for State and Schema",

        # Utilities
        "utils/__init__.py": "",
        "utils/logger.py": "# Logging configuration",
        "utils/cache.py": "# Caching mechanisms",
        "utils/retry.py": "# LLM call retry logic",

        # UI Components
        "ui/__init__.py": "",
        "ui/components.py": "# Reusable Streamlit components"
    }

    print(f"📁 Initializing: {project_root}\n")

    for filepath, content in files.items():
        # Create full path including the project root
        full_path = Path(project_root) / filepath
        
        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the file
        if not full_path.exists():
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created: {full_path}")
        else:
            print(f"Skipped: {full_path} (exists)")

    print(f"\n✅ '{project_root}' structure is ready!")

if __name__ == "__main__":
    create_trip_planner_structure()