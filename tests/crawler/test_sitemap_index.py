from typing import Any

import httpx

from hermes_agent.crawler.sitemap import SitemapLoader


def test_parse_document_detects_urlset() -> None:
    loader = SitemapLoader()

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/</loc>
        </url>
        <url>
            <loc>https://example.com/about</loc>
        </url>
    </urlset>
    """

    sitemap_type, urls = loader.parse_document(
        xml_content,
    )

    assert sitemap_type == "urlset"

    assert urls == [
        "https://example.com/",
        "https://example.com/about",
    ]


def test_parse_document_detects_sitemap_index() -> None:
    loader = SitemapLoader()

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    >
        <sitemap>
            <loc>
                https://example.com/page-sitemap.xml
            </loc>
        </sitemap>
        <sitemap>
            <loc>
                https://example.com/post-sitemap.xml
            </loc>
        </sitemap>
    </sitemapindex>
    """

    sitemap_type, urls = loader.parse_document(
        xml_content,
    )

    assert sitemap_type == "index"

    assert urls == [
        "https://example.com/page-sitemap.xml",
        "https://example.com/post-sitemap.xml",
    ]


def test_sitemap_loader_loads_child_sitemaps(
    monkeypatch: Any,
) -> None:
    responses = {
        "https://example.com/sitemap.xml": """
            <sitemapindex
                xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            >
                <sitemap>
                    <loc>
                        https://example.com/page-sitemap.xml
                    </loc>
                </sitemap>
                <sitemap>
                    <loc>
                        https://example.com/post-sitemap.xml
                    </loc>
                </sitemap>
            </sitemapindex>
        """,
        "https://example.com/page-sitemap.xml": """
            <urlset
                xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            >
                <url>
                    <loc>https://example.com/about</loc>
                </url>
                <url>
                    <loc>https://example.com/contact</loc>
                </url>
            </urlset>
        """,
        "https://example.com/post-sitemap.xml": """
            <urlset
                xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            >
                <url>
                    <loc>https://example.com/news/one</loc>
                </url>
            </urlset>
        """,
    }

    class MockResponse:
        def __init__(
            self,
            text: str,
        ) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    requested_urls: list[str] = []

    def mock_get(
        url: str,
        timeout: float,
        follow_redirects: bool,
    ) -> MockResponse:
        requested_urls.append(url)

        assert timeout == 20.0
        assert follow_redirects is True

        return MockResponse(
            responses[url],
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
        "https://example.com/contact",
        "https://example.com/news/one",
    ]

    assert requested_urls == [
        "https://example.com/sitemap.xml",
        "https://example.com/page-sitemap.xml",
        "https://example.com/post-sitemap.xml",
    ]


def test_sitemap_loader_removes_duplicate_urls(
    monkeypatch: Any,
) -> None:
    responses = {
        "https://example.com/sitemap.xml": """
            <sitemapindex>
                <sitemap>
                    <loc>
                        https://example.com/one.xml
                    </loc>
                </sitemap>
                <sitemap>
                    <loc>
                        https://example.com/two.xml
                    </loc>
                </sitemap>
            </sitemapindex>
        """,
        "https://example.com/one.xml": """
            <urlset>
                <url>
                    <loc>https://example.com/about</loc>
                </url>
            </urlset>
        """,
        "https://example.com/two.xml": """
            <urlset>
                <url>
                    <loc>https://example.com/about</loc>
                </url>
                <url>
                    <loc>https://example.com/service</loc>
                </url>
            </urlset>
        """,
    }

    class MockResponse:
        def __init__(
            self,
            text: str,
        ) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    monkeypatch.setattr(
        httpx,
        "get",
        lambda url, **kwargs: MockResponse(
            responses[url],
        ),
    )

    loader = SitemapLoader()

    urls = loader.load(
        "https://example.com",
    )

    assert urls == [
        "https://example.com/about",
        "https://example.com/service",
    ]


def test_sitemap_loader_skips_failed_child(
    monkeypatch: Any,
) -> None:
    index_xml = """
        <sitemapindex>
            <sitemap>
                <loc>
                    https://example.com/good.xml
                </loc>
            </sitemap>
            <sitemap>
                <loc>
                    https://example.com/missing.xml
                </loc>
            </sitemap>
        </sitemapindex>
    """

    child_xml = """
        <urlset>
            <url>
                <loc>https://example.com/about</loc>
            </url>
        </urlset>
    """

    class MockResponse:
        def __init__(
            self,
            text: str,
        ) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        if url == "https://example.com/sitemap.xml":
            return MockResponse(index_xml)

        if url == "https://example.com/good.xml":
            return MockResponse(child_xml)

        raise httpx.HTTPError(
            "사이트맵을 찾을 수 없습니다.",
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


def test_sitemap_loader_prevents_recursive_loop(
    monkeypatch: Any,
) -> None:
    responses = {
        "https://example.com/sitemap.xml": """
            <sitemapindex>
                <sitemap>
                    <loc>
                        https://example.com/child.xml
                    </loc>
                </sitemap>
            </sitemapindex>
        """,
        "https://example.com/child.xml": """
            <sitemapindex>
                <sitemap>
                    <loc>
                        https://example.com/sitemap.xml
                    </loc>
                </sitemap>
            </sitemapindex>
        """,
    }

    class MockResponse:
        def __init__(
            self,
            text: str,
        ) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    requested_urls: list[str] = []

    def mock_get(
        url: str,
        **kwargs: Any,
    ) -> MockResponse:
        requested_urls.append(url)

        return MockResponse(
            responses[url],
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
        "https://example.com/child.xml",
    ]
