from hermes_agent.indexers.website_indexer import WebsiteIndexer
from hermes_agent.rag.pipeline import RAGPipeline


class WebsiteRAGService:
    def __init__(
        self,
        website_indexer: WebsiteIndexer,
        pipeline: RAGPipeline,
    ) -> None:
        self._website_indexer = website_indexer
        self._pipeline = pipeline

    def index_website(self, url: str) -> int:
        return self._website_indexer.index(url)

    def answer(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:
        return self._pipeline.answer(
            question=question,
            top_k=top_k,
        )
