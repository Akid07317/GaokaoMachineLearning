#!/usr/bin/env python3
"""Preflight locally cached P0 asset/endpoint/context candidates.

This script only reads already-cached local files from the P0 local cache
inventory. It does not fetch remote pages and does not promote any row into
reference trend intake, canonical, ML, or the 32-school decision pool.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

INVENTORY = CLEAN / "reference_trend_520_p0_local_cache_inventory.csv"
OUT = CLEAN / "reference_trend_520_p0_cached_asset_endpoint_preflight.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_cached_asset_endpoint_preflight_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_cached_asset_endpoint_preflight_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_cached_asset_endpoint_preflight_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_cached_asset_endpoint_preflight.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

TARGET_FEASIBILITY = {
    "cached_asset_or_page_ocr_preflight",
    "cached_endpoint_or_portal_page_review",
    "cached_context_contains_guangxi_plan_terms_review",
}
TEXT_SUFFIXES = {".html", ".htm", ".txt", ".csv", ".json", ".js", ".md"}
KEYWORDS = ["广西", "2025", "招生计划", "计划", "物理", "本科普通批", "专业组"]

FIELDS = [
    "preflight_record_id",
    "cache_record_id",
    "drilldown_record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "drilldown_lane",
    "drilldown_priority",
    "source_url",
    "cache_path",
    "cache_suffix",
    "cache_size_bytes",
    "local_cache_feasibility",
    "preflight_route",
    "link_count",
    "image_link_count",
    "form_action_count",
    "script_link_count",
    "candidate_asset_links",
    "candidate_form_actions",
    "candidate_script_links",
    "keyword_hits",
    "guangxi_snippet",
    "plan_snippet",
    "safe_next_action",
    "expected_output_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def compact(values: list[str], limit: int = 5) -> str:
    seen: list[str] = []
    for value in values:
        clean = " ".join(str(value).strip().split())
        if clean and clean not in seen:
            seen.append(clean)
        if len(seen) >= limit:
            break
    return " | ".join(seen)


def snippet(text: str, token: str, window: int = 42) -> str:
    pos = text.find(token)
    if pos < 0:
        return ""
    start = max(0, pos - window)
    end = min(len(text), pos + len(token) + window)
    return " ".join(text[start:end].split())


def links_from_text(text: str) -> dict[str, list[str]]:
    hrefs = re.findall(r"""href\s*=\s*["']([^"']+)["']""", text, flags=re.I)
    images = re.findall(r"""<img[^>]+src\s*=\s*["']([^"']+)["']""", text, flags=re.I)
    forms = re.findall(r"""<form[^>]+action\s*=\s*["']([^"']*)["']""", text, flags=re.I)
    scripts = re.findall(r"""<script[^>]+src\s*=\s*["']([^"']+)["']""", text, flags=re.I)
    return {"hrefs": hrefs, "images": images, "forms": forms, "scripts": scripts}


def classify(row: dict[str, str], suffix: str, links: dict[str, list[str]], text: str) -> tuple[str, str]:
    feasibility = row.get("local_cache_feasibility", "")
    lower_links = " ".join(links["hrefs"] + links["images"] + links["forms"] + links["scripts"]).lower()
    has_asset_link = bool(links["images"]) or any(
        token in lower_links for token in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"]
    )
    has_endpoint_shape = bool(links["forms"]) or bool(links["scripts"])

    if suffix == ".pdf":
        return (
            "local_pdf_parse_needed",
            "Queue a local PDF parse/OCR preview only; do not infer group-year rows until fields are extracted and QAed.",
        )
    if feasibility == "cached_asset_or_page_ocr_preflight":
        if has_asset_link:
            return (
                "cached_html_asset_links_found",
                "Review cached asset links and parse/OCR only cached local assets or explicitly approved captures.",
            )
        return (
            "cached_html_no_asset_link_visible",
            "Keep as asset backoff; exact cached image/PDF or approved browser capture is needed before OCR.",
        )
    if feasibility == "cached_endpoint_or_portal_page_review":
        if has_endpoint_shape:
            return (
                "cached_endpoint_form_or_script_links_found",
                "Review local form/script references; live form/browser replay still requires approval.",
            )
        return (
            "cached_endpoint_no_form_or_script_visible",
            "Keep as endpoint metadata; exact cached endpoint response or approved browser/form replay is needed.",
        )
    if "广西" in text and "计划" in text:
        return (
            "cached_context_keyword_only_hold",
            "Use as source context only; hold until structured Guangxi group-year plan rows or links are identified.",
        )
    return (
        "cached_context_no_actionable_terms_hold",
        "Keep as context evidence only; no source_packet parse is safe this round.",
    )


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    inventory_rows = read_csv(INVENTORY)
    target_rows = [
        row for row in inventory_rows
        if row.get("local_cache_feasibility", "") in TARGET_FEASIBILITY and row.get("cache_exists", "") == "true"
    ]

    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for source in target_rows:
        rel = source.get("cache_path", "")
        path = ROOT / rel if rel else None
        exists = bool(path and path.exists())
        suffix = source.get("cache_suffix", "") or (path.suffix.lower() if path else "")
        text = read_text(path) if exists and suffix in TEXT_SUFFIXES else ""
        links = links_from_text(text) if text else {"hrefs": [], "images": [], "forms": [], "scripts": []}
        keyword_hits = [key for key in KEYWORDS if key in text]
        route, safe_action = classify(source, suffix, links, text)

        rows.append(
            {
                "preflight_record_id": f"reference_trend_520_p0_cached_preflight_{len(rows) + 1:04d}",
                "cache_record_id": source.get("cache_record_id", ""),
                "drilldown_record_id": source.get("drilldown_record_id", ""),
                "queue_record_id": source.get("queue_record_id", ""),
                "queue_rank": source.get("queue_rank", ""),
                "university_code": source.get("university_code", ""),
                "university_name": source.get("university_name", ""),
                "group_pair_key": source.get("group_pair_key", ""),
                "group_code": source.get("group_code", ""),
                "drilldown_lane": source.get("drilldown_lane", ""),
                "drilldown_priority": source.get("drilldown_priority", ""),
                "source_url": source.get("source_url", ""),
                "cache_path": rel,
                "cache_suffix": suffix,
                "cache_size_bytes": source.get("cache_size_bytes", ""),
                "local_cache_feasibility": source.get("local_cache_feasibility", ""),
                "preflight_route": route,
                "link_count": len(links["hrefs"]),
                "image_link_count": len(links["images"]),
                "form_action_count": len(links["forms"]),
                "script_link_count": len(links["scripts"]),
                "candidate_asset_links": compact(links["images"] + links["hrefs"]),
                "candidate_form_actions": compact(links["forms"]),
                "candidate_script_links": compact(links["scripts"]),
                "keyword_hits": "|".join(keyword_hits),
                "guangxi_snippet": snippet(text, "广西"),
                "plan_snippet": snippet(text, "招生计划") or snippet(text, "计划"),
                "safe_next_action": safe_action,
                "expected_output_layer": "cached_asset_endpoint_preflight_only_not_source_packet_not_canonical",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "p0_cached_preflight_only_not_32_school_decision_pool",
                "evidence_note": "Local cached-file preflight only; no network, no browser replay, no source_packet parse rows.",
            }
        )

        if not exists:
            exclusions.append(
                {
                    "record_id": source.get("cache_record_id", ""),
                    "university_name": source.get("university_name", ""),
                    "reason": "cache_path_missing_during_preflight",
                    "detail": rel,
                }
            )
        elif suffix == ".pdf":
            exclusions.append(
                {
                    "record_id": source.get("cache_record_id", ""),
                    "university_name": source.get("university_name", ""),
                    "reason": "pdf_binary_not_parsed_this_round",
                    "detail": rel,
                }
            )

    route_counts = Counter(str(row["preflight_route"]) for row in rows)
    feasibility_counts = Counter(str(row["local_cache_feasibility"]) for row in rows)
    suffix_counts = Counter(str(row["cache_suffix"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "input_inventory_rows", "value": len(inventory_rows), "note": "Rows read from local cache inventory."},
        {"metric": "target_cached_preflight_rows", "value": len(rows), "note": "Existing cached rows in asset/endpoint/context feasibility lanes."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
    ]
    rollup_rows += [
        {"metric": f"preflight_route::{key}", "value": count, "note": ""}
        for key, count in sorted(route_counts.items())
    ]
    rollup_rows += [
        {"metric": f"local_cache_feasibility::{key}", "value": count, "note": ""}
        for key, count in sorted(feasibility_counts.items())
    ]
    rollup_rows += [
        {"metric": f"cache_suffix::{key or 'none'}", "value": count, "note": ""}
        for key, count in sorted(suffix_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_inventory_exists",
            "status": "pass" if INVENTORY.exists() else "fail",
            "value": str(INVENTORY.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "target_cached_preflight_rows",
            "status": "pass" if len(rows) == 8 else "warn",
            "value": len(rows),
            "note": "Expected 8 from latest local cache inventory target feasibility lanes.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "network_or_browser_used",
            "status": "pass",
            "value": "false",
            "note": "This script only inspected local cached files.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    route_counts = {
        row["metric"].split("::", 1)[1]: row["value"]
        for row in rollup_rows
        if str(row["metric"]).startswith("preflight_route::")
    }
    route_lines = "\n".join(f"- `{key}`: {value}" for key, value in route_counts.items())
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 Cached Asset/Endpoint Preflight

Date: {date.today().isoformat()}

Scope: locally cached files from `reference_trend_520_p0_local_cache_inventory.csv` whose feasibility is asset OCR preflight, endpoint/portal review, or context-with-Guangxi-plan terms. This is a local preflight only: no network, no browser replay, no source_packet parse rows, no reference_trend_pool intake, no canonical/ML, and no 32-school decision_pool changes.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_asset_endpoint_preflight.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_rollup.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_qa.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_exclusion_log.csv`

## Coverage

- Target cached preflight rows: {len(rows)}
- QA status: {qa_status}

## Route Counts

{route_lines or "- none"}

## Boundary

Rows remain in preflight/QA only. PDF binaries, image assets, endpoint scripts/forms, and keyword-only context require a later explicit parse/OCR or approval step before any source_packet preview can be created.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 103. 2026-05-16 P0 cached asset/endpoint preflight"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    route_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("preflight_route::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 cached asset/endpoint preflight：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_asset_endpoint_preflight.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_rollup.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_qa.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_asset_endpoint_preflight.md`

覆盖结果：从 P0 local cache inventory 中抽取 8 条本地已缓存且可继续预检的 asset/endpoint/context rows；本轮只做本地文件链接、表单、脚本、关键词和短证据预检。路线分布：{route_summary or 'none'}。QA {qa_status}。

准入边界：本轮不联网、不浏览器 replay、不 OCR/PDF parse、不生成 source_packet parse rows；所有行仍停留在 preflight/QA 层，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。
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
    print(f"wrote {len(rows)} cached preflight rows")


if __name__ == "__main__":
    main()
