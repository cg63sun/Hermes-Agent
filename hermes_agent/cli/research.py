from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from hermes_agent.services.research_factory import (
    ResearchRAGFactory,
)
from hermes_agent.services.research_report import (
    ResearchReport,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "여러 웹사이트를 수집하고 "
            "Ollama 기반으로 질문에 답합니다."
        ),
    )

    parser.add_argument(
        "urls",
        nargs="+",
        help="수집할 웹사이트 URL",
    )

    parser.add_argument(
        "--question",
        "-q",
        required=True,
        help="수집한 내용을 바탕으로 질문할 내용",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="답변 생성에 사용할 검색 결과 수",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="문서를 나눌 청크 크기",
    )

    parser.add_argument(
        "--model",
        default="qwen3:8b",
        help="Ollama 답변 생성 모델",
    )

    parser.add_argument(
        "--embedding-model",
        default="nomic-embed-text",
        help="Ollama 임베딩 모델",
    )

    parser.add_argument(
        "--ollama-url",
        default="http://127.0.0.1:11434",
        help="Ollama 서버 주소",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Markdown 보고서 저장 경로",
    )

    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="웹사이트 수집 실패 시 즉시 중단",
    )

    return parser


def validate_url(url: str) -> str:
    normalized_url = url.strip()
    parsed = urlparse(normalized_url)

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        raise ValueError(
            f"URL은 http:// 또는 https://로 "
            f"시작해야 합니다: {url}"
        )

    if not parsed.netloc:
        raise ValueError(
            f"올바른 도메인이 포함되지 않았습니다: {url}"
        )

    return normalized_url


def run_research(
    urls: list[str],
    *,
    question: str,
    top_k: int = 5,
    chunk_size: int = 500,
    generation_model: str = "qwen3:8b",
    embedding_model: str = "nomic-embed-text",
    ollama_url: str = "http://127.0.0.1:11434",
    generation_timeout: float = 300.0,
    output: str | Path | None = None,
    continue_on_error: bool = True,
) -> str:
    if not urls:
        raise ValueError(
            "하나 이상의 URL이 필요합니다."
        )

    validated_urls = [
        validate_url(url)
        for url in urls
    ]

    normalized_question = question.strip()

    if not normalized_question:
        raise ValueError(
            "질문을 입력해야 합니다."
        )

    if top_k < 1:
        raise ValueError(
            "top_k는 1 이상이어야 합니다."
        )

    if chunk_size < 1:
        raise ValueError(
            "chunk_size는 1 이상이어야 합니다."
        )

    service = ResearchRAGFactory.create(
        chunk_size=chunk_size,
        generation_model_name=generation_model,
        embedding_model_name=embedding_model,
        ollama_base_url=ollama_url,
        generation_timeout=generation_timeout,
    )

    print("=" * 60)
    print("웹사이트 조사 시작")
    print("=" * 60)

    for url in validated_urls:
        print(f"- {url}")

    result = service.index(
        validated_urls,
        continue_on_error=continue_on_error,
    )

    print("=" * 60)
    print("인덱싱 완료")
    print("=" * 60)
    print(f"문서 수     : {result.document_count}")
    print(f"청크 수     : {result.chunk_count}")
    print(f"저장 수     : {result.indexed_count}")
    print(f"실패 수     : {result.failure_count}")

    if result.indexed_count == 0:
        raise RuntimeError(
            "인덱싱된 내용이 없습니다."
        )

    failure_messages: list[str] = []

    if result.failures:
        print("-" * 60)
        print("수집 실패")

        for failure in result.failures:
            failure_message = (
                f"{failure.url}: {failure.error}"
            )

            failure_messages.append(
                failure_message,
            )

            print(f"- {failure_message}")

    print("=" * 60)
    print("질문")
    print("=" * 60)
    print(normalized_question)

    answer = service.answer(
        normalized_question,
        top_k=top_k,
    )

    print("=" * 60)
    print("답변")
    print("=" * 60)
    print(answer)
    print("=" * 60)

    if output is not None:
        report = ResearchReport(
            urls=validated_urls,
            question=normalized_question,
            answer=answer,
            document_count=result.document_count,
            chunk_count=result.chunk_count,
            indexed_count=result.indexed_count,
            failure_count=result.failure_count,
            failures=failure_messages,
        )

        output_path = report.save_markdown(output)

        print(f"보고서 저장 : {output_path}")
        print("=" * 60)

    return answer


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        run_research(
            urls=args.urls,
            question=args.question,
            top_k=args.top_k,
            chunk_size=args.chunk_size,
            generation_model=args.model,
            embedding_model=args.embedding_model,
            ollama_url=args.ollama_url,
            output=args.output,
            continue_on_error=not args.stop_on_error,
        )
    except ValueError as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        parser.exit(
            status=130,
            message="\n조사가 사용자에 의해 중단되었습니다.\n",
        )
    except Exception as error:
        parser.exit(
            status=1,
            message=f"웹사이트 조사 실패: {error}\n",
        )


if __name__ == "__main__":
    main()
