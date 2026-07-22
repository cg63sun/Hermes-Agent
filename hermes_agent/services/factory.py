from hermes_agent.crawler.crawler import WebCrawler
from hermes_agent.documents.converter import DocumentConverter
from hermes_agent.embeddings.base import EmbeddingModel
from hermes_agent.generators.base import BaseGenerator
from hermes_agent.indexers import (
    ChunkIndexer,
    DocumentIndexer,
    WebsiteIndexer,
)
from hermes_agent.rag import (
    ChunkSplitter,
    ContextBuilder,
    PromptBuilder,
    RAGPipeline,
)
from hermes_agent.retriever.retriever import Retriever
from hermes_agent.services.website_rag import WebsiteRAGService
from hermes_agent.vectorstores import MemoryVectorStore


class WebsiteRAGFactory:
    @staticmethod
    def create(
        embedding_model: EmbeddingModel,
        generator: BaseGenerator,
        chunk_size: int = 500,
    ) -> WebsiteRAGService:
        vector_store = MemoryVectorStore()

        chunk_indexer = ChunkIndexer(
            embedding_model=embedding_model,
            vector_store=vector_store,
        )

        document_indexer = DocumentIndexer(
            splitter=ChunkSplitter(
                chunk_size=chunk_size,
            ),
            chunk_indexer=chunk_indexer,
        )

        website_indexer = WebsiteIndexer(
            crawler=WebCrawler(),
            converter=DocumentConverter(),
            document_indexer=document_indexer,
        )

        retriever = Retriever(
            embedding_model=embedding_model,
            vector_store=vector_store,
        )

        pipeline = RAGPipeline(
            retriever=retriever,
            context_builder=ContextBuilder(),
            prompt_builder=PromptBuilder(),
            generator=generator,
        )

        return WebsiteRAGService(
            website_indexer=website_indexer,
            pipeline=pipeline,
        )
