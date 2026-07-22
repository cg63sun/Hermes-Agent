from dataclasses import dataclass

from hermes_agent.crawler.crawl_report import CrawlReport


@dataclass
class MockPage:
    url: str
    title: str


def test_crawl_report_counts_results() -> None:
    report = CrawlReport(
        pages=[
            MockPage(
                url="https://example.com/",
                title="홈",
            ),
            MockPage(
                url="https://example.com/about",
                title="회사소개",
            ),
        ],
        visited_urls=[
            "https://example.com/",
            "https://example.com/about",
            "https://example.com/missing",
        ],
        failed_urls=[
            "https://example.com/missing",
        ],
        blocked_urls=[
            "https://example.com/admin",
        ],
    )

    assert report.page_count == 2
    assert report.visited_count == 3
    assert report.failed_count == 1
    assert report.blocked_count == 1


def test_crawl_report_returns_page_urls() -> None:
    report = CrawlReport(
        pages=[
            MockPage(
                url="https://example.com/",
                title="홈",
            ),
            MockPage(
                url="https://example.com/service",
                title="서비스",
            ),
        ],
    )

    assert report.page_urls == [
        "https://example.com/",
        "https://example.com/service",
    ]


def test_crawl_report_defaults_to_empty_lists() -> None:
    report = CrawlReport()

    assert report.pages == []
    assert report.visited_urls == []
    assert report.failed_urls == []
    assert report.blocked_urls == []

    assert report.page_count == 0
    assert report.visited_count == 0
    assert report.failed_count == 0
    assert report.blocked_count == 0
    assert report.page_urls == []
