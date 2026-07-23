import json

import pytest

from hermes_agent.generators.base import BaseGenerator
from hermes_agent.generators.mock import MockGenerator
from hermes_agent.services.research_report import ResearchReport
from hermes_agent.services.site_plan_generator import SitePlanGenerator


class SequenceGenerator(BaseGenerator):
    def __init__(self, responses: list[str]) -> None:
        self._responses = iter(responses)
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return next(self._responses)


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


def test_generate_marks_unverified_terms_for_manual_review() -> None:
    response = json.dumps(
        {
            "concept": "지역 기업을 위한 홈페이지",
            "key_messages": ["무료 문의 시스템 제공"],
            "sections": [
                {
                    "name": "사후 관리",
                    "purpose": "지속적인 운영 지원",
                    "headline": "제작 후 1개월 무상 수정",
                    "content": "호스팅 오류를 무상으로 해결합니다.",
                    "call_to_action": "상담 신청",
                },
            ],
        },
        ensure_ascii=False,
    )
    generator = SequenceGenerator(responses=[response])
    service = SitePlanGenerator(generator=generator)

    plan = service.generate(
        _report(),
        business_name="여수넷",
        business_type="홈페이지 제작",
        target_audience="지역 소상공인",
        goal="상담 문의 증가",
    )

    assert plan.key_messages == [
        "[직접 수정 필요] 무료 문의 시스템 제공",
    ]
    assert (
        plan.sections[0].headline
        == "[직접 수정 필요] 제작 후 1개월 무상 수정"
    )
    assert (
        plan.sections[0].content
        == "[직접 수정 필요] 호스팅 오류를 무상으로 해결합니다."
    )
    assert plan.sections[0].call_to_action == "상담 신청"
    assert len(generator.prompts) == 1
