import pytest

from hermes_agent.browser.browser_client import (
    BrowserClient,
)
from hermes_agent.browser.page_client import (
    PageClient,
)


def test_page_client_opens_page() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    try:
        page = page_client.open()

        assert page is not None
        assert page_client.is_open is True
        assert page.is_closed() is False
    finally:
        page_client.close()
        browser_client.close()


def test_page_client_returns_existing_page() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    try:
        first_page = page_client.open()
        second_page = page_client.open()

        assert first_page is second_page
    finally:
        page_client.close()
        browser_client.close()


def test_page_client_closes_page() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    page = page_client.open()
    page_client.close()

    assert page.is_closed() is True
    assert page_client.is_open is False

    browser_client.close()


def test_page_client_sets_viewport() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
        viewport_width=1280,
        viewport_height=720,
    )

    try:
        page = page_client.open()

        assert page.viewport_size == {
            "width": 1280,
            "height": 720,
        }
    finally:
        page_client.close()
        browser_client.close()


def test_page_client_supports_context_manager() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    try:
        with PageClient(browser) as page_client:
            assert page_client.is_open is True

        assert page_client.is_open is False
    finally:
        browser_client.close()


def test_page_property_raises_before_open() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    page_client = PageClient(
        browser,
    )

    try:
        with pytest.raises(
            RuntimeError,
            match=r"open\(\)",
        ):
            _ = page_client.page
    finally:
        browser_client.close()


def test_page_client_rejects_invalid_viewport_width() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    try:
        with pytest.raises(
            ValueError,
            match="viewport_width",
        ):
            PageClient(
                browser,
                viewport_width=0,
            )
    finally:
        browser_client.close()


def test_page_client_rejects_invalid_viewport_height() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    try:
        with pytest.raises(
            ValueError,
            match="viewport_height",
        ):
            PageClient(
                browser,
                viewport_height=0,
            )
    finally:
        browser_client.close()


def test_page_client_rejects_invalid_timeout() -> None:
    browser_client = BrowserClient(
        headless=True,
    )

    browser = browser_client.start()

    try:
        with pytest.raises(
            ValueError,
            match="timeout_ms",
        ):
            PageClient(
                browser,
                timeout_ms=0,
            )
    finally:
        browser_client.close()
