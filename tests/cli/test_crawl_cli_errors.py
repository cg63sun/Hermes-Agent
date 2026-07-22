from pathlib import Path
from typing import Any

import pytest

from hermes_agent.cli import crawl as crawl_cli


def test_validate_url_accepts_https() -> None:
    result = crawl_cli.validate_url(
        "https://example.com",
    )

    assert result == "https://example.com"


def test_validate_url_accepts_http() -> None:
    result = crawl_cli.validate_url(
        "http://example.com",
    )

    assert result == "http://example.com"


def test_validate_url_removes_spaces() -> None:
    result = crawl_cli.validate_url(
        "  https://example.com  ",
    )

    assert result == "https://example.com"


def test_validate_url_rejects_missing_scheme() -> None:
    with pytest.raises(
        ValueError,
        match="http:// 또는 https://",
    ):
        crawl_cli.validate_url(
            "example.com",
        )


def test_validate_url_rejects_invalid_scheme() -> None:
    with pytest.raises(
        ValueError,
        match="http:// 또는 https://",
    ):
        crawl_cli.validate_url(
            "ftp://example.com",
        )


def test_validate_url_rejects_missing_domain() -> None:
    with pytest.raises(
        ValueError,
        match="올바른 도메인",
    ):
        crawl_cli.validate_url(
            "https://",
        )


def test_run_crawl_rejects_zero_max_pages() -> None:
    with pytest.raises(
        ValueError,
        match="max_pages",
    ):
        crawl_cli.run_crawl(
            url="https://example.com",
            max_pages=0,
        )


def test_run_crawl_rejects_negative_depth() -> None:
    with pytest.raises(
        ValueError,
        match="max_depth",
    ):
        crawl_cli.run_crawl(
            url="https://example.com",
            max_depth=-1,
        )


class EmptyReport:
    page_count = 0
    visited_count = 1
    failed_count = 1
    blocked_count = 0

    def save_json(
        self,
        output: str | Path,
    ) -> Path:
        path = Path(output)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            "{}",
            encoding="utf-8",
        )

        return path


class EmptyManager:
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        pass

    def crawl_with_report(
        self,
        start_url: str,
        max_pages: int,
        max_depth: int,
    ) -> EmptyReport:
        return EmptyReport()


def test_run_crawl_raises_when_no_pages_collected(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        crawl_cli,
        "WebCrawler",
        lambda: object(),
    )

    monkeypatch.setattr(
        crawl_cli,
        "CrawlManager",
        EmptyManager,
    )

    monkeypatch.setattr(
        crawl_cli,
        "RobotsChecker",
        lambda: object(),
    )

    monkeypatch.setattr(
        crawl_cli,
        "SitemapLoader",
        lambda: object(),
    )

    monkeypatch.setattr(
        crawl_cli,
        "URLFilter",
        lambda: object(),
    )

    output_path = (
        tmp_path
        / "empty-report.json"
    )

    with pytest.raises(
        RuntimeError,
        match="수집된 페이지가 없습니다",
    ):
        crawl_cli.run_crawl(
            url="https://example.com",
            output=output_path,
        )

    assert output_path.exists()
