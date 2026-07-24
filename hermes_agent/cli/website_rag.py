from __future__ import annotations

import argparse
import sys

import httpx

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
        default=5,
        help="검색할 관련 청크 수",
    )

    parser.add_argument(
        "--source",
        default=None,
        help="검색 대상을 제한할 출처 URL",
    )

    return parser


def run(
    url: str,
    question: str,
    generator_model: str,
    embedding_model: str,
    chunk_size: int,
    top_k: int,
    source: str | None = None,
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
        source=source,
    )

    return (
        f"색인된 청크 수: {indexed_count}\n\n"
        f"답변:\n{answer}"
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = run(
            url=args.url,
            question=args.question,
            generator_model=args.generator_model,
            embedding_model=args.embedding_model,
            chunk_size=args.chunk_size,
            top_k=args.top_k,
            source=args.source,
        )
    except httpx.ConnectError:
        print(
            "오류: 웹사이트 또는 Ollama 서버에 연결할 수 없습니다.",
            file=sys.stderr,
        )
        return 1
    except httpx.HTTPStatusError as exc:
        print(
            f"오류: HTTP 요청에 실패했습니다. "
            f"상태 코드: {exc.response.status_code}",
            file=sys.stderr,
        )
        return 1
    except KeyError as exc:
        print(
            f"오류: 응답 데이터에 필요한 값이 없습니다: {exc}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(
            f"오류: {exc}",
            file=sys.stderr,
        )
        return 1

    print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
