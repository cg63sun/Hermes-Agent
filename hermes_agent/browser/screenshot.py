from pathlib import Path

from playwright.sync_api import Page


class Screenshot:
    """Capture screenshots from a page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def save(
        self,
        path: str | Path,
        full_page: bool = True,
    ) -> Path:
        """Save a screenshot and return the saved path."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        self.page.screenshot(
            path=str(output),
            full_page=full_page,
        )

        return output
