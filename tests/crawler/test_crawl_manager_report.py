from dataclasses import dataclass

from hermes_agent.crawler.crawl_manager import CrawlManager
from hermes_agent.crawler.url_filter import URLFilter


@dataclass
class MockPage:
    url: str
    title: str
    html: str
    text: str


class MockCrawler:
    def __init__(
        self,
        pages: dict[str, MockPage],
    ) -> None:
        self._pages = pages

    def fetch(self, url: str) -> MockPage:
        if url not in self._pages:
            raise RuntimeError(
                f"페이지를 가져올 수 없습니다: {url}",
            )

        return self._pages[url]


def test_crawl_manager_creates_report() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/about">회사소개</a>
                    <a href="/missing">없는 페이지</a>
                    <a href="/admin/users">관리자</a>
                """,
                text="홈",
            ),
            "https://example.com/about": MockPage(
                url="https://example.com/about",
                title="회사소개",
                html="",
                text="회사소개",
            ),
        },
    )

    manager = CrawlManager(
        crawler=crawler,
        url_filter=URLFilter(),
    )

    report = manager.crawl_with_report(
        start_url="https://example.com",
        max_pages=10,
        max_depth=1,
    )

    assert report.page_count == 2

    assert report.page_urls == [
        "https://example.com/",
        "https://example.com/about",
    ]

    assert report.failed_urls == [
        "https://example.com/missing",
    ]

    assert report.blocked_urls == [
        "https://example.com/admin/users",
    ]


def test_crawl_manager_report_handles_invalid_url() -> None:
    manager = CrawlManager(
        crawler=MockCrawler(pages={}),
    )

    report = manager.crawl_with_report(
        start_url="invalid-url",
    )

    assert report.page_count == 0
    assert report.failed_urls == [
        "invalid-url",
    ]
