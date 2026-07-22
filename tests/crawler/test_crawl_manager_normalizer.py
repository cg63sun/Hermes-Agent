from dataclasses import dataclass

from hermes_agent.crawler.crawl_manager import (
    CrawlManager,
)
from hermes_agent.crawler.url_normalizer import (
    URLNormalizer,
)


@dataclass
class MockPage:
    title: str
    url: str
    html: str
    text: str


class MockCrawler:
    def __init__(self) -> None:
        self.requested_urls: list[str] = []

    def fetch(
        self,
        url: str,
    ) -> MockPage:
        self.requested_urls.append(url)

        if url == "https://example.com/":
            return MockPage(
                title="Home",
                url=url,
                html="""
                <html>
                    <body>
                        <a href="/about/">
                            About 1
                        </a>

                        <a href="/about?utm_source=google">
                            About 2
                        </a>

                        <a href="/about#team">
                            About 3
                        </a>
                    </body>
                </html>
                """,
                text="Home",
            )

        return MockPage(
            title="About",
            url=url,
            html="<html><body>About</body></html>",
            text="About",
        )


def test_crawl_manager_normalizes_duplicate_links() -> None:
    crawler = MockCrawler()

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=None,
        sitemap_loader=None,
        url_filter=None,
        url_normalizer=URLNormalizer(),
    )

    pages = manager.crawl(
        start_url="https://example.com/",
        max_pages=10,
        max_depth=2,
    )

    assert len(pages) == 2

    assert crawler.requested_urls == [
        "https://example.com/",
        "https://example.com/about",
    ]


def test_crawl_manager_normalizes_start_url() -> None:
    crawler = MockCrawler()

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=None,
        sitemap_loader=None,
        url_filter=None,
        url_normalizer=URLNormalizer(),
    )

    manager.crawl(
        start_url=(
            "https://example.com/"
            "?utm_source=google#top"
        ),
        max_pages=1,
        max_depth=0,
    )

    assert crawler.requested_urls == [
        "https://example.com/",
    ]


def test_extract_links_removes_tracking_parameters() -> None:
    crawler = MockCrawler()

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=None,
        sitemap_loader=None,
        url_filter=None,
        url_normalizer=URLNormalizer(),
    )

    links = manager._extract_links(
        html="""
        <a href="/service?utm_campaign=test">
            Service
        </a>
        <a href="/contact?fbclid=123">
            Contact
        </a>
        """,
        current_url="https://example.com/",
    )

    assert links == [
        "https://example.com/service",
        "https://example.com/contact",
    ]
