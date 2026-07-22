from __future__ import annotations

import pytest

from hermes_agent.batch_research_loader import (
    BatchResearchLoader,
    BatchResearchResult,
    ResearchFailure,
)
from hermes_agent.documents.document import Document


class MockResearchLoader:
    def __init__(
        self,
        *,
        failures: set[str] | None = None,
    ) -> None:
        self.failures = (
            failures
            if failures is not None
            else set()
        )

        self.requested_urls: list[str] = []

    def load(
        self,
        url: str,
    ) -> Document:
        self.requested_urls.append(
            url,
        )

        if url in self.failures:
            raise RuntimeError(
                f"수집 실패: {url}",
            )

        return Document(
            id=url,
            title=f"Title: {url}",
            source=url,
            content=f"Content: {url}",
        )


def test_batch_loader_loads_multiple_documents() -> None:
    mock_loader = MockResearchLoader()

    loader = BatchResearchLoader(
        loader=mock_loader,
    )

    result = loader.load(
        [
            "https://example.com/one",
            "https://example.com/two",
        ],
    )

    assert isinstance(
        result,
        BatchResearchResult,
    )

    assert len(
        result.documents,
    ) == 2

    assert result.failures == []

    assert result.success_count == 2
    assert result.failure_count == 0
    assert result.total_count == 2

    assert mock_loader.requested_urls == [
        "https://example.com/one",
        "https://example.com/two",
    ]


def test_batch_loader_continues_after_failure() -> None:
    failed_url = (
        "https://example.com/fail"
    )

    mock_loader = MockResearchLoader(
        failures={
            failed_url,
        },
    )

    loader = BatchResearchLoader(
        loader=mock_loader,
    )

    result = loader.load(
        [
            "https://example.com/one",
            failed_url,
            "https://example.com/two",
        ],
    )

    assert result.success_count == 2
    assert result.failure_count == 1
    assert result.total_count == 3

    assert [
        document.source
        for document in result.documents
    ] == [
        "https://example.com/one",
        "https://example.com/two",
    ]

    assert result.failures == [
        ResearchFailure(
            url=failed_url,
            error=f"수집 실패: {failed_url}",
        ),
    ]


def test_batch_loader_can_stop_on_error() -> None:
    failed_url = (
        "https://example.com/fail"
    )

    mock_loader = MockResearchLoader(
        failures={
            failed_url,
        },
    )

    loader = BatchResearchLoader(
        loader=mock_loader,
    )

    with pytest.raises(
        RuntimeError,
        match="수집 실패",
    ):
        loader.load(
            [
                "https://example.com/one",
                failed_url,
                "https://example.com/two",
            ],
            continue_on_error=False,
        )

    assert mock_loader.requested_urls == [
        "https://example.com/one",
        failed_url,
    ]


def test_batch_loader_removes_duplicate_urls() -> None:
    mock_loader = MockResearchLoader()

    loader = BatchResearchLoader(
        loader=mock_loader,
    )

    result = loader.load(
        [
            "https://example.com",
            "https://example.com",
            "  https://example.com  ",
        ],
    )

    assert result.success_count == 1

    assert mock_loader.requested_urls == [
        "https://example.com",
    ]


def test_batch_loader_ignores_empty_urls() -> None:
    mock_loader = MockResearchLoader()

    loader = BatchResearchLoader(
        loader=mock_loader,
    )

    result = loader.load(
        [
            "",
            "   ",
            "https://example.com",
        ],
    )

    assert result.success_count == 1
    assert result.failure_count == 0

    assert mock_loader.requested_urls == [
        "https://example.com",
    ]


def test_batch_loader_handles_empty_list() -> None:
    mock_loader = MockResearchLoader()

    loader = BatchResearchLoader(
        loader=mock_loader,
    )

    result = loader.load(
        [],
    )

    assert result.documents == []
    assert result.failures == []
    assert result.total_count == 0

    assert mock_loader.requested_urls == []
