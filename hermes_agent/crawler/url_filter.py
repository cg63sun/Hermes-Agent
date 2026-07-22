from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import urlparse


class URLFilter:
    DEFAULT_BLOCKED_EXTENSIONS = {
        ".7z",
        ".avi",
        ".bmp",
        ".css",
        ".csv",
        ".doc",
        ".docx",
        ".eot",
        ".exe",
        ".gif",
        ".gz",
        ".ico",
        ".jpeg",
        ".jpg",
        ".js",
        ".json",
        ".m4a",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".ogg",
        ".otf",
        ".pdf",
        ".png",
        ".ppt",
        ".pptx",
        ".rar",
        ".rss",
        ".svg",
        ".tar",
        ".tif",
        ".tiff",
        ".ttf",
        ".wav",
        ".webm",
        ".webp",
        ".woff",
        ".woff2",
        ".xls",
        ".xlsx",
        ".xml",
        ".zip",
    }

    DEFAULT_BLOCKED_PATH_PREFIXES = {
        "/admin",
        "/login",
        "/logout",
        "/register",
        "/signin",
        "/signup",
        "/wp-admin",
        "/wp-login.php",
    }

    def __init__(
        self,
        blocked_extensions: set[str] | None = None,
        blocked_path_prefixes: set[str] | None = None,
    ) -> None:
        self._blocked_extensions = (
            blocked_extensions
            if blocked_extensions is not None
            else self.DEFAULT_BLOCKED_EXTENSIONS
        )

        self._blocked_path_prefixes = (
            blocked_path_prefixes
            if blocked_path_prefixes is not None
            else self.DEFAULT_BLOCKED_PATH_PREFIXES
        )

    def is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)

        if parsed.scheme.lower() not in {"http", "https"}:
            return False

        if not parsed.netloc:
            return False

        path = parsed.path.lower()

        if self._has_blocked_extension(path):
            return False

        if self._has_blocked_path_prefix(path):
            return False

        return True

    def _has_blocked_extension(self, path: str) -> bool:
        suffix = PurePosixPath(path).suffix.lower()

        return suffix in self._blocked_extensions

    def _has_blocked_path_prefix(self, path: str) -> bool:
        for prefix in self._blocked_path_prefixes:
            normalized_prefix = prefix.lower()

            if path == normalized_prefix:
                return True

            if path.startswith(normalized_prefix + "/"):
                return True

        return False
