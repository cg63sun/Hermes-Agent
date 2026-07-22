import json

import pytest

from hermes_agent.generators.mock import MockGenerator
from hermes_agent.services.research_report import ResearchReport
from hermes_agent.services.site_plan_generator import SitePlanGenerator


def _response() -> str:
    return json.dumps(
        {
            "concept": "신뢰를 주는 지역 밀착형 홈페이지",
            "key_messages": [
                "빠른 상담",
                "맞춤형 서비스",
            ],
            "sections": [
                {
                    "name": "메인",
                    "purpose": "핵심 서비스 소개",
                    "headline": "사업에 꼭 맞는 홈페이지",
                    "content": "고객의 목표에 맞춰 제작합니다.",
                    "call_to_action": "무료 상담 신청",
                },
            ],
        },
        ensure_ascii=False,
    )


def _report() -> ResearchReport:
    return ResearchReport(
        urls=["https://example.com"],
        question="경쟁사의 장점을 분석하세요.",
        answer="빠른 상담과 맞춤형 서비스를 강조합니다.",
    )


def test_generate_site_plan() -> None:
    service = SitePlanGenerator(
        generator=MockGenerator(response=_response()),
    )

    plan = service.generate(
        _report(),
        business_name="여수넷",
        business_type="홈페이지 제작",
        target_audience="지역 소상공인",
        goal="상담 문의 증가",
    )

    assert plan.business_name == "여수넷"
    assert plan.concept == "신뢰를 주는 지역 밀착형 홈페이지"
    assert plan.key_messages == ["빠른 상담", "맞춤형 서비스"]
    assert plan.sections[0].name == "메인"
    assert plan.sections[0].call_to_action == "무료 상담 신청"
    assert plan.source_urls == ["https://example.com"]


def test_generate_accepts_json_code_block() -> None:
    response = f"```json\n{_response()}\n```"
    service = SitePlanGenerator(
        generator=MockGenerator(response=response),
    )

    plan = service.generate(
        _report(),
        business_name="여수넷",
        business_type="홈페이지 제작",
        target_audience="지역 소상공인",
        goal="상담 문의 증가",
    )

    assert plan.sections[0].headline == "사업에 꼭 맞는 홈페이지"


def test_generate_rejects_invalid_json() -> None:
    service = SitePlanGenerator(
        generator=MockGenerator(response="기획안입니다."),
    )

    with pytest.raises(
        ValueError,
        match="Generator response must be valid JSON",
    ):
        service.generate(
            _report(),
            business_name="여수넷",
            business_type="홈페이지 제작",
            target_audience="지역 소상공인",
            goal="상담 문의 증가",
        )
