from typing import Any

import httpx

from hermes_agent.crawler.sitemap import SitemapLoader


class MockResponse:
    def __init__(
        self,
        text: str,
        status_code: int = 200,
    ) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "사이트맵 요청 실패",
                request=httpx.Request(
                    "GET",
                    "https://example.com",
                ),
                response=httpx.Response(
                    self.status_code,
                ),
            )


def test_sitemap_loader_uses_default_sitemap(
    monkeypatch: Any,
) -> None:
    requested_urls: list[str] = []

    sitemap_xml = """
    <urlset>
        <url>
            <loc>https://example.com/about</loc>
        </url>
    </urlset>
    """

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        requested_urls.append(url)

        return MockResponse(
            sitemap_xml,
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader()

    urls = loader.load(
        "https://example.com",
    )

    assert urls == [
        "https://example.com/about",
    ]

    assert requested_urls == [
        "https://example.com/sitemap.xml",
    ]


def test_sitemap_loader_falls_back_to_wordpress_sitemap(
    monkeypatch: Any,
) -> None:
    requested_urls: list[str] = []

    wordpress_sitemap_xml = """
    <urlset>
        <url>
            <loc>https://example.com/</loc>
        </url>
        <url>
            <loc>https://example.com/service</loc>
        </url>
    </urlset>
    """

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        requested_urls.append(url)

        if url.endswith("/sitemap.xml"):
            return MockResponse(
                "",
                status_code=404,
            )

        return MockResponse(
            wordpress_sitemap_xml,
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader()

    urls = loader.load(
        "https://example.com",
    )

    assert urls == [
        "https://example.com/",
        "https://example.com/service",
    ]

    assert requested_urls == [
        "https://example.com/sitemap.xml",
        "https://example.com/wp-sitemap.xml",
    ]


def test_sitemap_loader_returns_empty_when_all_fail(
    monkeypatch: Any,
) -> None:
    requested_urls: list[str] = []

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        requested_urls.append(url)

        return MockResponse(
            "",
            status_code=404,
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader()

    urls = loader.load(
        "https://example.com",
    )

    assert urls == []

    assert requested_urls == [
        "https://example.com/sitemap.xml",
        "https://example.com/wp-sitemap.xml",
    ]


def test_sitemap_loader_falls_back_when_default_is_empty(
    monkeypatch: Any,
) -> None:
    requested_urls: list[str] = []

    wordpress_sitemap_xml = """
    <urlset>
        <url>
            <loc>https://example.com/contact</loc>
        </url>
    </urlset>
    """

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        requested_urls.append(url)

        if url.endswith("/sitemap.xml"):
            return MockResponse(
                "<urlset></urlset>",
            )

        return MockResponse(
            wordpress_sitemap_xml,
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader()

    urls = loader.load(
        "https://example.com",
    )

    assert urls == [
        "https://example.com/contact",
    ]

    assert requested_urls == [
        "https://example.com/sitemap.xml",
        "https://example.com/wp-sitemap.xml",
    ]
