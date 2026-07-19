from dataclasses import dataclass, field


@dataclass(slots=True)
class Document:
    """A normalized document ready for processing."""

    id: str
    source: str
    title: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
