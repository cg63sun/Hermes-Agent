from abc import ABC, abstractmethod

from hermes_agent.rag.chunk import Chunk


class VectorStore(ABC):
    """Vector Store의 공통 인터페이스"""

    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Chunk와 Embedding을 저장합니다."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[Chunk]:
        """가장 유사한 Chunk를 검색합니다."""
        raise NotImplementedError
