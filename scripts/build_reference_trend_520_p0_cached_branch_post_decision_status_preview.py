#!/usr/bin/env python3
"""Preview post-decision status for P0 cached branch approvals.

This script reads the human decision sheet and classifies each row as waiting,
approved-pending-execution, rejected, hold, or request-fix. It does not execute
approved actions, replay forms, capture assets, OCR, create source_packet rows,
write intake, or touch canonical/ML.
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

DECISION_SHEET = CLEAN / "reference_trend_520_p0_cached_branch_human_approval_decision_sheet.csv"
OUT = CLEAN / "reference_trend_520_p0_cached_branch_post_decision_status_preview.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_cached_branch_post_decision_status_preview_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_cached_branch_post_decision_status_preview_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_cached_branch_post_decision_status_preview_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_cached_branch_post_decision_status_preview.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

APPROVE_DECISIONS = {
    "approve_browser_form_replay",
    "approve_browser_asset_capture",
    "manual_upload_asset",
    "accept_pdf_table_mapping_after_manual_check",
}

FIELDS = [
    "status_preview_id",
    "approval_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "approval_lane",
    "approval_priority",
    "candidate_kind",
    "candidate_value",
    "source_url",
    "selected_decision",
    "reviewer",
    "decision_time_iso",
    "decision_notes",
    "decision_presence_status",
    "post_decision_status_route",
    "ready_for_execution",
    "requires_user_action",
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


def route_for(row: dict[str, str]) -> tuple[str, str, str, str]:
    decision = (row.get("selected_decision") or "").strip()
    lane = row.get("approval_lane", "")
    if not decision:
        return (
            "waiting_human_decision",
            "false",
            "true",
            "Wait for selected_decision/reviewer/decision_notes before any replay, capture, OCR, or intake preview.",
        )
    if decision in APPROVE_DECISIONS:
        if lane == "browser_form_replay_approval":
            return (
                "approved_browser_form_replay_pending_explicit_execution",
                "false",
                "true",
                "Before execution, confirm browser/form replay remains approved for this exact endpoint and output only source_packet/preview/QA.",
            )
        if lane == "cached_asset_capture_or_manual_upload":
            return (
                "approved_asset_capture_or_upload_pending_preview",
                "false",
                "true",
                "Capture/upload the exact official asset, then generate only asset/OCR preview and QA.",
            )
        if lane == "manual_pdf_table_layout_qa":
            return (
                "accepted_pdf_layout_mapping_pending_preview",
                "false",
                "true",
                "Generate only PDF table-layout intake preview after checking notes contain Guangxi column and ordinary/special boundary rationale.",
            )
        return ("approved_pending_manual_execution", "false", "true", "Route approved item manually.")
    if decision.startswith("reject"):
        return ("rejected_by_human", "false", "false", "Keep rejected item out of source_packet/intake.")
    if decision == "hold":
        return ("held_by_human", "false", "true", "Keep item on hold until reviewer provides a new decision.")
    if decision == "request_fix":
        return ("request_fix_by_human", "false", "true", "Prepare a fix request preview; do not execute source access.")
    return ("unrecognized_decision_needs_review", "false", "true", "Review selected_decision value before routing.")


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    decision_rows = read_csv(DECISION_SHEET)
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for source in decision_rows:
        route, ready, requires_user_action, safe_next = route_for(source)
        decision = (source.get("selected_decision") or "").strip()
        has_human_fields = any(
            (source.get(field) or "").strip()
            for field in ["selected_decision", "reviewer", "decision_time_iso", "decision_notes"]
        )
        rows.append(
            {
                "approval_record_id": source.get("approval_record_id", ""),
                "queue_rank": source.get("queue_rank", ""),
                "university_code": source.get("university_code", ""),
                "university_name": source.get("university_name", ""),
                "group_pair_key": source.get("group_pair_key", ""),
                "group_code": source.get("group_code", ""),
                "approval_lane": source.get("approval_lane", ""),
                "approval_priority": source.get("approval_priority", ""),
                "candidate_kind": source.get("candidate_kind", ""),
                "candidate_value": source.get("candidate_value", ""),
                "source_url": source.get("source_url", ""),
                "selected_decision": decision,
                "reviewer": source.get("reviewer", ""),
                "decision_time_iso": source.get("decision_time_iso", ""),
                "decision_notes": source.get("decision_notes", ""),
                "decision_presence_status": "human_fields_present" if has_human_fields else "blank_waiting",
                "post_decision_status_route": route,
                "ready_for_execution": ready,
                "requires_user_action": requires_user_action,
                "safe_next_action": safe_next,
                "expected_output_layer": "post_decision_status_preview_only_not_source_packet_not_canonical",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "p0_cached_branch_post_decision_status_only_not_32_school_decision_pool",
                "evidence_note": "Status preview only; no replay, asset capture, OCR, source_packet parse, intake, canonical, or ML writes.",
            }
        )

    for index, row in enumerate(rows, start=1):
        row["status_preview_id"] = f"reference_trend_520_p0_cached_branch_status_{index:04d}"

    route_counts = Counter(str(row["post_decision_status_route"]) for row in rows)
    decision_counts = Counter(str(row["selected_decision"] or "__blank__") for row in rows)
    lane_counts = Counter(str(row["approval_lane"]) for row in rows)
    human_rows = sum(1 for row in rows if row["decision_presence_status"] == "human_fields_present")
    ready_rows = sum(1 for row in rows if row["ready_for_execution"] == "true")

    rollup_rows: list[dict[str, object]] = [
        {"metric": "decision_sheet_rows_read", "value": len(decision_rows), "note": str(DECISION_SHEET.relative_to(ROOT))},
        {"metric": "status_preview_rows", "value": len(rows), "note": "One status row per decision sheet row."},
        {"metric": "human_decision_rows_detected", "value": human_rows, "note": "Rows with selected_decision/reviewer/decision_notes/time."},
        {"metric": "ready_for_execution_rows", "value": ready_rows, "note": "This preview never executes rows."},
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
    rollup_rows += [
        {"metric": f"status_route::{key}", "value": count, "note": ""}
        for key, count in sorted(route_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "decision_sheet_exists",
            "status": "pass" if DECISION_SHEET.exists() else "fail",
            "value": str(DECISION_SHEET.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "one_status_row_per_decision_row",
            "status": "pass" if len(rows) == len(decision_rows) else "fail",
            "value": f"decision={len(decision_rows)}; status={len(rows)}",
            "note": "",
        },
        {
            "qa_check": "no_execution_marked_ready_without_manual_decision",
            "status": "pass" if ready_rows == 0 else "warn",
            "value": ready_rows,
            "note": "Execution remains gated even after a future approval.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
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
    route_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("status_route::")
    )
    decision_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("selected_decision::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 Cached Branch Post-Decision Status Preview

Date: {date.today().isoformat()}

Scope: status preview after reading the human approval decision sheet. This artifact shows whether any approval is ready for later execution, while keeping all execution and intake gates closed.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_post_decision_status_preview.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_exclusion_log.csv`

## Coverage

- Status preview rows: {len(rows)}
- QA status: {qa_status}

## Selected Decisions

{decision_lines or "- none"}

## Status Routes

{route_lines or "- none"}

## Boundary

This status preview does not execute approved actions. It does not run browser/form replay, capture assets, OCR or parse source packets, write reference trend intake, or touch canonical/ML or the 32-school decision_pool.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 110. 2026-05-17 P0 cached branch post-decision status preview"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    route_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("status_route::")
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

已新增 P0 cached branch post-decision status preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_post_decision_status_preview.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_branch_post_decision_status_preview.md`

覆盖结果：读取 109 决策表并生成 {len(rows)} 条 post-decision status rows；当前 selected_decision 分布：{decision_summary or 'none'}；status route 分布：{route_summary or 'none'}。QA {qa_status}。当前没有可执行授权行。

准入边界：本轮只做决策状态预览，不执行联网、浏览器/form replay、资产捕获、OCR、source_packet parse 或 reference trend intake；canonical/ML、32 所 decision_pool 均继续关闭。
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
    print(f"wrote {len(rows)} post-decision status rows")


if __name__ == "__main__":
    main()
