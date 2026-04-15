<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=50&duration=2000&pause=1000&color=818CF8&center=true&vCenter=true&width=500&lines=ShopMind+AI;The+Future+of+Shopping" alt="ShopMind AI Header" />

  <h3>🛍️ Your Premium Agentic Shopping Assistant</h3>

  <p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/LangGraph-232F3E?style=for-the-badge&logo=langchain&logoColor=white" />
    <img src="https://img.shields.io/badge/Groq-f3f4f6?style=for-the-badge&logo=groq&logoColor=black" />
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
    <img src="https://img.shields.io/badge/Tavily-000000?style=for-the-badge&logo=google-cloud&logoColor=white" />
    <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  </p>

  <p><b>A multi-agent pipeline designed to search, compare, and recommend products with clinical precision.</b></p>
</div>

---

## 🌟 Introduction

**ShopMind AI** is a state-of-the-art agentic shopping assistant that leverages the power of **LangGraph** and **Groq** to automate the product research process. Unlike traditional search engines, ShopMind AI uses a 7-agent pipeline to understand your intent, browse the web in real-time via Tavily, compare technical specifications, optimize for your budget, and analyze user sentiment—all to deliver a single, data-backed recommendation.

Whether you're looking for the best smartphone under a budget or a professional gaming laptop, ShopMind AI handles the heavy lifting, providing you with a crisp, structured, and visually stunning comparison dashboard.

---

## 🏗️ Architecture

```mermaid
graph TD
    UserQuery[User Query] --> QU[Query Understanding Agent]
    QU --> PSA[Product Search Agent]
    PSA --> CA[Comparison Agent]
    CA --> BOA[Budget Optimization Agent]
    BOA --> RIA[Review Insights Agent]
    RIA --> FRA[Final Recommendation Agent]
    FRA --> AA[Aggregator Agent]
    AA --> FinalOutput[Strict JSON / Premium UI]

    subgraph "LangGraph Orchestration"
    QU
    PSA
    CA
    BOA
    RIA
    FRA
    AA
    end
```

---

## 📁 Project Structure

```bash
shopping_assistant/
├── agents/
│   ├── schemas.py            # Pydantic models (strict output)
│   ├── llm.py                # Groq LLM configuration
│   ├── query_agent.py        # Agent 1: Understanding intent
│   ├── search_agent.py       # Agent 2: Real-time product lookup
│   ├── comparison_agent.py   # Agent 3: Feature & Value analysis
│   ├── budget_agent.py       # Agent 4: Budget filtering
│   ├── review_agent.py       # Agent 5: Sentiment & Review analysis
│   ├── recommendation_agent.py # Agent 6: Decision making
│   └── aggregator_agent.py   # Agent 7: Final data formatting
├── graph/
│   └── shopping_graph.py     # LangGraph workflow orchestration
├── tools/
│   └── search_tools.py       # Tavily API integration & caching
├── main.py                   # CLI Entry point
├── streamlit_app.py          # Premium Dashboard UI
├── ROADMAP_IMPLEMENTATION.md # Project implementation guide
├── requirements.txt          # Dependencies
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/KaustavWayne/shopping_assistant.git
cd shopping_assistant
```

### 2. Install Dependencies
```bash
# It is recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

### 4. Launch the App
```bash
streamlit run streamlit_app.py
```

---

## 🔑 Key Features

- **Multi-Agent Collaboration**: 7 specialized agents working in a stateful graph.
- **Ultra-Fast Performance**: Powered by Groq's LPU™ Inference Engine.
- **Real-Time Data**: Live web searching using Tavily API.
- **Pydantic Validation**: Guaranteed structured outputs for reliable UI rendering.
- **Premium UI**: Sleek, glassmorphism-inspired Streamlit dashboard.

---

## �‍💻 Author

<div align="left">
  <h3>Kaustav Roy Chowdhury</h3>
  <p><i>Building Intelligent Agentic Systems</i></p>

  <a href="https://www.linkedin.com/in/kaustavroychowdhury">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="https://github.com/KaustavWayne">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" />
  </a>
</div>

---

<div align="center">
  <p>Built with ❤️ using LangGraph & Groq</p>
</div>
