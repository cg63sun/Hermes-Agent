from hermes_agent.rag.chunk import Chunk
from hermes_agent.vectorstores.memory import MemoryVectorStore


def test_add_and_search():
    store = MemoryVectorStore()

    chunk1 = Chunk(
        id="1",
        document_id="doc",
        index=0,
        content="Apple",
    )

    chunk2 = Chunk(
        id="2",
        document_id="doc",
        index=1,
        content="Banana",
    )

    store.add(
        [chunk1, chunk2],
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ],
    )

    results = store.search(
        [1.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].content == "Apple"
    assert results[1].content == "Banana"
