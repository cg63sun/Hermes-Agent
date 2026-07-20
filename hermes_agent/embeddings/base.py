from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """Embedding 모델의 공통 인터페이스"""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """단일 텍스트를 임베딩합니다."""
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """여러 텍스트를 임베딩합니다."""
        return [self.embed(text) for text in texts]
