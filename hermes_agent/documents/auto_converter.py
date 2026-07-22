from __future__ import annotations

import hashlib

from hermes_agent.crawler.auto_crawler import (
    AutoCrawlResult,
)
from hermes_agent.documents.document import Document


class AutoDocumentConverter:
    def convert(
        self,
        result: AutoCrawlResult,
    ) -> Document:
        source = result.url.strip()
        title = result.title.strip()
        content = result.text.strip()

        if not source:
            raise ValueError(
                "문서의 URL이 비어 있습니다.",
            )

        if not title:
            title = source

        document_id = self._create_document_id(
            source,
        )

        return Document(
            id=document_id,
            title=title,
            source=source,
            content=content,
        )

    def _create_document_id(
        self,
        source: str,
    ) -> str:
        return hashlib.sha256(
            source.encode(
                "utf-8",
            ),
        ).hexdigest()
