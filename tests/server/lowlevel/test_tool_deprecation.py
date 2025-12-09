"""Tests for Gumloop tool deprecation filtering."""

import pytest

from mcp.server import Server
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import Tool


@pytest.mark.anyio
async def test_deprecated_tools_filtered():
    """Tools with is_deprecated=True should not appear in list_tools."""
    server = Server("test")

    @server.list_tools()
    async def list_tools():
        active = Tool(name="active", description="Active", inputSchema={"type": "object", "properties": {}})
        deprecated = Tool(name="deprecated", description="Old", inputSchema={"type": "object", "properties": {}})
        object.__setattr__(deprecated, "is_deprecated", True)
        return [active, deprecated]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.list_tools()

    assert len(result.tools) == 1
    assert result.tools[0].name == "active"


@pytest.mark.anyio
async def test_deprecated_properties_removed():
    """Properties with is_deprecated=True in inputSchema should be removed."""
    server = Server("test")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="tool",
                description="Tool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "active_param": {"type": "string"},
                        "old_param": {"type": "string", "is_deprecated": True},
                    },
                },
            )
        ]

    async with create_connected_server_and_client_session(server) as client:
        result = await client.list_tools()

    assert len(result.tools) == 1
    assert "active_param" in result.tools[0].inputSchema["properties"]
    assert "old_param" not in result.tools[0].inputSchema["properties"]
