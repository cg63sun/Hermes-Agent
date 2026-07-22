from hermes_agent.services import WebsiteRAGService


class MockWebsiteIndexer:
    def __init__(self) -> None:
        self.received_url: str | None = None

    def index(self, url: str) -> int:
        self.received_url = url
        return 3


class MockPipeline:
    def __init__(self) -> None:
        self.received_question: str | None = None
        self.received_top_k: int | None = None

    def answer(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:
        self.received_question = question
        self.received_top_k = top_k

        return "테스트 답변입니다."


def test_website_rag_service_indexes_website() -> None:
    website_indexer = MockWebsiteIndexer()

    service = WebsiteRAGService(
        website_indexer=website_indexer,
        pipeline=MockPipeline(),
    )

    indexed_count = service.index_website(
        "https://example.com",
    )

    assert indexed_count == 3
    assert website_indexer.received_url == (
        "https://example.com"
    )


def test_website_rag_service_answers_question() -> None:
    pipeline = MockPipeline()

    service = WebsiteRAGService(
        website_indexer=MockWebsiteIndexer(),
        pipeline=pipeline,
    )

    result = service.answer(
        question="이 회사의 서비스는 무엇인가요?",
        top_k=3,
    )

    assert result == "테스트 답변입니다."
    assert pipeline.received_question == (
        "이 회사의 서비스는 무엇인가요?"
    )
    assert pipeline.received_top_k == 3
