from __future__ import annotations

from dataclasses import dataclass, field

from hermes_agent.batch_research_loader import ResearchFailure
from hermes_agent.embeddings.base import EmbeddingModel
from hermes_agent.rag.chunk import Chunk
from hermes_agent.research_pipeline import (
    ResearchChunk,
    ResearchPipeline,
)
from hermes_agent.vectorstores.base import VectorStore


@dataclass(slots=True)
class ResearchIndexResult:
    document_count: int
    chunk_count: int
    indexed_count: int
    failures: list[ResearchFailure] = field(
        default_factory=list,
    )

    @property
    def failure_count(self) -> int:
        return len(self.failures)


class ResearchIndexer:
    def __init__(
        self,
        *,
        pipeline: ResearchPipeline,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        self._pipeline = pipeline
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    def index(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> ResearchIndexResult:
        pipeline_result = self._pipeline.run(
            urls,
            continue_on_error=continue_on_error,
        )

        research_chunks = [
            chunk
            for chunk in pipeline_result.chunks
            if chunk.content.strip()
        ]

        if not research_chunks:
            return ResearchIndexResult(
                document_count=pipeline_result.document_count,
                chunk_count=pipeline_result.chunk_count,
                indexed_count=0,
                failures=list(pipeline_result.failures),
            )

        texts = [
            chunk.content
            for chunk in research_chunks
        ]

        embeddings = self._embedding_model.embed_batch(
            texts,
        )

        if len(embeddings) != len(research_chunks):
            raise ValueError(
                "The number of embeddings does not match "
                "the number of research chunks."
            )

        vector_chunks = [
            self._to_vector_chunk(chunk)
            for chunk in research_chunks
        ]

        self._vector_store.add(
            vector_chunks,
            embeddings,
        )

        return ResearchIndexResult(
            document_count=pipeline_result.document_count,
            chunk_count=pipeline_result.chunk_count,
            indexed_count=len(vector_chunks),
            failures=list(pipeline_result.failures),
        )

    @staticmethod
    def _to_vector_chunk(
        research_chunk: ResearchChunk,
    ) -> Chunk:
        return Chunk(
            id=research_chunk.id,
            document_id=research_chunk.document_id,
            index=research_chunk.index,
            content=research_chunk.content,
            metadata={
                "title": research_chunk.title,
                "source": research_chunk.source,
            },
        )
