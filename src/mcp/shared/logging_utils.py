"""Logging utilities for MCP."""

import logging
import re
from urllib.parse import urlparse

__all__ = ["redact_url_logs"]


class UrlRedactingFilter(logging.Filter):
    """Redacts URLs in log messages to prevent credential leaks."""
    
    URL_PATTERN = re.compile(r'https?://[^\s]+')
    
    @staticmethod
    def _redact_url(match):
        """Redact a URL to only show scheme and netloc."""
        url = match.group(0)
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.URL_PATTERN.sub(self._redact_url, record.msg)
        
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self.URL_PATTERN.sub(self._redact_url, str(v))
                    for k, v in record.args.items()
                }
            else:
                record.args = tuple(
                    self.URL_PATTERN.sub(self._redact_url, str(arg))
                    for arg in record.args
                )
        
        # Sanitize exception info if present
        if record.exc_info and record.exc_info[1]:
            exc = record.exc_info[1]
            if hasattr(exc, 'args') and exc.args:
                redacted_args = tuple(
                    self.URL_PATTERN.sub(self._redact_url, str(arg)) if isinstance(arg, str) else arg
                    for arg in exc.args
                )
                exc.args = redacted_args
        
        return True


def redact_url_logs(logger: logging.Logger) -> None:
    """Add URL redacting filter to logger to strip paths and credentials from URLs."""
    logger.addFilter(UrlRedactingFilter())

