from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrawlReport:
    pages: list[Any] = field(default_factory=list)
    visited_urls: list[str] = field(default_factory=list)
    failed_urls: list[str] = field(default_factory=list)
    blocked_urls: list[str] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def visited_count(self) -> int:
        return len(self.visited_urls)

    @property
    def failed_count(self) -> int:
        return len(self.failed_urls)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_urls)

    @property
    def page_urls(self) -> list[str]:
        urls: list[str] = []

        for page in self.pages:
            url = getattr(page, "url", "")

            if url:
                urls.append(str(url))

        return urls
