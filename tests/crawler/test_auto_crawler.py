from __future__ import annotations

import pytest

from hermes_agent.browser.browser_crawler import (
    BrowserPage,
)
from hermes_agent.crawler.auto_crawler import (
    AutoCrawler,
    AutoCrawlResult,
)


class MockWebPage:
    def __init__(
        self,
        *,
        title: str = "Web Title",
        url: str = "https://example.com",
        html: str = "<html></html>",
        text: str = "충분한 본문 내용입니다.",
    ) -> None:
        self.title = title
        self.url = url
        self.html = html
        self.text = text


class MockWebCrawler:
    def __init__(
        self,
        *,
        page: MockWebPage | None = None,
        error: Exception | None = None,
    ) -> None:
        self.page = page
        self.error = error
        self.requested_urls: list[str] = []

    def fetch(
        self,
        url: str,
    ) -> MockWebPage:
        self.requested_urls.append(
            url,
        )

        if self.error is not None:
            raise self.error

        if self.page is None:
            raise RuntimeError(
                "Mock page is missing.",
            )

        return self.page


class MockBrowserCrawler:
    def __init__(
        self,
        page: BrowserPage,
    ) -> None:
        self.page = page
        self.requested_urls: list[str] = []

    def fetch(
        self,
        url: str,
    ) -> BrowserPage:
        self.requested_urls.append(
            url,
        )

        return self.page


def create_browser_page() -> BrowserPage:
    return BrowserPage(
        title="Browser Title",
        url="https://example.com/rendered",
        html="<html><body>Rendered</body></html>",
        text="브라우저로 렌더링된 충분한 본문입니다.",
        links=[
            "https://example.com/about",
        ],
        images=[
            "https://example.com/image.jpg",
        ],
        meta_description="Browser description",
        canonical_url=(
            "https://example.com/canonical"
        ),
        language="ko",
    )


def test_auto_crawler_uses_web_crawler() -> None:
    web_crawler = MockWebCrawler(
        page=MockWebPage(
            text=(
                "충분히 긴 본문입니다. "
                "일반 HTTP 수집 결과를 사용합니다."
            ),
        ),
    )

    browser_crawler = MockBrowserCrawler(
        create_browser_page(),
    )

    crawler = AutoCrawler(
        web_crawler=web_crawler,
        browser_crawler=browser_crawler,
        minimum_text_length=10,
    )

    result = crawler.fetch(
        "https://example.com",
    )

    assert isinstance(
        result,
        AutoCrawlResult,
    )

    assert result.source == "web"
    assert result.title == "Web Title"

    assert web_crawler.requested_urls == [
        "https://example.com",
    ]

    assert browser_crawler.requested_urls == []


def test_auto_crawler_uses_browser_for_short_text() -> None:
    web_crawler = MockWebCrawler(
        page=MockWebPage(
            text="짧음",
        ),
    )

    browser_crawler = MockBrowserCrawler(
        create_browser_page(),
    )

    crawler = AutoCrawler(
        web_crawler=web_crawler,
        browser_crawler=browser_crawler,
        minimum_text_length=20,
    )

    result = crawler.fetch(
        "https://example.com",
    )

    assert result.source == "browser"
    assert result.title == "Browser Title"

    assert result.links == [
        "https://example.com/about",
    ]

    assert result.images == [
        "https://example.com/image.jpg",
    ]

    assert browser_crawler.requested_urls == [
        "https://example.com",
    ]


def test_auto_crawler_uses_browser_when_web_fails() -> None:
    web_crawler = MockWebCrawler(
        error=RuntimeError(
            "Network error",
        ),
    )

    browser_crawler = MockBrowserCrawler(
        create_browser_page(),
    )

    crawler = AutoCrawler(
        web_crawler=web_crawler,
        browser_crawler=browser_crawler,
    )

    result = crawler.fetch(
        "https://example.com",
    )

    assert result.source == "browser"

    assert browser_crawler.requested_urls == [
        "https://example.com",
    ]


def test_auto_crawler_can_disable_fallback() -> None:
    web_crawler = MockWebCrawler(
        error=RuntimeError(
            "Network error",
        ),
    )

    browser_crawler = MockBrowserCrawler(
        create_browser_page(),
    )

    crawler = AutoCrawler(
        web_crawler=web_crawler,
        browser_crawler=browser_crawler,
        browser_fallback=False,
    )

    with pytest.raises(
        RuntimeError,
        match="Network error",
    ):
        crawler.fetch(
            "https://example.com",
        )

    assert browser_crawler.requested_urls == []


def test_auto_crawler_does_not_fallback_for_short_text_when_disabled() -> None:
    web_crawler = MockWebCrawler(
        page=MockWebPage(
            text="짧음",
        ),
    )

    browser_crawler = MockBrowserCrawler(
        create_browser_page(),
    )

    crawler = AutoCrawler(
        web_crawler=web_crawler,
        browser_crawler=browser_crawler,
        minimum_text_length=100,
        browser_fallback=False,
    )

    result = crawler.fetch(
        "https://example.com",
    )

    assert result.source == "web"
    assert result.text == "짧음"
    assert browser_crawler.requested_urls == []


def test_auto_crawler_rejects_empty_url() -> None:
    crawler = AutoCrawler(
        web_crawler=MockWebCrawler(
            page=MockWebPage(),
        ),
        browser_crawler=MockBrowserCrawler(
            create_browser_page(),
        ),
    )

    with pytest.raises(
        ValueError,
        match="URL",
    ):
        crawler.fetch(
            "   ",
        )


def test_auto_crawler_rejects_negative_minimum_length() -> None:
    with pytest.raises(
        ValueError,
        match="0 이상",
    ):
        AutoCrawler(
            web_crawler=MockWebCrawler(
                page=MockWebPage(),
            ),
            browser_crawler=MockBrowserCrawler(
                create_browser_page(),
            ),
            minimum_text_length=-1,
        )
