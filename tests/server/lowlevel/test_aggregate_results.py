"""Tests for Gumloop aggregate_tool_call_results config."""

import json
from typing import Any

import pytest

from mcp.server import Server
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent, Tool


@pytest.mark.anyio
async def test_aggregate_tool_call_results_enabled():
    """When aggregate_tool_call_results=True, multiple content items combine into single JSON."""
    server = Server("test")
    server.config = {"aggregate_tool_call_results": True}

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name="multi", description="Multi", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        return [TextContent(type="text", text="Result 1"), TextContent(type="text", text="Result 2")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("multi", {})

    assert result.isError is False
    assert len(result.content) == 1
    content = result.content[0]
    assert isinstance(content, TextContent)
    parsed = json.loads(content.text)
    assert len(parsed) == 2
    assert parsed[0]["text"] == "Result 1"
    assert parsed[1]["text"] == "Result 2"


@pytest.mark.anyio
async def test_aggregate_tool_call_results_disabled():
    """When aggregate_tool_call_results not set, multiple content items remain separate."""
    server = Server("test")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name="multi", description="Multi", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        return [TextContent(type="text", text="Result 1"), TextContent(type="text", text="Result 2")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("multi", {})

    assert result.isError is False
    assert len(result.content) == 2
    c0, c1 = result.content[0], result.content[1]
    assert isinstance(c0, TextContent) and isinstance(c1, TextContent)
    assert c0.text == "Result 1"
    assert c1.text == "Result 2"
