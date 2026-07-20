from hermes_agent.documents.document import Document
from hermes_agent.rag.splitter import ChunkSplitter


def test_split_document_into_chunks():
    document = Document(
        id="doc-1",
        source="https://example.com",
        title="Example",
        content="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    )

    splitter = ChunkSplitter(chunk_size=10)

    chunks = splitter.split(document)

    assert len(chunks) == 3

    assert chunks[0].content == "ABCDEFGHIJ"
    assert chunks[1].content == "KLMNOPQRST"
    assert chunks[2].content == "UVWXYZ"

    assert chunks[0].index == 0
    assert chunks[1].index == 1
    assert chunks[2].index == 2

    assert chunks[0].document_id == document.id
    assert chunks[1].document_id == document.id
    assert chunks[2].document_id == document.id
