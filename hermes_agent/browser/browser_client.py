from __future__ import annotations

from playwright.sync_api import (
    Browser,
    Playwright,
    sync_playwright,
)


class BrowserClient:
    def __init__(
        self,
        *,
        headless: bool = True,
        slow_mo: float = 0,
    ) -> None:
        self._headless = headless
        self._slow_mo = slow_mo

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    @property
    def browser(self) -> Browser:
        if self._browser is None:
            raise RuntimeError(
                "브라우저가 시작되지 않았습니다. "
                "start()를 먼저 실행하세요.",
            )

        return self._browser

    @property
    def is_running(self) -> bool:
        return (
            self._browser is not None
            and self._browser.is_connected()
        )

    def start(self) -> Browser:
        if self.is_running:
            return self.browser

        self._playwright = (
            sync_playwright().start()
        )

        try:
            self._browser = (
                self._playwright.chromium.launch(
                    headless=self._headless,
                    slow_mo=self._slow_mo,
                )
            )
        except Exception:
            self._stop_playwright()
            raise

        return self._browser

    def close(self) -> None:
        if self._browser is not None:
            try:
                self._browser.close()
            finally:
                self._browser = None

        self._stop_playwright()

    def __enter__(
        self,
    ) -> BrowserClient:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()

    def _stop_playwright(self) -> None:
        if self._playwright is not None:
            try:
                self._playwright.stop()
            finally:
                self._playwright = None
