from hermes_agent.embeddings import OllamaEmbeddingModel
from hermes_agent.generators import OllamaGenerator
from hermes_agent.services import WebsiteRAGFactory


def main() -> None:
    embedding_model = OllamaEmbeddingModel(
        model="nomic-embed-text",
    )

    generator = OllamaGenerator(
        model="qwen3:8b",
    )

    service = WebsiteRAGFactory.create(
        embedding_model=embedding_model,
        generator=generator,
        chunk_size=500,
    )

    indexed_count = service.index_website(
        "https://example.com",
    )

    print(f"색인된 청크 수: {indexed_count}")

    answer = service.answer(
        question="이 웹사이트는 어떤 내용을 설명하나요?",
        top_k=3,
    )

    print()
    print("답변:")
    print(answer)


if __name__ == "__main__":
    main()
