from dataclasses import dataclass

from hermes_agent.crawler.crawl_manager import CrawlManager


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
        return self._pages[url]


class MockRobotsChecker:
    def __init__(self) -> None:
        self.loaded_base_url: str | None = None

    def load(self, base_url: str) -> None:
        self.loaded_base_url = base_url

    def can_fetch(self, url: str) -> bool:
        return not url.endswith("/private")


def test_crawl_manager_respects_robots_rules() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/public">공개</a>
                    <a href="/private">비공개</a>
                """,
                text="홈",
            ),
            "https://example.com/public": MockPage(
                url="https://example.com/public",
                title="공개",
                html="",
                text="공개 페이지",
            ),
            "https://example.com/private": MockPage(
                url="https://example.com/private",
                title="비공개",
                html="",
                text="비공개 페이지",
            ),
        },
    )

    robots_checker = MockRobotsChecker()

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=robots_checker,
    )

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=10,
        max_depth=1,
    )

    assert robots_checker.loaded_base_url == (
        "https://example.com"
    )

    assert len(pages) == 2

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/public",
    ]


def test_crawl_manager_continues_when_robots_load_fails() -> None:
    class FailingRobotsChecker:
        def load(self, base_url: str) -> None:
            raise RuntimeError("robots.txt 오류")

        def can_fetch(self, url: str) -> bool:
            return True

    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="",
                text="홈",
            ),
        },
    )

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=FailingRobotsChecker(),
    )

    pages = manager.crawl(
        start_url="https://example.com",
    )

    assert len(pages) == 1
