from hermes_agent.embeddings.base import EmbeddingModel
from hermes_agent.rag.chunk import Chunk
from hermes_agent.vectorstores import MemoryVectorStore


class ChunkIndexer:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: MemoryVectorStore,
    ) -> None:
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    def index(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0

        embeddings = [
            self._embedding_model.embed(chunk.content)
            for chunk in chunks
        ]

        self._vector_store.add(
            chunks=chunks,
            embeddings=embeddings,
        )

        return len(chunks)
