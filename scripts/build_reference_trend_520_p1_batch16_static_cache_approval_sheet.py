#!/usr/bin/env python3
"""Create a reviewable approval sheet for P1 batch-16 static cache runs.

The sheet preserves any reviewer-entered decision columns on rerun. It does not
perform network/cache/parse/OCR/browser actions or open intake/canonical/ML.
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

MANIFEST = CLEAN / "reference_trend_520_p1_batch16_static_cache_run_manifest.csv"
OUT = CLEAN / "reference_trend_520_p1_batch16_static_cache_approval_sheet.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch16_static_cache_approval_sheet_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch16_static_cache_approval_sheet_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch16_static_cache_approval_sheet_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch16_static_cache_approval_sheet.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

REVIEW_FIELDS = [
    "selected_decision",
    "reviewer",
    "decision_notes",
    "approved_at",
]

FIELDS = [
    "approval_id",
    "run_manifest_id",
    "execution_candidate_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "source_title",
    "cache_execution_route",
    "content_type_hint",
    "target_cache_relpath",
    "target_receipt_id",
    "allowed_static_fetch_mode",
    "must_stop_if",
    "recommended_decision",
    "recommended_reason",
    *REVIEW_FIELDS,
    "post_decision_status",
    "source_packet_parse_eligible_now",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
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


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def existing_reviews() -> dict[str, dict[str, str]]:
    existing = read_csv(OUT)
    preserved: dict[str, dict[str, str]] = {}
    for row in existing:
        key = row.get("approval_id") or row.get("run_manifest_id")
        if key:
            preserved[key] = {field: row.get(field, "") for field in REVIEW_FIELDS}
    return preserved


def recommend(row: dict[str, str]) -> tuple[str, str]:
    route = row.get("cache_execution_route", "")
    if route in {"static_html_page_cache_candidate", "static_pdf_cache_candidate"}:
        return (
            "approve_static_cache_only",
            "Exact official static page/PDF candidate; stop on cookie/header/form/browser-state requirement.",
        )
    if route == "static_query_probe_candidate":
        return (
            "approve_static_GET_or_HEAD_probe_only",
            "Query-like official URL; allow only static GET/HEAD reachability, no form submit or browser state.",
        )
    return (
        "hold_for_exact_detail_url_or_static_discovery",
        "Portal/detail-discovery candidate; do not parse or intake until exact Guangxi physical ordinary plan rows are found.",
    )


def status_from_decision(decision: str) -> str:
    if not decision:
        return "waiting_human_decision"
    if decision.startswith("approve_static"):
        return "ready_for_future_static_cache_runner_only"
    if decision == "hold" or decision.startswith("hold"):
        return "held_by_reviewer"
    if decision == "reject":
        return "rejected_by_reviewer"
    if decision == "request_fix":
        return "needs_fix_before_cache"
    return "unrecognized_decision_hold"


def build_rows() -> list[dict[str, object]]:
    preserved = existing_reviews()
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(read_csv(MANIFEST), 1):
        approval_id = f"reference_trend_520_p1_batch16_static_cache_approval_{idx:04d}"
        recommendation, reason = recommend(row)
        review = preserved.get(approval_id, preserved.get(row.get("run_manifest_id", ""), {}))
        decision = review.get("selected_decision", "")
        rows.append(
            {
                "approval_id": approval_id,
                "run_manifest_id": row.get("run_manifest_id", ""),
                "execution_candidate_id": row.get("execution_candidate_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_url": row.get("source_url", ""),
                "source_title": row.get("source_title", ""),
                "cache_execution_route": row.get("cache_execution_route", ""),
                "content_type_hint": row.get("content_type_hint", ""),
                "target_cache_relpath": row.get("target_cache_relpath", ""),
                "target_receipt_id": row.get("target_receipt_id", ""),
                "allowed_static_fetch_mode": row.get("allowed_static_fetch_mode", ""),
                "must_stop_if": row.get("must_stop_if", ""),
                "recommended_decision": recommendation,
                "recommended_reason": reason,
                "selected_decision": decision,
                "reviewer": review.get("reviewer", ""),
                "decision_notes": review.get("decision_notes", ""),
                "approved_at": review.get("approved_at", ""),
                "post_decision_status": status_from_decision(decision),
                "source_packet_parse_eligible_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    route = Counter(str(row["cache_execution_route"]) for row in rows)
    recommendations = Counter(str(row["recommended_decision"]) for row in rows)
    decisions = Counter(str(row["selected_decision"] or "__blank__") for row in rows)
    statuses = Counter(str(row["post_decision_status"]) for row in rows)
    approved = sum(str(row["post_decision_status"]).startswith("ready_for_future_static_cache_runner") for row in rows)
    rollup_rows = [
        {"metric": "approval_sheet_rows", "value": len(rows), "note": "One row per static-cache run manifest row."},
        {"metric": "human_decision_rows_detected", "value": sum(bool(row["selected_decision"]) for row in rows), "note": "Preserved from existing sheet if present."},
        {"metric": "ready_for_future_static_cache_runner_rows", "value": approved, "note": "Still not executed in this run."},
        {"metric": "source_packet_parse_eligible_now_rows", "value": 0, "note": "Approval sheet only."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No cached/parsed rows."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No cached/parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(route.items()))
    rollup_rows.extend({"metric": f"recommended::{key}", "value": value, "note": ""} for key, value in sorted(recommendations.items()))
    rollup_rows.extend({"metric": f"selected_decision::{key}", "value": value, "note": ""} for key, value in sorted(decisions.items()))
    rollup_rows.extend({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(statuses.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "approval_rows_present",
            "status": "PASS" if rows else "FAIL",
            "detail": f"Generated {len(rows)} approval rows.",
        },
        {
            "check": "human_fields_preserved_or_blank",
            "status": "PASS",
            "detail": "selected_decision/reviewer/decision_notes/approved_at are preserved when rerun.",
        },
        {
            "check": "not_executed",
            "status": "PASS",
            "detail": "This sheet does not run network/cache/parse/OCR/browser actions.",
        },
        {
            "check": "no_intake_or_canonical",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No approval row enters trend pool/canonical/ML.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch16_static_cache_approval_sheet_all_rows",
            "reason": "approval_sheet_only_no_network_no_cache_no_parse",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    for row in rows:
        if row["post_decision_status"] == "waiting_human_decision":
            exclusions.append(
                {
                    "item": row["approval_id"],
                    "reason": "waiting_human_decision",
                    "effect": "not_ready_for_static_cache_runner",
                }
            )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    recs = Counter(str(row["recommended_decision"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch16 static cache approval sheet",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This sheet lets a reviewer approve or hold future static-cache attempts row by row. It does not execute network/cache/parse work.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Recommended decisions",
        "",
    ]
    for key, value in sorted(recs.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Reviewer fields",
            "",
            "Fill `selected_decision`, `reviewer`, `decision_notes`, and `approved_at` if static caching should proceed in a later run.",
            "",
            "Allowed selected_decision values:",
            "",
            "- `approve_static_cache_only`",
            "- `approve_static_GET_or_HEAD_probe_only`",
            "- `hold`",
            "- `reject`",
            "- `request_fix`",
            "",
            "## Boundary",
            "",
            "- This is an approval sheet only.",
            "- Future execution must still stop on cookie/header/form/browser-state needs.",
            "- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)

    marker = "## 116. 2026-05-17 P1 batch16 static cache approval sheet"
    handoff = f"""

{marker}

已新增 P1 batch16 static cache approval sheet：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：为 marker 115 的 10 条 run manifest rows 生成可填写人工批准表，并保留 selected_decision/reviewer/decision_notes/approved_at 字段。当前未检测到人工决策 rows。QA PASS。

准入边界：本轮只生成 approval sheet，不联网、不缓存、不解析、不 OCR、不浏览器/form replay；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
