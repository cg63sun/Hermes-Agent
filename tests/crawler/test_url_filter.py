from hermes_agent.crawler.url_filter import URLFilter


def test_url_filter_allows_normal_page() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/about",
    ) is True


def test_url_filter_blocks_image_file() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/images/photo.jpg",
    ) is False


def test_url_filter_blocks_javascript_file() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/assets/app.js",
    ) is False


def test_url_filter_blocks_pdf_file() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/files/catalog.pdf",
    ) is False


def test_url_filter_blocks_admin_path() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/admin/users",
    ) is False


def test_url_filter_blocks_wordpress_admin_path() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/wp-admin/edit.php",
    ) is False


def test_url_filter_blocks_login_page() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/login",
    ) is False


def test_url_filter_allows_query_string() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "https://example.com/products?page=2",
    ) is True


def test_url_filter_uses_custom_blocked_extension() -> None:
    url_filter = URLFilter(
        blocked_extensions={".html"},
        blocked_path_prefixes=set(),
    )

    assert url_filter.is_allowed(
        "https://example.com/index.html",
    ) is False

    assert url_filter.is_allowed(
        "https://example.com/about",
    ) is True


def test_url_filter_rejects_invalid_scheme() -> None:
    url_filter = URLFilter()

    assert url_filter.is_allowed(
        "ftp://example.com/file",
    ) is False
