from hermes_agent.config import WebsiteRAGConfig


def test_config_has_default_values() -> None:
    config = WebsiteRAGConfig()

    assert config.generator_model == "qwen3:8b"
    assert config.embedding_model == "nomic-embed-text"
    assert config.ollama_base_url == (
        "http://127.0.0.1:11434"
    )
    assert config.chunk_size == 500
    assert config.top_k == 3
    assert config.timeout == 120.0


def test_config_accepts_custom_values() -> None:
    config = WebsiteRAGConfig(
        generator_model="custom-generator",
        embedding_model="custom-embedding",
        ollama_base_url="http://localhost:11434",
        chunk_size=300,
        top_k=5,
        timeout=60.0,
    )

    assert config.generator_model == "custom-generator"
    assert config.embedding_model == "custom-embedding"
    assert config.chunk_size == 300
    assert config.top_k == 5
    assert config.timeout == 60.0
