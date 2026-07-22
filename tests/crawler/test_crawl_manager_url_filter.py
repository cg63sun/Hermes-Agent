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
        self.requested_urls: list[str] = []

    def fetch(self, url: str) -> MockPage:
        self.requested_urls.append(url)

        if url not in self._pages:
            raise RuntimeError(f"페이지가 없습니다: {url}")

        return self._pages[url]


def test_crawl_manager_skips_blocked_urls() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/about">회사소개</a>
                    <a href="/admin/users">관리자</a>
                    <a href="/files/catalog.pdf">카탈로그</a>
                    <a href="/images/photo.jpg">이미지</a>
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

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=10,
        max_depth=1,
    )

    assert len(pages) == 2

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/about",
    ]
