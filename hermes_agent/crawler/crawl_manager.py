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
from hermes_agent.crawler.robots import RobotsChecker
from hermes_agent.crawler.sitemap import SitemapLoader


class CrawlManager:
    def __init__(
        self,
        crawler: WebCrawler,
        robots_checker: RobotsChecker | None = None,
        sitemap_loader: SitemapLoader | None = None,
    ) -> None:
        self._crawler = crawler
        self._robots_checker = robots_checker
        self._sitemap_loader = sitemap_loader

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

        base_url = self._base_url(normalized_start_url)
        start_host = urlparse(normalized_start_url).netloc.lower()

        self._load_robots(base_url)

        queue: deque[tuple[str, int]] = deque(
            [(normalized_start_url, 0)],
        )

        queued_urls = {normalized_start_url}
        visited_urls: set[str] = set()
        pages: list[Any] = []

        self._add_sitemap_urls(
            queue=queue,
            queued_urls=queued_urls,
            base_url=base_url,
            start_host=start_host,
            max_pages=max_pages,
        )

        while queue and len(pages) < max_pages:
            current_url, depth = queue.popleft()

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            if not self._can_fetch(current_url):
                continue

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

                if not self._can_fetch(link):
                    continue

                queued_urls.add(link)
                queue.append((link, depth + 1))

        return pages

    def _load_robots(self, base_url: str) -> None:
        if self._robots_checker is None:
            return

        try:
            self._robots_checker.load(base_url)
        except Exception:
            pass

    def _add_sitemap_urls(
        self,
        queue: deque[tuple[str, int]],
        queued_urls: set[str],
        base_url: str,
        start_host: str,
        max_pages: int,
    ) -> None:
        if self._sitemap_loader is None:
            return

        try:
            sitemap_urls = self._sitemap_loader.load(base_url)
        except Exception:
            return

        for sitemap_url in sitemap_urls:
            if len(queue) >= max_pages:
                break

            normalized_url = self._normalize_url(sitemap_url)

            if not normalized_url:
                continue

            if not self._is_internal_url(
                url=normalized_url,
                start_host=start_host,
            ):
                continue

            if normalized_url in queued_urls:
                continue

            if not self._can_fetch(normalized_url):
                continue

            queued_urls.add(normalized_url)

            # sitemap에 있는 URL은 시작 페이지와 같은 우선순위로 처리합니다.
            queue.append((normalized_url, 0))

    def _can_fetch(self, url: str) -> bool:
        if self._robots_checker is None:
            return True

        try:
            return self._robots_checker.can_fetch(url)
        except Exception:
            return True

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

    def _base_url(self, url: str) -> str:
        parsed = urlparse(url)

        return f"{parsed.scheme}://{parsed.netloc}"
