"""Tests for Gumloop external_client config."""

from typing import Any

import pytest

from mcp.server import Server
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent, Tool


@pytest.mark.anyio
async def test_external_client_removes_custom_fields():
    """external_client=True should remove outputSchema, requiredScopes, creditCost from tools."""
    server = Server("test")
    server.config = {"external_client": True}

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tool = Tool(name="tool", description="Tool", inputSchema={"type": "object", "properties": {}})
        object.__setattr__(tool, "outputSchema", {"type": "object"})
        object.__setattr__(tool, "requiredScopes", ["read"])
        object.__setattr__(tool, "creditCost", 10)
        return [tool]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:  # pragma: no cover
        return [TextContent(type="text", text="ok")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.list_tools()

    assert len(result.tools) == 1
    assert result.tools[0].outputSchema is None
    assert not hasattr(result.tools[0], "requiredScopes")
    assert not hasattr(result.tools[0], "creditCost")


@pytest.mark.anyio
async def test_external_client_empty_result_default_message():
    """external_client=True with gummie_id and empty result returns default JSON."""
    server = Server("test")
    server.config = {"external_client": True, "gummie_id": "123"}

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name="empty", description="Empty", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        return []

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("empty", {})

    assert result.isError is False
    assert len(result.content) == 1
    content = result.content[0]
    assert isinstance(content, TextContent)
    assert content.text == '{"message": "No result found"}'


@pytest.mark.anyio
async def test_external_client_without_gummie_id_no_default():
    """external_client=True without gummie_id should NOT add default message."""
    server = Server("test")
    server.config = {"external_client": True}

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name="empty", description="Empty", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        return []

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("empty", {})

    assert result.isError is False
    assert len(result.content) == 0


@pytest.mark.anyio
async def test_external_client_filters_response_content():
    """external_client=True should filter response content through filter_response_content_for_external_mcp."""
    server = Server("test")
    server.config = {"external_client": True}

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name="tool", description="Tool", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        return [TextContent(type="text", text="result")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("tool", {})

    assert result.isError is False
    assert len(result.content) == 1
    content = result.content[0]
    assert isinstance(content, TextContent)
    assert content.text == "result"
