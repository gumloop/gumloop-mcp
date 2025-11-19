from mcp.types import ErrorData, AuthErrorData


class McpError(Exception):
    """
    Exception type raised when an error arrives over an MCP connection.
    """

    error: ErrorData

    def __init__(self, error: ErrorData):
        """Initialize McpError."""
        super().__init__(error.message)
        self.error = error


class AuthError(Exception):
    """
    Exception type raised for authentication and authorization failures.
    """

    details: AuthErrorData

    def __init__(self, details: AuthErrorData):
        """Initialize AuthError."""
        super().__init__(details.message)
        self.details = details
