from hermes_agent.generators import MockGenerator
from hermes_agent.rag import (
    ContextBuilder,
    PromptBuilder,
    RAGPipeline,
)
from hermes_agent.rag.chunk import Chunk


class MockRetriever:
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Chunk]:
        return [
            Chunk(
                id="chunk-1",
                document_id="doc-1",
                index=0,
                content="Python은 프로그래밍 언어입니다.",
            ),
        ]


def test_rag_pipeline_returns_generated_answer() -> None:
    pipeline = RAGPipeline(
        retriever=MockRetriever(),
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        generator=MockGenerator(
            response="Python은 프로그래밍 언어입니다.",
        ),
    )

    result = pipeline.answer(
        question="Python이란 무엇인가요?",
        top_k=3,
    )

    assert result == "Python은 프로그래밍 언어입니다."
