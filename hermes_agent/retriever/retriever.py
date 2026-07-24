from hermes_agent.embeddings.base import EmbeddingModel
from hermes_agent.rag.chunk import Chunk
from hermes_agent.vectorstores.base import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        source: str | None = None,
    ) -> list[Chunk]:
        embedding = self._embedding_model.embed(query)

        return self._vector_store.search(
            embedding,
            top_k,
            source=source,
        )