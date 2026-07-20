from hermes_agent.documents.document import Document


class MarkdownConverter:
    """Convert a Document into a Markdown-friendly Document."""

    def convert(self, document: Document) -> Document:
        content = document.content.strip()

        return Document(
            id=document.id,
            source=document.source,
            title=document.title,
            content=f"# {document.title}\n\n{content}",
            metadata=document.metadata.copy(),
        )
