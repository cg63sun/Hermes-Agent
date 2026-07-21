from hermes_agent.generators import MockGenerator


def test_mock_generator_returns_default_response() -> None:
    generator = MockGenerator()

    result = generator.generate("질문입니다.")

    assert result == "Mock response"


def test_mock_generator_returns_custom_response() -> None:
    generator = MockGenerator(
        response="Python은 프로그래밍 언어입니다.",
    )

    result = generator.generate("Python이란 무엇인가요?")

    assert result == "Python은 프로그래밍 언어입니다."
