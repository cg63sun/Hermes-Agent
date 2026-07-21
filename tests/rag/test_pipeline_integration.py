from hermes_agent.embeddings import MockEmbeddingModel
from hermes_agent.generators import MockGenerator
from hermes_agent.rag import (
    ContextBuilder,
    PromptBuilder,
    RAGPipeline,
)
from hermes_agent.rag.chunk import Chunk
from hermes_agent.retriever.retriever import Retriever
from hermes_agent.vectorstores import MemoryVectorStore


def test_rag_pipeline_with_real_components() -> None:
    embedding_model = MockEmbeddingModel()
    vector_store = MemoryVectorStore()

    python_chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        index=0,
        content="Python",
    )

    banana_chunk = Chunk(
        id="chunk-2",
        document_id="doc-2",
        index=0,
        content="Banana",
    )

    vector_store.add(
        chunks=[
            python_chunk,
            banana_chunk,
        ],
        embeddings=[
            embedding_model.embed(python_chunk.content),
            embedding_model.embed(banana_chunk.content),
        ],
    )

    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    pipeline = RAGPipeline(
        retriever=retriever,
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        generator=MockGenerator(
            response="Python 관련 답변입니다.",
        ),
    )

    result = pipeline.answer(
        question="Python",
        top_k=1,
    )

    assert result == "Python 관련 답변입니다."
