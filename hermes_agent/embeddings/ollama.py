import httpx

from .base import EmbeddingModel


class OllamaEmbeddingModel(EmbeddingModel):
    """Ollama Embedding 모델"""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
        timeout: float = 30.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def embed(self, text: str) -> list[float]:
        response = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.model,
                "prompt": text,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        return data["embedding"]
