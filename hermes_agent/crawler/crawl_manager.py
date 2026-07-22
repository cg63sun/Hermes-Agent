from __future__ import annotations

from collections import deque
from typing import Any
from urllib.parse import (
    urldefrag,
    urljoin,
    urlparse,
    urlunparse,
)

from bs4 import BeautifulSoup

from hermes_agent.crawler.crawler import WebCrawler


class CrawlManager:
    def __init__(self, crawler: WebCrawler) -> None:
        self._crawler = crawler

    def crawl(
        self,
        start_url: str,
        max_pages: int = 50,
        max_depth: int = 2,
    ) -> list[Any]:
        if max_pages <= 0:
            return []

        if max_depth < 0:
            return []

        normalized_start_url = self._normalize_url(start_url)

        if not normalized_start_url:
            return []

        start_host = urlparse(normalized_start_url).netloc.lower()

        queue: deque[tuple[str, int]] = deque(
            [(normalized_start_url, 0)],
        )

        queued_urls = {normalized_start_url}
        visited_urls: set[str] = set()
        pages: list[Any] = []

        while queue and len(pages) < max_pages:
            current_url, depth = queue.popleft()

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            try:
                page = self._crawler.fetch(current_url)
            except Exception:
                continue

            pages.append(page)

            if depth >= max_depth:
                continue

            html = getattr(page, "html", "")

            for link in self._extract_links(
                html=html,
                base_url=current_url,
            ):
                if len(pages) + len(queue) >= max_pages:
                    break

                if not self._is_internal_url(
                    url=link,
                    start_host=start_host,
                ):
                    continue

                if link in visited_urls or link in queued_urls:
                    continue

                queued_urls.add(link)
                queue.append((link, depth + 1))

        return pages

    def _extract_links(
        self,
        html: str,
        base_url: str,
    ) -> list[str]:
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []

        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href", "")).strip()

            if not href:
                continue

            if href.startswith(
                (
                    "#",
                    "mailto:",
                    "tel:",
                    "javascript:",
                    "data:",
                ),
            ):
                continue

            absolute_url = urljoin(base_url, href)
            normalized_url = self._normalize_url(absolute_url)

            if normalized_url:
                links.append(normalized_url)

        return links

    def _normalize_url(self, url: str) -> str:
        url_without_fragment, _ = urldefrag(url.strip())

        parsed = urlparse(url_without_fragment)

        if parsed.scheme.lower() not in {"http", "https"}:
            return ""

        if not parsed.netloc:
            return ""

        path = parsed.path or "/"

        if path != "/":
            path = path.rstrip("/")

        normalized = parsed._replace(
            scheme=parsed.scheme.lower(),
            netloc=parsed.netloc.lower(),
            path=path,
            fragment="",
        )

        return urlunparse(normalized)

    def _is_internal_url(
        self,
        url: str,
        start_host: str,
    ) -> bool:
        return urlparse(url).netloc.lower() == start_host
