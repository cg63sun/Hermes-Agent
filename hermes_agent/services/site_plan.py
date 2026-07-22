from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SiteSection:
    """A single section in a website plan."""

    name: str
    purpose: str
    headline: str
    content: str
    call_to_action: str = ""


@dataclass(slots=True)
class SitePlan:
    """Structured website plan created from research results."""

    business_name: str
    business_type: str
    target_audience: str
    goal: str
    concept: str
    key_messages: list[str] = field(default_factory=list)
    sections: list[SiteSection] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(
        self,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
        )

    def save_json(
        self,
        file_path: str | Path,
    ) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    def to_markdown(self) -> str:
        lines = [
            f"# {self.business_name} 홈페이지 기획안",
            "",
            "## 기본 방향",
            "",
            f"- 업종: {self.business_type}",
            f"- 핵심 고객: {self.target_audience}",
            f"- 홈페이지 목표: {self.goal}",
            f"- 콘셉트: {self.concept}",
            "",
            "## 핵심 메시지",
            "",
        ]

        lines.extend(
            f"- {message}"
            for message in self.key_messages
        )

        lines.extend(["", "## 페이지 구성", ""])

        for index, section in enumerate(self.sections, start=1):
            lines.extend(
                [
                    f"### {index}. {section.name}",
                    "",
                    f"- 목적: {section.purpose}",
                    f"- 제목: {section.headline}",
                    f"- 내용: {section.content}",
                ],
            )

            if section.call_to_action:
                lines.append(
                    f"- 행동 유도: {section.call_to_action}",
                )

            lines.append("")

        lines.extend(["## 참고 사이트", ""])

        if self.source_urls:
            lines.extend(f"- {url}" for url in self.source_urls)
        else:
            lines.append("- 없음")

        lines.append("")
        return "\n".join(lines)

    def save_markdown(
        self,
        file_path: str | Path,
    ) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")
        return path
