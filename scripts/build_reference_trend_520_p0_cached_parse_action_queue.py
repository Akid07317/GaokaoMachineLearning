#!/usr/bin/env python3
"""Create next-action queue from cached asset/endpoint preflight rows.

The queue is a local-only planning layer. It may point to a cached PDF, HTML
asset links, endpoint metadata, or keyword-only holds, but it does not parse
PDF/OCR content and does not create source_packet/intake/canonical rows.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
RAW_REFERENCE = ROOT / "raw_sources" / "reference_trend"

PREFLIGHT = CLEAN / "reference_trend_520_p0_cached_asset_endpoint_preflight.csv"
OUT = CLEAN / "reference_trend_520_p0_cached_parse_action_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_cached_parse_action_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_cached_parse_action_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_cached_parse_action_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_cached_parse_action_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "parse_action_id",
    "preflight_record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "source_url",
    "cache_path",
    "preflight_route",
    "parse_action_route",
    "parse_action_priority",
    "candidate_kind",
    "candidate_value",
    "candidate_local_path",
    "candidate_local_exists",
    "is_duplicate_candidate",
    "requires_network",
    "requires_browser_or_form_approval",
    "requires_manual_ocr_or_pdf_parse",
    "safe_next_action",
    "expected_output_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


DECORATIVE_TOKENS = {
    "logo",
    "banner",
    "bg",
    "nav",
    "dh_",
    "qr_",
    "vr",
    "static",
    "jquery",
    "style",
    "common",
    "main.js",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def bool_str(value: bool) -> str:
    return "true" if value else "false"


def clean_link(link: str) -> str:
    return str(link or "").strip()


def is_remote(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https"}


def strip_query(link: str) -> str:
    return link.split("?", 1)[0].split("#", 1)[0]


def safe_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except (OSError, ValueError):
        return ""


def find_by_basename(link: str) -> str:
    basename = Path(strip_query(link)).name
    if not basename or not RAW_REFERENCE.exists():
        return ""
    matches = []
    try:
        for path in RAW_REFERENCE.rglob(basename):
            if path.is_file():
                matches.append(path)
                if len(matches) >= 3:
                    break
    except OSError:
        return ""
    return " | ".join(safe_relative(path) for path in matches if safe_relative(path))


def resolve_local(link: str, cache_path: str) -> str:
    if not link or is_remote(link):
        return ""
    link_no_query = strip_query(link)
    base = ROOT / cache_path
    candidates: list[Path] = []
    if link_no_query.startswith("/"):
        candidates.append(ROOT / link_no_query.lstrip("/"))
    else:
        candidates.append((base.parent / link_no_query).resolve())
    for candidate in candidates:
        if candidate.exists():
            return safe_relative(candidate)
    return find_by_basename(link_no_query)


def classify_asset(link: str, local_path: str) -> tuple[str, str, str]:
    low = link.lower()
    ext = Path(strip_query(low)).suffix
    content_like = (
        "__local" in low
        or "/article/images/" in low
        or ext in {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
    )
    decorative = any(token in low for token in DECORATIVE_TOKENS)
    if content_like and local_path:
        return (
            "local_asset_parse_candidate",
            "P0A1_local_asset_exists",
            "Parse/OCR only the local cached asset in a later preview; hold for QA before any source_packet.",
        )
    if content_like and not decorative:
        return (
            "asset_link_needs_cached_capture_or_approval",
            "P0A2_content_asset_not_cached",
            "Request exact cached asset or approved browser capture before OCR; do not fetch by terminal curl.",
        )
    return (
        "decorative_or_site_asset_low_priority",
        "P2A9_decorative_asset_hold",
        "Keep as page chrome evidence only; no OCR/parse action unless manually promoted.",
    )


def base_row(source: dict[str, str]) -> dict[str, object]:
    return {
        "preflight_record_id": source.get("preflight_record_id", ""),
        "queue_record_id": source.get("queue_record_id", ""),
        "queue_rank": source.get("queue_rank", ""),
        "university_code": source.get("university_code", ""),
        "university_name": source.get("university_name", ""),
        "group_pair_key": source.get("group_pair_key", ""),
        "group_code": source.get("group_code", ""),
        "source_url": source.get("source_url", ""),
        "cache_path": source.get("cache_path", ""),
        "preflight_route": source.get("preflight_route", ""),
        "expected_output_layer": "cached_parse_action_queue_only_not_source_packet_not_canonical",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "p0_cached_parse_queue_only_not_32_school_decision_pool",
        "evidence_note": "Local next-action queue only; no network, no OCR/PDF parse, no source_packet parse rows.",
    }


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    preflight_rows = read_csv(PREFLIGHT)
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    seen_candidate_keys: set[str] = set()

    for source in preflight_rows:
        route = source.get("preflight_route", "")
        cache_path = source.get("cache_path", "")

        if route == "local_pdf_parse_needed":
            local_path = cache_path if (ROOT / cache_path).exists() else ""
            record = base_row(source)
            record.update(
                {
                    "parse_action_route": "local_pdf_text_extract_preview_queue",
                    "parse_action_priority": "P0P1_local_pdf_parse_preview",
                    "candidate_kind": "local_pdf",
                    "candidate_value": cache_path,
                    "candidate_local_path": local_path,
                    "candidate_local_exists": bool_str(bool(local_path)),
                    "is_duplicate_candidate": "false",
                    "requires_network": "false",
                    "requires_browser_or_form_approval": "false",
                    "requires_manual_ocr_or_pdf_parse": "true",
                    "safe_next_action": "Run a local PDF text extraction preview in a later round, then QA fields before source_packet.",
                }
            )
            rows.append(record)
            continue

        if route == "cached_endpoint_form_or_script_links_found":
            candidates = split_pipe(source.get("candidate_form_actions", "")) or split_pipe(source.get("candidate_script_links", ""))
            for candidate in candidates[:8]:
                local_path = resolve_local(candidate, cache_path)
                key = f"{source.get('university_code')}|endpoint|{candidate}"
                duplicate = key in seen_candidate_keys
                seen_candidate_keys.add(key)
                record = base_row(source)
                record.update(
                    {
                        "parse_action_route": "endpoint_metadata_review_before_live_replay",
                        "parse_action_priority": "P0E1_endpoint_shape_review",
                        "candidate_kind": "form_action_or_script",
                        "candidate_value": candidate,
                        "candidate_local_path": local_path,
                        "candidate_local_exists": bool_str(bool(local_path)),
                        "is_duplicate_candidate": bool_str(duplicate),
                        "requires_network": "false",
                        "requires_browser_or_form_approval": "true",
                        "requires_manual_ocr_or_pdf_parse": "false",
                        "safe_next_action": "Review cached endpoint metadata; any live form/browser replay still needs approval.",
                    }
                )
                rows.append(record)
            continue

        if route == "cached_html_asset_links_found":
            for link in split_pipe(source.get("candidate_asset_links", "")):
                local_path = resolve_local(link, cache_path)
                action_route, priority, safe_action = classify_asset(link, local_path)
                key = f"{source.get('university_code')}|asset|{strip_query(link)}"
                duplicate = key in seen_candidate_keys
                seen_candidate_keys.add(key)
                record = base_row(source)
                record.update(
                    {
                        "parse_action_route": action_route,
                        "parse_action_priority": priority,
                        "candidate_kind": "asset_link",
                        "candidate_value": link,
                        "candidate_local_path": local_path,
                        "candidate_local_exists": bool_str(bool(local_path)),
                        "is_duplicate_candidate": bool_str(duplicate),
                        "requires_network": "false",
                        "requires_browser_or_form_approval": "true" if action_route == "asset_link_needs_cached_capture_or_approval" else "false",
                        "requires_manual_ocr_or_pdf_parse": "true" if action_route == "local_asset_parse_candidate" else "false",
                        "safe_next_action": safe_action,
                    }
                )
                rows.append(record)
            continue

        if route == "cached_context_keyword_only_hold":
            record = base_row(source)
            record.update(
                {
                    "parse_action_route": "keyword_context_hold_no_structured_plan_rows",
                    "parse_action_priority": "P1H7_context_hold",
                    "candidate_kind": "keyword_context",
                    "candidate_value": source.get("keyword_hits", ""),
                    "candidate_local_path": cache_path,
                    "candidate_local_exists": bool_str(bool(cache_path and (ROOT / cache_path).exists())),
                    "is_duplicate_candidate": "false",
                    "requires_network": "false",
                    "requires_browser_or_form_approval": "false",
                    "requires_manual_ocr_or_pdf_parse": "false",
                    "safe_next_action": "Keep as context only; require structured Guangxi group-year plan rows before source_packet preview.",
                }
            )
            rows.append(record)
            continue

        exclusions.append(
            {
                "record_id": source.get("preflight_record_id", ""),
                "university_name": source.get("university_name", ""),
                "reason": "unsupported_preflight_route",
                "detail": route,
            }
        )

    for index, row in enumerate(rows, start=1):
        row["parse_action_id"] = f"reference_trend_520_p0_parse_action_{index:04d}"

    route_counts = Counter(str(row["parse_action_route"]) for row in rows)
    priority_counts = Counter(str(row["parse_action_priority"]) for row in rows)
    local_exists_counts = Counter(str(row["candidate_local_exists"]) for row in rows)
    duplicate_counts = Counter(str(row["is_duplicate_candidate"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "input_preflight_rows", "value": len(preflight_rows), "note": "Rows read from cached asset/endpoint preflight."},
        {"metric": "parse_action_rows", "value": len(rows), "note": "Local next-action queue rows."},
        {"metric": "candidate_local_exists_true", "value": local_exists_counts.get("true", 0), "note": ""},
        {"metric": "candidate_local_exists_false", "value": local_exists_counts.get("false", 0), "note": ""},
        {"metric": "duplicate_candidate_true", "value": duplicate_counts.get("true", 0), "note": ""},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
    ]
    rollup_rows += [
        {"metric": f"parse_action_route::{key}", "value": count, "note": ""}
        for key, count in sorted(route_counts.items())
    ]
    rollup_rows += [
        {"metric": f"parse_action_priority::{key}", "value": count, "note": ""}
        for key, count in sorted(priority_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_preflight_exists",
            "status": "pass" if PREFLIGHT.exists() else "fail",
            "value": str(PREFLIGHT.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "parse_action_rows_generated",
            "status": "pass" if rows else "warn",
            "value": len(rows),
            "note": "Queue is a planning layer, not parse output.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "network_browser_or_ocr_used",
            "status": "pass",
            "value": "false",
            "note": "No network, browser replay, PDF parse, or OCR was performed.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    route_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("parse_action_route::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 Cached Parse Action Queue

Date: {date.today().isoformat()}

Scope: local next-action queue derived from `reference_trend_520_p0_cached_asset_endpoint_preflight.csv`. This queue tells the next run whether to attempt local PDF text extraction, local asset/OCR review, endpoint metadata review, or keep keyword-only context on hold. It does not perform parsing/OCR, does not fetch remote pages, and does not create source_packet/intake/canonical rows.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_parse_action_queue.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_exclusion_log.csv`

## Coverage

- Parse action rows: {len(rows)}
- QA status: {qa_status}

## Route Counts

{route_lines or "- none"}

## Boundary

All rows remain outside reference_trend_pool intake and outside canonical/ML. Rows requiring live asset capture or form/browser replay remain approval-gated.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 104. 2026-05-16 P0 cached parse action queue"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    route_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("parse_action_route::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 cached parse action queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_parse_action_queue.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_parse_action_queue.md`

覆盖结果：从 8 条 cached asset/endpoint preflight rows 派生 {len(rows)} 条本地下一步 action rows；路线分布：{route_summary or 'none'}。QA {qa_status}。

准入边界：本轮只生成本地解析/审批/hold 队列，不执行 PDF parse/OCR、不联网、不浏览器 replay、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
        )


def main() -> None:
    rows, rollup_rows, qa_rows, exclusions = build()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusions, ["record_id", "university_name", "reason", "detail"])
    write_doc(rows, rollup_rows, qa_rows)
    append_handoff(rows, rollup_rows, qa_rows)
    print(f"wrote {len(rows)} cached parse action rows")


if __name__ == "__main__":
    main()
