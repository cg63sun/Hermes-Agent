from hermes_agent.browser.client import BrowserClient
from hermes_agent.browser.extractor import Extractor
from hermes_agent.browser.navigator import Navigator
from hermes_agent.browser.page import PageClient
from hermes_agent.models.page import WebPage


class WebCrawler:
    """Simple web crawler."""

    def fetch(self, url: str) -> WebPage:
        browser_client = BrowserClient()

        try:
            browser = browser_client.start()

            page_client = PageClient(browser)
            page = page_client.open()

            navigator = Navigator(page)
            navigator.goto(url)

            extractor = Extractor(page)

            result = WebPage(
                url=navigator.url,
                title=extractor.title(),
                text=extractor.text(),
                html=extractor.html(),
            )

            page_client.close()

            return result

        finally:
            browser_client.stop()
