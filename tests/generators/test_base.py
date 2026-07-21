import pytest

from hermes_agent.generators import BaseGenerator


class MockGenerator(BaseGenerator):
    def generate(self, prompt: str) -> str:
        return f"Generated: {prompt}"


def test_generator_generates_answer() -> None:
    generator = MockGenerator()

    result = generator.generate("Python이란 무엇인가요?")

    assert result == "Generated: Python이란 무엇인가요?"


def test_base_generator_cannot_be_created() -> None:
    with pytest.raises(TypeError):
        BaseGenerator()
