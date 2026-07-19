from playwright.sync_api import Page


class Navigator:
    """Navigate a Playwright page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """Navigate to a URL."""
        self.page.goto(url, wait_until=wait_until)

    @property
    def url(self) -> str:
        """Return the current URL."""
        return self.page.url

    @property
    def title(self) -> str:
        """Return the current page title."""
        return self.page.title()
