from abc import ABC, abstractmethod

from hermes_agent.documents.document import Document
from hermes_agent.rag.chunk import Chunk


class TextSplitter(ABC):
    """Base interface for text splitters."""

    @abstractmethod
    def split(self, document: Document) -> list[Chunk]:
        """Split a document into chunks."""
        raise NotImplementedError
