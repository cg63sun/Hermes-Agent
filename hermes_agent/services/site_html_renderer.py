from __future__ import annotations

from html import escape
from pathlib import Path

from .site_plan import SitePlan


class SiteHtmlRenderer:
    """Render a site plan as a complete, standalone HTML document."""

    _STYLE_OPEN = "  <style>\n"
    _STYLE_CLOSE = "  </style>\n"
    _EXTERNAL_STYLESHEET = '  <link rel="stylesheet" href="assets/style.css">\n'
    _EXTERNAL_SCRIPT = '  <script src="assets/script.js" defer></script>\n'

    def render(self, plan: SitePlan) -> str:
        business_name = escape(plan.business_name)
        business_type = escape(plan.business_type)
        target_audience = escape(plan.target_audience)
        goal = escape(plan.goal)
        concept = escape(plan.concept)

        key_messages = "\n".join(
            f'          <li class="message-item">{escape(message)}</li>'
            for message in plan.key_messages
        )
        sections = "\n".join(
            self._render_section(index, section)
            for index, section in enumerate(plan.sections, start=1)
        )

        return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{concept}">
  <title>{business_name}</title>
  <style>
    :root {{
      color-scheme: light;
      --primary: #155eef;
      --primary-dark: #0b45bc;
      --accent: #5b8cff;
      --ink: #101828;
      --muted: #667085;
      --surface: #ffffff;
      --soft: #f4f7ff;
      --line: #dfe7f3;
      --shadow: 0 24px 70px rgba(35, 61, 99, 0.14);
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--surface);
      font-family: Pretendard, "Noto Sans KR", -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.7;
      word-break: keep-all;
    }}
    a {{ color: inherit; text-decoration: none; }}
    .container {{ width: min(1180px, calc(100% - 48px)); margin: 0 auto; }}

    .site-header {{
      position: sticky;
      top: 0;
      z-index: 20;
      border-bottom: 1px solid rgba(223, 231, 243, 0.8);
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(16px);
    }}
    .header-inner {{
      display: flex;
      min-height: 74px;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}
    .brand {{ font-size: 1.3rem; font-weight: 900; letter-spacing: -0.04em; }}
    .nav {{ display: flex; align-items: center; gap: 28px; }}
    .nav a {{ color: var(--muted); font-size: 0.94rem; font-weight: 700; }}
    .nav a:hover {{ color: var(--primary); }}
    .header-cta, .primary-cta, .secondary-cta, .card-cta {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      font-weight: 800;
      transition: transform 160ms ease, box-shadow 160ms ease;
    }}
    .header-cta {{
      padding: 10px 18px;
      color: #fff !important;
      background: var(--primary);
    }}
    .header-cta:hover, .primary-cta:hover, .secondary-cta:hover,
    .card-cta:hover {{ transform: translateY(-2px); }}

    .hero {{
      position: relative;
      overflow: hidden;
      padding: 104px 0 112px;
      background:
        radial-gradient(circle at 88% 16%, rgba(91, 140, 255, .3), transparent 28%),
        linear-gradient(145deg, #f8faff 0%, #eaf1ff 100%);
    }}
    .hero::before {{
      position: absolute;
      width: 420px;
      height: 420px;
      left: -180px;
      bottom: -260px;
      border-radius: 50%;
      background: rgba(21, 94, 239, .08);
      content: "";
    }}
    .hero-grid {{
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(380px, .85fr);
      align-items: center;
      gap: 72px;
    }}
    .eyebrow {{
      margin: 0 0 14px;
      color: var(--primary);
      font-size: .92rem;
      font-weight: 900;
      letter-spacing: .08em;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.8rem, 5.5vw, 5.2rem);
      line-height: 1.08;
      letter-spacing: -.06em;
    }}
    .hero-copy {{
      max-width: 680px;
      margin: 26px 0 0;
      color: var(--muted);
      font-size: clamp(1.05rem, 1.8vw, 1.28rem);
    }}
    .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 36px; }}
    .primary-cta {{
      padding: 15px 25px;
      color: #fff;
      background: var(--primary);
      box-shadow: 0 14px 30px rgba(21, 94, 239, .27);
    }}
    .secondary-cta {{
      padding: 14px 24px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, .72);
    }}
    .hero-visual {{
      position: relative;
      min-height: 430px;
      padding: 28px;
      border: 1px solid rgba(255, 255, 255, .8);
      border-radius: 36px;
      background: rgba(255, 255, 255, .66);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .browser-bar {{ display: flex; gap: 7px; padding-bottom: 20px; }}
    .browser-bar i {{ width: 9px; height: 9px; border-radius: 50%; background: #c9d4e7; }}
    .visual-panel {{
      padding: 26px;
      border-radius: 24px;
      color: #fff;
      background: linear-gradient(145deg, #0e2a5a, #155eef);
    }}
    .visual-label {{ margin: 0; color: #bed1ff; font-size: .8rem; font-weight: 800; }}
    .visual-title {{ margin: 12px 0 24px; font-size: 1.65rem; line-height: 1.35; }}
    .visual-bars {{ display: grid; gap: 11px; }}
    .visual-bars span {{
      display: block;
      height: 9px;
      border-radius: 999px;
      background: rgba(255, 255, 255, .34);
    }}
    .visual-bars span:nth-child(2) {{ width: 78%; }}
    .visual-bars span:nth-child(3) {{ width: 56%; }}
    .floating-card {{
      position: absolute;
      right: -28px;
      bottom: 38px;
      width: 220px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: #fff;
      box-shadow: 0 18px 45px rgba(35, 61, 99, .18);
    }}
    .floating-card strong {{ display: block; margin-bottom: 4px; font-size: 1.05rem; }}
    .floating-card span {{ color: var(--muted); font-size: .88rem; }}
    .status-dot {{
      display: inline-block;
      width: 9px;
      height: 9px;
      margin-right: 7px;
      border-radius: 50%;
      background: #12b76a;
    }}

    .messages {{ position: relative; z-index: 2; margin-top: -42px; }}
    .message-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin: 0;
      padding: 25px 28px;
      list-style: none;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    .message-item {{ position: relative; padding-left: 28px; font-weight: 800; }}
    .message-item::before {{ position: absolute; left: 0; color: var(--primary); content: "✓"; }}

    .services, .process, .ai-section {{ padding: 112px 0; }}
    .section-heading {{ max-width: 760px; margin-bottom: 46px; }}
    .section-heading h2 {{
      margin: 0;
      font-size: clamp(2.15rem, 4vw, 3.45rem);
      line-height: 1.18;
      letter-spacing: -.05em;
    }}
    .section-heading p:last-child {{ margin: 15px 0 0; color: var(--muted); }}
    .service-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 24px;
    }}
    .service-card {{
      display: flex;
      min-height: 350px;
      flex-direction: column;
      padding: 36px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--surface);
      box-shadow: 0 12px 38px rgba(35, 61, 99, .08);
      transition: transform 180ms ease, box-shadow 180ms ease;
    }}
    .service-card:hover {{
      transform: translateY(-5px);
      box-shadow: 0 22px 50px rgba(35, 61, 99, .13);
    }}
    .card-number {{ color: var(--primary); font-size: .88rem; font-weight: 900; }}
    .service-card h3 {{ margin: 18px 0 10px; font-size: 1.7rem; line-height: 1.3; letter-spacing: -.04em; }}
    .card-purpose {{ margin: 0 0 20px; color: var(--primary-dark); font-weight: 800; }}
    .card-content {{ margin: 0; color: var(--muted); }}
    .card-cta {{
      align-self: flex-start;
      margin-top: auto;
      padding: 10px 17px;
      border: 1px solid var(--primary);
      color: var(--primary);
    }}

    .process {{ background: var(--soft); }}
    .process-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }}
    .process-card {{
      padding: 26px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: #fff;
    }}
    .process-card span {{ color: var(--primary); font-weight: 900; }}
    .process-card h3 {{ margin: 13px 0 8px; font-size: 1.18rem; }}
    .process-card p {{ margin: 0; color: var(--muted); font-size: .94rem; }}

    .ai-box {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 56px;
      align-items: center;
      padding: 58px;
      border-radius: 34px;
      color: #fff;
      background: linear-gradient(135deg, #101828, #173b7a);
      box-shadow: var(--shadow);
    }}
    .ai-box h2 {{ margin: 0; font-size: clamp(2rem, 4vw, 3.35rem); line-height: 1.2; letter-spacing: -.05em; }}
    .ai-box p {{ margin: 18px 0 0; color: #cbd8ee; }}
    .chat-demo {{ padding: 22px; border-radius: 24px; background: #fff; color: var(--ink); }}
    .chat-head {{ padding-bottom: 15px; border-bottom: 1px solid var(--line); font-weight: 900; }}
    .bubble {{ max-width: 88%; margin-top: 14px; padding: 12px 15px; border-radius: 16px; font-size: .92rem; }}
    .bubble.question {{ margin-left: auto; background: var(--primary); color: #fff; border-bottom-right-radius: 5px; }}
    .bubble.answer {{ background: var(--soft); border-bottom-left-radius: 5px; }}

    .closing {{ padding: 92px 0; color: #fff; background: var(--primary); text-align: center; }}
    .closing h2 {{ margin: 0; font-size: clamp(2.15rem, 4vw, 3.5rem); line-height: 1.22; letter-spacing: -.05em; }}
    .closing p {{ max-width: 700px; margin: 18px auto 30px; color: #dce7ff; }}
    .closing .secondary-cta {{ color: var(--ink); background: #fff; border: 0; }}
    footer {{ padding: 28px 0; color: var(--muted); background: #f8fafc; text-align: center; }}

    @media (max-width: 900px) {{
      .nav a:not(.header-cta) {{ display: none; }}
      .hero-grid, .ai-box {{ grid-template-columns: 1fr; }}
      .hero-visual {{ min-height: 390px; }}
      .floating-card {{ right: 18px; }}
      .process-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 680px) {{
      .container {{ width: min(100% - 28px, 1180px); }}
      .header-inner {{ min-height: 64px; }}
      .header-cta {{ padding: 9px 14px; font-size: .88rem; }}
      .hero {{ padding: 72px 0 86px; }}
      .hero-grid {{ gap: 46px; }}
      .hero-visual {{ min-height: 350px; padding: 18px; }}
      .floating-card {{ right: 10px; bottom: 25px; width: 205px; }}
      .services, .process, .ai-section {{ padding: 82px 0; }}
      .service-grid, .process-grid {{ grid-template-columns: 1fr; }}
      .service-card {{ min-height: 0; padding: 28px; }}
      .card-cta {{ margin-top: 28px; }}
      .ai-box {{ padding: 34px 24px; gap: 34px; }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="#top">{business_name}</a>
      <nav class="nav" aria-label="주요 메뉴">
        <a href="#services">서비스</a>
        <a href="#process">제작 과정</a>
        <a href="#ai">AI 챗봇</a>
        <a class="header-cta" href="#contact">상담하기</a>
      </nav>
    </div>
  </header>

  <main id="top">
    <section class="hero">
      <div class="container hero-grid">
        <div>
          <p class="eyebrow">{business_type}</p>
          <h1>{concept}</h1>
          <p class="hero-copy">{target_audience}를 위한 맞춤형 서비스로 {goal}을 함께 만들어갑니다.</p>
          <div class="hero-actions">
            <a class="primary-cta" href="#services">서비스 알아보기</a>
            <a class="secondary-cta" href="#contact">무료 상담 시작하기</a>
          </div>
        </div>
        <div class="hero-visual" aria-label="홈페이지와 AI 서비스 예시">
          <div class="browser-bar"><i></i><i></i><i></i></div>
          <div class="visual-panel">
            <p class="visual-label">SMART BUSINESS WEBSITE</p>
            <h2 class="visual-title">홈페이지가 고객을 만나고<br>AI가 상담을 이어갑니다.</h2>
            <div class="visual-bars"><span></span><span></span><span></span></div>
          </div>
          <div class="floating-card">
            <strong><i class="status-dot"></i>AI 상담 운영 중</strong>
            <span>24시간 고객 질문에 자동 응답</span>
          </div>
        </div>
      </div>
    </section>

    <section class="messages" aria-label="핵심 메시지">
      <div class="container"><ul class="message-list">
{key_messages}
      </ul></div>
    </section>

    <section class="services" id="services">
      <div class="container">
        <div class="section-heading">
          <p class="eyebrow">OUR SERVICES</p>
          <h2>{business_name}이 제공하는 서비스</h2>
          <p>보기 좋은 화면을 넘어 실제 문의와 성장을 돕는 온라인 기반을 만듭니다.</p>
        </div>
        <div class="service-grid">
{sections}
        </div>
      </div>
    </section>

    <section class="process" id="process">
      <div class="container">
        <div class="section-heading">
          <p class="eyebrow">WORK PROCESS</p>
          <h2>복잡하지 않은 제작 과정</h2>
          <p>상담부터 오픈과 운영까지 필요한 과정을 순서대로 함께합니다.</p>
        </div>
        <div class="process-grid">
          <article class="process-card"><span>01</span><h3>상담과 목표 설정</h3><p>업종, 고객, 필요한 기능과 사업 목표를 확인합니다.</p></article>
          <article class="process-card"><span>02</span><h3>기획과 콘텐츠 구성</h3><p>메뉴 구조와 핵심 메시지를 정리하고 화면을 설계합니다.</p></article>
          <article class="process-card"><span>03</span><h3>디자인과 개발</h3><p>모바일에 최적화된 화면과 필요한 기능을 구현합니다.</p></article>
          <article class="process-card"><span>04</span><h3>검수와 운영 지원</h3><p>내용과 동작을 검수한 뒤 안정적인 운영을 지원합니다.</p></article>
        </div>
      </div>
    </section>

    <section class="ai-section" id="ai">
      <div class="container">
        <div class="ai-box">
          <div>
            <p class="eyebrow">AI CHATBOT</p>
            <h2>방문자가 궁금한 순간,<br>AI가 바로 답합니다.</h2>
            <p>홈페이지 내용과 업종별 자료를 기반으로 자주 묻는 질문에 답하고 상담과 문의로 자연스럽게 연결합니다.</p>
          </div>
          <div class="chat-demo" aria-label="AI 챗봇 대화 예시">
            <div class="chat-head"><i class="status-dot"></i>{business_name} AI 상담</div>
            <div class="bubble question">홈페이지 제작 기간은 얼마나 걸리나요?</div>
            <div class="bubble answer">필요한 페이지와 기능에 따라 달라집니다. 상담 후 일정과 견적을 자세히 안내해 드릴게요.</div>
          </div>
        </div>
      </div>
    </section>

    <section class="closing" id="contact">
      <div class="container">
        <h2>좋은 홈페이지는<br>좋은 대화에서 시작됩니다.</h2>
        <p>{business_name}과 함께 사업에 맞는 방향을 찾아보세요.</p>
        <a class="secondary-cta" href="#top">상담 준비하기</a>
      </div>
    </section>
  </main>

  <footer><div class="container">
    <small>&copy; {business_name}. All rights reserved.</small>
  </div></footer>
</body>
</html>
"""

    def save(self, plan: SitePlan, file_path: str | Path) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(plan), encoding="utf-8")
        return path

    def save_bundle(
        self,
        plan: SitePlan,
        output_dir: str | Path,
    ) -> tuple[Path, Path, Path]:
        """Save a deployable site with separate HTML, CSS, and JavaScript."""
        directory = Path(output_dir)
        assets_directory = directory / "assets"
        assets_directory.mkdir(parents=True, exist_ok=True)

        standalone_html = self.render(plan)
        css, bundled_html = self._extract_external_css(standalone_html)
        bundled_html = bundled_html.replace(
            "</head>\n",
            f"{self._EXTERNAL_SCRIPT}</head>\n",
            1,
        )

        html_path = directory / "index.html"
        css_path = assets_directory / "style.css"
        script_path = assets_directory / "script.js"

        html_path.write_text(bundled_html, encoding="utf-8")
        css_path.write_text(css, encoding="utf-8")
        script_path.write_text(self.render_script(), encoding="utf-8")
        return html_path, css_path, script_path

    @classmethod
    def _extract_external_css(cls, html: str) -> tuple[str, str]:
        style_start = html.index(cls._STYLE_OPEN)
        css_start = style_start + len(cls._STYLE_OPEN)
        style_end = html.index(cls._STYLE_CLOSE, css_start)

        css = html[css_start:style_end]
        css = "\n".join(
            line[4:] if line.startswith("    ") else line
            for line in css.splitlines()
        )
        if css:
            css += "\n"

        bundled_html = (
            html[:style_start]
            + cls._EXTERNAL_STYLESHEET
            + html[style_end + len(cls._STYLE_CLOSE) :]
        )
        return css, bundled_html

    @staticmethod
    def render_script() -> str:
        return """document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", (event) => {
    const target = document.querySelector(link.getAttribute("href"));

    if (target) {
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});
"""

    @staticmethod
    def _render_section(index: int, section: object) -> str:
        name = escape(str(getattr(section, "name")))
        purpose = escape(str(getattr(section, "purpose")))
        headline = escape(str(getattr(section, "headline")))
        content = escape(str(getattr(section, "content")))
        call_to_action = escape(str(getattr(section, "call_to_action")))

        call_to_action_html = ""
        if call_to_action:
            call_to_action_html = (
                "\n"
                '        <a class="card-cta" href="#contact">'
                f"{call_to_action}</a>"
            )

        return f"""      <article class="service-card">
        <span class="card-number">{index:02d} · {name}</span>
        <h3>{headline}</h3>
        <p class="card-purpose">{purpose}</p>
        <p class="card-content">{content}</p>{call_to_action_html}
      </article>"""
