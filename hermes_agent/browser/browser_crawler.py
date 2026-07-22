from __future__ import annotations

from dataclasses import dataclass

from hermes_agent.browser.browser_client import (
    BrowserClient,
)
from hermes_agent.browser.extractor import Extractor
from hermes_agent.browser.navigator import Navigator
from hermes_agent.browser.page_client import PageClient


@dataclass(slots=True)
class BrowserPage:
    title: str
    url: str
    html: str
    text: str
    links: list[str]
    images: list[str]
    meta_description: str
    canonical_url: str
    language: str


class BrowserCrawler:
    def __init__(
        self,
        *,
        headless: bool = True,
        timeout_ms: float = 30_000,
        wait_until: str = "domcontentloaded",
        viewport_width: int = 1440,
        viewport_height: int = 900,
    ) -> None:
        self._headless = headless
        self._timeout_ms = timeout_ms
        self._wait_until = wait_until
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height

    def fetch(
        self,
        url: str,
    ) -> BrowserPage:
        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError(
                "가져올 URL을 입력하세요.",
            )

        browser_client = BrowserClient(
            headless=self._headless,
        )

        page_client: PageClient | None = None

        try:
            browser = browser_client.start()

            page_client = PageClient(
                browser,
                viewport_width=self._viewport_width,
                viewport_height=self._viewport_height,
                timeout_ms=self._timeout_ms,
            )

            page = page_client.open()

            navigator = Navigator(
                page,
                wait_until=self._wait_until,
                timeout_ms=self._timeout_ms,
            )

            navigator.goto(
                normalized_url,
            )

            extractor = Extractor(
                page,
            )

            return BrowserPage(
                title=extractor.title(),
                url=navigator.url,
                html=extractor.html(),
                text=extractor.text(),
                links=extractor.links(),
                images=extractor.images(),
                meta_description=(
                    extractor.meta_description()
                ),
                canonical_url=(
                    extractor.canonical_url()
                ),
                language=extractor.language(),
            )

        finally:
            if page_client is not None:
                page_client.close()

            browser_client.close()
