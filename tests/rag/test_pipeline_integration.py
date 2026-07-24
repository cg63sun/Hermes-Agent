from unittest.mock import Mock
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
def test_retriever_filters_chunks_by_source() -> None:
    embedding_model = MockEmbeddingModel()
    vector_store = MemoryVectorStore()

    python_chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        index=0,
        content="Python",
        metadata={
            "source": "https://python.example.com",
        },
    )

    banana_chunk = Chunk(
        id="chunk-2",
        document_id="doc-2",
        index=0,
        content="Banana",
        metadata={
            "source": "https://banana.example.com",
        },
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

    chunks = retriever.retrieve(
        query="Python",
        top_k=1,
        source="https://banana.example.com",
    )

    assert chunks == [banana_chunk]

def test_rag_pipeline_passes_source_to_retriever() -> None:
    retriever = Mock(spec=Retriever)
    retriever.retrieve.return_value = []

    pipeline = RAGPipeline(
        retriever=retriever,
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        generator=MockGenerator(
            response="경쟁사 분석 결과",
        ),
    )

    result = pipeline.answer(
        question="서비스와 가격을 분석해줘",
        top_k=5,
        source="https://competitor.example.com",
    )

    assert result == "경쟁사 분석 결과"

    retriever.retrieve.assert_called_once_with(
        query="서비스와 가격을 분석해줘",
        top_k=5,
        source="https://competitor.example.com",
    )
