from __future__ import annotations

from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)


class URLNormalizer:
    TRACKING_PARAMETERS = {
        "fbclid",
        "gclid",
        "ref",
        "referrer",
        "source",
    }

    TRACKING_PREFIXES = (
        "utm_",
    )

    def normalize(
        self,
        url: str,
        *,
        base_url: str | None = None,
    ) -> str:
        normalized_url = url.strip()

        if not normalized_url:
            return ""

        if base_url:
            normalized_url = urljoin(
                base_url,
                normalized_url,
            )

        parsed = urlsplit(
            normalized_url,
        )

        scheme = parsed.scheme.lower()
        hostname = (
            parsed.hostname.lower()
            if parsed.hostname
            else ""
        )

        netloc = self._build_netloc(
            scheme=scheme,
            hostname=hostname,
            port=parsed.port,
            username=parsed.username,
            password=parsed.password,
        )

        path = self._normalize_path(
            parsed.path,
        )

        query = self._normalize_query(
            parsed.query,
        )

        return urlunsplit(
            (
                scheme,
                netloc,
                path,
                query,
                "",
            ),
        )

    def is_same_url(
        self,
        first_url: str,
        second_url: str,
    ) -> bool:
        return (
            self.normalize(first_url)
            == self.normalize(second_url)
        )

    def _build_netloc(
        self,
        *,
        scheme: str,
        hostname: str,
        port: int | None,
        username: str | None,
        password: str | None,
    ) -> str:
        authentication = ""

        if username:
            authentication = username

            if password:
                authentication += f":{password}"

            authentication += "@"

        port_text = ""

        if port is not None:
            is_default_http = (
                scheme == "http"
                and port == 80
            )

            is_default_https = (
                scheme == "https"
                and port == 443
            )

            if not is_default_http and not is_default_https:
                port_text = f":{port}"

        return (
            f"{authentication}"
            f"{hostname}"
            f"{port_text}"
        )

    def _normalize_path(
        self,
        path: str,
    ) -> str:
        if not path:
            return "/"

        parts = [
            part
            for part in path.split("/")
            if part
        ]

        normalized_path = (
            "/" + "/".join(parts)
        )

        if normalized_path != "/":
            normalized_path = (
                normalized_path.rstrip("/")
            )

        return normalized_path

    def _normalize_query(
        self,
        query: str,
    ) -> str:
        if not query:
            return ""

        parameters = parse_qsl(
            query,
            keep_blank_values=True,
        )

        filtered_parameters = []

        for key, value in parameters:
            normalized_key = key.lower()

            if normalized_key in self.TRACKING_PARAMETERS:
                continue

            if any(
                normalized_key.startswith(prefix)
                for prefix in self.TRACKING_PREFIXES
            ):
                continue

            filtered_parameters.append(
                (key, value),
            )

        filtered_parameters.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
        )

        return urlencode(
            filtered_parameters,
            doseq=True,
        )
