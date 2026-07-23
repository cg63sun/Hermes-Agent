from hermes_agent.services.site_html_renderer import SiteHtmlRenderer
from hermes_agent.services.site_plan import SitePlan, SiteSection


def make_site_plan() -> SitePlan:
    return SitePlan(
        business_name="여수넷",
        business_type="홈페이지 제작 및 AI 챗봇 개발",
        target_audience="여수 지역 소상공인과 중소기업",
        goal="상담 문의 증가",
        concept="지역 사업자를 위한 AI 웹에이전시",
        key_messages=[
            "맞춤형 홈페이지 제작",
            "24시간 응대하는 AI 챗봇",
        ],
        sections=[
            SiteSection(
                name="홈페이지 제작",
                purpose="핵심 서비스 소개",
                headline="사업에 꼭 맞는 홈페이지",
                content="기획부터 제작과 운영까지 함께합니다.",
                call_to_action="제작 상담하기",
            ),
            SiteSection(
                name="AI 챗봇",
                purpose="AI 서비스 소개",
                headline="고객 질문에 24시간 답변",
                content="홈페이지 내용을 학습해 고객에게 답변합니다.",
                call_to_action="AI 챗봇 알아보기",
            ),
        ],
        source_urls=[
            "https://veryeasy.kr/price",
            "https://website.it.kr",
        ],
    )


def test_render_creates_complete_korean_html_document() -> None:
    html = SiteHtmlRenderer().render(make_site_plan())

    assert html.startswith("<!doctype html>")
    assert '<html lang="ko">' in html
    assert '<meta charset="utf-8">' in html
    assert 'name="viewport"' in html
    assert "<title>여수넷</title>" in html
    assert "지역 사업자를 위한 AI 웹에이전시" in html
    assert "맞춤형 홈페이지 제작" in html
    assert "24시간 응대하는 AI 챗봇" in html


def test_render_includes_every_section_and_call_to_action() -> None:
    html = SiteHtmlRenderer().render(make_site_plan())

    assert html.count('class="service-card"') == 2
    assert "사업에 꼭 맞는 홈페이지" in html
    assert "기획부터 제작과 운영까지 함께합니다." in html
    assert "제작 상담하기" in html
    assert "고객 질문에 24시간 답변" in html
    assert "AI 챗봇 알아보기" in html


def test_render_does_not_publish_competitor_source_urls() -> None:
    html = SiteHtmlRenderer().render(make_site_plan())

    assert "veryeasy.kr" not in html
    assert "website.it.kr" not in html


def test_render_escapes_plan_text() -> None:
    plan = make_site_plan()
    plan.business_name = '<script>alert("x")</script>'
    plan.sections[0].content = "<strong>안전한 내용</strong>"

    html = SiteHtmlRenderer().render(plan)

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<strong>안전한 내용</strong>" not in html
    assert "&lt;strong&gt;안전한 내용&lt;/strong&gt;" in html


def test_save_writes_utf8_html_file(tmp_path) -> None:
    output_path = tmp_path / "nested" / "index.html"
    renderer = SiteHtmlRenderer()

    result = renderer.save(make_site_plan(), output_path)

    assert result == output_path
    assert output_path.exists()
    saved_html = output_path.read_text(encoding="utf-8")
    assert saved_html == renderer.render(make_site_plan())
    assert "여수넷" in saved_html
