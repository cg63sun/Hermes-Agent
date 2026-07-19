from playwright.sync_api import Page


class Extractor:
    """Extract information from a page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def html(self) -> str:
        """Return page HTML."""
        return self.page.content()

    def text(self) -> str:
        """Return visible page text."""
        return self.page.locator("body").inner_text()

    def title(self) -> str:
        """Return page title."""
        return self.page.title()
