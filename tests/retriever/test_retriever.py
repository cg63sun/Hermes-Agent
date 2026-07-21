from hermes_agent.embeddings.mock import MockEmbeddingModel
from hermes_agent.rag.chunk import Chunk
from hermes_agent.retriever import Retriever
from hermes_agent.vectorstores.memory import MemoryVectorStore


def test_retrieve_returns_similar_chunks() -> None:
    embedding_model = MockEmbeddingModel()
    vector_store = MemoryVectorStore()

    python_chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        content="Python",
        index=0,
    )

    banana_chunk = Chunk(
        id="chunk-2",
        document_id="doc-1",
        content="Banana",
        index=1,
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

    results = retriever.retrieve(
        query="Python",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].content == "Python"
