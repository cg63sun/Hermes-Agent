from pathlib import Path
from typing import Any

from hermes_agent.cli import crawl as crawl_cli


class MockReport:
    page_count = 2
    visited_count = 3
    failed_count = 1
    blocked_count = 1

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


class MockManager:
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self.kwargs = kwargs

    def crawl_with_report(
        self,
        start_url: str,
        max_pages: int,
        max_depth: int,
    ) -> MockReport:
        assert start_url == "https://example.com"
        assert max_pages == 10
        assert max_depth == 1

        return MockReport()


def test_run_crawl_saves_report(
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
        MockManager,
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
        / "crawl-report.json"
    )

    result = crawl_cli.run_crawl(
        url="https://example.com",
        max_pages=10,
        max_depth=1,
        output=output_path,
    )

    assert result == output_path
    assert output_path.exists()


def test_build_parser_defaults() -> None:
    parser = crawl_cli.build_parser()

    args = parser.parse_args(
        ["https://example.com"],
    )

    assert args.url == "https://example.com"
    assert args.max_pages == 50
    assert args.max_depth == 2
    assert args.output == "output/crawl-report.json"
    assert args.no_robots is False
    assert args.no_sitemap is False
    assert args.no_filter is False


def test_build_parser_options() -> None:
    parser = crawl_cli.build_parser()

    args = parser.parse_args(
        [
            "https://example.com",
            "--max-pages",
            "20",
            "--max-depth",
            "3",
            "--output",
            "reports/result.json",
            "--no-robots",
            "--no-sitemap",
            "--no-filter",
        ],
    )

    assert args.max_pages == 20
    assert args.max_depth == 3
    assert args.output == "reports/result.json"
    assert args.no_robots is True
    assert args.no_sitemap is True
    assert args.no_filter is True
