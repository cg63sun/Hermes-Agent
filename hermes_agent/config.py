from dataclasses import dataclass


@dataclass(frozen=True)
class WebsiteRAGConfig:
    generator_model: str = "qwen3:8b"
    embedding_model: str = "nomic-embed-text"
    ollama_base_url: str = "http://127.0.0.1:11434"
    chunk_size: int = 500
    top_k: int = 3
    timeout: float = 120.0
