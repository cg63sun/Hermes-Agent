from playwright.sync_api import Browser, Playwright, sync_playwright


class BrowserClient:
    """Simple Playwright browser client."""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    def start(self, headless: bool = True) -> Browser:
        """Start the browser."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        return self._browser

    def stop(self) -> None:
        """Stop the browser."""
        if self._browser:
            self._browser.close()
            self._browser = None

        if self._playwright:
            self._playwright.stop()
            self._playwright = None
