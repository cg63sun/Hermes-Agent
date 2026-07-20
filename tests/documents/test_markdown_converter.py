from hermes_agent.documents.document import Document
from hermes_agent.documents.markdown_converter import MarkdownConverter


def test_markdown_converter_adds_title():
    document = Document(
        id="doc-1",
        source="https://example.com",
        title="Example Domain",
        content="Hello World",
    )

    converter = MarkdownConverter()
    result = converter.convert(document)

    expected = "# Example Domain\n\nHello World"

    assert result.content == expected
    assert result.id == document.id
    assert result.source == document.source
    assert result.title == document.title
