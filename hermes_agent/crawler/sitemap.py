from __future__ import annotations

from urllib.parse import urljoin
from xml.etree import ElementTree

import httpx


class SitemapLoader:
    DEFAULT_SITEMAP_PATHS = (
        "sitemap.xml",
        "wp-sitemap.xml",
    )

    def __init__(
        self,
        timeout: float = 20.0,
        max_sitemaps: int = 20,
    ) -> None:
        self._timeout = timeout
        self._max_sitemaps = max_sitemaps

    def load(
        self,
        base_url: str,
    ) -> list[str]:
        base_url_with_slash = (
            base_url.rstrip("/") + "/"
        )

        for sitemap_path in self.DEFAULT_SITEMAP_PATHS:
            sitemap_url = urljoin(
                base_url_with_slash,
                sitemap_path,
            )

            try:
                urls = self.load_url(sitemap_url)
            except Exception:
                continue

            if urls:
                return urls

        return []

    def load_url(
        self,
        sitemap_url: str,
    ) -> list[str]:
        visited_sitemaps: set[str] = set()

        return self._load_recursive(
            sitemap_url=sitemap_url,
            visited_sitemaps=visited_sitemaps,
        )

    def parse(
        self,
        xml_content: str,
    ) -> list[str]:
        _, urls = self.parse_document(
            xml_content,
        )

        return urls

    def parse_document(
        self,
        xml_content: str,
    ) -> tuple[str, list[str]]:
        if not xml_content.strip():
            return "empty", []

        root = ElementTree.fromstring(
            xml_content,
        )

        root_name = self._local_name(
            root.tag,
        )

        urls: list[str] = []

        for element in root.iter():
            if self._local_name(
                element.tag,
            ) != "loc":
                continue

            if not element.text:
                continue

            url = element.text.strip()

            if url:
                urls.append(url)

        if root_name == "sitemapindex":
            return "index", urls

        if root_name == "urlset":
            return "urlset", urls

        return "unknown", urls

    def _load_recursive(
        self,
        sitemap_url: str,
        visited_sitemaps: set[str],
    ) -> list[str]:
        if sitemap_url in visited_sitemaps:
            return []

        if len(visited_sitemaps) >= self._max_sitemaps:
            return []

        visited_sitemaps.add(
            sitemap_url,
        )

        response = httpx.get(
            sitemap_url,
            timeout=self._timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        sitemap_type, urls = self.parse_document(
            response.text,
        )

        if sitemap_type != "index":
            return self._remove_duplicates(urls)

        page_urls: list[str] = []

        for child_sitemap_url in urls:
            if len(visited_sitemaps) >= self._max_sitemaps:
                break

            try:
                child_urls = self._load_recursive(
                    sitemap_url=child_sitemap_url,
                    visited_sitemaps=visited_sitemaps,
                )
            except Exception:
                continue

            page_urls.extend(
                child_urls,
            )

        return self._remove_duplicates(
            page_urls,
        )

    def _local_name(
        self,
        tag: str,
    ) -> str:
        if "}" in tag:
            return tag.rsplit(
                "}",
                1,
            )[1]

        return tag

    def _remove_duplicates(
        self,
        urls: list[str],
    ) -> list[str]:
        return list(
            dict.fromkeys(urls),
        )
