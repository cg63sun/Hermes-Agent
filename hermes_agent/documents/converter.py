from uuid import uuid4

from hermes_agent.documents.document import Document
from hermes_agent.models.page import WebPage


class DocumentConverter:
    """Convert WebPage objects into Documents."""

    def from_webpage(self, page: WebPage) -> Document:
        return Document(
            id=str(uuid4()),
            source=page.url,
            title=page.title,
            content=page.text,
            metadata={
                "url": page.url,
            },
        )
