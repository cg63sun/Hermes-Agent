from hermes_agent.crawler.url_normalizer import (
    URLNormalizer,
)


def test_normalize_removes_fragment() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/about#team",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_removes_utm_parameters() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/about"
        "?utm_source=google"
        "&utm_medium=cpc"
        "&page=2",
    )

    assert result == (
        "https://example.com/about?page=2"
    )


def test_normalize_removes_fbclid() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/about"
        "?fbclid=12345",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_removes_gclid() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/about"
        "?gclid=abcdef",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_removes_ref() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/about"
        "?ref=homepage",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_preserves_normal_query() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/search"
        "?keyword=hermes&page=2",
    )

    assert result == (
        "https://example.com/search"
        "?keyword=hermes&page=2"
    )


def test_normalize_sorts_query_parameters() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/search"
        "?page=2&keyword=hermes",
    )

    assert result == (
        "https://example.com/search"
        "?keyword=hermes&page=2"
    )


def test_normalize_removes_duplicate_slashes() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com//about///team/",
    )

    assert result == (
        "https://example.com/about/team"
    )


def test_normalize_removes_trailing_slash() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/about/",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_preserves_root_slash() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/",
    )

    assert result == (
        "https://example.com/"
    )


def test_normalize_lowercases_scheme_and_domain() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "HTTPS://EXAMPLE.COM/About",
    )

    assert result == (
        "https://example.com/About"
    )


def test_normalize_removes_default_https_port() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com:443/about",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_removes_default_http_port() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "http://example.com:80/about",
    )

    assert result == (
        "http://example.com/about"
    )


def test_normalize_preserves_custom_port() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "http://example.com:8080/about",
    )

    assert result == (
        "http://example.com:8080/about"
    )


def test_normalize_converts_relative_url() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "/about",
        base_url="https://example.com/service/",
    )

    assert result == (
        "https://example.com/about"
    )


def test_normalize_converts_relative_child_url() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "detail",
        base_url="https://example.com/service/",
    )

    assert result == (
        "https://example.com/service/detail"
    )


def test_normalize_empty_url() -> None:
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "   ",
    )

    assert result == ""


def test_is_same_url_ignores_tracking_parameters() -> None:
    normalizer = URLNormalizer()

    result = normalizer.is_same_url(
        "https://example.com/about",
        "https://example.com/about/"
        "?utm_source=google#team",
    )

    assert result is True


def test_is_same_url_detects_different_pages() -> None:
    normalizer = URLNormalizer()

    result = normalizer.is_same_url(
        "https://example.com/about",
        "https://example.com/contact",
    )

    assert result is False
