from __future__ import annotations

from hermes_agent.indexers.research_indexer import (
    ResearchIndexResult,
)
from hermes_agent.services.research_rag import (
    ResearchRAGService,
)


class MockResearchIndexer:
    def __init__(
        self,
        result: ResearchIndexResult,
    ) -> None:
        self.result = result
        self.received_urls: list[list[str]] = []
        self.received_continue_on_error: list[bool] = []

    def index(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> ResearchIndexResult:
        self.received_urls.append(urls)
        self.received_continue_on_error.append(
            continue_on_error,
        )

        return self.result


class MockRAGPipeline:
    def __init__(
        self,
        answer_text: str,
    ) -> None:
        self.answer_text = answer_text
        self.received_questions: list[str] = []
        self.received_top_k: list[int] = []
        self.received_sources: list[str | None] = []

    def answer(
        self,
        question: str,
        top_k: int = 5,
        source: str | None = None,
    ) -> str:
        self.received_questions.append(question)
        self.received_top_k.append(top_k)
        self.received_sources.append(source)

        return self.answer_text


def create_service() -> tuple[
    ResearchRAGService,
    MockResearchIndexer,
    MockRAGPipeline,
]:
    indexer = MockResearchIndexer(
        ResearchIndexResult(
            document_count=2,
            chunk_count=5,
            indexed_count=5,
            failures=[],
        ),
    )

    pipeline = MockRAGPipeline(
        answer_text="테스트 답변입니다.",
    )

    service = ResearchRAGService(
        research_indexer=indexer,
        pipeline=pipeline,
    )

    return service, indexer, pipeline


def test_research_rag_service_indexes_urls() -> None:
    service, indexer, _ = create_service()

    urls = [
        "https://example.com",
        "https://example.org",
    ]

    result = service.index(urls)

    assert result.document_count == 2
    assert result.chunk_count == 5
    assert result.indexed_count == 5
    assert result.failure_count == 0

    assert indexer.received_urls == [
        urls,
    ]

    assert (
        indexer.received_continue_on_error
        == [
            True,
        ]
    )


def test_research_rag_service_passes_index_options() -> None:
    service, indexer, _ = create_service()

    service.index(
        [
            "https://example.com",
        ],
        continue_on_error=False,
    )

    assert (
        indexer.received_continue_on_error
        == [
            False,
        ]
    )


def test_research_rag_service_answers_question() -> None:
    service, _, pipeline = create_service()

    answer = service.answer(
        "  회사 소개를 알려줘.  ",
        top_k=3,
    )

    assert answer == "테스트 답변입니다."

    assert pipeline.received_questions == [
        "회사 소개를 알려줘.",
    ]

    assert pipeline.received_top_k == [
        3,
    ]


def test_research_rag_service_rejects_empty_question() -> None:
    service, _, _ = create_service()

    try:
        service.answer("   ")
    except ValueError as error:
        assert (
            str(error)
            == "Question must not be empty."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )


def test_research_rag_service_rejects_invalid_top_k() -> None:
    service, _, _ = create_service()

    try:
        service.answer(
            "회사 소개",
            top_k=0,
        )
    except ValueError as error:
        assert (
            str(error)
            == "top_k must be at least 1."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )
def test_research_rag_service_creates_report() -> None:
    service, indexer, pipeline = create_service()

    urls = [
        "https://example.com",
        "https://example.org",
    ]

    report = service.research(
        urls,
        "  회사 소개를 알려줘.  ",
        top_k=3,
        continue_on_error=False,
    )

    assert report.urls == urls
    assert report.question == "회사 소개를 알려줘."
    assert report.answer == "테스트 답변입니다."
    assert report.document_count == 2
    assert report.chunk_count == 5
    assert report.indexed_count == 5
    assert report.failure_count == 0
    assert report.failures == []

    assert indexer.received_urls == [urls]
    assert indexer.received_continue_on_error == [False]

    assert pipeline.received_questions == [
        "회사 소개를 알려줘.",
    ]
    assert pipeline.received_top_k == [3]

def test_research_rag_service_passes_source() -> None:
    service, _, pipeline = create_service()

    answer = service.answer(
        "회사 소개를 알려줘.",
        top_k=3,
        source="https://example.com",
    )

    assert answer == "테스트 답변입니다."
    assert pipeline.received_questions == [
        "회사 소개를 알려줘.",
    ]
    assert pipeline.received_top_k == [3]
    assert pipeline.received_sources == [
        "https://example.com",
    ]
