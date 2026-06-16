"""Run a local ProjectRAG query through the LangGraph workflow."""

import sys
from pprint import pprint

from app.workflows.rag_workflow import build_workflow


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is ProjectRAG?"
    pprint(build_workflow().invoke({"question": question}))

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
__test__ = False
