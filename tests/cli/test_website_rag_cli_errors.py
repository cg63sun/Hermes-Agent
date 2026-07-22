from typing import Any

import httpx

from hermes_agent.cli import website_rag


def test_main_returns_zero_on_success(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    monkeypatch.setattr(
        website_rag,
        "run",
        lambda **kwargs: "색인된 청크 수: 1\n\n답변:\n테스트",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "website-rag",
            "--url",
            "https://example.com",
            "--question",
            "테스트 질문",
        ],
    )

    exit_code = website_rag.main()

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "색인된 청크 수: 1" in captured.out


def test_main_handles_connect_error(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    def raise_connect_error(**kwargs: Any) -> str:
        request = httpx.Request(
            "GET",
            "http://127.0.0.1:11434",
        )

        raise httpx.ConnectError(
            "연결 실패",
            request=request,
        )

    monkeypatch.setattr(
        website_rag,
        "run",
        raise_connect_error,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "website-rag",
            "--url",
            "https://example.com",
            "--question",
            "테스트 질문",
        ],
    )

    exit_code = website_rag.main()

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "연결할 수 없습니다" in captured.err
