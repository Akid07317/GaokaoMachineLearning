#!/usr/bin/env python3
"""Create a human decision sheet for P0 cached-branch approvals.

The sheet is intentionally separate from the approval queue so operators can
fill decisions without editing the generated queue. Existing filled decisions
are preserved on rerun. This script does not perform browser replay, asset
capture, OCR, source_packet parsing, intake, canonical, or ML writes.
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

QUEUE = CLEAN / "reference_trend_520_p0_cached_branch_human_approval_queue.csv"
OUT = CLEAN / "reference_trend_520_p0_cached_branch_human_approval_decision_sheet.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_cached_branch_human_approval_decision_sheet_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_cached_branch_human_approval_decision_sheet_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_cached_branch_human_approval_decision_sheet_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_cached_branch_human_approval_decision_sheet.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

HUMAN_FIELDS = [
    "suggested_decision_options",
    "selected_decision",
    "reviewer",
    "decision_time_iso",
    "decision_notes",
    "approval_acceptance_status",
    "post_decision_next_route",
    "post_decision_output_layer",
]

FIELDS = [
    "approval_record_id",
    "source_artifact",
    "source_record_id",
    "source_queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "approval_lane",
    "approval_priority",
    "approval_required",
    "approval_prompt",
    "candidate_kind",
    "candidate_value",
    "candidate_local_path",
    "source_url",
    "cache_path",
    "raw_source_row_count",
    "duplicate_or_collapsed_count",
    "blocked_reason",
    "safe_next_action",
    "expected_output_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
    *HUMAN_FIELDS,
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


def decision_options(lane: str) -> str:
    if lane == "browser_form_replay_approval":
        return "approve_browser_form_replay|reject_endpoint|hold|request_fix"
    if lane == "cached_asset_capture_or_manual_upload":
        return "approve_browser_asset_capture|manual_upload_asset|reject_asset|hold|request_fix"
    if lane == "manual_pdf_table_layout_qa":
        return "accept_pdf_table_mapping_after_manual_check|reject_pdf_mapping|hold|request_fix"
    return "approve|reject|hold|request_fix"


def next_route(lane: str) -> str:
    if lane == "browser_form_replay_approval":
        return "if_approved_capture_response_to_source_packet_preview_only"
    if lane == "cached_asset_capture_or_manual_upload":
        return "if_approved_generate_asset_or_ocr_preview_only"
    if lane == "manual_pdf_table_layout_qa":
        return "if_accepted_generate_pdf_table_layout_intake_preview_only"
    return "manual_review_required"


def read_existing_decisions() -> dict[str, dict[str, str]]:
    existing_rows = read_csv(OUT)
    preserved: dict[str, dict[str, str]] = {}
    for row in existing_rows:
        key = row.get("approval_record_id", "")
        if not key:
            continue
        preserved[key] = {field: row.get(field, "") for field in HUMAN_FIELDS}
    return preserved


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    queue_rows = read_csv(QUEUE)
    preserved = read_existing_decisions()
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for source in queue_rows:
        record = {field: source.get(field, "") for field in FIELDS if field not in HUMAN_FIELDS}
        lane = source.get("approval_lane", "")
        record.update(
            {
                "suggested_decision_options": decision_options(lane),
                "selected_decision": "",
                "reviewer": "",
                "decision_time_iso": "",
                "decision_notes": "",
                "approval_acceptance_status": "waiting_human_decision",
                "post_decision_next_route": next_route(lane),
                "post_decision_output_layer": "post_human_decision_preview_only_not_canonical",
            }
        )
        existing = preserved.get(source.get("approval_record_id", ""), {})
        for field in HUMAN_FIELDS:
            if existing.get(field):
                record[field] = existing[field]
        rows.append(record)

    queue_ids = {row.get("approval_record_id", "") for row in queue_rows}
    for existing_id in sorted(set(preserved) - queue_ids):
        exclusions.append(
            {
                "record_id": existing_id,
                "university_name": "",
                "reason": "existing_decision_row_not_in_current_queue",
                "detail": "Preserved source queue no longer includes this approval_record_id.",
            }
        )

    lane_counts = Counter(str(row.get("approval_lane", "")) for row in rows)
    decision_counts = Counter(str(row.get("selected_decision", "") or "__blank__") for row in rows)
    filled_rows = sum(
        1
        for row in rows
        if any(str(row.get(field, "")).strip() for field in ["selected_decision", "reviewer", "decision_notes"])
    )

    rollup_rows: list[dict[str, object]] = [
        {"metric": "approval_queue_rows_read", "value": len(queue_rows), "note": str(QUEUE.relative_to(ROOT))},
        {"metric": "decision_sheet_rows", "value": len(rows), "note": "One row per approval queue row."},
        {"metric": "existing_human_decision_rows_preserved", "value": filled_rows, "note": "Rows with selected_decision/reviewer/decision_notes retained."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
        {"metric": "network_browser_or_replay_used", "value": "false", "note": "This builder only reads local CSV artifacts."},
    ]
    rollup_rows += [
        {"metric": f"approval_lane::{key}", "value": count, "note": ""}
        for key, count in sorted(lane_counts.items())
    ]
    rollup_rows += [
        {"metric": f"selected_decision::{key}", "value": count, "note": ""}
        for key, count in sorted(decision_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "approval_queue_exists",
            "status": "pass" if QUEUE.exists() else "fail",
            "value": str(QUEUE.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "one_decision_row_per_queue_row",
            "status": "pass" if len(rows) == len(queue_rows) else "fail",
            "value": f"queue={len(queue_rows)}; sheet={len(rows)}",
            "note": "",
        },
        {
            "qa_check": "human_fields_available",
            "status": "pass" if all(field in FIELDS for field in HUMAN_FIELDS) else "fail",
            "value": "|".join(HUMAN_FIELDS),
            "note": "",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row.get("canonical_ml_entry_open") == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "network_browser_or_replay_used",
            "status": "pass",
            "value": "false",
            "note": "No live access was performed.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    lane_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("approval_lane::")
    )
    decision_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("selected_decision::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 Cached Branch Human Approval Decision Sheet

Date: {date.today().isoformat()}

Scope: human-fillable decision sheet for the P0 cached branch approval queue. Fill `selected_decision`, `reviewer`, `decision_time_iso`, and `decision_notes` here rather than editing the generated approval queue.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_decision_sheet.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_exclusion_log.csv`

## Coverage

- Decision sheet rows: {len(rows)}
- QA status: {qa_status}

## Approval Lanes

{lane_lines or "- none"}

## Current Decisions

{decision_lines or "- none"}

## Boundary

This sheet is a human decision surface only. It does not approve actions by itself, does not run browser/form replay, does not capture assets, does not OCR or parse source packets, and does not write reference trend intake, canonical, ML, or 32-school decision_pool rows.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 109. 2026-05-17 P0 cached branch human approval decision sheet"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    lane_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("approval_lane::")
    )
    decision_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("selected_decision::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 cached branch human approval decision sheet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_decision_sheet.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_branch_human_approval_decision_sheet.md`

覆盖结果：为 108 approval queue 生成 {len(rows)} 条可填写人工决策 rows；lane 分布：{lane_summary or 'none'}；当前 selected_decision 分布：{decision_summary or 'none'}。QA {qa_status}。若后续人工填写 selected_decision/reviewer/decision_notes，脚本重跑会保留已填字段。

准入边界：本轮只生成可填写人工决策表，不执行联网、浏览器/form replay、资产捕获、OCR、source_packet parse 或 reference trend intake；canonical/ML、32 所 decision_pool 均继续关闭。
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
    print(f"wrote {len(rows)} cached branch decision rows")


if __name__ == "__main__":
    main()
