from __future__ import annotations

from dataclasses import dataclass

from hermes_agent.batch_research_loader import (
    BatchResearchLoader,
    ResearchFailure,
)
from hermes_agent.documents.document import Document
from hermes_agent.rag.splitter import ChunkSplitter


@dataclass(slots=True)
class ResearchChunk:
    id: str
    document_id: str
    title: str
    source: str
    content: str
    index: int


@dataclass(slots=True)
class ResearchPipelineResult:
    documents: list[Document]
    chunks: list[ResearchChunk]
    failures: list[ResearchFailure]

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def failure_count(self) -> int:
        return len(self.failures)


class ResearchPipeline:
    def __init__(
        self,
        *,
        loader: BatchResearchLoader | None = None,
        chunker: ChunkSplitter | None = None,
    ) -> None:
        self._loader = (
            loader
            if loader is not None
            else BatchResearchLoader()
        )

        self._chunker = (
            chunker
            if chunker is not None
            else ChunkSplitter()
        )

    def run(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> ResearchPipelineResult:
        batch_result = self._loader.load(
            urls,
            continue_on_error=continue_on_error,
        )

        chunks: list[ResearchChunk] = []

        for document in batch_result.documents:
            chunks.extend(
                self._split_document(document),
            )

        return ResearchPipelineResult(
            documents=batch_result.documents,
            chunks=chunks,
            failures=batch_result.failures,
        )

    def _split_document(
        self,
        document: Document,
    ) -> list[ResearchChunk]:
        split_chunks = self._chunker.split(
            document,
        )

        chunks: list[ResearchChunk] = []

        for split_chunk in split_chunks:
            content = split_chunk.content.strip()

            if not content:
                continue

            chunks.append(
                ResearchChunk(
                    id=split_chunk.id,
                    document_id=document.id,
                    title=document.title,
                    source=document.source,
                    content=content,
                    index=split_chunk.index,
                ),
            )

        return chunks
