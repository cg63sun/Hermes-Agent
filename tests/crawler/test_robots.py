from typing import Any

import httpx

from hermes_agent.crawler.robots import RobotsChecker


def test_robots_checker_allows_before_load() -> None:
    checker = RobotsChecker()

    assert checker.can_fetch(
        "https://example.com/private",
    ) is True


def test_robots_checker_respects_rules(
    monkeypatch: Any,
) -> None:
    class MockResponse:
        text = """
        User-agent: *
        Disallow: /private
        Allow: /public
        """

        def raise_for_status(self) -> None:
            pass

    def mock_get(
        url: str,
        timeout: float,
        follow_redirects: bool,
    ) -> MockResponse:
        assert url == "https://example.com/robots.txt"
        assert timeout == 10.0
        assert follow_redirects is True

        return MockResponse()

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    checker = RobotsChecker(
        user_agent="HermesAgent",
    )

    checker.load(
        "https://example.com",
    )

    assert checker.can_fetch(
        "https://example.com/public",
    ) is True

    assert checker.can_fetch(
        "https://example.com/private",
    ) is False


def test_robots_checker_uses_custom_user_agent(
    monkeypatch: Any,
) -> None:
    class MockResponse:
        text = """
        User-agent: HermesAgent
        Disallow: /admin

        User-agent: *
        Allow: /
        """

        def raise_for_status(self) -> None:
            pass

    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    checker = RobotsChecker(
        user_agent="HermesAgent",
    )

    checker.load(
        "https://example.com",
    )

    assert checker.can_fetch(
        "https://example.com/admin",
    ) is False

    assert checker.can_fetch(
        "https://example.com/about",
    ) is True
