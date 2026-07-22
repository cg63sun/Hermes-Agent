from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Page


class Extractor:
    def __init__(
        self,
        page: Page,
    ) -> None:
        self._page = page

    def title(self) -> str:
        return self._page.title().strip()

    def html(self) -> str:
        return self._page.content()

    def text(self) -> str:
        body = self._page.locator(
            "body",
        )

        if body.count() == 0:
            return ""

        try:
            content = body.inner_text()
        except Exception:
            return ""

        return content.strip()

    def links(
        self,
        *,
        absolute: bool = True,
    ) -> list[str]:
        hrefs = self._page.locator(
            "a[href]",
        ).evaluate_all(
            """
            elements => elements.map(
                element => element.getAttribute("href")
            )
            """,
        )

        links: list[str] = []

        for href in hrefs:
            if not isinstance(
                href,
                str,
            ):
                continue

            normalized_href = href.strip()

            if not normalized_href:
                continue

            if self._is_unsupported_url(
                normalized_href,
            ):
                continue

            if absolute:
                normalized_href = urljoin(
                    self._base_url(),
                    normalized_href,
                )

            links.append(
                normalized_href,
            )

        return self._remove_duplicates(
            links,
        )

    def images(
        self,
        *,
        absolute: bool = True,
    ) -> list[str]:
        sources = self._page.locator(
            "img",
        ).evaluate_all(
            """
            elements => elements.map(
                element => ({
                    src:
                        element.getAttribute("src")
                        || element.getAttribute("data-src")
                        || "",
                    currentSrc:
                        element.currentSrc
                        || ""
                })
            )
            """,
        )

        images: list[str] = []

        for source_data in sources:
            if not isinstance(
                source_data,
                dict,
            ):
                continue

            if absolute:
                source = (
                    source_data.get(
                        "currentSrc",
                    )
                    or source_data.get(
                        "src",
                    )
                    or ""
                )
            else:
                source = (
                    source_data.get(
                        "src",
                    )
                    or ""
                )

            if not isinstance(
                source,
                str,
            ):
                continue

            normalized_source = source.strip()

            if not normalized_source:
                continue

            if normalized_source.lower().startswith(
                "data:",
            ):
                continue

            if absolute:
                normalized_source = urljoin(
                    self._base_url(),
                    normalized_source,
                )

            images.append(
                normalized_source,
            )

        return self._remove_duplicates(
            images,
        )

    def meta_description(self) -> str:
        locator = self._page.locator(
            'meta[name="description"]',
        )

        if locator.count() == 0:
            return ""

        content = locator.first.get_attribute(
            "content",
        )

        if content is None:
            return ""

        return content.strip()

    def canonical_url(self) -> str:
        locator = self._page.locator(
            'link[rel="canonical"]',
        )

        if locator.count() == 0:
            return ""

        href = locator.first.get_attribute(
            "href",
        )

        if href is None:
            return ""

        normalized_href = href.strip()

        if not normalized_href:
            return ""

        return urljoin(
            self._base_url(),
            normalized_href,
        )

    def headings(
        self,
    ) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}

        for level in range(
            1,
            7,
        ):
            selector = f"h{level}"

            values = self._page.locator(
                selector,
            ).all_inner_texts()

            cleaned_values = [
                value.strip()
                for value in values
                if value.strip()
            ]

            result[selector] = cleaned_values

        return result

    def language(self) -> str:
        locator = self._page.locator(
            "html",
        )

        if locator.count() == 0:
            return ""

        language = locator.first.get_attribute(
            "lang",
        )

        if language is None:
            return ""

        return language.strip()

    def _base_url(self) -> str:
        try:
            base_url = self._page.evaluate(
                "() => document.baseURI",
            )
        except Exception:
            base_url = self._page.url

        if not isinstance(
            base_url,
            str,
        ):
            return self._page.url

        normalized_base_url = base_url.strip()

        if not normalized_base_url:
            return self._page.url

        return normalized_base_url

    def _is_unsupported_url(
        self,
        url: str,
    ) -> bool:
        lowered_url = url.lower()

        unsupported_prefixes = (
            "javascript:",
            "mailto:",
            "tel:",
            "data:",
        )

        return lowered_url.startswith(
            unsupported_prefixes,
        )

    def _remove_duplicates(
        self,
        values: list[str],
    ) -> list[str]:
        return list(
            dict.fromkeys(values),
        )