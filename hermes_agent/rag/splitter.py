from uuid import uuid4

from hermes_agent.documents.document import Document
from hermes_agent.rag.chunk import Chunk


class ChunkSplitter:
    """Split a document into fixed-size chunks."""

    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size

    def split(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []

        text = document.content

        for index, start in enumerate(range(0, len(text), self.chunk_size)):
            content = text[start:start + self.chunk_size]

            chunks.append(
                Chunk(
                    id=str(uuid4()),
                    document_id=document.id,
                    index=index,
                    content=content,
                    metadata=document.metadata.copy(),
                )
            )

        return chunks
