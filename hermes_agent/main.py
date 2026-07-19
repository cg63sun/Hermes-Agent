from hermes_agent.browser.client import BrowserClient
from hermes_agent.browser.page import PageClient
from hermes_agent.browser.navigator import Navigator
from hermes_agent.browser.extractor import Extractor


def main() -> None:
    browser_client = BrowserClient()

    try:
        browser = browser_client.start()

        page_client = PageClient(browser)
        page = page_client.open()

        navigator = Navigator(page)
        navigator.goto("https://example.com")

        extractor = Extractor(page)

        print("=" * 60)
        print("Title :", extractor.title())
        print("URL   :", navigator.url)
        print("=" * 60)
        print(extractor.text()[:300])

        page_client.close()

    finally:
        browser_client.stop()


if __name__ == "__main__":
    main()
