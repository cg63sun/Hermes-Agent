from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ResearchReport:
    urls: list[str] = field(default_factory=list)
    question: str = ""
    answer: str = ""
    document_count: int = 0
    chunk_count: int = 0
    indexed_count: int = 0
    failure_count: int = 0
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "urls": list(self.urls),
            "question": self.question,
            "answer": self.answer,
            "summary": {
                "document_count": self.document_count,
                "chunk_count": self.chunk_count,
                "indexed_count": self.indexed_count,
                "failure_count": self.failure_count,
            },
            "failures": list(self.failures),
        }

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
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Path:
        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_json(
                indent=indent,
                ensure_ascii=ensure_ascii,
            ),
            encoding="utf-8",
        )

        return path

    def to_markdown(self) -> str:
        lines: list[str] = [
            "# Hermes Research Report",
            "",
            "## 대상 사이트",
            "",
        ]

        if self.urls:
            for url in self.urls:
                lines.append(f"- {url}")
        else:
            lines.append("- 없음")

        lines.extend(
            [
                "",
                "## 질문",
                "",
                self.question or "질문 없음",
                "",
                "## 답변",
                "",
                self.answer or "답변 없음",
                "",
                "## 통계",
                "",
                f"- Documents: {self.document_count}",
                f"- Chunks: {self.chunk_count}",
                f"- Indexed: {self.indexed_count}",
                f"- Failures: {self.failure_count}",
            ],
        )

        if self.failures:
            lines.extend(
                [
                    "",
                    "## 실패 목록",
                    "",
                ],
            )

            for failure in self.failures:
                lines.append(f"- {failure}")

        lines.append("")

        return "\n".join(lines)

    def save_markdown(
        self,
        file_path: str | Path,
    ) -> Path:
        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_markdown(),
            encoding="utf-8",
        )

        return path
