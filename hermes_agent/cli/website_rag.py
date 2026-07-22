from __future__ import annotations

import argparse

from hermes_agent.embeddings import OllamaEmbeddingModel
from hermes_agent.generators import OllamaGenerator
from hermes_agent.services import WebsiteRAGFactory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="웹사이트를 색인하고 질문합니다.",
    )

    parser.add_argument(
        "--url",
        required=True,
        help="색인할 웹사이트 주소",
    )

    parser.add_argument(
        "--question",
        required=True,
        help="웹사이트 내용에 대한 질문",
    )

    parser.add_argument(
        "--generator-model",
        default="qwen3:8b",
        help="답변 생성에 사용할 Ollama 모델",
    )

    parser.add_argument(
        "--embedding-model",
        default="nomic-embed-text",
        help="임베딩에 사용할 Ollama 모델",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="문서 청크 크기",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="검색할 청크 개수",
    )

    return parser


def run(
    url: str,
    question: str,
    generator_model: str,
    embedding_model: str,
    chunk_size: int,
    top_k: int,
) -> str:
    service = WebsiteRAGFactory.create(
        embedding_model=OllamaEmbeddingModel(
            model=embedding_model,
        ),
        generator=OllamaGenerator(
            model=generator_model,
        ),
        chunk_size=chunk_size,
    )

    indexed_count = service.index_website(url)

    answer = service.answer(
        question=question,
        top_k=top_k,
    )

    return (
        f"색인된 청크 수: {indexed_count}\n\n"
        f"답변:\n{answer}"
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    result = run(
        url=args.url,
        question=args.question,
        generator_model=args.generator_model,
        embedding_model=args.embedding_model,
        chunk_size=args.chunk_size,
        top_k=args.top_k,
    )

    print(result)


if __name__ == "__main__":
    main()
