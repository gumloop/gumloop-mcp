"""Tests for Gumloop logging utilities."""

import logging

from mcp.shared.logging_utils import UrlRedactingFilter, redact_url_logs


def test_redacts_gumloop_url_in_msg():
    """URLs in msg should be redacted to scheme://netloc."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "https://mcp.gumloop.com/api/secret", (), None)
    f.filter(record)
    assert record.msg == "https://mcp.gumloop.com"


def test_preserves_non_gumloop_url():
    """Non-gumloop URLs should not be redacted."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "https://example.com/path", (), None)
    f.filter(record)
    assert record.msg == "https://example.com/path"


def test_redacts_url_in_tuple_args():
    """URLs in tuple args should be redacted."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "%s", ("https://mcp.gumloop.com/secret",), None)
    f.filter(record)
    assert record.args == ("https://mcp.gumloop.com",)


def test_redacts_url_in_dict_args():
    """URLs in dict args should be redacted."""
    f = UrlRedactingFilter()
    record = logging.LogRecord(
        "test", logging.INFO, "", 0, "%(url)s", ({"url": "https://mcp.gumloop.com/secret"},), None
    )
    f.filter(record)
    assert record.args == {"url": "https://mcp.gumloop.com"}


def test_redacts_url_in_exception():
    """URLs in exception args should be redacted."""
    f = UrlRedactingFilter()
    exc = ValueError("Error at https://mcp.gumloop.com/api/secret")
    record = logging.LogRecord("test", logging.ERROR, "", 0, "Error", (), (ValueError, exc, None))
    f.filter(record)
    assert exc.args == ("Error at https://mcp.gumloop.com",)


def test_handles_non_string_args():
    """Non-string args should pass through unchanged."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "%d %s", (42, "text"), None)
    f.filter(record)
    assert record.args == (42, "text")


def test_handles_non_string_dict_args():
    """Non-string dict values should pass through unchanged."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "%(num)d", ({"num": 42},), None)
    f.filter(record)
    assert record.args == {"num": 42}


def test_redact_url_logs_adds_filter():
    """redact_url_logs should add filter to logger."""
    logger = logging.getLogger("test.gumloop.redact")
    initial = len(logger.filters)
    redact_url_logs(logger)
    assert len(logger.filters) == initial + 1
    assert any(isinstance(f, UrlRedactingFilter) for f in logger.filters)


def test_handles_subdomain():
    """Should redact URLs with subdomains before mcp.gumloop.com."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "https://api.mcp.gumloop.com/secret", (), None)
    f.filter(record)
    assert record.msg == "https://api.mcp.gumloop.com"


def test_handles_non_string_msg():
    """Non-string msg should pass through unchanged."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, 12345, (), None)
    f.filter(record)
    assert record.msg == 12345


def test_handles_empty_args():
    """Empty args should pass through."""
    f = UrlRedactingFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", None, None)
    f.filter(record)
    assert record.args is None


def test_handles_exception_without_args():
    """Exception without args should pass through."""
    f = UrlRedactingFilter()
    exc = ValueError()
    exc.args = ()
    record = logging.LogRecord("test", logging.ERROR, "", 0, "Error", (), (ValueError, exc, None))
    f.filter(record)
    assert exc.args == ()
