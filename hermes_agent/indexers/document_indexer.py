from hermes_agent.documents import Document
from hermes_agent.indexers.chunk_indexer import ChunkIndexer
from hermes_agent.rag.splitter import ChunkSplitter


class DocumentIndexer:
    def __init__(
        self,
        splitter: ChunkSplitter,
        chunk_indexer: ChunkIndexer,
    ) -> None:
        self._splitter = splitter
        self._chunk_indexer = chunk_indexer

    def index(self, document: Document) -> int:
        chunks = self._splitter.split(document)

        return self._chunk_indexer.index(chunks)