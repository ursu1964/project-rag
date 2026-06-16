import pytest

from app.mcp.tool_contracts import TOOL_MODES, ToolContract
from app.mcp.tool_registry import get_tool, list_tools, register_tool


def test_default_tools_are_registered():
    names = {tool.name for tool in list_tools()}
    assert {"search_documents", "query_graph", "add_memory", "import_inventory"}.issubset(names)


def test_get_tool_returns_contract():
    tool = get_tool("query_graph")
    assert isinstance(tool, ToolContract)
    assert tool.mode == "read_only"


def test_register_tool_rejects_invalid_mode():
    with pytest.raises(ValueError):
        register_tool("bad", "bad", lambda: None, "invalid")


def test_supported_modes():
    assert TOOL_MODES == {"read_only", "recommendation", "approval_required", "execution_disabled"}
