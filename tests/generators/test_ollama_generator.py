from typing import Any

import httpx

from hermes_agent.generators import OllamaGenerator


class MockResponse:
    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, str]:
        return {
            "response": "Python은 프로그래밍 언어입니다.",
        }


def test_ollama_generator_returns_response(
    monkeypatch: Any,
) -> None:
    request_data: dict[str, Any] = {}

    def mock_post(
        url: str,
        json: dict[str, Any],
        timeout: float,
    ) -> MockResponse:
        request_data["url"] = url
        request_data["json"] = json
        request_data["timeout"] = timeout

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    generator = OllamaGenerator(
        model="qwen3:8b",
        base_url="http://127.0.0.1:11434/",
        timeout=30.0,
    )

    result = generator.generate("Python이란 무엇인가요?")

    assert result == "Python은 프로그래밍 언어입니다."

    assert request_data["url"] == (
        "http://127.0.0.1:11434/api/generate"
    )

    assert request_data["json"] == {
        "model": "qwen3:8b",
        "prompt": "Python이란 무엇인가요?",
        "stream": False,
    }

    assert request_data["timeout"] == 30.0

def test_ollama_generator_sends_json_schema(
    monkeypatch: Any,
) -> None:
    request_data: dict[str, Any] = {}

    def mock_post(
        url: str,
        json: dict[str, Any],
        timeout: float,
    ) -> MockResponse:
        request_data["json"] = json
        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    json_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
        },
        "required": ["name"],
    }

    generator = OllamaGenerator(
        json_schema=json_schema,
    )

    generator.generate("JSON으로 작성하세요.")

    assert request_data["json"]["format"] == json_schema
