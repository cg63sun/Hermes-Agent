from typing import Any

import httpx

from hermes_agent.crawler.sitemap import SitemapLoader


def test_sitemap_loader_parses_urls() -> None:
    loader = SitemapLoader()

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/</loc>
        </url>
        <url>
            <loc>https://example.com/about</loc>
        </url>
        <url>
            <loc>https://example.com/service</loc>
        </url>
    </urlset>
    """

    urls = loader.parse(xml_content)

    assert urls == [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/service",
    ]


def test_sitemap_loader_handles_empty_xml() -> None:
    loader = SitemapLoader()

    urls = loader.parse("")

    assert urls == []


def test_sitemap_loader_loads_sitemap(
    monkeypatch: Any,
) -> None:
    requested_data: dict[str, Any] = {}

    class MockResponse:
        text = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/about</loc>
            </url>
        </urlset>
        """

        def raise_for_status(self) -> None:
            pass

    def mock_get(
        url: str,
        timeout: float,
        follow_redirects: bool,
    ) -> MockResponse:
        requested_data["url"] = url
        requested_data["timeout"] = timeout
        requested_data["follow_redirects"] = follow_redirects

        return MockResponse()

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader(
        timeout=15.0,
    )

    urls = loader.load(
        "https://example.com",
    )

    assert urls == [
        "https://example.com/about",
    ]

    assert requested_data["url"] == (
        "https://example.com/sitemap.xml"
    )
    assert requested_data["timeout"] == 15.0
    assert requested_data["follow_redirects"] is True
