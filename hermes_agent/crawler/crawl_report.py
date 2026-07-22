from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": {
                "page_count": self.page_count,
                "visited_count": self.visited_count,
                "failed_count": self.failed_count,
                "blocked_count": self.blocked_count,
            },
            "pages": [
                self._page_to_dict(page)
                for page in self.pages
            ],
            "visited_urls": list(self.visited_urls),
            "failed_urls": list(self.failed_urls),
            "blocked_urls": list(self.blocked_urls),
        }

    def to_json(
        self,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
        )

    def save_json(
        self,
        file_path: str | Path,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Path:
        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_json(
                indent=indent,
                ensure_ascii=ensure_ascii,
            ),
            encoding="utf-8",
        )

        return path

    def _page_to_dict(
        self,
        page: Any,
    ) -> dict[str, Any]:
        return {
            "url": str(
                getattr(page, "url", ""),
            ),
            "title": str(
                getattr(page, "title", ""),
            ),
            "text": str(
                getattr(page, "text", ""),
            ),
        }
