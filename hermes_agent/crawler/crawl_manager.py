from __future__ import annotations

from collections import deque
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from hermes_agent.crawler.crawl_report import CrawlReport
from hermes_agent.crawler.crawler import WebCrawler
from hermes_agent.crawler.robots import RobotsChecker
from hermes_agent.crawler.sitemap import SitemapLoader
from hermes_agent.crawler.url_filter import URLFilter
from hermes_agent.crawler.url_normalizer import URLNormalizer


class CrawlManager:
    def __init__(
        self,
        crawler: WebCrawler,
        robots_checker: RobotsChecker | None = None,
        sitemap_loader: SitemapLoader | None = None,
        url_filter: URLFilter | None = None,
        url_normalizer: URLNormalizer | None = None,
    ) -> None:
        self._crawler = crawler
        self._robots_checker = robots_checker
        self._sitemap_loader = sitemap_loader
        self._url_filter = url_filter

        self._url_normalizer = (
            url_normalizer
            if url_normalizer is not None
            else URLNormalizer()
        )

        self._root_url = ""
        self._root_host = ""

    def crawl(
        self,
        start_url: str,
        max_pages: int = 50,
        max_depth: int = 2,
    ) -> list:
        report = self.crawl_with_report(
            start_url=start_url,
            max_pages=max_pages,
            max_depth=max_depth,
        )

        return report.pages

    def crawl_with_report(
        self,
        start_url: str,
        max_pages: int = 50,
        max_depth: int = 2,
    ) -> CrawlReport:
        if max_pages <= 0:
            return CrawlReport(
                pages=[],
                visited_urls=[],
                failed_urls=[],
                blocked_urls=[],
            )

        if max_depth < 0:
            raise ValueError(
                "max_depth는 0 이상이어야 합니다.",
            )

        normalized_start_url = self._normalize_start_url(
            start_url,
        )

        if not normalized_start_url:
            return CrawlReport(
                pages=[],
                visited_urls=[],
                failed_urls=[],
                blocked_urls=[],
            )

        self._root_url = normalized_start_url
        self._root_host = self._hostname(
            normalized_start_url,
        )

        pages: list = []
        visited_urls: list[str] = []
        failed_urls: list[str] = []
        blocked_urls: list[str] = []

        visited: set[str] = set()
        queued: set[str] = set()

        queue: deque[tuple[str, int]] = deque()

        robots_loaded = self._load_robots(
            normalized_start_url,
        )

        self._enqueue_url(
            queue=queue,
            queued=queued,
            url=normalized_start_url,
            depth=0,
        )

        self._add_sitemap_urls(
            queue=queue,
            queued=queued,
            visited=visited,
            blocked_urls=blocked_urls,
            start_url=normalized_start_url,
            robots_loaded=robots_loaded,
        )

        while queue and len(pages) < max_pages:
            current_url, current_depth = queue.popleft()

            queued.discard(
                current_url,
            )

            normalized_url = self._normalize_start_url(
                current_url,
            )

            if not normalized_url:
                continue

            if normalized_url in visited:
                continue

            visited.add(
                normalized_url,
            )

            visited_urls.append(
                normalized_url,
            )

            if not self._is_internal_url(
                normalized_url,
            ):
                blocked_urls.append(
                    normalized_url,
                )
                continue

            if not self._is_url_allowed(
                normalized_url,
            ):
                blocked_urls.append(
                    normalized_url,
                )
                continue

            if not self._can_fetch(
                normalized_url,
                robots_loaded=robots_loaded,
            ):
                blocked_urls.append(
                    normalized_url,
                )
                continue

            try:
                page = self._crawler.fetch(
                    normalized_url,
                )
            except Exception:
                failed_urls.append(
                    normalized_url,
                )
                continue

            pages.append(
                page,
            )

            if current_depth >= max_depth:
                continue

            page_html = getattr(
                page,
                "html",
                "",
            )

            page_url = getattr(
                page,
                "url",
                normalized_url,
            )

            links = self._extract_links(
                html=page_html,
                current_url=page_url,
            )

            for link in links:
                if link in visited:
                    continue

                if link in queued:
                    continue

                self._enqueue_url(
                    queue=queue,
                    queued=queued,
                    url=link,
                    depth=current_depth + 1,
                )

        return CrawlReport(
            pages=pages,
            visited_urls=self._remove_duplicates(
                visited_urls,
            ),
            failed_urls=self._remove_duplicates(
                failed_urls,
            ),
            blocked_urls=self._remove_duplicates(
                blocked_urls,
            ),
        )

    def _load_robots(
        self,
        start_url: str,
    ) -> bool:
        if self._robots_checker is None:
            return False

        base_url = self._base_url(
            start_url,
        )

        try:
            self._robots_checker.load(
                base_url,
            )
        except Exception:
            return False

        return True

    def _add_sitemap_urls(
        self,
        *,
        queue: deque[tuple[str, int]],
        queued: set[str],
        visited: set[str],
        blocked_urls: list[str],
        start_url: str,
        robots_loaded: bool,
    ) -> None:
        if self._sitemap_loader is None:
            return

        try:
            sitemap_urls = self._sitemap_loader.load(
                self._base_url(
                    start_url,
                ),
            )
        except Exception:
            return

        for sitemap_url in sitemap_urls:
            normalized_url = self._normalize_start_url(
                sitemap_url,
            )

            if not normalized_url:
                continue

            if normalized_url in visited:
                continue

            if normalized_url in queued:
                continue

            if not self._is_internal_url(
                normalized_url,
            ):
                blocked_urls.append(
                    normalized_url,
                )
                continue

            if not self._is_url_allowed(
                normalized_url,
            ):
                blocked_urls.append(
                    normalized_url,
                )
                continue

            if not self._can_fetch(
                normalized_url,
                robots_loaded=robots_loaded,
            ):
                blocked_urls.append(
                    normalized_url,
                )
                continue

            self._enqueue_url(
                queue=queue,
                queued=queued,
                url=normalized_url,
                depth=0,
            )

    def _enqueue_url(
        self,
        *,
        queue: deque[tuple[str, int]],
        queued: set[str],
        url: str,
        depth: int,
    ) -> None:
        normalized_url = self._normalize_start_url(
            url,
        )

        if not normalized_url:
            return

        if normalized_url in queued:
            return

        queue.append(
            (
                normalized_url,
                depth,
            ),
        )

        queued.add(
            normalized_url,
        )

    def _can_fetch(
        self,
        url: str,
        *,
        robots_loaded: bool = True,
    ) -> bool:
        if self._robots_checker is None:
            return True

        if not robots_loaded:
            return True

        try:
            return self._robots_checker.can_fetch(
                url,
            )
        except Exception:
            return True

    def _is_url_allowed(
        self,
        url: str,
    ) -> bool:
        if self._url_filter is None:
            return True

        try:
            return self._url_filter.is_allowed(
                url,
            )
        except AttributeError:
            try:
                return self._url_filter.allow(
                    url,
                )
            except AttributeError:
                return True
        except Exception:
            return False

    def _extract_links(
        self,
        html: str,
        current_url: str,
    ) -> list[str]:
        if not html:
            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        links: list[str] = []

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = anchor.get(
                "href",
            )

            if not isinstance(
                href,
                str,
            ):
                continue

            href = href.strip()

            if not href:
                continue

            if self._is_unsupported_link(
                href,
            ):
                continue

            normalized_url = self._normalize_url(
                href,
                base_url=current_url,
            )

            if not normalized_url:
                continue

            if not self._is_internal_url(
                normalized_url,
            ):
                continue

            # 여기에서는 URLFilter 검사를 하지 않습니다.
            # 큐에 넣은 뒤 crawl_with_report()에서 검사해야
            # blocked_urls 보고서에 기록할 수 있습니다.

            links.append(
                normalized_url,
            )

        return self._remove_duplicates(
            links,
        )

    def _normalize_start_url(
        self,
        url: str,
    ) -> str:
        stripped_url = url.strip()

        if not stripped_url:
            return ""

        parsed = urlsplit(
            stripped_url,
        )

        # http 또는 https 절대 URL인 경우에만 정규화합니다.
        if (
            parsed.scheme.lower() in {"http", "https"}
            and parsed.netloc
        ):
            return self._url_normalizer.normalize(
                stripped_url,
            )

        # 기존 테스트 호환을 위해 상대형 시작 URL은
        # 원래 문자열 그대로 유지합니다.
        return stripped_url

    def _normalize_url(
        self,
        url: str,
        base_url: str | None = None,
    ) -> str:
        return self._url_normalizer.normalize(
            url,
            base_url=base_url,
        )

    def _is_internal_url(
        self,
        url: str,
    ) -> bool:
        if not self._root_host:
            return True

        url_host = self._hostname(
            url,
        )

        if not url_host:
            return True

        return url_host == self._root_host

    def _hostname(
        self,
        url: str,
    ) -> str:
        parsed = urlsplit(
            url,
        )

        return (
            parsed.hostname or ""
        ).lower()

    def _base_url(
        self,
        url: str,
    ) -> str:
        parsed = urlsplit(
            url,
        )

        if not parsed.scheme or not parsed.netloc:
            return url.rstrip("/")

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
        )

    def _is_unsupported_link(
        self,
        href: str,
    ) -> bool:
        lowered_href = href.lower()

        unsupported_prefixes = (
            "mailto:",
            "tel:",
            "javascript:",
            "data:",
        )

        return lowered_href.startswith(
            unsupported_prefixes,
        )

    def _remove_duplicates(
        self,
        values: list[str],
    ) -> list[str]:
        return list(
            dict.fromkeys(values),
        )