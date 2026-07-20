from unittest.mock import Mock, patch

from hermes_agent.embeddings.ollama import OllamaEmbeddingModel


def test_embed_returns_embedding():
    fake_response = Mock()
    fake_response.json.return_value = {
        "embedding": [0.1, 0.2, 0.3]
    }
    fake_response.raise_for_status.return_value = None

    with patch("httpx.post", return_value=fake_response) as mock_post:
        model = OllamaEmbeddingModel()

        embedding = model.embed("Hello")

        assert embedding == [0.1, 0.2, 0.3]

        mock_post.assert_called_once()
