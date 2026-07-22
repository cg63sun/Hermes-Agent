from __future__ import annotations

from playwright.sync_api import (
    Page,
    Response,
)


class Navigator:
    def __init__(
        self,
        page: Page,
        *,
        wait_until: str = "domcontentloaded",
        timeout_ms: float = 30_000,
    ) -> None:
        if timeout_ms <= 0:
            raise ValueError(
                "timeout_ms는 1 이상이어야 합니다.",
            )

        self._page = page
        self._wait_until = wait_until
        self._timeout_ms = timeout_ms

    @property
    def url(self) -> str:
        return self._page.url

    @property
    def title(self) -> str:
        return self._page.title()

    def goto(
        self,
        url: str,
    ) -> Response | None:
        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError(
                "이동할 URL을 입력하세요.",
            )

        return self._page.goto(
            normalized_url,
            wait_until=self._wait_until,
            timeout=self._timeout_ms,
        )

    def back(self) -> Response | None:
        return self._page.go_back(
            wait_until=self._wait_until,
            timeout=self._timeout_ms,
        )

    def forward(self) -> Response | None:
        return self._page.go_forward(
            wait_until=self._wait_until,
            timeout=self._timeout_ms,
        )

    def reload(self) -> Response | None:
        return self._page.reload(
            wait_until=self._wait_until,
            timeout=self._timeout_ms,
        )
