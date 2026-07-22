from __future__ import annotations

from hermes_agent.batch_research_loader import ResearchFailure
from hermes_agent.documents.document import Document
from hermes_agent.rag.chunk import Chunk
from hermes_agent.research_pipeline import (
    ResearchChunk,
    ResearchPipelineResult,
)
from hermes_agent.indexers.research_indexer import (
    ResearchIndexer,
    ResearchIndexResult,
)


class MockResearchPipeline:
    def __init__(
        self,
        result: ResearchPipelineResult,
    ) -> None:
        self.result = result
        self.received_urls: list[list[str]] = []
        self.received_continue_on_error: list[bool] = []

    def run(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> ResearchPipelineResult:
        self.received_urls.append(urls)
        self.received_continue_on_error.append(
            continue_on_error,
        )

        return self.result


class MockEmbeddingModel:
    def __init__(
        self,
        embeddings: list[list[float]],
    ) -> None:
        self.embeddings = embeddings
        self.received_texts: list[list[str]] = []

    def embed(
        self,
        text: str,
    ) -> list[float]:
        raise AssertionError(
            "ResearchIndexer should use embed_batch()."
        )

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self.received_texts.append(texts)
        return self.embeddings


class MockVectorStore:
    def __init__(self) -> None:
        self.add_calls: list[
            tuple[
                list[Chunk],
                list[list[float]],
            ]
        ] = []

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        self.add_calls.append(
            (
                chunks,
                embeddings,
            )
        )

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[Chunk]:
        return []


def create_document() -> Document:
    return Document(
        id="document-1",
        title="테스트 회사",
        source="https://example.com",
        content="회사 소개 본문",
    )


def create_research_chunk(
    *,
    chunk_id: str,
    index: int,
    content: str,
) -> ResearchChunk:
    return ResearchChunk(
        id=chunk_id,
        document_id="document-1",
        title="테스트 회사",
        source="https://example.com",
        content=content,
        index=index,
    )


def test_research_indexer_indexes_all_chunks() -> None:
    pipeline = MockResearchPipeline(
        ResearchPipelineResult(
            documents=[
                create_document(),
            ],
            chunks=[
                create_research_chunk(
                    chunk_id="chunk-1",
                    index=0,
                    content="첫 번째 청크",
                ),
                create_research_chunk(
                    chunk_id="chunk-2",
                    index=1,
                    content="두 번째 청크",
                ),
            ],
            failures=[],
        ),
    )

    embedding_model = MockEmbeddingModel(
        embeddings=[
            [1.0, 0.0],
            [0.0, 1.0],
        ],
    )

    vector_store = MockVectorStore()

    indexer = ResearchIndexer(
        pipeline=pipeline,
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    result = indexer.index(
        [
            "https://example.com",
        ],
    )

    assert isinstance(
        result,
        ResearchIndexResult,
    )

    assert result.document_count == 1
    assert result.chunk_count == 2
    assert result.indexed_count == 2
    assert result.failure_count == 0

    assert embedding_model.received_texts == [
        [
            "첫 번째 청크",
            "두 번째 청크",
        ],
    ]

    assert len(vector_store.add_calls) == 1

    stored_chunks, stored_embeddings = (
        vector_store.add_calls[0]
    )

    assert stored_embeddings == [
        [1.0, 0.0],
        [0.0, 1.0],
    ]

    assert len(stored_chunks) == 2

    assert stored_chunks[0] == Chunk(
        id="chunk-1",
        document_id="document-1",
        index=0,
        content="첫 번째 청크",
        metadata={
            "title": "테스트 회사",
            "source": "https://example.com",
        },
    )

    assert stored_chunks[1] == Chunk(
        id="chunk-2",
        document_id="document-1",
        index=1,
        content="두 번째 청크",
        metadata={
            "title": "테스트 회사",
            "source": "https://example.com",
        },
    )


def test_research_indexer_passes_options_to_pipeline() -> None:
    pipeline = MockResearchPipeline(
        ResearchPipelineResult(
            documents=[],
            chunks=[],
            failures=[],
        ),
    )

    indexer = ResearchIndexer(
        pipeline=pipeline,
        embedding_model=MockEmbeddingModel([]),
        vector_store=MockVectorStore(),
    )

    urls = [
        "https://example.com/one",
        "https://example.com/two",
    ]

    indexer.index(
        urls,
        continue_on_error=False,
    )

    assert pipeline.received_urls == [
        urls,
    ]

    assert (
        pipeline.received_continue_on_error
        == [
            False,
        ]
    )


def test_research_indexer_preserves_failures() -> None:
    failure = ResearchFailure(
        url="https://example.com/fail",
        error="수집 실패",
    )

    pipeline = MockResearchPipeline(
        ResearchPipelineResult(
            documents=[],
            chunks=[],
            failures=[
                failure,
            ],
        ),
    )

    vector_store = MockVectorStore()

    indexer = ResearchIndexer(
        pipeline=pipeline,
        embedding_model=MockEmbeddingModel([]),
        vector_store=vector_store,
    )

    result = indexer.index(
        [
            "https://example.com/fail",
        ],
    )

    assert result.indexed_count == 0
    assert result.failure_count == 1
    assert result.failures == [failure]

    assert vector_store.add_calls == []


def test_research_indexer_ignores_empty_chunks() -> None:
    pipeline = MockResearchPipeline(
        ResearchPipelineResult(
            documents=[
                create_document(),
            ],
            chunks=[
                create_research_chunk(
                    chunk_id="chunk-1",
                    index=0,
                    content="저장할 청크",
                ),
                create_research_chunk(
                    chunk_id="chunk-2",
                    index=1,
                    content="   ",
                ),
            ],
            failures=[],
        ),
    )

    embedding_model = MockEmbeddingModel(
        embeddings=[
            [1.0, 0.0],
        ],
    )

    vector_store = MockVectorStore()

    indexer = ResearchIndexer(
        pipeline=pipeline,
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    result = indexer.index(
        [
            "https://example.com",
        ],
    )

    assert result.chunk_count == 2
    assert result.indexed_count == 1

    assert embedding_model.received_texts == [
        [
            "저장할 청크",
        ],
    ]

    stored_chunks, _ = vector_store.add_calls[0]

    assert len(stored_chunks) == 1
    assert stored_chunks[0].id == "chunk-1"


def test_research_indexer_handles_empty_result() -> None:
    embedding_model = MockEmbeddingModel([])
    vector_store = MockVectorStore()

    indexer = ResearchIndexer(
        pipeline=MockResearchPipeline(
            ResearchPipelineResult(
                documents=[],
                chunks=[],
                failures=[],
            ),
        ),
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    result = indexer.index([])

    assert result.document_count == 0
    assert result.chunk_count == 0
    assert result.indexed_count == 0
    assert result.failure_count == 0

    assert embedding_model.received_texts == []
    assert vector_store.add_calls == []


def test_research_indexer_rejects_embedding_count_mismatch() -> None:
    pipeline = MockResearchPipeline(
        ResearchPipelineResult(
            documents=[
                create_document(),
            ],
            chunks=[
                create_research_chunk(
                    chunk_id="chunk-1",
                    index=0,
                    content="첫 번째 청크",
                ),
                create_research_chunk(
                    chunk_id="chunk-2",
                    index=1,
                    content="두 번째 청크",
                ),
            ],
            failures=[],
        ),
    )

    indexer = ResearchIndexer(
        pipeline=pipeline,
        embedding_model=MockEmbeddingModel(
            embeddings=[
                [1.0, 0.0],
            ],
        ),
        vector_store=MockVectorStore(),
    )

    try:
        indexer.index(
            [
                "https://example.com",
            ],
        )
    except ValueError as error:
        assert (
            "number of embeddings"
            in str(error)
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )
