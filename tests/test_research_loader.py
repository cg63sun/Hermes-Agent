from __future__ import annotations

import pytest

from hermes_agent.crawler.auto_crawler import (
    AutoCrawlResult,
)
from hermes_agent.documents.document import Document
from hermes_agent.research_loader import (
    ResearchLoader,
)


class MockAutoCrawler:
    def __init__(
        self,
        result: AutoCrawlResult,
    ) -> None:
        self.result = result
        self.requested_urls: list[str] = []

    def fetch(
        self,
        url: str,
    ) -> AutoCrawlResult:
        self.requested_urls.append(
            url,
        )

        return self.result


class MockDocumentConverter:
    def __init__(
        self,
        document: Document,
    ) -> None:
        self.document = document
        self.received_results: list[
            AutoCrawlResult
        ] = []

    def convert(
        self,
        result: AutoCrawlResult,
    ) -> Document:
        self.received_results.append(
            result,
        )

        return self.document


def create_crawl_result() -> AutoCrawlResult:
    return AutoCrawlResult(
        title="Hermes Agent",
        url="https://example.com",
        html=(
            "<html><body>"
            "Hermes Agent"
            "</body></html>"
        ),
        text="Hermes Agent 테스트 본문입니다.",
        source="web",
        links=[
            "https://example.com/about",
        ],
        images=[
            "https://example.com/image.jpg",
        ],
        meta_description="테스트 페이지",
        canonical_url="https://example.com",
        language="ko",
    )


def create_document() -> Document:
    return Document(
        id="test-document-id",
        title="Hermes Agent",
        source="https://example.com",
        content="Hermes Agent 테스트 본문입니다.",
    )


def test_research_loader_loads_document() -> None:
    crawl_result = create_crawl_result()
    document = create_document()

    crawler = MockAutoCrawler(
        crawl_result,
    )

    converter = MockDocumentConverter(
        document,
    )

    loader = ResearchLoader(
        crawler=crawler,
        converter=converter,
    )

    loaded_document = loader.load(
        "https://example.com",
    )

    assert loaded_document is document

    assert crawler.requested_urls == [
        "https://example.com",
    ]

    assert converter.received_results == [
        crawl_result,
    ]


def test_research_loader_strips_url() -> None:
    crawler = MockAutoCrawler(
        create_crawl_result(),
    )

    converter = MockDocumentConverter(
        create_document(),
    )

    loader = ResearchLoader(
        crawler=crawler,
        converter=converter,
    )

    loader.load(
        "  https://example.com  ",
    )

    assert crawler.requested_urls == [
        "https://example.com",
    ]


def test_research_loader_rejects_empty_url() -> None:
    crawler = MockAutoCrawler(
        create_crawl_result(),
    )

    converter = MockDocumentConverter(
        create_document(),
    )

    loader = ResearchLoader(
        crawler=crawler,
        converter=converter,
    )

    with pytest.raises(
        ValueError,
        match="URL",
    ):
        loader.load(
            "   ",
        )

    assert crawler.requested_urls == []

    assert converter.received_results == []
