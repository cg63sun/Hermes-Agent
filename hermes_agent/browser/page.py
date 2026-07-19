from playwright.sync_api import Browser, Page


class PageClient:
    """Manage Playwright pages."""

    def __init__(self, browser: Browser) -> None:
        self.browser = browser
        self.page: Page | None = None

    def open(self) -> Page:
        """Create a new page."""
        self.page = self.browser.new_page()
        return self.page

    def close(self) -> None:
        """Close the current page."""
        if self.page is not None:
            self.page.close()
            self.page = None
