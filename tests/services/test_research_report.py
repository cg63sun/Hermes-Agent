import json

from hermes_agent.services.research_report import ResearchReport


def test_research_report_to_dict() -> None:
    report = ResearchReport(
        urls=["https://example.com"],
        question="이 사이트는 무엇인가요?",
        answer="예제 사이트입니다.",
        document_count=1,
        chunk_count=3,
        indexed_count=3,
        failure_count=0,
        failures=[],
    )

    result = report.to_dict()

    assert result["urls"] == ["https://example.com"]
    assert result["question"] == "이 사이트는 무엇인가요?"
    assert result["answer"] == "예제 사이트입니다."
    assert result["summary"]["document_count"] == 1
    assert result["summary"]["chunk_count"] == 3
    assert result["summary"]["indexed_count"] == 3
    assert result["summary"]["failure_count"] == 0
    assert result["failures"] == []


def test_research_report_to_json() -> None:
    report = ResearchReport(
        urls=["https://example.com"],
        question="질문",
        answer="답변",
    )

    data = json.loads(report.to_json())

    assert data["question"] == "질문"
    assert data["answer"] == "답변"


def test_research_report_save_json(tmp_path) -> None:
    report = ResearchReport(
        urls=["https://example.com"],
        question="질문",
        answer="답변",
        document_count=1,
        chunk_count=2,
        indexed_count=2,
    )

    output_path = tmp_path / "research-report.json"
    saved_path = report.save_json(output_path)

    assert saved_path == output_path
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["urls"] == ["https://example.com"]
    assert data["summary"]["document_count"] == 1
    assert data["summary"]["chunk_count"] == 2
    assert data["summary"]["indexed_count"] == 2
