from __future__ import annotations

from hermes_agent.crawler.auto_crawler import (
    AutoCrawler,
)
from hermes_agent.documents.auto_converter import (
    AutoDocumentConverter,
)
from hermes_agent.documents.document import Document


class ResearchLoader:
    def __init__(
        self,
        *,
        crawler: AutoCrawler | None = None,
        converter: AutoDocumentConverter | None = None,
    ) -> None:
        self._crawler = (
            crawler
            if crawler is not None
            else AutoCrawler()
        )

        self._converter = (
            converter
            if converter is not None
            else AutoDocumentConverter()
        )

    def load(
        self,
        url: str,
    ) -> Document:
        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError(
                "불러올 URL을 입력하세요.",
            )

        crawl_result = self._crawler.fetch(
            normalized_url,
        )

        return self._converter.convert(
            crawl_result,
        )
