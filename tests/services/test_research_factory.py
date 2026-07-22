from __future__ import annotations

from hermes_agent.embeddings.base import EmbeddingModel
from hermes_agent.generators.base import BaseGenerator
from hermes_agent.services.research_factory import (
    ResearchRAGFactory,
)
from hermes_agent.services.research_rag import (
    ResearchRAGService,
)


class MockEmbeddingModel(EmbeddingModel):
    def embed(
        self,
        text: str,
    ) -> list[float]:
        return [
            float(len(text)),
            1.0,
        ]


class MockGenerator(BaseGenerator):
    def generate(
        self,
        prompt: str,
    ) -> str:
        return "테스트 답변"


def test_research_factory_creates_service() -> None:
    service = ResearchRAGFactory.create(
        embedding_model=MockEmbeddingModel(),
        generator=MockGenerator(),
    )

    assert isinstance(
        service,
        ResearchRAGService,
    )


def test_research_factory_accepts_chunk_size() -> None:
    service = ResearchRAGFactory.create(
        embedding_model=MockEmbeddingModel(),
        generator=MockGenerator(),
        chunk_size=1000,
    )

    assert isinstance(
        service,
        ResearchRAGService,
    )


def test_research_factory_rejects_zero_chunk_size() -> None:
    try:
        ResearchRAGFactory.create(
            embedding_model=MockEmbeddingModel(),
            generator=MockGenerator(),
            chunk_size=0,
        )
    except ValueError as error:
        assert (
            str(error)
            == "chunk_size must be at least 1."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )


def test_research_factory_rejects_negative_chunk_size() -> None:
    try:
        ResearchRAGFactory.create(
            embedding_model=MockEmbeddingModel(),
            generator=MockGenerator(),
            chunk_size=-1,
        )
    except ValueError as error:
        assert (
            str(error)
            == "chunk_size must be at least 1."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )
