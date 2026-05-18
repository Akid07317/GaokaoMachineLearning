from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import csv

from gaokao_planner.html_tables import decode_html
from gaokao_planner.source_fetch import FetchResult, detect_antibot_shell, fetch_url


DEFAULT_FOLLOW_HINTS = [
    "招生",
    "招办",
    "招生网",
    "招考",
    "计划",
    "专业",
    "分数",
    "录取",
    "章程",
    "广西",
    "物理",
    "历年",
    "招生政策",
    "历年分数",
    "本科",
    "gaokao",
    "zsb",
    "admission",
]

FOLLOWABLE_SUFFIXES = {".html", ".htm", ".shtml", ".aspx", ".php", ".psp", ".pdf", ""}
SKIP_SCHEMES = ("javascript:", "mailto:", "tel:")
SKIP_SUFFIXES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".bmp",
    ".mp4",
    ".mp3",
    ".zip",
    ".rar",
    ".7z",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
}


@dataclass
class DiscoverySeed:
    seed_id: str
    seed_url: str
    source_name: str
    year_hint: str
    allowed_domains: list[str]
    include_keywords: list[str]
    follow_keywords: list[str]
    max_depth: int
    max_pages: int
    notes: str


@dataclass
class DiscoveryPage:
    seed_id: str
    page_url: str
    depth: int
    status: str
    output_path: str
    page_title: str
    link_count: int
    error_message: str
    fetched_at: str


@dataclass
class CandidateLink:
    seed_id: str
    seed_url: str
    year_hint: str
    source_name: str
    source_page_url: str
    source_page_title: str
    depth: int
    link_text: str
    target_url: str
    target_domain: str
    target_suffix: str
    score: int
    matched_keywords: str
    follow_recommended: str
    notes: str


@dataclass
class ExtractedLink:
    href: str
    text: str


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[ExtractedLink] = []
        self.title = ""
        self._current_href = ""
        self._inside_anchor = False
        self._anchor_parts: list[str] = []
        self._inside_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "a":
            href = ""
            for key, value in attrs:
                if key.lower() == "href" and value:
                    href = value
                    break
            self._current_href = href
            self._inside_anchor = True
            self._anchor_parts = []
        elif name == "title":
            self._inside_title = True
            self._title_parts = []

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name == "a":
            text = " ".join("".join(self._anchor_parts).split())
            if self._current_href:
                self.links.append(ExtractedLink(href=self._current_href, text=text))
            self._current_href = ""
            self._inside_anchor = False
            self._anchor_parts = []
        elif name == "title":
            self.title = " ".join("".join(self._title_parts).split())
            self._inside_title = False
            self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_anchor:
            self._anchor_parts.append(data)
        if self._inside_title:
            self._title_parts.append(data)


def read_discovery_seeds(path: str | Path) -> list[DiscoverySeed]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    seeds: list[DiscoverySeed] = []
    for row in rows:
        seeds.append(
            DiscoverySeed(
                seed_id=row["seed_id"].strip(),
                seed_url=row["seed_url"].strip(),
                source_name=row.get("source_name", "").strip(),
                year_hint=row.get("year_hint", "").strip(),
                allowed_domains=_split_csv_field(row.get("allowed_domains", "")),
                include_keywords=_split_csv_field(row.get("include_keywords", "")),
                follow_keywords=_split_csv_field(row.get("follow_keywords", "")),
                max_depth=int(row.get("max_depth", "1") or "1"),
                max_pages=int(row.get("max_pages", "20") or "20"),
                notes=row.get("notes", "").strip(),
            )
        )
    return seeds


def _split_csv_field(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(fragment="", params="")
    return urlunparse(cleaned)


def domain_matches(url: str, allowed_domains: list[str]) -> bool:
    host = urlparse(url).netloc.lower()
    if not host:
        return False
    return any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains)


def suffix_for_url(url: str) -> str:
    path = urlparse(url).path.lower()
    suffix = Path(path).suffix.lower()
    return suffix


def is_skippable_url(url: str) -> bool:
    lowered = url.lower().strip()
    if not lowered or lowered.startswith(SKIP_SCHEMES):
        return True
    suffix = suffix_for_url(lowered)
    return suffix in SKIP_SUFFIXES


def is_followable_url(url: str) -> bool:
    return suffix_for_url(url) in FOLLOWABLE_SUFFIXES


def extract_links_from_html(html: str, base_url: str) -> tuple[str, list[ExtractedLink]]:
    parser = LinkParser()
    parser.feed(html)
    results: list[ExtractedLink] = []
    for link in parser.links:
        absolute = normalize_url(urljoin(base_url, link.href))
        results.append(ExtractedLink(href=absolute, text=link.text.strip()))
    return parser.title.strip(), results


def keyword_matches(text: str, keywords: list[str]) -> list[str]:
    haystack = text.lower()
    hits: list[str] = []
    for keyword in keywords:
        if keyword.lower() in haystack:
            hits.append(keyword)
    return hits


def candidate_score(
    url: str,
    link_text: str,
    page_title: str,
    include_keywords: list[str],
) -> tuple[int, list[str]]:
    combined = " ".join(part for part in [url, link_text, page_title] if part)
    matched = keyword_matches(combined, include_keywords)
    score = len(matched) * 10
    suffix = suffix_for_url(url)
    if "广西" in combined:
        score += 5
    if suffix == ".pdf":
        score += 3
    if "招生计划" in combined or "历年分数" in combined or "招生章程" in combined:
        score += 8
    return score, matched


def should_follow_link(
    url: str,
    link_text: str,
    page_title: str,
    follow_keywords: list[str],
    allowed_domains: list[str],
) -> bool:
    if is_skippable_url(url) or not is_followable_url(url):
        return False
    if not domain_matches(url, allowed_domains):
        return False
    combined = " ".join(part for part in [url, link_text, page_title] if part)
    hints = follow_keywords or DEFAULT_FOLLOW_HINTS
    return bool(keyword_matches(combined, hints))


def build_cache_path(cache_dir: str | Path, seed_id: str, depth: int, url: str) -> Path:
    digest = sha1(url.encode("utf-8")).hexdigest()[:12]
    suffix = suffix_for_url(url) or ".html"
    if suffix == ".pdf":
        extension = ".pdf"
    else:
        extension = ".html"
    return Path(cache_dir) / seed_id / f"d{depth:02d}_{digest}{extension}"


def fetch_page(
    seed_id: str,
    url: str,
    depth: int,
    cache_dir: str | Path,
    timeout: int,
    verify_ssl: bool,
) -> tuple[DiscoveryPage, str | None, list[ExtractedLink]]:
    cache_path = build_cache_path(cache_dir, seed_id, depth, url)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).isoformat()

    try:
        raw = fetch_url(url, timeout=timeout, verify_ssl=verify_ssl)
        cache_path.write_bytes(raw)
        if detect_antibot_shell(raw):
            return (
                DiscoveryPage(
                    seed_id=seed_id,
                    page_url=url,
                    depth=depth,
                    status="blocked_antibot_html",
                    output_path=str(cache_path),
                    page_title="",
                    link_count=0,
                    error_message="Downloaded anti-bot shell instead of source content.",
                    fetched_at=fetched_at,
                ),
                None,
                [],
            )
        if suffix_for_url(url) == ".pdf":
            return (
                DiscoveryPage(
                    seed_id=seed_id,
                    page_url=url,
                    depth=depth,
                    status="ok_pdf",
                    output_path=str(cache_path),
                    page_title="",
                    link_count=0,
                    error_message="",
                    fetched_at=fetched_at,
                ),
                None,
                [],
            )
        html = decode_html(raw)
        title, links = extract_links_from_html(html, url)
        return (
            DiscoveryPage(
                seed_id=seed_id,
                page_url=url,
                depth=depth,
                status="ok",
                output_path=str(cache_path),
                page_title=title,
                link_count=len(links),
                error_message="",
                fetched_at=fetched_at,
            ),
            title,
            links,
        )
    except Exception as error:  # pragma: no cover - defensive crawl guard.
        result = FetchResult(
            source_id=seed_id,
            url=url,
            status="error",
            output_path=str(cache_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )
        return (
            DiscoveryPage(
                seed_id=seed_id,
                page_url=url,
                depth=depth,
                status=result.status,
                output_path=result.output_path,
                page_title="",
                link_count=0,
                error_message=result.error_message,
                fetched_at=result.fetched_at,
            ),
            None,
            [],
        )


def crawl_seed(
    seed: DiscoverySeed,
    cache_dir: str | Path,
    timeout: int = 20,
    verify_ssl: bool = True,
) -> tuple[list[DiscoveryPage], list[CandidateLink]]:
    pages: list[DiscoveryPage] = []
    candidates: dict[str, CandidateLink] = {}
    queue: deque[tuple[str, int, str]] = deque([(normalize_url(seed.seed_url), 0, "")])
    visited: set[str] = set()

    while queue and len(visited) < seed.max_pages:
        url, depth, origin_text = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        page, title, links = fetch_page(
            seed_id=seed.seed_id,
            url=url,
            depth=depth,
            cache_dir=cache_dir,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        pages.append(page)

        if page.status not in {"ok", "ok_pdf"}:
            continue
        if page.status == "ok_pdf":
            continue

        for link in links:
            target_url = normalize_url(link.href)
            if is_skippable_url(target_url):
                continue
            if not domain_matches(target_url, seed.allowed_domains):
                continue

            score, matched = candidate_score(
                target_url,
                link.text,
                title or "",
                seed.include_keywords,
            )
            follow_recommended = "false"
            if should_follow_link(
                target_url,
                link.text,
                title or "",
                seed.follow_keywords,
                seed.allowed_domains,
            ):
                follow_recommended = "true"
                if depth < seed.max_depth:
                    queue.append((target_url, depth + 1, link.text))

            if score <= 0 and follow_recommended != "true":
                continue

            candidate = CandidateLink(
                seed_id=seed.seed_id,
                seed_url=seed.seed_url,
                year_hint=seed.year_hint,
                source_name=seed.source_name,
                source_page_url=url,
                source_page_title=title or "",
                depth=depth,
                link_text=link.text or origin_text,
                target_url=target_url,
                target_domain=urlparse(target_url).netloc.lower(),
                target_suffix=suffix_for_url(target_url) or "html",
                score=score,
                matched_keywords="|".join(matched),
                follow_recommended=follow_recommended,
                notes=seed.notes,
            )
            existing = candidates.get(target_url)
            if existing is None or candidate.score > existing.score:
                candidates[target_url] = candidate

    ordered_candidates = sorted(
        candidates.values(),
        key=lambda row: (-row.score, row.depth, row.target_url),
    )
    return pages, ordered_candidates


def write_pages_log(rows: list[DiscoveryPage], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "seed_id",
                "page_url",
                "depth",
                "status",
                "output_path",
                "page_title",
                "link_count",
                "error_message",
                "fetched_at",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_candidate_links(rows: list[CandidateLink], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "seed_id",
                "seed_url",
                "year_hint",
                "source_name",
                "source_page_url",
                "source_page_title",
                "depth",
                "link_text",
                "target_url",
                "target_domain",
                "target_suffix",
                "score",
                "matched_keywords",
                "follow_recommended",
                "notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
