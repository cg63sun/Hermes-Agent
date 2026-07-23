from __future__ import annotations

from html import escape
from pathlib import Path

from .site_plan import SitePlan


class SiteHtmlRenderer:
    """Render a site plan as a complete, standalone HTML document."""

    def render(self, plan: SitePlan) -> str:
        business_name = escape(plan.business_name)
        business_type = escape(plan.business_type)
        target_audience = escape(plan.target_audience)
        goal = escape(plan.goal)
        concept = escape(plan.concept)

        key_messages = "\n".join(
            (
                '          <li class="message-item">'
                f"{escape(message)}</li>"
            )
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
      --ink: #172033;
      --muted: #5f6b7a;
      --surface: #ffffff;
      --soft: #f3f7ff;
      --line: #dbe5f3;
      --shadow: 0 18px 50px rgba(35, 61, 99, 0.12);
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      color: var(--ink);
      background: var(--surface);
      font-family:
        Pretendard, "Noto Sans KR", -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
      line-height: 1.7;
      word-break: keep-all;
    }}

    a {{
      color: inherit;
      text-decoration: none;
    }}

    .container {{
      width: min(1120px, calc(100% - 40px));
      margin: 0 auto;
    }}

    .site-header {{
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 1px solid rgba(219, 229, 243, 0.85);
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(14px);
    }}

    .header-inner {{
      display: flex;
      min-height: 72px;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}

    .brand {{
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.03em;
    }}

    .header-cta,
    .primary-cta,
    .card-cta {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      font-weight: 700;
      transition:
        transform 160ms ease,
        background 160ms ease;
    }}

    .header-cta {{
      padding: 10px 18px;
      color: #ffffff;
      background: var(--primary);
    }}

    .header-cta:hover,
    .primary-cta:hover,
    .card-cta:hover {{
      transform: translateY(-2px);
    }}

    .hero {{
      overflow: hidden;
      padding: 112px 0 96px;
      background:
        radial-gradient(circle at 85% 20%, #cfe0ff 0, transparent 32%),
        linear-gradient(145deg, #f7faff 0%, #eaf2ff 100%);
    }}

    .eyebrow {{
      margin: 0 0 14px;
      color: var(--primary);
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: 0.06em;
    }}

    h1 {{
      max-width: 850px;
      margin: 0;
      font-size: clamp(2.4rem, 6vw, 4.9rem);
      line-height: 1.12;
      letter-spacing: -0.055em;
    }}

    .hero-copy {{
      max-width: 700px;
      margin: 24px 0 0;
      color: var(--muted);
      font-size: clamp(1.05rem, 2vw, 1.3rem);
    }}

    .primary-cta {{
      margin-top: 34px;
      padding: 15px 26px;
      color: #ffffff;
      background: var(--primary);
      box-shadow: 0 12px 28px rgba(21, 94, 239, 0.28);
    }}

    .messages {{
      position: relative;
      z-index: 2;
      margin-top: -36px;
    }}

    .message-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin: 0;
      padding: 24px;
      list-style: none;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--surface);
      box-shadow: var(--shadow);
    }}

    .message-item {{
      position: relative;
      padding-left: 28px;
      font-weight: 700;
    }}

    .message-item::before {{
      position: absolute;
      left: 0;
      color: var(--primary);
      content: "✓";
    }}

    .services {{
      padding: 110px 0;
    }}

    .section-heading {{
      max-width: 700px;
      margin-bottom: 42px;
    }}

    .section-heading h2 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1.2;
      letter-spacing: -0.045em;
    }}

    .section-heading p {{
      margin: 14px 0 0;
      color: var(--muted);
    }}

    .service-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 24px;
    }}

    .service-card {{
      display: flex;
      min-height: 330px;
      flex-direction: column;
      padding: 34px;
      border: 1px solid var(--line);
      border-radius: 26px;
      background: var(--surface);
      box-shadow: 0 10px 35px rgba(35, 61, 99, 0.08);
    }}

    .card-number {{
      color: var(--primary);
      font-size: 0.9rem;
      font-weight: 800;
    }}

    .service-card h3 {{
      margin: 18px 0 10px;
      font-size: 1.65rem;
      line-height: 1.3;
      letter-spacing: -0.035em;
    }}

    .card-purpose {{
      margin: 0 0 20px;
      color: var(--primary-dark);
      font-weight: 700;
    }}

    .card-content {{
      margin: 0;
      color: var(--muted);
    }}

    .card-cta {{
      align-self: flex-start;
      margin-top: auto;
      padding: 11px 18px;
      border: 1px solid var(--primary);
      color: var(--primary);
    }}

    .closing {{
      padding: 82px 0;
      color: #ffffff;
      background: var(--ink);
      text-align: center;
    }}

    .closing h2 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.3rem);
      line-height: 1.25;
      letter-spacing: -0.045em;
    }}

    .closing p {{
      max-width: 700px;
      margin: 18px auto 0;
      color: #cbd5e1;
    }}

    footer {{
      padding: 28px 0;
      color: var(--muted);
      background: #f8fafc;
      text-align: center;
    }}

    @media (max-width: 760px) {{
      .container {{
        width: min(100% - 28px, 1120px);
      }}

      .header-inner {{
        min-height: 64px;
      }}

      .header-cta {{
        padding: 9px 14px;
        font-size: 0.9rem;
      }}

      .hero {{
        padding: 82px 0 76px;
      }}

      .services {{
        padding: 82px 0;
      }}

      .service-grid {{
        grid-template-columns: 1fr;
      }}

      .service-card {{
        min-height: 0;
        padding: 28px;
      }}

      .card-cta {{
        margin-top: 28px;
      }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="#top">{business_name}</a>
      <a class="header-cta" href="#services">서비스 보기</a>
    </div>
  </header>

  <main id="top">
    <section class="hero">
      <div class="container">
        <p class="eyebrow">{business_type}</p>
        <h1>{concept}</h1>
        <p class="hero-copy">
          {target_audience}를 위한 맞춤형 서비스로
          {goal}을 함께 만들어갑니다.
        </p>
        <a class="primary-cta" href="#services">자세히 알아보기</a>
      </div>
    </section>

    <section class="messages" aria-label="핵심 메시지">
      <div class="container">
        <ul class="message-list">
{key_messages}
        </ul>
      </div>
    </section>

    <section class="services" id="services">
      <div class="container">
        <div class="section-heading">
          <p class="eyebrow">OUR SERVICES</p>
          <h2>{business_name}이 제공하는 서비스</h2>
          <p>사업에 필요한 서비스를 이해하기 쉽게 안내합니다.</p>
        </div>
        <div class="service-grid">
{sections}
        </div>
      </div>
    </section>

    <section class="closing">
      <div class="container">
        <h2>좋은 홈페이지는<br>좋은 대화에서 시작됩니다.</h2>
        <p>{business_name}과 함께 사업에 맞는 방향을 찾아보세요.</p>
      </div>
    </section>
  </main>

  <footer>
    <div class="container">
      <small>&copy; {business_name}. All rights reserved.</small>
    </div>
  </footer>
</body>
</html>
"""

    def save(
        self,
        plan: SitePlan,
        file_path: str | Path,
    ) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(plan), encoding="utf-8")
        return path

    @staticmethod
    def _render_section(index: int, section: object) -> str:
        name = escape(str(getattr(section, "name")))
        purpose = escape(str(getattr(section, "purpose")))
        headline = escape(str(getattr(section, "headline")))
        content = escape(str(getattr(section, "content")))
        call_to_action = escape(
            str(getattr(section, "call_to_action")),
        )

        call_to_action_html = ""
        if call_to_action:
            call_to_action_html = (
                "\n"
                '            <a class="card-cta" href="#top">'
                f"{call_to_action}</a>"
            )

        return f"""          <article class="service-card">
            <span class="card-number">{index:02d} · {name}</span>
            <h3>{headline}</h3>
            <p class="card-purpose">{purpose}</p>
            <p class="card-content">{content}</p>{call_to_action_html}
          </article>"""
