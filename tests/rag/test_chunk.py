from hermes_agent.rag.chunk import Chunk


def test_chunk_creation():
    chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        index=0,
        content="Hello World",
    )

    assert chunk.id == "chunk-1"
    assert chunk.document_id == "doc-1"
    assert chunk.index == 0
    assert chunk.content == "Hello World"
    assert chunk.metadata == {}
