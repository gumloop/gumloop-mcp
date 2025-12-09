"""Tests for Gumloop restricted_tools config."""

import pytest

from mcp.server import Server
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent, Tool


@pytest.mark.anyio
async def test_restricted_tools_filtered_from_list():
    """Tools in restricted_tools config should not appear in list_tools."""
    server = Server("test")
    server.config = {"restricted_tools": ["blocked"]}

    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="allowed", description="Allowed", inputSchema={"type": "object", "properties": {}}),
            Tool(name="blocked", description="Blocked", inputSchema={"type": "object", "properties": {}}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        return [TextContent(type="text", text="ok")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.list_tools()

    assert len(result.tools) == 1
    assert result.tools[0].name == "allowed"


@pytest.mark.anyio
async def test_restricted_tool_call_returns_error():
    """Calling a restricted tool should return an error."""
    server = Server("test")
    server.config = {"restricted_tools": ["blocked"]}

    @server.list_tools()
    async def list_tools():
        return [Tool(name="blocked", description="Blocked", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        return [TextContent(type="text", text="should not reach")]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("blocked", {})

    assert result.isError is True
    assert "restricted" in result.content[0].text.lower()


@pytest.mark.anyio
async def test_no_restrictions_allows_all():
    """Without restricted_tools config, all tools should be available."""
    server = Server("test")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="tool1", description="Tool 1", inputSchema={"type": "object", "properties": {}}),
            Tool(name="tool2", description="Tool 2", inputSchema={"type": "object", "properties": {}}),
        ]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.list_tools()

    assert len(result.tools) == 2
