from __future__ import annotations

from dataclasses import dataclass

from hermes_agent.documents.document import Document
from hermes_agent.research_loader import ResearchLoader


@dataclass(slots=True)
class ResearchFailure:
    url: str
    error: str


@dataclass(slots=True)
class BatchResearchResult:
    documents: list[Document]
    failures: list[ResearchFailure]

    @property
    def success_count(self) -> int:
        return len(
            self.documents,
        )

    @property
    def failure_count(self) -> int:
        return len(
            self.failures,
        )

    @property
    def total_count(self) -> int:
        return (
            self.success_count
            + self.failure_count
        )


class BatchResearchLoader:
    def __init__(
        self,
        *,
        loader: ResearchLoader | None = None,
    ) -> None:
        self._loader = (
            loader
            if loader is not None
            else ResearchLoader()
        )

    def load(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> BatchResearchResult:
        normalized_urls = self._normalize_urls(
            urls,
        )

        documents: list[Document] = []
        failures: list[ResearchFailure] = []

        for url in normalized_urls:
            try:
                document = self._loader.load(
                    url,
                )
            except Exception as error:
                if not continue_on_error:
                    raise

                failures.append(
                    ResearchFailure(
                        url=url,
                        error=str(error),
                    ),
                )

                continue

            documents.append(
                document,
            )

        return BatchResearchResult(
            documents=documents,
            failures=failures,
        )

    def _normalize_urls(
        self,
        urls: list[str],
    ) -> list[str]:
        normalized_urls: list[str] = []

        for url in urls:
            if not isinstance(
                url,
                str,
            ):
                continue

            normalized_url = url.strip()

            if not normalized_url:
                continue

            normalized_urls.append(
                normalized_url,
            )

        return list(
            dict.fromkeys(
                normalized_urls,
            ),
        )
