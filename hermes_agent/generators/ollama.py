from typing import Any

import httpx

from hermes_agent.generators.base import BaseGenerator


class OllamaGenerator(BaseGenerator):
    def __init__(
        self,
        model: str = "qwen3:8b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
        json_schema: dict[str, Any] | None = None,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._json_schema = json_schema

    def generate(self, prompt: str) -> str:
        request_json: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }

        if self._json_schema is not None:
            request_json["format"] = self._json_schema

        response = httpx.post(
            f"{self._base_url}/api/generate",
            json=request_json,
            timeout=self._timeout,
        )

        response.raise_for_status()

        data = response.json()

        return str(data["response"]).strip()
