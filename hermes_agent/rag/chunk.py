from dataclasses import dataclass, field


@dataclass(slots=True)
class Chunk:
    """A chunk of a document for embedding."""

    id: str
    document_id: str
    index: int
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
