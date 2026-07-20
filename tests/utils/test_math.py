from hermes_agent.utils.math import cosine_similarity


def test_same_vector():
    assert cosine_similarity([1, 0], [1, 0]) == 1.0


def test_orthogonal_vector():
    assert cosine_similarity([1, 0], [0, 1]) == 0.0


def test_zero_vector():
    assert cosine_similarity([0, 0], [1, 1]) == 0.0
