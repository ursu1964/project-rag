"""Answer generation agent."""

from __future__ import annotations

import json

from app.core.timing import elapsed_ms, now_ms
from app.tools.ollama_client import generate


def run(state: dict) -> dict:
    start_ms = now_ms()
    question = str(state.get("question") or state.get("query") or "")
    context = state.get("compressed_context") or state.get("merged_context") or {
        "memory": state.get("memory_context") or [],
        "vector": state.get("vector_context") or [],
        "graph": state.get("graph_context") or {},
    }
    prompt = (
        "Answer the question using only the provided context. Do not invent facts.\n"
        "Return structured Markdown exactly with these sections:\n\n"
        "Direct Answer:\n"
        "...\n\n"
        "Evidence Used:\n"
        "- Vector evidence:\n"
        "- Graph evidence:\n"
        "- Memory evidence:\n\n"
        "Limitations:\n"
        "...\n\n"
        "Rules:\n"
        "- Do not invent facts.\n"
        "- Cite supporting evidence with citation_id values from the context, such as [V1] or [G1].\n"
        "- If graph evidence is empty, say so.\n"
        "- If vector evidence is empty, say so.\n"
        "- For infrastructure impact questions, prioritize graph evidence.\n"
        "- If the context is insufficient, say you do not know.\n\n"
        f"Question:\n{question}\n\n"
        f"Context JSON:\n{json.dumps(context, default=str)}\n\n"
        "Structured Markdown Answer:"
    )
    answer = generate(prompt)
    metrics = {**(state.get("metrics") or {}), "llm_generation_ms": elapsed_ms(start_ms)}
    return {**state, "answer": answer, "reasoner_prompt": prompt, "metrics": metrics}
