import pytest

from hermes_agent.browser.browser_crawler import (
    BrowserCrawler,
    BrowserPage,
)


def test_browser_crawler_fetches_page() -> None:
    crawler = BrowserCrawler(
        headless=True,
    )

    page = crawler.fetch(
        "https://example.com",
    )

    assert isinstance(
        page,
        BrowserPage,
    )

    assert page.title == (
        "Example Domain"
    )

    assert page.url.startswith(
        "https://example.com",
    )

    assert "Example Domain" in page.html
    assert "Example Domain" in page.text

    assert isinstance(
        page.links,
        list,
    )

    assert isinstance(
        page.images,
        list,
    )


def test_browser_crawler_extracts_links() -> None:
    crawler = BrowserCrawler(
        headless=True,
    )

    page = crawler.fetch(
        "https://example.com",
    )

    assert any(
        "iana.org" in link
        for link in page.links
    )


def test_browser_crawler_rejects_empty_url() -> None:
    crawler = BrowserCrawler(
        headless=True,
    )

    with pytest.raises(
        ValueError,
        match="URL",
    ):
        crawler.fetch(
            "   ",
        )
