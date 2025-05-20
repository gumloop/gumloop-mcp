"""FastMCP - A more ergonomic interface for MCP servers."""

from .server import Context, FastMCP
from .utilities.types import Image

__version__ = "0.1.0"
__all__ = ["FastMCP", "Context", "Image"]
