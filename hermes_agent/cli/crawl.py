from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse
from hermes_agent.crawler import URLNormalizer

from hermes_agent.crawler import (
    CrawlManager,
    RobotsChecker,
    SitemapLoader,
    URLFilter,
    WebCrawler,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "웹사이트를 크롤링하고 JSON 보고서를 저장합니다."
        ),
    )

    parser.add_argument(
        "url",
        help="크롤링을 시작할 URL",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="최대 수집 페이지 수",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="최대 링크 탐색 깊이",
    )

    parser.add_argument(
        "--output",
        default="output/crawl-report.json",
        help="JSON 보고서 저장 경로",
    )

    parser.add_argument(
        "--no-robots",
        action="store_true",
        help="robots.txt 검사를 사용하지 않음",
    )

    parser.add_argument(
        "--no-sitemap",
        action="store_true",
        help="sitemap.xml을 사용하지 않음",
    )

    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="URL 필터를 사용하지 않음",
    )

    return parser


def validate_url(url: str) -> str:
    normalized_url = url.strip()
    parsed = urlparse(normalized_url)

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        raise ValueError(
            "URL은 http:// 또는 https://로 시작해야 합니다.",
        )

    if not parsed.netloc:
        raise ValueError(
            "올바른 도메인이 포함된 URL을 입력하세요.",
        )

    return normalized_url


def run_crawl(
    url: str,
    *,
    max_pages: int = 50,
    max_depth: int = 2,
    output: str | Path = "output/crawl-report.json",
    use_robots: bool = True,
    use_sitemap: bool = True,
    use_filter: bool = True,
) -> Path:
    validated_url = validate_url(url)

    if max_pages <= 0:
        raise ValueError(
            "max_pages는 1 이상이어야 합니다.",
        )

    if max_depth < 0:
        raise ValueError(
            "max_depth는 0 이상이어야 합니다.",
        )

    crawler = WebCrawler()

    manager = CrawlManager(
        crawler=crawler,
        robots_checker=(
            RobotsChecker()
            if use_robots
            else None
        ),
        sitemap_loader=(
            SitemapLoader()
            if use_sitemap
            else None
        ),
        url_filter=(
            URLFilter()
            if use_filter
            else None
        ),
        url_normalizer=URLNormalizer(),
    )

    report = manager.crawl_with_report(
        start_url=validated_url,
        max_pages=max_pages,
        max_depth=max_depth,
    )

    output_path = report.save_json(output)

    print("=" * 60)
    print("크롤링 완료")
    print("=" * 60)
    print(f"성공 페이지 : {report.page_count}")
    print(f"방문 URL    : {report.visited_count}")
    print(f"실패 URL    : {report.failed_count}")
    print(f"차단 URL    : {report.blocked_count}")
    print(f"보고서 저장 : {output_path}")
    print("=" * 60)

    if report.page_count == 0:
        raise RuntimeError(
            "수집된 페이지가 없습니다. "
            "URL 또는 네트워크 상태를 확인하세요.",
        )

    return output_path


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        run_crawl(
            url=args.url,
            max_pages=args.max_pages,
            max_depth=args.max_depth,
            output=args.output,
            use_robots=not args.no_robots,
            use_sitemap=not args.no_sitemap,
            use_filter=not args.no_filter,
        )
    except ValueError as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        parser.exit(
            status=130,
            message="\n크롤링이 사용자에 의해 중단되었습니다.\n",
        )
    except Exception as error:
        parser.exit(
            status=1,
            message=f"크롤링 실패: {error}\n",
        )


if __name__ == "__main__":
    main()
