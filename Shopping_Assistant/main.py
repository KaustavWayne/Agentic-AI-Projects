"""
main.py
CLI entry point for the Agentic Shopping Assistant.
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

from graph.shopping_graph import run_shopping_assistant


def main():
    print("\n" + "═" * 60)
    print("  🛍️  Agentic AI Shopping Assistant")
    print("  Powered by LangGraph + Groq (llama-3.1-8b-instant)")
    print("═" * 60 + "\n")

    query = input("What are you looking for? (e.g. 'best smartphone under 20000')\n> ").strip()
    if not query:
        print("No query provided. Exiting.")
        return

    print("\n⏳ Processing your request through the agent pipeline...\n")
    result = run_shopping_assistant(query)

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        return

    print("\n" + "═" * 60)
    print("  ✅ Final Output (Strict JSON)")
    print("═" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
