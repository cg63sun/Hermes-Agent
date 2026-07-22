from __future__ import annotations

import json
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

        response = self._generator.generate(
            self._build_prompt(
                report=report,
                business_name=business_name,
                business_type=business_type,
                target_audience=target_audience,
                goal=goal,
            ),
        )

        data = self._parse_response(response)

        return SitePlan(
            business_name=business_name,
            business_type=business_type,
            target_audience=target_audience,
            goal=goal,
            concept=self._required_value(data, "concept"),
            key_messages=self._string_list(
                data,
                "key_messages",
            ),
            sections=self._sections(data),
            source_urls=list(report.urls),
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
                    name=cls._required_value(raw_section, "name"),
                    purpose=cls._required_value(
                        raw_section,
                        "purpose",
                    ),
                    headline=cls._required_value(
                        raw_section,
                        "headline",
                    ),
                    content=cls._required_value(
                        raw_section,
                        "content",
                    ),
                    call_to_action=cls._optional_value(
                        raw_section,
                        "call_to_action",
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
            cls._required(str(value), key)
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
