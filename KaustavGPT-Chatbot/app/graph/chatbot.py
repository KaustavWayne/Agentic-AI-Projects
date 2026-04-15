from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from app.llm import llm
from app.tools import all_tools
from app.database import checkpointer

llm_with_tools = llm.bind_tools(all_tools)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState, config=None):
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    # system_message = SystemMessage(
    #     content=(
    #         "You are Kaustav GPT, a helpful AI assistant. "
    #         "You have access to EXACTLY these tools — use ONLY these, never invent others:\n"
    #         "1. `duckduckgo_search` — search the web for any question, recipes, news, facts, etc.\n"
    #         "2. `get_stock_price` — fetch live stock price for a ticker symbol (e.g. TSLA, AAPL)\n"
    #         "3. `calculator` — perform arithmetic: add, sub, mul, div\n"
    #         "4. `rag_tool` — answer questions from an uploaded PDF (always pass thread_id)\n\n"
    #         f"Current thread_id: `{thread_id}`\n\n"
    #         "IMPORTANT RULES:\n"
    #         "- For ANY question about recipes, cooking, facts, news, or general knowledge → use `duckduckgo_search`\n"
    #         "- NEVER call a tool not listed above (e.g. never call brave_search, tavily, or anything else)\n"
    #         "- If no PDF is uploaded and user asks about a document, politely ask them to upload one\n"
    #         "- Be concise, friendly, and helpful"
    #     )
    # )
    system_message = SystemMessage(
            content=(
                "You are Kaustav GPT, a helpful AI assistant built on a powerful language model. "
                "You have broad knowledge and can answer most questions directly from your training.\n\n"
                "You have access to EXACTLY these tools — use ONLY when needed:\n"
                "1. `duckduckgo_search` — ONLY use for: current news, live events, recent prices, "
                "weather, sports scores, or anything that changes over time and needs up-to-date info.\n"
                "2. `get_stock_price` — fetch live stock price for a ticker symbol (e.g. TSLA, AAPL)\n"
                "3. `calculator` — perform arithmetic: add, sub, mul, div\n"
                "4. `rag_tool` — answer questions from an uploaded PDF (always pass thread_id)\n\n"
                f"Current thread_id: `{thread_id}`\n\n"
                "IMPORTANT RULES:\n"
                "- Answer from your own knowledge first for: general facts, recipes, history, science, "
                "coding, math explanations, definitions, advice — NO search needed for these.\n"
                "- Only search the web when the question requires CURRENT or LIVE information "
                "(today's news, latest prices, recent events after your training cutoff).\n"
                "- NEVER call a tool not listed above (e.g. never call brave_search, tavily)\n"
                "- If no PDF is uploaded and user asks about a document, ask them to upload one.\n"
                "- Be concise, friendly, and helpful.\n\n"
                "FORMATTING RULES:\n"
                "- ALWAYS wrap any code in triple backticks with the language name.\n"
                "- Example: ```python\nprint('hello')\n``` \n"
                "- NEVER write code as plain text without backticks.\n"
                "- For bash/terminal commands use ```bash\n```\n"
                "- For JSON use ```json\n```\n"
                "- For plain text output or results, use ```text\n```"
                "- For mathematical formulas ALWAYS use LaTeX: wrap inline math in $...$ and block equations in $$...$$\n"
                "- Example: The formula is $$\\text{Attention}(Q,K,V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$\n"
            )
        )

    response = llm_with_tools.invoke([system_message, *state["messages"]], config=config)
    return {"messages": [response]}


tool_node = ToolNode(all_tools)

_graph = StateGraph(ChatState)
_graph.add_node("chat_node", chat_node)
_graph.add_node("tools", tool_node)

_graph.add_edge(START, "chat_node")
_graph.add_conditional_edges("chat_node", tools_condition)
_graph.add_edge("tools", "chat_node")

chatbot = _graph.compile(checkpointer=checkpointer)
