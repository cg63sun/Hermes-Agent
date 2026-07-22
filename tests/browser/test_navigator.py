import pytest

from hermes_agent.browser.browser_client import (
    BrowserClient,
)
from hermes_agent.browser.navigator import (
    Navigator,
)
from hermes_agent.browser.page_client import (
    PageClient,
)


def test_navigator_goto() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    page = page_client.open()

    navigator = Navigator(
        page,
    )

    try:
        navigator.goto(
            "https://example.com",
        )

        assert navigator.url.startswith(
            "https://example.com",
        )

        assert navigator.title == (
            "Example Domain"
        )
    finally:
        page_client.close()
        browser_client.close()


def test_navigator_rejects_empty_url() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    page = page_client.open()

    navigator = Navigator(
        page,
    )

    try:
        with pytest.raises(
            ValueError,
            match="URL",
        ):
            navigator.goto(
                "   ",
            )
    finally:
        page_client.close()
        browser_client.close()


def test_navigator_reload() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    page = page_client.open()

    navigator = Navigator(
        page,
    )

    try:
        navigator.goto(
            "https://example.com",
        )

        before_url = navigator.url

        navigator.reload()

        assert navigator.url == before_url
    finally:
        page_client.close()
        browser_client.close()


def test_navigator_back_and_forward() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    page = page_client.open()

    navigator = Navigator(
        page,
    )

    try:
        navigator.goto(
            "https://example.com",
        )

        navigator.goto(
            "https://www.iana.org/help/example-domains",
        )

        navigator.back()

        assert "example.com" in navigator.url

        navigator.forward()

        assert "iana.org" in navigator.url
    finally:
        page_client.close()
        browser_client.close()


def test_navigator_rejects_invalid_timeout() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    page = page_client.open()

    try:
        with pytest.raises(
            ValueError,
            match="timeout_ms",
        ):
            Navigator(
                page,
                timeout_ms=0,
            )
    finally:
        page_client.close()
        browser_client.close()
