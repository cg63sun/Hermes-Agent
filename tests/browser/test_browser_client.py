from hermes_agent.browser.browser_client import (
    BrowserClient,
)


def test_browser_client_starts_browser() -> None:
    client = BrowserClient(
        headless=True,
    )

    try:
        browser = client.start()

        assert browser is not None
        assert client.is_running is True
        assert browser.is_connected() is True
    finally:
        client.close()


def test_browser_client_returns_existing_browser() -> None:
    client = BrowserClient(
        headless=True,
    )

    try:
        first_browser = client.start()
        second_browser = client.start()

        assert first_browser is second_browser
    finally:
        client.close()


def test_browser_client_closes_browser() -> None:
    client = BrowserClient(
        headless=True,
    )

    client.start()
    client.close()

    assert client.is_running is False


def test_browser_client_supports_context_manager() -> None:
    with BrowserClient(
        headless=True,
    ) as client:
        assert client.is_running is True

    assert client.is_running is False


def test_browser_property_raises_before_start() -> None:
    client = BrowserClient(
        headless=True,
    )

    try:
        client.browser
    except RuntimeError as error:
        assert "start()" in str(error)
    else:
        raise AssertionError(
            "RuntimeError가 발생해야 합니다.",
        )
