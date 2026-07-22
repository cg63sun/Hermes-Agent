from __future__ import annotations

import hashlib

import pytest

from hermes_agent.crawler.auto_crawler import (
    AutoCrawlResult,
)
from hermes_agent.documents.auto_converter import (
    AutoDocumentConverter,
)


def create_result(
    *,
    title: str = "Hermes Agent",
    url: str = "https://example.com/page",
    text: str = "Hermes Agent 테스트 본문입니다.",
) -> AutoCrawlResult:
    return AutoCrawlResult(
        title=title,
        url=url,
        html="<html></html>",
        text=text,
        source="web",
        links=[
            "https://example.com/about",
        ],
        images=[
            "https://example.com/image.jpg",
        ],
        meta_description="테스트 설명",
        canonical_url=(
            "https://example.com/page"
        ),
        language="ko",
    )


def test_auto_converter_creates_document() -> None:
    converter = AutoDocumentConverter()

    result = create_result()

    document = converter.convert(
        result,
    )

    assert document.title == "Hermes Agent"

    assert document.source == (
        "https://example.com/page"
    )

    assert document.content == (
        "Hermes Agent 테스트 본문입니다."
    )


def test_auto_converter_creates_stable_id() -> None:
    converter = AutoDocumentConverter()

    result = create_result()

    document = converter.convert(
        result,
    )

    expected_id = hashlib.sha256(
        "https://example.com/page".encode(
            "utf-8",
        ),
    ).hexdigest()

    assert document.id == expected_id


def test_auto_converter_same_url_has_same_id() -> None:
    converter = AutoDocumentConverter()

    first_document = converter.convert(
        create_result(
            title="첫 번째 제목",
        ),
    )

    second_document = converter.convert(
        create_result(
            title="두 번째 제목",
        ),
    )

    assert (
        first_document.id
        == second_document.id
    )


def test_auto_converter_different_urls_have_different_ids() -> None:
    converter = AutoDocumentConverter()

    first_document = converter.convert(
        create_result(
            url="https://example.com/one",
        ),
    )

    second_document = converter.convert(
        create_result(
            url="https://example.com/two",
        ),
    )

    assert (
        first_document.id
        != second_document.id
    )


def test_auto_converter_uses_url_when_title_is_empty() -> None:
    converter = AutoDocumentConverter()

    document = converter.convert(
        create_result(
            title="   ",
        ),
    )

    assert document.title == (
        "https://example.com/page"
    )


def test_auto_converter_strips_values() -> None:
    converter = AutoDocumentConverter()

    document = converter.convert(
        create_result(
            title="  Hermes Agent  ",
            url="  https://example.com/page  ",
            text="  테스트 본문  ",
        ),
    )

    assert document.title == "Hermes Agent"

    assert document.source == (
        "https://example.com/page"
    )

    assert document.content == "테스트 본문"


def test_auto_converter_allows_empty_content() -> None:
    converter = AutoDocumentConverter()

    document = converter.convert(
        create_result(
            text="   ",
        ),
    )

    assert document.content == ""


def test_auto_converter_rejects_empty_url() -> None:
    converter = AutoDocumentConverter()

    with pytest.raises(
        ValueError,
        match="URL",
    ):
        converter.convert(
            create_result(
                url="   ",
            ),
        )
