from hermes_agent.embeddings import MockEmbeddingModel
from hermes_agent.generators import MockGenerator
from hermes_agent.services import (
    WebsiteRAGFactory,
    WebsiteRAGService,
)


def test_factory_creates_website_rag_service() -> None:
    service = WebsiteRAGFactory.create(
        embedding_model=MockEmbeddingModel(),
        generator=MockGenerator(
            response="테스트 답변입니다.",
        ),
        chunk_size=100,
    )

    assert isinstance(service, WebsiteRAGService)


def test_factory_service_can_answer_without_documents() -> None:
    service = WebsiteRAGFactory.create(
        embedding_model=MockEmbeddingModel(),
        generator=MockGenerator(
            response="문서가 없습니다.",
        ),
        chunk_size=100,
    )

    result = service.answer(
        question="테스트 질문",
    )

    assert result == "문서가 없습니다."
