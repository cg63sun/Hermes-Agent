from hermes_agent.rag.chunk import Chunk
from hermes_agent.utils.math import cosine_similarity

from .base import VectorStore


class MemoryVectorStore(VectorStore):
    """메모리 기반 Vector Store"""

    def __init__(self):
        self._items: list[tuple[Chunk, list[float]]] = []

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        for chunk, embedding in zip(chunks, embeddings):
            self._items.append((chunk, embedding))

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        source: str | None = None,
    ) -> list[Chunk]:
        scored = []

        for chunk, vector in self._items:
            if (
                source is not None
                and chunk.metadata.get("source") != source
            ):
                continue

            score = cosine_similarity(embedding, vector)
            scored.append((score, chunk))

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            chunk
            for _, chunk in scored[:top_k]
        ]
