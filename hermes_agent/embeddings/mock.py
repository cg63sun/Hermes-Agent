from .base import EmbeddingModel


class MockEmbeddingModel(EmbeddingModel):
    """테스트용 Embedding 모델"""

    def embed(self, text: str) -> list[float]:
        if not text:
            return []

        return [float(ord(char)) for char in text]

