from hermes_agent.embeddings.mock import MockEmbeddingModel


def test_embed_single_text():
    model = MockEmbeddingModel()

    assert model.embed("ABC") == [65.0, 66.0, 67.0]


def test_embed_empty_text():
    model = MockEmbeddingModel()

    assert model.embed("") == []


def test_embed_batch():
    model = MockEmbeddingModel()

    result = model.embed_batch(["A", "BC"])

    assert result == [
        [65.0],
        [66.0, 67.0],
    ]
