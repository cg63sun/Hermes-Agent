from __future__ import annotations

import json
import re
from typing import Any

from hermes_agent.generators.base import BaseGenerator
from hermes_agent.services.research_report import ResearchReport
from hermes_agent.services.site_plan import SitePlan, SiteSection


class SitePlanGenerator:
    """Create a structured website plan from a research report."""

    def __init__(
        self,
        *,
        generator: BaseGenerator,
    ) -> None:
        self._generator = generator

    def generate(
        self,
        report: ResearchReport,
        *,
        business_name: str,
        business_type: str,
        target_audience: str,
        goal: str,
    ) -> SitePlan:
        business_name = self._required(
            business_name,
            "business_name",
        )
        business_type = self._required(
            business_type,
            "business_type",
        )
        target_audience = self._required(
            target_audience,
            "target_audience",
        )
        goal = self._required(goal, "goal")

        prompt = self._build_prompt(
            report=report,
            business_name=business_name,
            business_type=business_type,
            target_audience=target_audience,
            goal=goal,
        )

        for attempt in range(2):
            response = self._generator.generate(prompt)

            try:
                data = self._parse_response(response)
                return SitePlan(
                    business_name=business_name,
                    business_type=business_type,
                    target_audience=target_audience,
                    goal=goal,
                    concept=self._manual_review_value(
                        self._required_value(data, "concept"),
                    ),
                    key_messages=self._string_list(
                        data,
                        "key_messages",
                    ),
                    sections=self._sections(data),
                    source_urls=list(report.urls),
                )
            except ValueError as error:
                if attempt == 1:
                    raise

                prompt = self._build_retry_prompt(
                    original_prompt=prompt,
                    error=error,
                )

        raise RuntimeError("Site plan generation did not complete.")

    @staticmethod
    def _build_retry_prompt(
        *,
        original_prompt: str,
        error: ValueError,
    ) -> str:
        return (
            f"{original_prompt}\n\n"
            "[JSON 형식 오류 재생성 요청]\n"
            f"이전 응답 오류: {error}\n"
            "기획안 내용을 유지하되 JSON 전체를 처음부터 다시 출력하세요.\n"
            "concept, key_messages, sections를 반드시 포함하세요.\n"
            "sections의 모든 항목에는 name, purpose, headline, content, "
            "call_to_action을 반드시 포함하세요.\n"
            "설명이나 마크다운 코드 블록 없이 JSON 객체 하나만 출력하세요."
        )

    def _build_prompt(
        self,
        *,
        report: ResearchReport,
        business_name: str,
        business_type: str,
        target_audience: str,
        goal: str,
    ) -> str:
        return (
            "아래 경쟁사 연구 결과를 참고하여 홈페이지 기획안을 작성하세요.\n"
            "연구 내용을 그대로 복사하지 말고 공통 장점과 차별점을 반영하세요.\n"
            "경쟁사의 핵심 장점, 가격, 혜택, 제작 범위와 사후 관리 조건을 "
            "아래 사업의 홈페이지 초안에 적극적으로 반영하세요.\n"
            "가격, 수치, 기간, 무료·무상, 할인, 보장처럼 사업자가 직접 "
            "확인해야 하는 조건도 초안에서 삭제하지 마세요.\n"
            "이러한 조건은 최종 확정 전 직접 수정할 수 있도록 유지하세요.\n"
            "반드시 설명이나 마크다운 없이 JSON 객체 하나만 출력하세요.\n\n"
            "[사업 정보]\n"
            f"상호: {business_name}\n"
            f"업종: {business_type}\n"
            f"핵심 고객: {target_audience}\n"
            f"홈페이지 목표: {goal}\n\n"
            "[경쟁사 연구 결과]\n"
            f"{report.answer.strip()}\n\n"
            "[JSON 형식]\n"
            "{\n"
            '  "concept": "홈페이지 전체 콘셉트",\n'
            '  "key_messages": ["핵심 메시지"],\n'
            '  "sections": [\n'
            "    {\n"
            '      "name": "섹션 이름",\n'
            '      "purpose": "섹션 목적",\n'
            '      "headline": "대표 문구",\n'
            '      "content": "구체적인 내용",\n'
            '      "call_to_action": "행동 유도 문구"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    @staticmethod
    def _parse_response(response: str) -> dict[str, Any]:
        text = response.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Generator response must be valid JSON."
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "Generator response must be a JSON object."
            )

        return data

    @classmethod
    def _manual_review_value(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if value.startswith("[직접 수정 필요]"):
            return value

        text = value

        # Free consultations and estimates are ordinary calls to action.
        for allowed_phrase in (
            "무료 상담",
            "상담 무료",
            "무료 견적",
        ):
            text = text.replace(allowed_phrase, "상담")

        patterns = (
            r"\d+(?:[.,]\d+)?\s*(?:원|천원|만원|억원|%|퍼센트)",
            r"\d+\s*(?:일|주|개월|달|년)(?:간|동안|까지)?",
            r"무료|무상|할인|보장|일정\s*기간",
            r"(?:기본형|템플릿형|맞춤형).{0,30}(?:제공|선택|구성)",
        )

        if any(re.search(pattern, text) for pattern in patterns):
            return f"[직접 수정 필요] {value}"

        return value

    @classmethod
    def _sections(
        cls,
        data: dict[str, Any],
    ) -> list[SiteSection]:
        raw_sections = data.get("sections")

        if not isinstance(raw_sections, list) or not raw_sections:
            raise ValueError(
                "Generator response must include sections."
            )

        sections: list[SiteSection] = []

        for raw_section in raw_sections:
            if not isinstance(raw_section, dict):
                raise ValueError(
                    "Each section must be a JSON object."
                )

            sections.append(
                SiteSection(
                    name=cls._manual_review_value(
                        cls._required_value(raw_section, "name"),
                    ),
                    purpose=cls._manual_review_value(
                        cls._required_value(
                            raw_section,
                            "purpose",
                        ),
                    ),
                    headline=cls._manual_review_value(
                        cls._required_value(
                            raw_section,
                            "headline",
                        ),
                    ),
                    content=cls._manual_review_value(
                        cls._required_value(
                            raw_section,
                            "content",
                        ),
                    ),
                    call_to_action=cls._manual_review_value(
                        cls._optional_value(
                            raw_section,
                            "call_to_action",
                        ),
                    ),
                ),
            )

        return sections

    @classmethod
    def _string_list(
        cls,
        data: dict[str, Any],
        key: str,
    ) -> list[str]:
        values = data.get(key)

        if not isinstance(values, list) or not values:
            raise ValueError(
                f"Generator response must include {key}."
            )

        return [
            cls._manual_review_value(
                cls._required(str(value), key),
            )
            for value in values
        ]

    @classmethod
    def _required_value(
        cls,
        data: dict[str, Any],
        key: str,
    ) -> str:
        value = data.get(key)

        if not isinstance(value, str):
            raise ValueError(
                f"Generator response must include {key}."
            )

        return cls._required(value, key)

    @staticmethod
    def _optional_value(
        data: dict[str, Any],
        key: str,
    ) -> str:
        value = data.get(key, "")

        if not isinstance(value, str):
            raise ValueError(
                f"Generator response field {key} must be a string."
            )

        return value.strip()

    @staticmethod
    def _required(value: str, name: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(f"{name} must not be empty.")

        return value
