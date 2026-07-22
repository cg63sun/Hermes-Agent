import json

from hermes_agent.services.site_plan import SitePlan, SiteSection


def make_site_plan() -> SitePlan:
    return SitePlan(
        business_name="여수넷",
        business_type="홈페이지 제작업체",
        target_audience="홈페이지가 필요한 소상공인",
        goal="상담 문의 확보",
        concept="신뢰할 수 있는 AI 웹에이전시",
        key_messages=[
            "맞춤형 홈페이지 제작",
            "AI 챗봇 기본 탑재",
        ],
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


def test_site_plan_to_dict_and_json() -> None:
    plan = make_site_plan()

    result = plan.to_dict()
    json_result = json.loads(plan.to_json())

    assert result["business_name"] == "여수넷"
    assert result["key_messages"] == [
        "맞춤형 홈페이지 제작",
        "AI 챗봇 기본 탑재",
    ]
    assert result["sections"][0]["name"] == "메인"
    assert json_result == result


def test_site_plan_to_markdown() -> None:
    markdown = make_site_plan().to_markdown()

    assert "# 여수넷 홈페이지 기획안" in markdown
    assert "- 업종: 홈페이지 제작업체" in markdown
    assert "- AI 챗봇 기본 탑재" in markdown
    assert "### 1. 메인" in markdown
    assert "- 행동 유도: 무료 상담 신청" in markdown
    assert "- https://example.com" in markdown


def test_site_plan_save_files(tmp_path) -> None:
    plan = make_site_plan()
    json_path = tmp_path / "nested" / "site-plan.json"
    markdown_path = tmp_path / "nested" / "site-plan.md"

    assert plan.save_json(json_path) == json_path
    assert plan.save_markdown(markdown_path) == markdown_path
    assert json.loads(json_path.read_text(encoding="utf-8"))[
        "business_name"
    ] == "여수넷"
    assert "# 여수넷 홈페이지 기획안" in markdown_path.read_text(
        encoding="utf-8",
    )
