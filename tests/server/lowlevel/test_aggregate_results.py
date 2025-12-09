"""Tests for Gumloop aggregate_tool_call_results config."""

import json

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
    async def list_tools():
        return [Tool(name="multi", description="Multi", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        return [TextContent(type="text", text="Result 1"), TextContent(type="text", text="Result 2")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("multi", {})

    assert result.isError is False
    assert len(result.content) == 1
    parsed = json.loads(result.content[0].text)
    assert len(parsed) == 2
    assert parsed[0]["text"] == "Result 1"
    assert parsed[1]["text"] == "Result 2"


@pytest.mark.anyio
async def test_aggregate_tool_call_results_disabled():
    """When aggregate_tool_call_results not set, multiple content items remain separate."""
    server = Server("test")

    @server.list_tools()
    async def list_tools():
        return [Tool(name="multi", description="Multi", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        return [TextContent(type="text", text="Result 1"), TextContent(type="text", text="Result 2")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("multi", {})

    assert result.isError is False
    assert len(result.content) == 2
    assert result.content[0].text == "Result 1"
    assert result.content[1].text == "Result 2"
