import gzip
from typing import Any

import httpx

from hermes_agent.crawler.sitemap import SitemapLoader


class MockResponse:
    def __init__(
        self,
        *,
        text: str = "",
        content: bytes = b"",
        status_code: int = 200,
    ) -> None:
        self.text = text

        if content:
            self.content = content
        else:
            self.content = text.encode("utf-8")

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


def test_load_url_reads_gzip_sitemap(
    monkeypatch: Any,
) -> None:
    xml_content = """
    <urlset>
        <url>
            <loc>https://example.com/about</loc>
        </url>
        <url>
            <loc>https://example.com/contact</loc>
        </url>
    </urlset>
    """

    compressed_content = gzip.compress(
        xml_content.encode("utf-8"),
    )

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        assert url == (
            "https://example.com/sitemap.xml.gz"
        )

        return MockResponse(
            content=compressed_content,
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader()

    urls = loader.load_url(
        "https://example.com/sitemap.xml.gz",
    )

    assert urls == [
        "https://example.com/about",
        "https://example.com/contact",
    ]


def test_load_falls_back_to_gzip_sitemap(
    monkeypatch: Any,
) -> None:
    requested_urls: list[str] = []

    xml_content = """
    <urlset>
        <url>
            <loc>https://example.com/service</loc>
        </url>
    </urlset>
    """

    compressed_content = gzip.compress(
        xml_content.encode("utf-8"),
    )

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        requested_urls.append(url)

        if url.endswith("sitemap.xml.gz"):
            return MockResponse(
                content=compressed_content,
            )

        return MockResponse(
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

    assert urls == [
        "https://example.com/service",
    ]

    assert requested_urls == [
        "https://example.com/sitemap.xml",
        "https://example.com/wp-sitemap.xml",
        "https://example.com/sitemap.xml.gz",
    ]


def test_gzip_sitemap_index_loads_children(
    monkeypatch: Any,
) -> None:
    index_xml = """
    <sitemapindex>
        <sitemap>
            <loc>
                https://example.com/pages.xml.gz
            </loc>
        </sitemap>
    </sitemapindex>
    """

    pages_xml = """
    <urlset>
        <url>
            <loc>https://example.com/page-one</loc>
        </url>
        <url>
            <loc>https://example.com/page-two</loc>
        </url>
    </urlset>
    """

    responses = {
        "https://example.com/sitemap.xml.gz": (
            gzip.compress(
                index_xml.encode("utf-8"),
            )
        ),
        "https://example.com/pages.xml.gz": (
            gzip.compress(
                pages_xml.encode("utf-8"),
            )
        ),
    }

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        return MockResponse(
            content=responses[url],
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    loader = SitemapLoader()

    urls = loader.load_url(
        "https://example.com/sitemap.xml.gz",
    )

    assert urls == [
        "https://example.com/page-one",
        "https://example.com/page-two",
    ]
