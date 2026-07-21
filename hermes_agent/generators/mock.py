from hermes_agent.generators.base import BaseGenerator


class MockGenerator(BaseGenerator):
    def __init__(self, response: str = "Mock response") -> None:
        self._response = response

    def generate(self, prompt: str) -> str:
        return self._response
