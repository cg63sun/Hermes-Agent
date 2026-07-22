from __future__ import annotations

from urllib.parse import urljoin
from xml.etree import ElementTree

import httpx


class SitemapLoader:
    def __init__(
        self,
        timeout: float = 20.0,
    ) -> None:
        self._timeout = timeout

    def load(self, base_url: str) -> list[str]:
        sitemap_url = urljoin(
            base_url.rstrip("/") + "/",
            "sitemap.xml",
        )

        response = httpx.get(
            sitemap_url,
            timeout=self._timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        return self.parse(response.text)

    def parse(self, xml_content: str) -> list[str]:
        if not xml_content.strip():
            return []

        root = ElementTree.fromstring(xml_content)

        urls: list[str] = []

        for element in root.iter():
            if not element.tag.endswith("loc"):
                continue

            if not element.text:
                continue

            url = element.text.strip()

            if url:
                urls.append(url)

        return urls
