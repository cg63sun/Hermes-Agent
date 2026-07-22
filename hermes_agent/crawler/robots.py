from __future__ import annotations

from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import httpx


class RobotsChecker:
    def __init__(
        self,
        user_agent: str = "HermesAgent",
        timeout: float = 10.0,
    ) -> None:
        self._user_agent = user_agent
        self._timeout = timeout
        self._parser = RobotFileParser()
        self._loaded_base_url: str | None = None

    def load(self, base_url: str) -> None:
        robots_url = urljoin(
            base_url.rstrip("/") + "/",
            "robots.txt",
        )

        response = httpx.get(
            robots_url,
            timeout=self._timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        self._parser.set_url(robots_url)
        self._parser.parse(response.text.splitlines())
        self._loaded_base_url = base_url

    def can_fetch(self, url: str) -> bool:
        if self._loaded_base_url is None:
            return True

        return self._parser.can_fetch(
            self._user_agent,
            url,
        )
