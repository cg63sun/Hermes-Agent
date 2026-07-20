from hermes_agent.documents.converter import DocumentConverter
from hermes_agent.models.page import WebPage


def test_convert_webpage_to_document():
    page = WebPage(
        url="https://example.com",
        title="Example Domain",
        text="Hello World",
        html="<html>Hello World</html>",
    )

    converter = DocumentConverter()
    document = converter.from_webpage(page)

    assert document.source == page.url
    assert document.title == page.title
    assert document.content == page.text

    assert document.metadata["url"] == page.url
    assert document.id != ""
