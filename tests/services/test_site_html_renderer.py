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


def test_save_bundle_writes_separate_site_files(tmp_path) -> None:
    output_dir = tmp_path / "site"
    renderer = SiteHtmlRenderer()

    html_path, css_path, script_path = renderer.save_bundle(
        make_site_plan(),
        output_dir,
    )

    assert html_path == output_dir / "index.html"
    assert css_path == output_dir / "assets" / "style.css"
    assert script_path == output_dir / "assets" / "script.js"

    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    script = script_path.read_text(encoding="utf-8")

    assert '<link rel="stylesheet" href="assets/style.css">' in html
    assert '<script src="assets/script.js" defer></script>' in html
    assert "<style>" not in html
    assert "여수넷" in html
    assert ":root {" in css
    assert ".service-card {" in css
    assert "scrollIntoView" in script


def test_save_bundle_does_not_change_standalone_rendering(tmp_path) -> None:
    renderer = SiteHtmlRenderer()
    original_html = renderer.render(make_site_plan())

    renderer.save_bundle(make_site_plan(), tmp_path / "site")

    assert renderer.render(make_site_plan()) == original_html
    assert "<style>" in original_html

def test_render_includes_extended_design_sections() -> None:
    html = SiteHtmlRenderer().render(make_site_plan())

    assert 'href="#services"' in html
    assert 'href="#process"' in html
    assert 'href="#ai"' in html
    assert 'href="#contact"' in html

    assert 'class="hero-visual"' in html
    assert "AI 상담 운영 중" in html

    assert '<section class="process" id="process">' in html
    assert html.count('class="process-card"') == 4
    assert "상담과 목표 설정" in html
    assert "기획과 콘텐츠 구성" in html
    assert "디자인과 개발" in html
    assert "검수와 운영 지원" in html

    assert '<section class="ai-section" id="ai">' in html
    assert 'class="chat-demo"' in html
    assert "홈페이지와 AI 챗봇을 한 번에 준비하세요." in html

    assert '<section class="closing" id="contact">' in html


def test_save_bundle_contains_extended_design_assets(tmp_path) -> None:
    output_dir = tmp_path / "site"
    renderer = SiteHtmlRenderer()

    _, css_path, script_path = renderer.save_bundle(
        make_site_plan(),
        output_dir,
    )

    css = css_path.read_text(encoding="utf-8")
    script = script_path.read_text(encoding="utf-8")

    assert ".hero-grid {" in css
    assert ".hero-visual {" in css
    assert ".process-grid {" in css
    assert ".ai-box {" in css
    assert ".chat-demo {" in css
    assert "@media (max-width: 760px)" in css

    assert 'document.querySelectorAll(\'a[href^="#"]\')' in script
    assert "scrollIntoView" in script
