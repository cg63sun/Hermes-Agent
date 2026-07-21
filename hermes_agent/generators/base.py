from abc import ABC, abstractmethod


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """프롬프트를 받아 답변을 생성합니다."""
        raise NotImplementedError
