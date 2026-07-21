from hermes_agent.embeddings import MockEmbeddingModel
from hermes_agent.indexers import ChunkIndexer
from hermes_agent.rag.chunk import Chunk
from hermes_agent.vectorstores import MemoryVectorStore


def test_chunk_indexer_indexes_chunks() -> None:
    embedding_model = MockEmbeddingModel()
    vector_store = MemoryVectorStore()

    indexer = ChunkIndexer(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    chunks = [
        Chunk(
            id="chunk-1",
            document_id="doc-1",
            index=0,
            content="Python",
        ),
        Chunk(
            id="chunk-2",
            document_id="doc-1",
            index=1,
            content="Banana",
        ),
    ]

    indexed_count = indexer.index(chunks)

    assert indexed_count == 2

    results = vector_store.search(
        embedding_model.embed("Python"),
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].content == "Python"


def test_chunk_indexer_handles_empty_list() -> None:
    indexer = ChunkIndexer(
        embedding_model=MockEmbeddingModel(),
        vector_store=MemoryVectorStore(),
    )

    indexed_count = indexer.index([])

    assert indexed_count == 0
