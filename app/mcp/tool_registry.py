"""Simple internal tool registry for future MCP integration."""

from __future__ import annotations

from typing import Callable

from app.devops.inventory_importer import import_inventory_from_json
from app.graph.graphdb_client import sparql_query
from app.mcp.tool_contracts import TOOL_MODES, ToolContract
from app.memory.memory_store import add_memory
from app.rag.vector_store import similarity_search

_TOOLS: dict[str, ToolContract] = {}


def register_tool(name: str, description: str, callable: Callable, mode: str) -> ToolContract:
    """Register an internal tool contract."""
    if mode not in TOOL_MODES:
        raise ValueError(f"Unsupported tool mode: {mode}")
    contract = ToolContract(name=name, description=description, callable=callable, mode=mode)
    _TOOLS[name] = contract
    return contract


def list_tools() -> list[ToolContract]:
    """List registered internal tools."""
    return list(_TOOLS.values())


def get_tool(name: str) -> ToolContract:
    """Get a registered internal tool by name."""
    return _TOOLS[name]


def _register_defaults() -> None:
    register_tool(
        "search_documents",
        "Search document chunks using pgvector similarity.",
        similarity_search,
        "read_only",
    )
    register_tool(
        "query_graph",
        "Run a read-only SPARQL query against GraphDB.",
        sparql_query,
        "read_only",
    )
    register_tool(
        "add_memory",
        "Add an item to ProjectRAG memory.",
        add_memory,
        "recommendation",
    )
    register_tool(
        "import_inventory",
        "Import local JSON inventory into graph facts and graph triples.",
        import_inventory_from_json,
        "approval_required",
    )


_register_defaults()
