from hermes_agent.rag.chunk import Chunk


class ContextBuilder:
    def build(
        self,
        chunks: list[Chunk],
        separator: str = "\n\n",
    ) -> str:
        contents = [
            chunk.content.strip()
            for chunk in chunks
            if chunk.content.strip()
        ]

        return separator.join(contents)
