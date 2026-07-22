from __future__ import annotations

from hermes_agent.indexers.research_indexer import (
    ResearchIndexer,
    ResearchIndexResult,
)
from hermes_agent.rag.pipeline import RAGPipeline
from hermes_agent.services.research_report import ResearchReport


class ResearchRAGService:
    """Research multiple websites and answer questions from indexed content."""

    def __init__(
        self,
        *,
        research_indexer: ResearchIndexer,
        pipeline: RAGPipeline,
    ) -> None:
        self._research_indexer = research_indexer
        self._pipeline = pipeline

    def index(
        self,
        urls: list[str],
        *,
        continue_on_error: bool = True,
    ) -> ResearchIndexResult:
        return self._research_indexer.index(
            urls,
            continue_on_error=continue_on_error,
        )

    def answer(
        self,
        question: str,
        *,
        top_k: int = 5,
    ) -> str:
        question = question.strip()

        if not question:
            raise ValueError(
                "Question must not be empty."
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1."
            )

        return self._pipeline.answer(
            question=question,
            top_k=top_k,
        )

    def research(
        self,
        urls: list[str],
        question: str,
        *,
        top_k: int = 5,
        continue_on_error: bool = True,
    ) -> ResearchReport:
        normalized_question = question.strip()

        index_result = self.index(
            urls,
            continue_on_error=continue_on_error,
        )

        answer = self.answer(
            normalized_question,
            top_k=top_k,
        )

        failures = [
            f"{failure.url}: {failure.error}"
            for failure in index_result.failures
        ]

        return ResearchReport(
            urls=list(urls),
            question=normalized_question,
            answer=answer,
            document_count=index_result.document_count,
            chunk_count=index_result.chunk_count,
            indexed_count=index_result.indexed_count,
            failure_count=index_result.failure_count,
            failures=failures,
        )
