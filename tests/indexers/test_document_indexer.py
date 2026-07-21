from hermes_agent.documents import Document
from hermes_agent.embeddings import MockEmbeddingModel
from hermes_agent.indexers import (
    ChunkIndexer,
    DocumentIndexer,
)
from hermes_agent.rag import ChunkSplitter
from hermes_agent.vectorstores import MemoryVectorStore


def test_document_indexer_indexes_document() -> None:
    embedding_model = MockEmbeddingModel()
    vector_store = MemoryVectorStore()

    chunk_indexer = ChunkIndexer(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    document_indexer = DocumentIndexer(
        splitter=ChunkSplitter(
            chunk_size=6,
        ),
        chunk_indexer=chunk_indexer,
    )

    document = Document(
        id="doc-1",
        title="테스트 문서",
        source="test",
        content="PythonBanana",
    )

    indexed_count = document_indexer.index(document)

    assert indexed_count == 2

    results = vector_store.search(
        embedding_model.embed("Python"),
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].content == "Python"


def test_document_indexer_handles_empty_document() -> None:
    document_indexer = DocumentIndexer(
        splitter=ChunkSplitter(
            chunk_size=100,
        ),
        chunk_indexer=ChunkIndexer(
            embedding_model=MockEmbeddingModel(),
            vector_store=MemoryVectorStore(),
        ),
    )

    document = Document(
        id="doc-empty",
        title="빈 문서",
        source="test",
        content="",
    )

    indexed_count = document_indexer.index(document)

    assert indexed_count == 0
