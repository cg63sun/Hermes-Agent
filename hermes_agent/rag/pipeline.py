from hermes_agent.generators.base import BaseGenerator
from hermes_agent.rag.context_builder import ContextBuilder
from hermes_agent.rag.prompt_builder import PromptBuilder
from hermes_agent.retriever.retriever import Retriever


class RAGPipeline:
    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        prompt_builder: PromptBuilder,
        generator: BaseGenerator,
    ) -> None:
        self._retriever = retriever
        self._context_builder = context_builder
        self._prompt_builder = prompt_builder
        self._generator = generator

    def answer(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:
        chunks = self._retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        context = self._context_builder.build(chunks)

        prompt = self._prompt_builder.build(
            question=question,
            context=context,
        )

        return self._generator.generate(prompt)
