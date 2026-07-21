import httpx

from hermes_agent.generators.base import BaseGenerator


class OllamaGenerator(BaseGenerator):
    def __init__(
        self,
        model: str = "qwen3:8b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=self._timeout,
        )

        response.raise_for_status()

        data = response.json()

        return str(data["response"]).strip()
