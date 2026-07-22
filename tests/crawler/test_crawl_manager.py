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


def test_crawl_manager_crawls_internal_links() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/about">회사소개</a>
                    <a href="/service">서비스</a>
                    <a href="https://outside.com/page">
                        외부 링크
                    </a>
                """,
                text="홈페이지",
            ),
            "https://example.com/about": MockPage(
                url="https://example.com/about",
                title="회사소개",
                html='<a href="/service">서비스</a>',
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

    manager = CrawlManager(crawler=crawler)

    pages = manager.crawl(
        start_url="https://example.com/",
        max_pages=10,
        max_depth=2,
    )

    assert len(pages) == 3

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/service",
    ]


def test_crawl_manager_removes_duplicate_links() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/about">회사소개</a>
                    <a href="/about/">회사소개 중복</a>
                    <a href="/about#team">회사소개 팀</a>
                """,
                text="홈페이지",
            ),
            "https://example.com/about": MockPage(
                url="https://example.com/about",
                title="회사소개",
                html="",
                text="회사소개 내용",
            ),
        },
    )

    manager = CrawlManager(crawler=crawler)

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


def test_crawl_manager_respects_max_pages() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/one">One</a>
                    <a href="/two">Two</a>
                    <a href="/three">Three</a>
                """,
                text="홈",
            ),
            "https://example.com/one": MockPage(
                url="https://example.com/one",
                title="One",
                html="",
                text="One",
            ),
            "https://example.com/two": MockPage(
                url="https://example.com/two",
                title="Two",
                html="",
                text="Two",
            ),
            "https://example.com/three": MockPage(
                url="https://example.com/three",
                title="Three",
                html="",
                text="Three",
            ),
        },
    )

    manager = CrawlManager(crawler=crawler)

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=2,
        max_depth=2,
    )

    assert len(pages) == 2


def test_crawl_manager_respects_max_depth() -> None:
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
                html='<a href="/history">연혁</a>',
                text="회사소개",
            ),
            "https://example.com/history": MockPage(
                url="https://example.com/history",
                title="연혁",
                html="",
                text="연혁",
            ),
        },
    )

    manager = CrawlManager(crawler=crawler)

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


def test_crawl_manager_skips_failed_page() -> None:
    crawler = MockCrawler(
        pages={
            "https://example.com/": MockPage(
                url="https://example.com/",
                title="홈",
                html="""
                    <a href="/missing">없는 페이지</a>
                    <a href="/about">회사소개</a>
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

    manager = CrawlManager(crawler=crawler)

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=10,
        max_depth=1,
    )

    assert len(pages) == 2
    assert pages[0].title == "홈"
    assert pages[1].title == "회사소개"


def test_crawl_manager_handles_zero_max_pages() -> None:
    manager = CrawlManager(
        crawler=MockCrawler(pages={}),
    )

    pages = manager.crawl(
        start_url="https://example.com",
        max_pages=0,
    )

    assert pages == []
