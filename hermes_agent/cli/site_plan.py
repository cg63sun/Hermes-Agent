from __future__ import annotations

import argparse
from pathlib import Path

from hermes_agent.cli.research import run_research
from hermes_agent.generators.ollama import OllamaGenerator
from hermes_agent.services.research_report import ResearchReport
from hermes_agent.services.site_html_renderer import SiteHtmlRenderer
from hermes_agent.services.site_plan import SitePlan
from hermes_agent.services.site_plan_generator import SitePlanGenerator


DEFAULT_QUESTION = (
    "경쟁사 홈페이지의 주요 서비스, 강점, 핵심 메시지, "
    "페이지 구성과 차별화 요소를 분석하세요."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "여러 웹사이트를 조사하여 "
            "홈페이지 기획안을 자동 생성합니다."
        ),
    )

    parser.add_argument(
        "urls",
        nargs="+",
        help="조사할 경쟁사 웹사이트 URL",
    )
    parser.add_argument(
        "--business-name",
        required=True,
        help="홈페이지를 만들 상호",
    )
    parser.add_argument(
        "--business-type",
        required=True,
        help="사업 업종",
    )
    parser.add_argument(
        "--target-audience",
        required=True,
        help="핵심 고객",
    )
    parser.add_argument(
        "--goal",
        required=True,
        help="홈페이지 제작 목표",
    )
    parser.add_argument(
        "--question",
        default=DEFAULT_QUESTION,
        help="경쟁사 조사 질문",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="연구 답변에 사용할 검색 결과 수",
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
        help="Ollama 생성 모델",
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
        "--generation-timeout",
        type=float,
        default=300.0,
        help="Ollama 생성 요청 제한시간(초)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output/site-plan.md",
        help="기획안 Markdown 저장 경로",
    )
    parser.add_argument(
        "--json-output",
        help="기획안 JSON 저장 경로",
    )
    parser.add_argument(
        "--html-output",
        help="완성된 홈페이지 HTML 저장 경로",
    )
    parser.add_argument(
        "--site-output-dir",
        help="HTML, CSS, JavaScript를 분리한 홈페이지 저장 폴더",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="웹사이트 수집 실패 시 즉시 중단",
    )

    return parser


def run_site_plan(
    urls: list[str],
    *,
    business_name: str,
    business_type: str,
    target_audience: str,
    goal: str,
    question: str = DEFAULT_QUESTION,
    top_k: int = 5,
    chunk_size: int = 500,
    generation_model: str = "qwen3:8b",
    embedding_model: str = "nomic-embed-text",
    ollama_url: str = "http://127.0.0.1:11434",
    generation_timeout: float = 300.0,
    output: str | Path = "output/site-plan.md",
    json_output: str | Path | None = None,
    html_output: str | Path | None = None,
    site_output_dir: str | Path | None = None,
    continue_on_error: bool = True,
) -> SitePlan:
    answer = run_research(
        urls,
        question=question,
        top_k=top_k,
        chunk_size=chunk_size,
        generation_model=generation_model,
        embedding_model=embedding_model,
        ollama_url=ollama_url,
        generation_timeout=generation_timeout,
        continue_on_error=continue_on_error,
    )

    report = ResearchReport(
        urls=list(urls),
        question=question.strip(),
        answer=answer,
    )
    service = SitePlanGenerator(
        generator=OllamaGenerator(
            model=generation_model,
            base_url=ollama_url,
            timeout=generation_timeout,
            json_schema={
                "type": "object",
                "properties": {
                    "concept": {
                        "type": "string",
                    },
                    "key_messages": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                },
                                "purpose": {
                                    "type": "string",
                                },
                                "headline": {
                                    "type": "string",
                                },
                                "content": {
                                    "type": "string",
                                },
                                "call_to_action": {
                                    "type": "string",
                                },
                            },
                            "required": [
                                "name",
                                "purpose",
                                "headline",
                                "content",
                                "call_to_action",
                            ],
                        },
                    },
                },
                "required": [
                    "concept",
                    "key_messages",
                    "sections",
                ],
            },
        ),
    )
    plan = service.generate(
        report,
        business_name=business_name,
        business_type=business_type,
        target_audience=target_audience,
        goal=goal,
    )

    output_path = plan.save_markdown(output)

    print("=" * 60)
    print("홈페이지 기획안 생성 완료")
    print("=" * 60)
    print(f"상호        : {plan.business_name}")
    print(f"페이지 구성 : {len(plan.sections)}개")
    print(f"기획안 저장 : {output_path}")

    if json_output is not None:
        json_path = plan.save_json(json_output)
        print(f"JSON 저장   : {json_path}")

    if html_output is not None:
        html_path = SiteHtmlRenderer().save(plan, html_output)
        print(f"HTML 저장   : {html_path}")

    if site_output_dir is not None:
        site_paths = SiteHtmlRenderer().save_bundle(
            plan,
            site_output_dir,
        )
        print(f"사이트 저장 : {Path(site_output_dir)}")
        for site_path in site_paths:
            print(f"              {site_path}")

    print("=" * 60)
    return plan


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        run_site_plan(
            urls=args.urls,
            business_name=args.business_name,
            business_type=args.business_type,
            target_audience=args.target_audience,
            goal=args.goal,
            question=args.question,
            top_k=args.top_k,
            chunk_size=args.chunk_size,
            generation_model=args.model,
            embedding_model=args.embedding_model,
            ollama_url=args.ollama_url,
            generation_timeout=args.generation_timeout,
            output=args.output,
            json_output=args.json_output,
            html_output=args.html_output,
            site_output_dir=args.site_output_dir,
            continue_on_error=not args.stop_on_error,
        )
    except ValueError as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        parser.exit(
            status=130,
            message="\n기획안 생성이 사용자에 의해 중단되었습니다.\n",
        )
    except Exception as error:
        parser.exit(
            status=1,
            message=f"홈페이지 기획안 생성 실패: {error}\n",
        )


if __name__ == "__main__":
    main()
