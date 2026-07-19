"""
Custom exceptions for Hermes Agent.
"""


class HermesError(Exception):
    """Base exception for all Hermes Agent errors."""


class ConfigurationError(HermesError):
    """Raised when configuration is invalid."""


class BrowserError(HermesError):
    """Raised when browser operations fail."""


class CrawlError(HermesError):
    """Raised when crawling fails."""
