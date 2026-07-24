from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from hermes_agent.cli import research as research_cli


class FakeService:
    def __init__(self) -> None:
        self.received_source: str | None = None

    def index(
        self,
        urls: list[str],
        *,
        continue_on_error: bool,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            document_count=1,
            chunk_count=2,
            indexed_count=2,
            failure_count=0,
            failures=[],
        )

    def answer(
        self,
        question: str,
        *,
        top_k: int,
        source: str | None = None,
    ) -> str:
        self.received_source = source
        return "테스트 답변입니다."


def test_build_parser_accepts_source() -> None:
    parser = research_cli.build_parser()

    args = parser.parse_args(
        [
            "https://example.com",
            "--question",
            "회사 소개를 알려줘.",
            "--source",
            "https://example.com",
        ],
    )

    assert args.source == "https://example.com"


def test_run_research_passes_source(
    monkeypatch: Any,
) -> None:
    service = FakeService()

    monkeypatch.setattr(
        research_cli.ResearchRAGFactory,
        "create",
        lambda **kwargs: service,
    )

    answer = research_cli.run_research(
        ["https://example.com"],
        question="회사 소개를 알려줘.",
        source="https://example.com",
    )

    assert answer == "테스트 답변입니다."
    assert service.received_source == "https://example.com"
