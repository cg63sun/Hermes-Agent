from hermes_agent.documents.document import Document


def test_document_creation():
    document = Document(
        id="doc-1",
        source="https://example.com",
        title="Example",
        content="Hello World",
    )

    assert document.id == "doc-1"
    assert document.source == "https://example.com"
    assert document.title == "Example"
    assert document.content == "Hello World"
    assert document.metadata == {}
