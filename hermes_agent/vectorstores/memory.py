from hermes_agent.rag.chunk import Chunk

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
    ) -> list[Chunk]:
        if not self._items:
            return []

        # 임시 구현
        return [chunk for chunk, _ in self._items[:top_k]]
