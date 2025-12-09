"""Tests for Gumloop AuthError exception handling."""

import json

import pytest

from mcp.server import Server
from mcp.shared.exceptions import AuthError
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import AuthErrorData, TextContent, Tool


@pytest.mark.anyio
async def test_auth_error_returns_structured_data():
    """AuthError raised in tool should return isError=False with serialized AuthErrorData."""
    server = Server("test")

    @server.list_tools()
    async def list_tools():
        return [Tool(name="auth", description="Auth", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        raise AuthError(AuthErrorData(error="credentials_not_found", message="Auth required", service="svc", error_status=401))

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("auth", {})

    assert result.isError is False
    parsed = json.loads(result.content[0].text)
    assert parsed["error"] == "credentials_not_found"
    assert parsed["message"] == "Auth required"
    assert parsed["service"] == "svc"
    assert parsed["error_status"] == 401


@pytest.mark.anyio
async def test_regular_exception_returns_is_error_true():
    """Regular exceptions should return isError=True."""
    server = Server("test")

    @server.list_tools()
    async def list_tools():
        return [Tool(name="error", description="Error", inputSchema={"type": "object", "properties": {}})]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        raise ValueError("Something went wrong")

    async with create_connected_server_and_client_session(server) as client:
        result = await client.call_tool("error", {})

    assert result.isError is True
    assert "Something went wrong" in result.content[0].text
