from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from hermes_agent.browser.browser_crawler import (
    BrowserCrawler,
    BrowserPage,
)
from hermes_agent.crawler.crawler import (
    WebCrawler,
)


class WebPageLike(Protocol):
    title: str
    url: str
    html: str
    text: str


@dataclass(slots=True)
class AutoCrawlResult:
    title: str
    url: str
    html: str
    text: str
    source: str
    links: list[str]
    images: list[str]
    meta_description: str
    canonical_url: str
    language: str


class AutoCrawler:
    def __init__(
        self,
        *,
        web_crawler: WebCrawler | None = None,
        browser_crawler: BrowserCrawler | None = None,
        minimum_text_length: int = 100,
        browser_fallback: bool = True,
    ) -> None:
        if minimum_text_length < 0:
            raise ValueError(
                "minimum_text_length는 0 이상이어야 합니다.",
            )

        self._web_crawler = (
            web_crawler
            if web_crawler is not None
            else WebCrawler()
        )

        self._browser_crawler = (
            browser_crawler
            if browser_crawler is not None
            else BrowserCrawler()
        )

        self._minimum_text_length = (
            minimum_text_length
        )

        self._browser_fallback = (
            browser_fallback
        )

    def fetch(
        self,
        url: str,
    ) -> AutoCrawlResult:
        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError(
                "가져올 URL을 입력하세요.",
            )

        try:
            web_page = self._web_crawler.fetch(
                normalized_url,
            )
        except Exception:
            if not self._browser_fallback:
                raise

            return self._fetch_with_browser(
                normalized_url,
            )

        if self._should_use_browser(
            web_page,
        ):
            return self._fetch_with_browser(
                normalized_url,
            )

        return self._from_web_page(
            web_page,
        )

    def _should_use_browser(
        self,
        page: WebPageLike,
    ) -> bool:
        if not self._browser_fallback:
            return False

        text = getattr(
            page,
            "text",
            "",
        )

        if not isinstance(
            text,
            str,
        ):
            return True

        return len(
            text.strip(),
        ) < self._minimum_text_length

    def _fetch_with_browser(
        self,
        url: str,
    ) -> AutoCrawlResult:
        page = self._browser_crawler.fetch(
            url,
        )

        return self._from_browser_page(
            page,
        )

    def _from_web_page(
        self,
        page: WebPageLike,
    ) -> AutoCrawlResult:
        return AutoCrawlResult(
            title=self._string_value(
                getattr(
                    page,
                    "title",
                    "",
                ),
            ),
            url=self._string_value(
                getattr(
                    page,
                    "url",
                    "",
                ),
            ),
            html=self._string_value(
                getattr(
                    page,
                    "html",
                    "",
                ),
            ),
            text=self._string_value(
                getattr(
                    page,
                    "text",
                    "",
                ),
            ),
            source="web",
            links=[],
            images=[],
            meta_description="",
            canonical_url="",
            language="",
        )

    def _from_browser_page(
        self,
        page: BrowserPage,
    ) -> AutoCrawlResult:
        return AutoCrawlResult(
            title=page.title,
            url=page.url,
            html=page.html,
            text=page.text,
            source="browser",
            links=list(
                page.links,
            ),
            images=list(
                page.images,
            ),
            meta_description=(
                page.meta_description
            ),
            canonical_url=(
                page.canonical_url
            ),
            language=page.language,
        )

    def _string_value(
        self,
        value: object,
    ) -> str:
        if isinstance(
            value,
            str,
        ):
            return value

        if value is None:
            return ""

        return str(
            value,
        )
