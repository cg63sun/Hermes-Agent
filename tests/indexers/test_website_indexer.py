from hermes_agent.indexers import WebsiteIndexer


class MockCrawler:
    def fetch(self, url: str) -> object:
        return {
            "url": url,
            "title": "Example",
            "text": "Python",
        }


class MockConverter:
    def from_webpage(self, page: object) -> object:
        return {
            "id": "doc-1",
            "content": "Python",
        }


class MockDocumentIndexer:
    def __init__(self) -> None:
        self.received_document: object | None = None

    def index(self, document: object) -> int:
        self.received_document = document
        return 1


def test_website_indexer_indexes_url() -> None:
    document_indexer = MockDocumentIndexer()

    website_indexer = WebsiteIndexer(
        crawler=MockCrawler(),
        converter=MockConverter(),
        document_indexer=document_indexer,
    )

    indexed_count = website_indexer.index(
        "https://example.com",
    )

    assert indexed_count == 1
    assert document_indexer.received_document == {
        "id": "doc-1",
        "content": "Python",
    }
