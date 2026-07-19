from dataclasses import dataclass


@dataclass(slots=True)
class WebPage:
    """Represents a crawled web page."""

    url: str
    title: str
    text: str
    html: str
