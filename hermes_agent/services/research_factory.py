from __future__ import annotations

from hermes_agent.batch_research_loader import (
    BatchResearchLoader,
)
from hermes_agent.embeddings.base import EmbeddingModel
from hermes_agent.embeddings.ollama import (
    OllamaEmbeddingModel,
)
from hermes_agent.generators.base import BaseGenerator
from hermes_agent.generators.ollama import OllamaGenerator
from hermes_agent.indexers.research_indexer import (
    ResearchIndexer,
)
from hermes_agent.rag import (
    ChunkSplitter,
    ContextBuilder,
    PromptBuilder,
    RAGPipeline,
)
from hermes_agent.research_loader import ResearchLoader
from hermes_agent.research_pipeline import ResearchPipeline
from hermes_agent.retriever.retriever import Retriever
from hermes_agent.services.research_rag import (
    ResearchRAGService,
)
from hermes_agent.vectorstores import MemoryVectorStore


class ResearchRAGFactory:
    """Create a complete multi-website research RAG service."""

    @staticmethod
    def create(
        *,
        embedding_model: EmbeddingModel | None = None,
        generator: BaseGenerator | None = None,
        chunk_size: int = 500,
        embedding_model_name: str = "nomic-embed-text",
        generation_model_name: str = "qwen3:8b",
        ollama_base_url: str = "http://127.0.0.1:11434",
        embedding_timeout: float = 30.0,
        generation_timeout: float = 120.0,
    ) -> ResearchRAGService:
        if chunk_size < 1:
            raise ValueError(
                "chunk_size must be at least 1."
            )

        resolved_embedding_model = (
            embedding_model
            if embedding_model is not None
            else OllamaEmbeddingModel(
                model=embedding_model_name,
                base_url=ollama_base_url,
                timeout=embedding_timeout,
            )
        )

        resolved_generator = (
            generator
            if generator is not None
            else OllamaGenerator(
                model=generation_model_name,
                base_url=ollama_base_url,
                timeout=generation_timeout,
            )
        )

        vector_store = MemoryVectorStore()

        research_loader = ResearchLoader()

        batch_loader = BatchResearchLoader(
            loader=research_loader,
        )

        research_pipeline = ResearchPipeline(
            loader=batch_loader,
            chunker=ChunkSplitter(
                chunk_size=chunk_size,
            ),
        )

        research_indexer = ResearchIndexer(
            pipeline=research_pipeline,
            embedding_model=resolved_embedding_model,
            vector_store=vector_store,
        )

        retriever = Retriever(
            embedding_model=resolved_embedding_model,
            vector_store=vector_store,
        )

        rag_pipeline = RAGPipeline(
            retriever=retriever,
            context_builder=ContextBuilder(),
            prompt_builder=PromptBuilder(),
            generator=resolved_generator,
        )

        return ResearchRAGService(
            research_indexer=research_indexer,
            pipeline=rag_pipeline,
        )
