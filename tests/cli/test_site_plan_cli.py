from __future__ import annotations

import json

from hermes_agent.cli import site_plan as site_plan_cli
from hermes_agent.services.site_plan import SitePlan, SiteSection


def _plan() -> SitePlan:
    return SitePlan(
        business_name="여수넷",
        business_type="홈페이지 제작",
        target_audience="지역 소상공인",
        goal="상담 문의 증가",
        concept="신뢰할 수 있는 AI 웹에이전시",
        key_messages=["맞춤형 홈페이지", "AI 챗봇 기본 탑재"],
        sections=[
            SiteSection(
                name="메인",
                purpose="핵심 서비스 소개",
                headline="홈페이지에 AI를 더합니다",
                content="홈페이지 제작과 AI 기능을 함께 제공합니다.",
                call_to_action="무료 상담 신청",
            ),
        ],
        source_urls=["https://example.com"],
    )


def test_site_plan_parser_reads_arguments() -> None:
    args = site_plan_cli.build_parser().parse_args(
        [
            "https://example.com",
            "--business-name",
            "여수넷",
            "--business-type",
            "홈페이지 제작",
            "--target-audience",
            "지역 소상공인",
            "--goal",
            "상담 문의 증가",
            "--json-output",
            "output/site-plan.json",
            "--html-output",
            "output/index.html",
        ],
    )

    assert args.urls == ["https://example.com"]
    assert args.business_name == "여수넷"
    assert args.model == "qwen3:8b"
    assert args.embedding_model == "nomic-embed-text"
    assert args.top_k == 5
    assert args.chunk_size == 500
    assert args.generation_timeout == 300.0
    assert args.json_output == "output/site-plan.json"
    assert args.html_output == "output/index.html"


def test_run_site_plan_saves_markdown_json_and_html(
    monkeypatch,
    tmp_path,
) -> None:
    plan = _plan()
    captured: dict[str, object] = {}

    def fake_run_research(urls, **kwargs):
        captured["urls"] = urls
        captured["research_options"] = kwargs
        return "경쟁사는 빠른 상담과 맞춤 서비스를 강조합니다."

    class FakeOllamaGenerator:
        def __init__(
            self,
            *,
            model: str,
            base_url: str,
            timeout: float,
        ) -> None:
            captured["model"] = model
            captured["base_url"] = base_url
            captured["generation_timeout"] = timeout

    class FakeSitePlanGenerator:
        def __init__(self, *, generator) -> None:
            captured["generator"] = generator

        def generate(self, report, **kwargs) -> SitePlan:
            captured["report"] = report
            captured["plan_options"] = kwargs
            return plan

    monkeypatch.setattr(site_plan_cli, "run_research", fake_run_research)
    monkeypatch.setattr(
        site_plan_cli,
        "OllamaGenerator",
        FakeOllamaGenerator,
    )
    monkeypatch.setattr(
        site_plan_cli,
        "SitePlanGenerator",
        FakeSitePlanGenerator,
    )

    markdown_path = tmp_path / "site-plan.md"
    json_path = tmp_path / "site-plan.json"
    html_path = tmp_path / "index.html"

    result = site_plan_cli.run_site_plan(
        ["https://example.com"],
        business_name="여수넷",
        business_type="홈페이지 제작",
        target_audience="지역 소상공인",
        goal="상담 문의 증가",
        output=markdown_path,
        json_output=json_path,
        html_output=html_path,
        generation_timeout=450.0,
    )

    assert result is plan
    assert captured["model"] == "qwen3:8b"
    assert captured["urls"] == ["https://example.com"]
    assert captured["generation_timeout"] == 450.0
    assert captured["research_options"]["generation_timeout"] == 450.0
    assert captured["report"].answer.startswith("경쟁사는")
    assert "# 여수넷 홈페이지 기획안" in markdown_path.read_text(
        encoding="utf-8",
    )
    assert json.loads(json_path.read_text(encoding="utf-8"))[
        "business_name"
    ] == "여수넷"

    saved_html = html_path.read_text(encoding="utf-8")
    assert "<!doctype html>" in saved_html.lower()
    assert "여수넷" in saved_html
    assert "https://example.com" not in saved_html
