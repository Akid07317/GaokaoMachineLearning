#!/usr/bin/env python3
"""Inventory cached local files for P0 local candidate drilldown rows.

This script only inspects local files referenced by the drilldown queue. It
does not fetch remote pages and does not promote any row into intake/canonical.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

DRILLDOWN = CLEAN / "reference_trend_520_p0_local_candidate_drilldown_queue.csv"
OUT = CLEAN / "reference_trend_520_p0_local_cache_inventory.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_local_cache_inventory_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_local_cache_inventory_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_local_cache_inventory_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_local_cache_inventory.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

TEXT_SUFFIXES = {".html", ".htm", ".txt", ".csv", ".json", ".js", ".md"}
KEYWORDS = ["广西", "2025", "招生计划", "计划", "物理", "本科普通批", "专业组"]

FIELDS = [
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
    "source_packet_status",
    "raw_file_path_token",
    "cache_path",
    "cache_exists",
    "cache_suffix",
    "cache_size_bytes",
    "is_text_like",
    "contains_guangxi",
    "contains_2025",
    "contains_plan_keyword",
    "contains_physics",
    "contains_group_keyword",
    "local_cache_feasibility",
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


def bool_str(value: bool) -> str:
    return "true" if value else "false"


def file_text_flags(path: Path) -> dict[str, bool]:
    suffix = path.suffix.lower()
    if suffix not in TEXT_SUFFIXES:
        return {key: False for key in KEYWORDS}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {key: False for key in KEYWORDS}
    return {key: key in text for key in KEYWORDS}


def classify(drilldown_row: dict[str, str], path: Path | None, exists: bool, flags: dict[str, bool]) -> tuple[str, str]:
    lane = drilldown_row.get("drilldown_lane", "")
    if path is None:
        return (
            "metadata_only_no_cache_path",
            "Keep as metadata route; require exact official URL/cache or approval before parsing.",
        )
    if not exists:
        return (
            "cache_missing_needs_exact_url_or_approved_fetch",
            "Do not retry terminal curl blindly; request exact cached asset, browser/header approval, or continue as backoff.",
        )
    if lane == "context_or_no_rows_hold":
        if flags.get("广西") and flags.get("计划"):
            return (
                "cached_context_contains_guangxi_plan_terms_review",
                "Review text manually for hidden plan/link references; still hold until structured Guangxi rows are found.",
            )
        return (
            "cached_context_no_structured_plan_hold",
            "Use as context only; no source_packet parse unless structured Guangxi plan rows are identified.",
        )
    if lane == "endpoint_or_portal_drilldown":
        return (
            "cached_endpoint_or_portal_page_review",
            "Inspect cached form/action/script links locally; browser/form replay still needs approval if endpoint is not in cache.",
        )
    if lane == "image_or_asset_ocr_candidate":
        return (
            "cached_asset_or_page_ocr_preflight",
            "If a cached image/PDF asset is present, queue OCR/PDF parse preview; if only HTML is cached, locate asset link first.",
        )
    if lane == "metadata_drilldown_needed":
        return (
            "cached_metadata_review",
            "Review cached file and candidate metadata before deciding parse, rejection, or approval route.",
        )
    return (
        "cached_file_no_parse_route",
        "Keep cached file as evidence; no direct intake/canonical action.",
    )


def split_paths(raw: str) -> list[str]:
    return [part.strip() for part in str(raw or "").split("|") if part.strip()]


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    drilldown_rows = read_csv(DRILLDOWN)
    rows: list[dict[str, object]] = []
    for drilldown in drilldown_rows:
        tokens = split_paths(drilldown.get("raw_file_path", ""))
        if not tokens:
            tokens = [""]
        for token in tokens:
            path = (ROOT / token) if token else None
            exists = bool(path and path.exists())
            suffix = path.suffix.lower() if path else ""
            size = path.stat().st_size if exists and path else ""
            flags = file_text_flags(path) if exists and path else {key: False for key in KEYWORDS}
            feasibility, safe_action = classify(drilldown, path, exists, flags)
            index = len(rows) + 1
            rows.append(
                {
                    "cache_record_id": f"reference_trend_520_p0_cache_inventory_{index:04d}",
                    "drilldown_record_id": drilldown.get("drilldown_record_id", ""),
                    "queue_record_id": drilldown.get("queue_record_id", ""),
                    "queue_rank": drilldown.get("queue_rank", ""),
                    "university_code": drilldown.get("university_code", ""),
                    "university_name": drilldown.get("university_name", ""),
                    "group_pair_key": drilldown.get("group_pair_key", ""),
                    "group_code": drilldown.get("group_code", ""),
                    "drilldown_lane": drilldown.get("drilldown_lane", ""),
                    "drilldown_priority": drilldown.get("drilldown_priority", ""),
                    "source_url": drilldown.get("source_url", ""),
                    "source_packet_status": drilldown.get("source_packet_status", ""),
                    "raw_file_path_token": token,
                    "cache_path": str(path.relative_to(ROOT)) if path else "",
                    "cache_exists": bool_str(exists),
                    "cache_suffix": suffix,
                    "cache_size_bytes": size,
                    "is_text_like": bool_str(suffix in TEXT_SUFFIXES),
                    "contains_guangxi": bool_str(flags.get("广西", False)),
                    "contains_2025": bool_str(flags.get("2025", False)),
                    "contains_plan_keyword": bool_str(flags.get("招生计划", False) or flags.get("计划", False)),
                    "contains_physics": bool_str(flags.get("物理", False)),
                    "contains_group_keyword": bool_str(flags.get("专业组", False)),
                    "local_cache_feasibility": feasibility,
                    "safe_next_action": safe_action,
                    "expected_output_layer": "local_cache_inventory_or_future_parse_preview_only_not_canonical",
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "p0_local_cache_inventory_only_not_32_school_decision_pool",
                    "evidence_note": "Local filesystem inventory only; no web fetch, no browser replay, no source_packet intake.",
                }
            )

    feasibility_counts = Counter(str(row["local_cache_feasibility"]) for row in rows)
    exists_counts = Counter(str(row["cache_exists"]) for row in rows)
    lane_counts = Counter(str(row["drilldown_lane"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "drilldown_input_rows", "value": len(drilldown_rows), "note": "Rows read from P0 local candidate drilldown queue."},
        {"metric": "cache_inventory_rows", "value": len(rows), "note": "One row per raw_file_path token, plus one metadata row when no raw path exists."},
        {"metric": "cache_exists_true", "value": exists_counts.get("true", 0), "note": ""},
        {"metric": "cache_exists_false", "value": exists_counts.get("false", 0), "note": ""},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
    ]
    rollup_rows += [
        {"metric": f"local_cache_feasibility::{key}", "value": count, "note": ""}
        for key, count in sorted(feasibility_counts.items())
    ]
    rollup_rows += [
        {"metric": f"drilldown_lane::{key}", "value": count, "note": ""}
        for key, count in sorted(lane_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_drilldown_exists",
            "status": "pass" if DRILLDOWN.exists() else "fail",
            "value": str(DRILLDOWN.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "input_drilldown_rows",
            "status": "pass" if len(drilldown_rows) == 60 else "review",
            "value": len(drilldown_rows),
            "note": "Expected 60 from latest drilldown queue.",
        },
        {
            "qa_check": "cache_inventory_rows_generated",
            "status": "pass" if rows else "fail",
            "value": len(rows),
            "note": "",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
    ]

    exclusion_rows: list[dict[str, object]] = [
        {
            "exclusion_record_id": "reference_trend_520_p0_cache_inventory_exclusion_0001",
            "excluded_scope": "remote_fetch_and_browser_replay",
            "excluded_rows": len(rows),
            "reason": "This run only checked local cache paths and did not fetch web/browser/header/cookie/form content.",
        },
        {
            "exclusion_record_id": "reference_trend_520_p0_cache_inventory_exclusion_0002",
            "excluded_scope": "reference_trend_intake_canonical_ml",
            "excluded_rows": len(rows),
            "reason": "Cache inventory is evidence routing only and cannot create intake/canonical/ML rows.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusion_rows


def write_doc(rows: list[dict[str, object]]) -> None:
    feasibility_counts = Counter(str(row["local_cache_feasibility"]) for row in rows)
    lines = [
        "# Reference Trend 520 P0 Local Cache Inventory",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: verify local cache availability for P0 local candidate drilldown rows and prevent parsing attempts against missing files.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Coverage",
        "",
        f"- Cache inventory rows: {len(rows)}",
        f"- Existing cache files: {sum(1 for row in rows if row['cache_exists'] == 'true')}",
        f"- Missing/no-cache rows: {sum(1 for row in rows if row['cache_exists'] == 'false')}",
        "",
        "## Feasibility Rollup",
        "",
    ]
    for key, count in sorted(feasibility_counts.items()):
        lines.append(f"- {key}: {count}")
    lines += [
        "",
        "## Boundary",
        "",
        "This artifact is local-cache evidence only. It does not fetch the web, does not create source_packet parse rows, and does not open reference_trend_pool/canonical/ML or the 32-school decision_pool.",
    ]
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 102. 2026-05-16 P0 local cache inventory"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    feasibility_counts = Counter(str(row["local_cache_feasibility"]) for row in rows)
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            "\n\n"
            f"{marker}\n\n"
            "已新增 P0 local cache inventory：\n\n"
            f"- `{OUT.relative_to(ROOT)}`\n"
            f"- `{ROLLUP.relative_to(ROOT)}`\n"
            f"- `{QA.relative_to(ROOT)}`\n"
            f"- `{EXCLUSION.relative_to(ROOT)}`\n"
            f"- `{DOC.relative_to(ROOT)}`\n\n"
            f"覆盖结果：从 60 条 P0 local drilldown rows 派生 {len(rows)} 条 cache inventory rows；"
            f"本地缓存存在 {sum(1 for row in rows if row['cache_exists'] == 'true')} 条，缺失/无缓存 {sum(1 for row in rows if row['cache_exists'] == 'false')} 条。"
            + "；".join(f"{key}={count}" for key, count in sorted(feasibility_counts.items()))
            + "。\n\n"
            "准入边界：本轮只做本地缓存路径存在性和轻量文本关键词盘点，不执行联网抓取，不生成 source_packet parse rows，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。\n"
        )


def main() -> None:
    rows, rollup_rows, qa_rows, exclusion_rows = build()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusion_rows, ["exclusion_record_id", "excluded_scope", "excluded_rows", "reason"])
    write_doc(rows)
    append_handoff(rows)


if __name__ == "__main__":
    main()
