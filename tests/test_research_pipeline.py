from __future__ import annotations

from dataclasses import dataclass

from hermes_agent.batch_research_loader import (
    BatchResearchResult,
    ResearchFailure,
)
from hermes_agent.documents.document import Document
from hermes_agent.research_pipeline import (
    ResearchChunk,
    ResearchPipeline,
    ResearchPipelineResult,
)


@dataclass
class MockSplitChunk:
    id: str
    document_id: str
    index: int
    content: str


class MockBatchResearchLoader:
    def __init__(
        self,
        result: BatchResearchResult,
    ) -> None:
        self.result = result
        self.received_urls: list[list[str]] = []
        self.received_continue_on_error: list[bool] = []

    def load(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> BatchResearchResult:
        self.received_urls.append(urls)
        self.received_continue_on_error.append(
            continue_on_error,
        )

        return self.result


class MockChunker:
    def __init__(
        self,
        chunks_by_document_id: dict[
            str,
            list[MockSplitChunk],
        ],
    ) -> None:
        self.chunks_by_document_id = (
            chunks_by_document_id
        )

        self.received_documents: list[Document] = []

    def split(
        self,
        document: Document,
    ) -> list[MockSplitChunk]:
        self.received_documents.append(
            document,
        )

        return self.chunks_by_document_id.get(
            document.id,
            [],
        )


def create_document(
    *,
    document_id: str,
    title: str,
    source: str,
    content: str,
) -> Document:
    return Document(
        id=document_id,
        title=title,
        source=source,
        content=content,
    )


def test_research_pipeline_creates_chunks() -> None:
    first_document = create_document(
        document_id="doc-1",
        title="첫 번째 문서",
        source="https://example.com/one",
        content="첫 번째 문서 본문",
    )

    second_document = create_document(
        document_id="doc-2",
        title="두 번째 문서",
        source="https://example.com/two",
        content="두 번째 문서 본문",
    )

    batch_result = BatchResearchResult(
        documents=[
            first_document,
            second_document,
        ],
        failures=[],
    )

    loader = MockBatchResearchLoader(
        batch_result,
    )

    chunker = MockChunker(
        {
            "doc-1": [
                MockSplitChunk(
                    id="chunk-1",
                    document_id="doc-1",
                    index=0,
                    content="첫 번째 청크",
                ),
                MockSplitChunk(
                    id="chunk-2",
                    document_id="doc-1",
                    index=1,
                    content="두 번째 청크",
                ),
            ],
            "doc-2": [
                MockSplitChunk(
                    id="chunk-3",
                    document_id="doc-2",
                    index=0,
                    content="세 번째 청크",
                ),
            ],
        },
    )

    pipeline = ResearchPipeline(
        loader=loader,
        chunker=chunker,
    )

    result = pipeline.run(
        [
            "https://example.com/one",
            "https://example.com/two",
        ],
    )

    assert isinstance(
        result,
        ResearchPipelineResult,
    )

    assert result.document_count == 2
    assert result.chunk_count == 3
    assert result.failure_count == 0

    assert result.chunks == [
        ResearchChunk(
            id="chunk-1",
            document_id="doc-1",
            title="첫 번째 문서",
            source="https://example.com/one",
            content="첫 번째 청크",
            index=0,
        ),
        ResearchChunk(
            id="chunk-2",
            document_id="doc-1",
            title="첫 번째 문서",
            source="https://example.com/one",
            content="두 번째 청크",
            index=1,
        ),
        ResearchChunk(
            id="chunk-3",
            document_id="doc-2",
            title="두 번째 문서",
            source="https://example.com/two",
            content="세 번째 청크",
            index=0,
        ),
    ]


def test_research_pipeline_passes_urls_to_loader() -> None:
    loader = MockBatchResearchLoader(
        BatchResearchResult(
            documents=[],
            failures=[],
        ),
    )

    pipeline = ResearchPipeline(
        loader=loader,
        chunker=MockChunker({}),
    )

    urls = [
        "https://example.com/one",
        "https://example.com/two",
    ]

    pipeline.run(
        urls,
        continue_on_error=False,
    )

    assert loader.received_urls == [
        urls,
    ]

    assert (
        loader.received_continue_on_error
        == [
            False,
        ]
    )


def test_research_pipeline_preserves_failures() -> None:
    failure = ResearchFailure(
        url="https://example.com/fail",
        error="수집 실패",
    )

    pipeline = ResearchPipeline(
        loader=MockBatchResearchLoader(
            BatchResearchResult(
                documents=[],
                failures=[
                    failure,
                ],
            ),
        ),
        chunker=MockChunker({}),
    )

    result = pipeline.run(
        [
            "https://example.com/fail",
        ],
    )

    assert result.documents == []
    assert result.chunks == []
    assert result.failures == [failure]
    assert result.failure_count == 1


def test_research_pipeline_ignores_empty_chunks() -> None:
    document = create_document(
        document_id="doc-1",
        title="테스트 문서",
        source="https://example.com",
        content="테스트 본문",
    )

    chunker = MockChunker(
        {
            "doc-1": [
                MockSplitChunk(
                    id="chunk-1",
                    document_id="doc-1",
                    index=0,
                    content="첫 번째 청크",
                ),
                MockSplitChunk(
                    id="chunk-2",
                    document_id="doc-1",
                    index=1,
                    content="   ",
                ),
                MockSplitChunk(
                    id="chunk-3",
                    document_id="doc-1",
                    index=2,
                    content="두 번째 청크",
                ),
            ],
        },
    )

    pipeline = ResearchPipeline(
        loader=MockBatchResearchLoader(
            BatchResearchResult(
                documents=[document],
                failures=[],
            ),
        ),
        chunker=chunker,
    )

    result = pipeline.run(
        [
            "https://example.com",
        ],
    )

    assert result.chunk_count == 2

    assert [
        chunk.content
        for chunk in result.chunks
    ] == [
        "첫 번째 청크",
        "두 번째 청크",
    ]


def test_research_pipeline_handles_empty_documents() -> None:
    chunker = MockChunker({})

    pipeline = ResearchPipeline(
        loader=MockBatchResearchLoader(
            BatchResearchResult(
                documents=[],
                failures=[],
            ),
        ),
        chunker=chunker,
    )

    result = pipeline.run([])

    assert result.document_count == 0
    assert result.chunk_count == 0
    assert result.failure_count == 0

    assert chunker.received_documents == []
