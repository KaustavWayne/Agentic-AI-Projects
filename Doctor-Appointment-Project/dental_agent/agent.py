"""
Dental Agent — entry point.

`dental_graph` is built in dental_agent/workflows/graph.py using the modern
llm.bind_tools + ToolNode + StateGraph approach.  This module re-exports it
so that api.py / main.py can keep their existing import unchanged:

    from dental_agent.agent import dental_graph
"""

from dental_agent.workflows.graph import dental_graph  # noqa: F401

__all__ = ["dental_graph"]
