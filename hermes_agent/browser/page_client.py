from __future__ import annotations

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
)


class PageClient:
    def __init__(
        self,
        browser: Browser,
        *,
        viewport_width: int = 1440,
        viewport_height: int = 900,
        timeout_ms: float = 30_000,
    ) -> None:
        if viewport_width <= 0:
            raise ValueError(
                "viewport_width는 1 이상이어야 합니다.",
            )

        if viewport_height <= 0:
            raise ValueError(
                "viewport_height는 1 이상이어야 합니다.",
            )

        if timeout_ms <= 0:
            raise ValueError(
                "timeout_ms는 1 이상이어야 합니다.",
            )

        self._browser = browser
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height
        self._timeout_ms = timeout_ms

        self._context: BrowserContext | None = None
        self._page: Page | None = None

    @property
    def context(self) -> BrowserContext:
        if self._context is None:
            raise RuntimeError(
                "브라우저 컨텍스트가 생성되지 않았습니다. "
                "open()을 먼저 실행하세요.",
            )

        return self._context

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError(
                "페이지가 열리지 않았습니다. "
                "open()을 먼저 실행하세요.",
            )

        return self._page

    @property
    def is_open(self) -> bool:
        return (
            self._page is not None
            and not self._page.is_closed()
        )

    def open(self) -> Page:
        if self.is_open:
            return self.page

        if not self._browser.is_connected():
            raise RuntimeError(
                "브라우저가 실행 중이 아닙니다.",
            )

        self._context = (
            self._browser.new_context(
                viewport={
                    "width": self._viewport_width,
                    "height": self._viewport_height,
                },
            )
        )

        try:
            self._page = self._context.new_page()

            self._page.set_default_timeout(
                self._timeout_ms,
            )

            self._page.set_default_navigation_timeout(
                self._timeout_ms,
            )
        except Exception:
            self.close()
            raise

        return self._page

    def close(self) -> None:
        if self._page is not None:
            try:
                if not self._page.is_closed():
                    self._page.close()
            finally:
                self._page = None

        if self._context is not None:
            try:
                self._context.close()
            finally:
                self._context = None

    def __enter__(
        self,
    ) -> PageClient:
        self.open()
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()
