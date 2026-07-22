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

        if url not in self._pages:
            raise RuntimeError(f"페이지가 없습니다: {url}")

        return self._pages[url]


class MockSitemapLoader:
    def __init__(
        self,
        urls: list[str],
    ) -> None:
        self._urls = urls
        self.loaded_base_url: str | None = None

    def load(self, base_url: str) -> list[str]:
        self.loaded_base_url = base_url
        return self._urls


def test_crawl_manager_adds_sitemap_urls() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="",
                text="홈페이지",
            ),
            "https://example.com/about": MockPage(
                url="https://example.com/about",
                title="회사소개",
                html="",
                text="회사소개 내용",
            ),
            "https://example.com/service": MockPage(
                url="https://example.com/service",
                title="서비스",
                html="",
                text="서비스 내용",
            ),
        },
    )

    sitemap_loader = MockSitemapLoader(
        urls=[
            "https://example.com/about",
            "https://example.com/service",
        ],
    )

    manager = CrawlManager(
        crawler=crawler,
        sitemap_loader=sitemap_loader,
    )

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=10,
        max_depth=1,
    )

    assert sitemap_loader.loaded_base_url == (
        "https://example.com"
    )

    assert len(pages) == 3

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/service",
    ]


def test_crawl_manager_ignores_external_sitemap_urls() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="",
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

    sitemap_loader = MockSitemapLoader(
        urls=[
            "https://example.com/about",
            "https://outside.com/page",
        ],
    )

    manager = CrawlManager(
        crawler=crawler,
        sitemap_loader=sitemap_loader,
    )

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=10,
    )

    assert len(pages) == 2

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/about",
    ]


def test_crawl_manager_removes_duplicate_sitemap_urls() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html='<a href="/about">회사소개</a>',
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

    sitemap_loader = MockSitemapLoader(
        urls=[
            "https://example.com/about",
            "https://example.com/about/",
            "https://example.com/about#team",
        ],
    )

    manager = CrawlManager(
        crawler=crawler,
        sitemap_loader=sitemap_loader,
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


def test_crawl_manager_continues_when_sitemap_load_fails() -> None:
    class FailingSitemapLoader:
        def load(self, base_url: str) -> list[str]:
            raise RuntimeError("sitemap.xml 오류")

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
        sitemap_loader=FailingSitemapLoader(),
    )

    pages = manager.crawl(
        start_url="https://example.com",
    )

    assert len(pages) == 1
    assert pages[0].title == "홈"


def test_crawl_manager_applies_robots_to_sitemap_urls() -> None:
    class MockRobotsChecker:
        def load(self, base_url: str) -> None:
            pass

        def can_fetch(self, url: str) -> bool:
            return not url.endswith("/private")

    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="",
                text="홈",
            ),
            "https://example.com/public": MockPage(
                url="https://example.com/public",
                title="공개",
                html="",
                text="공개",
            ),
            "https://example.com/private": MockPage(
                url="https://example.com/private",
                title="비공개",
                html="",
                text="비공개",
            ),
        },
    )

    sitemap_loader = MockSitemapLoader(
        urls=[
            "https://example.com/public",
            "https://example.com/private",
        ],
    )

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=MockRobotsChecker(),
        sitemap_loader=sitemap_loader,
    )

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=10,
    )

    assert len(pages) == 2

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/public",
    ]
