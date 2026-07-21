from hermes_agent.rag.chunk import Chunk
from hermes_agent.rag.context_builder import ContextBuilder


def test_build_context_from_chunks() -> None:
    chunks = [
        Chunk(
            id="chunk-1",
            document_id="doc-1",
            index=0,
            content="Python은 프로그래밍 언어입니다.",
        ),
        Chunk(
            id="chunk-2",
            document_id="doc-1",
            index=1,
            content="Python은 문법이 간결합니다.",
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(chunks)

    assert context == (
        "Python은 프로그래밍 언어입니다.\n\n"
        "Python은 문법이 간결합니다."
    )


def test_build_context_ignores_empty_chunks() -> None:
    chunks = [
        Chunk(
            id="chunk-1",
            document_id="doc-1",
            index=0,
            content="첫 번째 내용",
        ),
        Chunk(
            id="chunk-2",
            document_id="doc-1",
            index=1,
            content="   ",
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(chunks)

    assert context == "첫 번째 내용"


def test_build_empty_context() -> None:
    builder = ContextBuilder()

    context = builder.build([])

    assert context == ""
