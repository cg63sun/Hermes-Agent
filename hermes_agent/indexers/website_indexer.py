from hermes_agent.crawler.crawler import WebCrawler
from hermes_agent.documents.converter import DocumentConverter
from hermes_agent.indexers.document_indexer import DocumentIndexer


class WebsiteIndexer:
    def __init__(
        self,
        crawler: WebCrawler,
        converter: DocumentConverter,
        document_indexer: DocumentIndexer,
    ) -> None:
        self._crawler = crawler
        self._converter = converter
        self._document_indexer = document_indexer

    def index(self, url: str) -> int:
        page = self._crawler.fetch(url)
        document = self._converter.from_webpage(page)

        return self._document_indexer.index(document)
