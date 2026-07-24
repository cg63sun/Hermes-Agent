from __future__ import annotations

from typing import Any

from hermes_agent.cli import website_rag as website_rag_cli


class MockService:
    def __init__(self) -> None:
        self.received_source: str | None = None

    def index_website(self, url: str) -> int:
        return 3

    def answer(
        self,
        question: str,
        top_k: int = 5,
        source: str | None = None,
    ) -> str:
        self.received_source = source
        return "테스트 답변입니다."


def test_run_passes_source(monkeypatch: Any) -> None:
    service = MockService()

    monkeypatch.setattr(
        website_rag_cli.WebsiteRAGFactory,
        "create",
        lambda **kwargs: service,
    )

    result = website_rag_cli.run(
        url="https://example.com",
        question="회사 소개를 알려줘.",
        generator_model="qwen3:8b",
        embedding_model="nomic-embed-text",
        chunk_size=500,
        top_k=3,
        source="https://example.com",
    )

    assert service.received_source == "https://example.com"
    assert "테스트 답변입니다." in result


def test_build_parser_accepts_source() -> None:
    parser = website_rag_cli.build_parser()

    args = parser.parse_args(
        [
            "--url",
            "https://example.com",
            "--question",
            "회사 소개를 알려줘.",
            "--source",
            "https://example.com",
        ],
    )

    assert args.source == "https://example.com"
