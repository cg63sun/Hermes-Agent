import json
from dataclasses import dataclass
from pathlib import Path

from hermes_agent.crawler.crawl_report import CrawlReport


@dataclass
class MockPage:
    url: str
    title: str
    text: str


def test_crawl_report_converts_to_dict() -> None:
    report = CrawlReport(
        pages=[
            MockPage(
                url="https://example.com/",
                title="홈",
                text="홈페이지 내용",
            ),
        ],
        visited_urls=[
            "https://example.com/",
            "https://example.com/missing",
        ],
        failed_urls=[
            "https://example.com/missing",
        ],
        blocked_urls=[
            "https://example.com/admin",
        ],
    )

    data = report.to_dict()

    assert data["summary"] == {
        "page_count": 1,
        "visited_count": 2,
        "failed_count": 1,
        "blocked_count": 1,
    }

    assert data["pages"] == [
        {
            "url": "https://example.com/",
            "title": "홈",
            "text": "홈페이지 내용",
        },
    ]

    assert data["failed_urls"] == [
        "https://example.com/missing",
    ]

    assert data["blocked_urls"] == [
        "https://example.com/admin",
    ]


def test_crawl_report_converts_to_json() -> None:
    report = CrawlReport(
        pages=[
            MockPage(
                url="https://example.com/about",
                title="회사소개",
                text="회사소개 내용",
            ),
        ],
    )

    json_content = report.to_json()
    data = json.loads(json_content)

    assert data["summary"]["page_count"] == 1

    assert data["pages"][0]["title"] == (
        "회사소개"
    )

    assert data["pages"][0]["text"] == (
        "회사소개 내용"
    )


def test_crawl_report_preserves_korean_text() -> None:
    report = CrawlReport(
        pages=[
            MockPage(
                url="https://example.com/",
                title="홈페이지",
                text="안녕하세요",
            ),
        ],
    )

    json_content = report.to_json()

    assert "홈페이지" in json_content
    assert "안녕하세요" in json_content
    assert "\\ud648" not in json_content


def test_crawl_report_saves_json_file(
    tmp_path: Path,
) -> None:
    report = CrawlReport(
        pages=[
            MockPage(
                url="https://example.com/service",
                title="서비스",
                text="서비스 내용",
            ),
        ],
        visited_urls=[
            "https://example.com/service",
        ],
    )

    output_path = (
        tmp_path
        / "reports"
        / "crawl-report.json"
    )

    saved_path = report.save_json(
        output_path,
    )

    assert saved_path == output_path
    assert output_path.exists()

    data = json.loads(
        output_path.read_text(
            encoding="utf-8",
        ),
    )

    assert data["summary"]["page_count"] == 1

    assert data["pages"][0]["url"] == (
        "https://example.com/service"
    )


def test_crawl_report_saves_empty_report(
    tmp_path: Path,
) -> None:
    report = CrawlReport()

    output_path = (
        tmp_path
        / "empty-report.json"
    )

    report.save_json(output_path)

    data = json.loads(
        output_path.read_text(
            encoding="utf-8",
        ),
    )

    assert data["summary"] == {
        "page_count": 0,
        "visited_count": 0,
        "failed_count": 0,
        "blocked_count": 0,
    }

    assert data["pages"] == []
    assert data["visited_urls"] == []
    assert data["failed_urls"] == []
    assert data["blocked_urls"] == []
