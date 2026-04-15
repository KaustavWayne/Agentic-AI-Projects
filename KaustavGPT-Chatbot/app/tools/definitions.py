from __future__ import annotations

from typing import Optional

import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from app.rag import get_retriever
from app.rag.retriever import _THREAD_METADATA

# ── Web search ───────────────────────────────────────────────────────────────
search_tool = DuckDuckGoSearchRun(region="us-en")


# ── Calculator ───────────────────────────────────────────────────────────────
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as exc:
        return {"error": str(exc)}


# ── Stock price ──────────────────────────────────────────────────────────────
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch the latest stock price for a given ticker symbol (e.g. 'AAPL', 'TSLA')
    using the Alpha Vantage API.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey=SHQRH39LI8CYJESB"
    )
    r = requests.get(url, timeout=10)
    return r.json()


# ── RAG tool ─────────────────────────────────────────────────────────────────
@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant information from the PDF uploaded for this chat thread.
    Always pass the thread_id when calling this tool.
    """
    retriever = get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    return {
        "query": query,
        "context": [doc.page_content for doc in result],
        "metadata": [doc.metadata for doc in result],
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


# ── Exported list ────────────────────────────────────────────────────────────
all_tools = [search_tool, get_stock_price, calculator, rag_tool]
