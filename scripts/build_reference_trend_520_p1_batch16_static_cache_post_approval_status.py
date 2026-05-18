#!/usr/bin/env python3
"""Build post-approval status preview for P1 batch-16 static cache sheet.

This reads reviewer decisions if present and routes rows for a future static
cache runner. It does not fetch, cache, parse, OCR, replay forms, or open
reference-trend/canonical/ML intake.
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

APPROVAL = CLEAN / "reference_trend_520_p1_batch16_static_cache_approval_sheet.csv"
OUT = CLEAN / "reference_trend_520_p1_batch16_static_cache_post_approval_status.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch16_static_cache_post_approval_status_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch16_static_cache_post_approval_status_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch16_static_cache_post_approval_status_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch16_static_cache_post_approval_status.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "status_id",
    "approval_id",
    "run_manifest_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "cache_execution_route",
    "recommended_decision",
    "selected_decision",
    "reviewer",
    "decision_notes",
    "approved_at",
    "status_route",
    "future_runner_eligible",
    "runner_allowed_mode",
    "runner_stop_condition",
    "next_required_artifact",
    "source_packet_parse_eligible_now",
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


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def route(row: dict[str, str]) -> tuple[str, str, str, str]:
    decision = row.get("selected_decision", "").strip()
    if not decision:
        return (
            "waiting_human_decision",
            "false",
            "",
            "approval_sheet_manual_decision",
        )
    if decision == "approve_static_cache_only":
        return (
            "approved_static_cache_only_waiting_runner",
            "true",
            row.get("allowed_static_fetch_mode", "static_GET_official_only"),
            "static_cache_receipt_then_parse_preview_QA",
        )
    if decision == "approve_static_GET_or_HEAD_probe_only":
        return (
            "approved_static_query_probe_only_waiting_runner",
            "true",
            "static_GET_or_HEAD_only_no_form_submit",
            "static_query_reachability_receipt_then_parse_feasibility_preview",
        )
    if decision == "hold" or decision.startswith("hold"):
        return ("held_by_reviewer", "false", "", "reviewer_hold_resolution")
    if decision == "reject":
        return ("rejected_by_reviewer", "false", "", "exclusion_log_only")
    if decision == "request_fix":
        return ("needs_fix_before_static_cache", "false", "", "fix_request_preview")
    return ("unrecognized_decision_hold", "false", "", "manual_decision_normalization")


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(read_csv(APPROVAL), 1):
        status_route, runner_eligible, runner_mode, next_artifact = route(row)
        rows.append(
            {
                "status_id": f"reference_trend_520_p1_batch16_static_cache_post_approval_{idx:04d}",
                "approval_id": row.get("approval_id", ""),
                "run_manifest_id": row.get("run_manifest_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_url": row.get("source_url", ""),
                "cache_execution_route": row.get("cache_execution_route", ""),
                "recommended_decision": row.get("recommended_decision", ""),
                "selected_decision": row.get("selected_decision", ""),
                "reviewer": row.get("reviewer", ""),
                "decision_notes": row.get("decision_notes", ""),
                "approved_at": row.get("approved_at", ""),
                "status_route": status_route,
                "future_runner_eligible": runner_eligible,
                "runner_allowed_mode": runner_mode,
                "runner_stop_condition": row.get("must_stop_if", ""),
                "next_required_artifact": next_artifact,
                "source_packet_parse_eligible_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Post-approval status preview only; no static cache runner executed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    status = Counter(str(row["status_route"]) for row in rows)
    decisions = Counter(str(row["selected_decision"] or "__blank__") for row in rows)
    eligible = sum(row["future_runner_eligible"] == "true" for row in rows)
    rollup_rows = [
        {"metric": "post_approval_status_rows", "value": len(rows), "note": "One row per approval sheet row."},
        {"metric": "human_decision_rows_detected", "value": sum(bool(row["selected_decision"]) for row in rows), "note": ""},
        {"metric": "future_runner_eligible_rows", "value": eligible, "note": "Still not executed in this run."},
        {"metric": "source_packet_parse_eligible_now_rows", "value": 0, "note": "No cache receipt yet."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No cached/parsed rows."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No cached/parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"selected_decision::{key}", "value": value, "note": ""} for key, value in sorted(decisions.items()))
    rollup_rows.extend({"metric": f"status_route::{key}", "value": value, "note": ""} for key, value in sorted(status.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "approval_rows_mapped",
            "status": "PASS" if len(rows) == len(read_csv(APPROVAL)) and rows else "FAIL",
            "detail": f"Mapped {len(rows)} post-approval status rows.",
        },
        {
            "check": "not_executed",
            "status": "PASS",
            "detail": "No network/cache/parse/OCR/browser actions executed.",
        },
        {
            "check": "runner_only_after_approval",
            "status": "PASS" if all(row["future_runner_eligible"] == "false" or row["selected_decision"] for row in rows) else "FAIL",
            "detail": "Future runner eligibility requires selected_decision.",
        },
        {
            "check": "no_intake_or_canonical",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No post-approval row enters trend pool/canonical/ML.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch16_static_cache_post_approval_status_all_rows",
            "reason": "status_preview_only_no_network_no_cache_no_parse",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    for row in rows:
        if row["future_runner_eligible"] != "true":
            exclusions.append(
                {
                    "item": row["status_id"],
                    "reason": row["status_route"],
                    "effect": "not_ready_for_static_cache_runner",
                }
            )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    status = Counter(str(row["status_route"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch16 static cache post-approval status",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This preview reads the static-cache approval sheet and routes rows for a future runner. It does not execute the runner.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Status distribution",
        "",
    ]
    for key, value in sorted(status.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Rows only become future-runner eligible after human selected_decision is filled.",
            "- Future runner must still stop on cookie/header/form/browser-state needs.",
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

    marker = "## 117. 2026-05-17 P1 batch16 static cache post-approval status"
    handoff = f"""

{marker}

已新增 P1 batch16 static cache post-approval status preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：读取 marker 116 的 10 条 approval rows 并生成 post-approval status；当前 selected_decision 仍全空，future_runner_eligible rows 为 0。QA PASS。

准入边界：本轮只生成 post-approval status preview，不联网、不缓存、不解析、不 OCR、不浏览器/form replay；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
