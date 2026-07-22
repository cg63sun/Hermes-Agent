from collections.abc import Generator

import pytest

from hermes_agent.browser.browser_client import (
    BrowserClient,
)
from hermes_agent.browser.extractor import Extractor
from hermes_agent.browser.page_client import (
    PageClient,
)


TEST_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">

    <base href="https://example.com/test">

    <title>Hermes 테스트 페이지</title>

    <meta
        name="description"
        content="Hermes Agent 브라우저 추출 테스트"
    >

    <link
        rel="canonical"
        href="/canonical-page"
    >
</head>

<body>
    <h1>메인 제목</h1>

    <h2>첫 번째 소제목</h2>
    <h2>두 번째 소제목</h2>

    <p>
        Hermes Agent 테스트 본문입니다.
    </p>

    <a href="/about">
        About
    </a>

    <a href="https://example.org/contact">
        Contact
    </a>

    <a href="/about">
        About duplicate
    </a>

    <a href="mailto:test@example.com">
        Email
    </a>

    <a href="javascript:void(0)">
        JavaScript
    </a>

    <img
        src="/images/logo.png"
        alt="Logo"
    >

    <img
        src="https://cdn.example.com/banner.jpg"
        alt="Banner"
    >

    <img
        src="/images/logo.png"
        alt="Logo duplicate"
    >

    <img
        src="data:image/png;base64,abc"
        alt="Inline image"
    >
</body>
</html>
"""


@pytest.fixture
def extractor() -> Generator[
    Extractor,
    None,
    None,
]:
    browser_client = BrowserClient(
        headless=True,
    )

    page_client: PageClient | None = None

    try:
        browser = browser_client.start()

        page_client = PageClient(
            browser,
        )

        page = page_client.open()

        page.set_content(
            TEST_HTML,
            wait_until="domcontentloaded",
        )

        yield Extractor(
            page,
        )

    finally:
        if page_client is not None:
            page_client.close()

        browser_client.close()


def test_extractor_title(
    extractor: Extractor,
) -> None:
    assert extractor.title() == (
        "Hermes 테스트 페이지"
    )


def test_extractor_html(
    extractor: Extractor,
) -> None:
    html = extractor.html()

    assert "<html" in html
    assert "메인 제목" in html

    assert (
        "Hermes 테스트 페이지"
        in html
    )


def test_extractor_text(
    extractor: Extractor,
) -> None:
    text = extractor.text()

    assert "메인 제목" in text

    assert (
        "Hermes Agent 테스트 본문입니다."
        in text
    )

    assert "<p>" not in text


def test_extractor_absolute_links(
    extractor: Extractor,
) -> None:
    assert extractor.links() == [
        "https://example.com/about",
        "https://example.org/contact",
    ]


def test_extractor_relative_links(
    extractor: Extractor,
) -> None:
    assert extractor.links(
        absolute=False,
    ) == [
        "/about",
        "https://example.org/contact",
    ]


def test_extractor_filters_unsupported_links(
    extractor: Extractor,
) -> None:
    links = extractor.links()

    assert all(
        not link.startswith(
            "mailto:",
        )
        for link in links
    )

    assert all(
        not link.startswith(
            "javascript:",
        )
        for link in links
    )


def test_extractor_images(
    extractor: Extractor,
) -> None:
    assert extractor.images() == [
        "https://example.com/images/logo.png",
        "https://cdn.example.com/banner.jpg",
    ]


def test_extractor_relative_images(
    extractor: Extractor,
) -> None:
    assert extractor.images(
        absolute=False,
    ) == [
        "/images/logo.png",
        "https://cdn.example.com/banner.jpg",
    ]


def test_extractor_meta_description(
    extractor: Extractor,
) -> None:
    assert extractor.meta_description() == (
        "Hermes Agent 브라우저 추출 테스트"
    )


def test_extractor_canonical_url(
    extractor: Extractor,
) -> None:
    assert extractor.canonical_url() == (
        "https://example.com/canonical-page"
    )


def test_extractor_headings(
    extractor: Extractor,
) -> None:
    headings = extractor.headings()

    assert headings["h1"] == [
        "메인 제목",
    ]

    assert headings["h2"] == [
        "첫 번째 소제목",
        "두 번째 소제목",
    ]

    assert headings["h3"] == []
    assert headings["h4"] == []
    assert headings["h5"] == []
    assert headings["h6"] == []


def test_extractor_language(
    extractor: Extractor,
) -> None:
    assert extractor.language() == "ko"
