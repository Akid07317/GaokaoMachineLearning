#!/usr/bin/env python3
"""Build a P0 source-discovery next-action board from queue reconciliation.

This is a routing artifact only. It does not fetch the web, does not write
canonical/ML inputs, and does not add rows to the 32-school decision pool.
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

RECONCILIATION = CLEAN / "reference_trend_520_plan_source_queue_status_reconciliation.csv"
OUT = CLEAN / "reference_trend_520_p0_source_discovery_next_actions.csv"
APPROVAL = CLEAN / "reference_trend_520_p0_source_discovery_manual_approval_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_source_discovery_next_actions_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_source_discovery_next_actions_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_source_discovery_next_actions_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_source_discovery_next_actions.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

P0_PRIORITY = "P0_plan_source_packet_urgent"

BLOCKED_PATTERN = re.compile(
    r"(captcha|blocked|timeout|shortlink|reachability|backoff|search_backoff|"
    r"no_first_party|no_structured_official_plan_candidate_found|404)",
    re.IGNORECASE,
)

NEXT_ACTION_FIELDS = [
    "action_record_id",
    "upstream_record_id",
    "queue_record_id",
    "queue_rank",
    "source_packet_priority",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "reconciled_status",
    "confidence_tier",
    "action_lane",
    "action_priority",
    "approval_required",
    "approval_reason",
    "blocked_without_approval",
    "safe_next_action",
    "expected_output_layer",
    "discovery_rows",
    "parse_rows",
    "mapping_rows",
    "plan_count_parse_rows",
    "group_code_parse_rows",
    "score_rank_parse_rows",
    "artifact_paths",
    "source_status_summary",
    "mapping_status_summary",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]

APPROVAL_FIELDS = [
    "approval_record_id",
    "action_record_id",
    "queue_record_id",
    "queue_rank",
    "source_packet_priority",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "approval_category",
    "approval_priority",
    "approval_status",
    "selected_decision",
    "reviewer",
    "decision_notes",
    "reviewed_at",
    "approval_reason",
    "blocked_without_approval",
    "safe_next_action_if_approved",
    "safe_next_action_if_denied",
    "expected_output_layer",
    "artifact_paths",
    "source_status_summary",
    "mapping_status_summary",
    "reference_trend_pool_eligible_before_approval",
    "calibration_eligible_before_approval",
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


def boolish(value: object) -> str:
    return "true" if str(value).strip().lower() in {"true", "1", "yes"} else "false"


def classify(row: dict[str, str]) -> dict[str, str]:
    status = row.get("reconciled_status", "")
    status_summary = row.get("source_status_summary", "")
    next_action = row.get("reconciled_next_action", "")
    searchable = f"{status_summary} {next_action}"

    if status == "needs_official_source_discovery":
        return {
            "action_lane": "live_official_source_discovery_approval",
            "action_priority": "P0A_requires_approval_before_live_search",
            "approval_required": "yes_live_official_discovery",
            "approval_reason": "No local official source candidate or source packet is reconciled for this P0 row.",
            "blocked_without_approval": "true",
            "safe_next_action": "Request explicit approval for web or browser official-source discovery; write results only to source_packet/reachability preview.",
        }

    if status == "source_candidate_exists_not_structured":
        if BLOCKED_PATTERN.search(searchable):
            return {
                "action_lane": "blocked_existing_candidate_needs_approval_or_exact_url",
                "action_priority": "P0B_existing_candidate_blocked",
                "approval_required": "yes_for_browser_header_cookie_or_manual_route",
                "approval_reason": "A local candidate exists, but the recorded route is blocked, timed out, backoff-only, captcha-gated, or missing a structured official plan row.",
                "blocked_without_approval": "true_for_live_retry_false_for_local_review",
                "safe_next_action": "Do not blind-search again; request exact URL or browser/header/cookie/manual approval, then create a source_packet preview only.",
            }
        return {
            "action_lane": "existing_candidate_parse_or_endpoint_drilldown",
            "action_priority": "P0C_local_candidate_before_new_search",
            "approval_required": "no_for_cached_local_parse_conditional_for_live_retry",
            "approval_reason": "A candidate exists; try local parse or endpoint drilldown first.",
            "blocked_without_approval": "false_for_local_parse_true_for_live_retry",
            "safe_next_action": "Parse cached candidate or inspect known endpoint shape; avoid new source discovery unless local parse fails.",
        }

    if status == "source_packet_parse_exists_but_field_gaps_remain":
        return {
            "action_lane": "parse_gap_review_before_new_search",
            "action_priority": "P0D_parse_gap_review",
            "approval_required": "no_for_local_gap_review",
            "approval_reason": "A parse preview exists but field coverage is incomplete.",
            "blocked_without_approval": "false",
            "safe_next_action": "Review source_packet parse gaps, source_contains_* fields, and whether plan_count/group_code/min_score can be recovered locally.",
        }

    if status == "plan_count_source_packet_exists_hold_for_group_mapping":
        return {
            "action_lane": "plan_count_available_group_mapping_hold",
            "action_priority": "P0E_group_mapping_before_intake",
            "approval_required": "human_mapping_acceptance_required",
            "approval_reason": "Official plan count source packet exists, but group mapping is not accepted.",
            "blocked_without_approval": "true_for_intake_false_for_queueing",
            "safe_next_action": "Prepare or reuse group mapping acceptance sheet; do not open intake/canonical until accepted.",
        }

    if status == "mapping_workbench_exists_hold_for_group_acceptance":
        return {
            "action_lane": "group_mapping_human_acceptance_hold",
            "action_priority": "P0E_group_mapping_before_intake",
            "approval_required": "human_mapping_acceptance_required",
            "approval_reason": "Group mapping workbench exists and is waiting for human acceptance.",
            "blocked_without_approval": "true_for_intake_false_for_review_packet",
            "safe_next_action": "Route to mapping review packet or acceptance sheet; keep row outside intake/canonical.",
        }

    return {
        "action_lane": "unknown_reconciliation_status",
        "action_priority": "P0Z_manual_triage",
        "approval_required": "manual_triage_required",
        "approval_reason": f"Unhandled reconciliation status: {status}",
        "blocked_without_approval": "true",
        "safe_next_action": "Manual triage before any additional source work.",
    }


def preserve_approval_fields(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    old = {row.get("approval_record_id", ""): row for row in read_csv(APPROVAL)}
    for row in rows:
        old_row = old.get(str(row.get("approval_record_id", "")), {})
        for field in ("selected_decision", "reviewer", "decision_notes", "reviewed_at"):
            if old_row.get(field):
                row[field] = old_row[field]
    return rows


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    source_rows = read_csv(RECONCILIATION)
    p0_rows = [row for row in source_rows if row.get("source_packet_priority") == P0_PRIORITY]
    action_rows: list[dict[str, object]] = []
    approval_rows: list[dict[str, object]] = []

    for index, row in enumerate(p0_rows, start=1):
        cls = classify(row)
        action_record_id = f"reference_trend_520_p0_next_action_{index:04d}"
        base = {
            "action_record_id": action_record_id,
            "upstream_record_id": row.get("record_id", ""),
            "queue_record_id": row.get("queue_record_id", ""),
            "queue_rank": row.get("queue_rank", ""),
            "source_packet_priority": row.get("source_packet_priority", ""),
            "university_code": row.get("university_code", ""),
            "university_name": row.get("university_name", ""),
            "group_pair_key": row.get("group_pair_key", ""),
            "group_code": row.get("group_code", ""),
            "rank_2024": row.get("rank_2024", ""),
            "rank_2025": row.get("rank_2025", ""),
            "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
            "trend_direction": row.get("trend_direction", ""),
            "reconciled_status": row.get("reconciled_status", ""),
            "confidence_tier": row.get("confidence_tier", ""),
            **cls,
            "expected_output_layer": "source_packet_reachability_or_review_preview_only_not_canonical",
            "discovery_rows": row.get("discovery_rows", ""),
            "parse_rows": row.get("parse_rows", ""),
            "mapping_rows": row.get("mapping_rows", ""),
            "plan_count_parse_rows": row.get("plan_count_parse_rows", ""),
            "group_code_parse_rows": row.get("group_code_parse_rows", ""),
            "score_rank_parse_rows": row.get("score_rank_parse_rows", ""),
            "artifact_paths": row.get("artifact_paths", ""),
            "source_status_summary": row.get("source_status_summary", ""),
            "mapping_status_summary": row.get("mapping_status_summary", ""),
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "p0_source_discovery_routing_only_not_32_school_decision_pool",
            "evidence_note": "Derived from plan_source_queue_status_reconciliation; no web fetch performed.",
        }
        action_rows.append(base)

        if cls["blocked_without_approval"].startswith("true") or cls["approval_required"].startswith("yes"):
            approval_rows.append(
                {
                    "approval_record_id": f"reference_trend_520_p0_source_approval_{len(approval_rows)+1:04d}",
                    "action_record_id": action_record_id,
                    "queue_record_id": base["queue_record_id"],
                    "queue_rank": base["queue_rank"],
                    "source_packet_priority": base["source_packet_priority"],
                    "university_code": base["university_code"],
                    "university_name": base["university_name"],
                    "group_pair_key": base["group_pair_key"],
                    "group_code": base["group_code"],
                    "approval_category": cls["action_lane"],
                    "approval_priority": cls["action_priority"],
                    "approval_status": "pending_human_approval",
                    "selected_decision": "",
                    "reviewer": "",
                    "decision_notes": "",
                    "reviewed_at": "",
                    "approval_reason": cls["approval_reason"],
                    "blocked_without_approval": cls["blocked_without_approval"],
                    "safe_next_action_if_approved": cls["safe_next_action"],
                    "safe_next_action_if_denied": "Keep in source reachability/backoff layer; do not retry through terminal curl or enter intake/canonical.",
                    "expected_output_layer": "source_packet_reachability_or_review_preview_only_not_canonical",
                    "artifact_paths": base["artifact_paths"],
                    "source_status_summary": base["source_status_summary"],
                    "mapping_status_summary": base["mapping_status_summary"],
                    "reference_trend_pool_eligible_before_approval": "false",
                    "calibration_eligible_before_approval": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "manual_approval_queue_only_not_32_school_decision_pool",
                    "evidence_note": "Approval unlocks only a downstream source_packet/reachability preview with QA.",
                }
            )

    approval_rows = preserve_approval_fields(approval_rows)

    lane_counts = Counter(row["action_lane"] for row in action_rows)
    status_counts = Counter(row["reconciled_status"] for row in action_rows)
    approval_counts = Counter(row["approval_category"] for row in approval_rows)

    rollup_rows: list[dict[str, object]] = [
        {"metric": "p0_next_action_rows", "value": len(action_rows), "note": "Rows routed from P0 reconciliation."},
        {"metric": "manual_approval_rows", "value": len(approval_rows), "note": "Rows requiring live discovery, browser/header/manual approval, or human mapping acceptance before downstream preview."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "This artifact is a routing layer only."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No row enters reference_trend_pool from this packet."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration eligibility assigned."},
    ]
    rollup_rows += [
        {"metric": f"reconciled_status::{status}", "value": count, "note": ""}
        for status, count in sorted(status_counts.items())
    ]
    rollup_rows += [
        {"metric": f"action_lane::{lane}", "value": count, "note": ""}
        for lane, count in sorted(lane_counts.items())
    ]
    rollup_rows += [
        {"metric": f"approval_category::{category}", "value": count, "note": ""}
        for category, count in sorted(approval_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_reconciliation_exists",
            "status": "pass" if RECONCILIATION.exists() else "fail",
            "value": str(RECONCILIATION.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "p0_rows_routed",
            "status": "pass" if len(action_rows) == 117 else "review",
            "value": len(action_rows),
            "note": "Expected current P0 queue size is 117 from reconciliation rollup.",
        },
        {
            "qa_check": "manual_approval_queue_generated",
            "status": "pass" if approval_rows else "review",
            "value": len(approval_rows),
            "note": "Rows in this file need explicit approval or human acceptance before downstream source work.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in action_rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "decision_pool_boundary",
            "status": "pass" if all("not_32_school_decision_pool" in str(row["decision_pool_boundary"]) for row in action_rows) else "fail",
            "value": "separate",
            "note": "No 32-school decision_pool mutation.",
        },
    ]

    exclusion_rows: list[dict[str, object]] = [
        {
            "exclusion_record_id": "reference_trend_520_p0_next_actions_exclusion_0001",
            "excluded_scope": "canonical_ml_and_decision_pool",
            "excluded_rows": len(action_rows),
            "reason": "Routing layer only; source discovery and approvals cannot directly create canonical/ML/decision_pool rows.",
        },
        {
            "exclusion_record_id": "reference_trend_520_p0_next_actions_exclusion_0002",
            "excluded_scope": "blind_duplicate_discovery",
            "excluded_rows": sum(1 for row in action_rows if row["reconciled_status"] != "needs_official_source_discovery"),
            "reason": "Rows with local candidates, parse previews, or mapping workbench artifacts are routed away from blind duplicate web search.",
        },
    ]

    return action_rows, approval_rows, rollup_rows, qa_rows + exclusion_rows


def write_doc(action_rows: list[dict[str, object]], approval_rows: list[dict[str, object]], rollup_rows: list[dict[str, object]]) -> None:
    lane_counts = Counter(str(row["action_lane"]) for row in action_rows)
    approval_counts = Counter(str(row["approval_category"]) for row in approval_rows)
    lines = [
        "# Reference Trend 520 P0 Source Discovery Next Actions",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: route P0 plan-source queue rows after reconciliation so the project does not keep blind-searching schools that already have local candidates, parse previews, or group-mapping workbenches.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{APPROVAL.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Coverage",
        "",
        f"- P0 next-action rows: {len(action_rows)}",
        f"- Manual/live approval rows: {len(approval_rows)}",
        "",
        "## Action Lane Rollup",
        "",
    ]
    for lane, count in sorted(lane_counts.items()):
        lines.append(f"- {lane}: {count}")
    lines += [
        "",
        "## Approval Queue Rollup",
        "",
    ]
    for category, count in sorted(approval_counts.items()):
        lines.append(f"- {category}: {count}")
    lines += [
        "",
        "## Boundary",
        "",
        "This artifact is non-baseline and non-canonical. Approval unlocks only a downstream `source_packet`, reachability preview, parse preview, or mapping review packet with QA. It does not open canonical/ML and does not merge anything into the 32-school decision_pool.",
    ]
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_handoff(action_rows: list[dict[str, object]], approval_rows: list[dict[str, object]]) -> None:
    marker = "## 100. 2026-05-16 P0 source discovery next actions"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    lane_counts = Counter(str(row["action_lane"]) for row in action_rows)
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            "\n\n"
            f"{marker}\n\n"
            "已新增 P0 source discovery next-actions / manual approval queue：\n\n"
            f"- `{OUT.relative_to(ROOT)}`\n"
            f"- `{APPROVAL.relative_to(ROOT)}`\n"
            f"- `{ROLLUP.relative_to(ROOT)}`\n"
            f"- `{QA.relative_to(ROOT)}`\n"
            f"- `{EXCLUSION.relative_to(ROOT)}`\n"
            f"- `{DOC.relative_to(ROOT)}`\n\n"
            f"覆盖结果：P0 rows {len(action_rows)} 行全部完成路由；manual/live approval rows {len(approval_rows)} 行。"
            + "；".join(f"{lane}={count}" for lane, count in sorted(lane_counts.items()))
            + "。\n\n"
            "准入边界：本轮只做 P0 来源发现路由和人工/浏览器/联网批准队列，不执行联网抓取，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。\n"
        )


def main() -> None:
    action_rows, approval_rows, rollup_rows, qa_and_exclusion = build()
    qa_rows = [row for row in qa_and_exclusion if "qa_check" in row]
    exclusion_rows = [row for row in qa_and_exclusion if "exclusion_record_id" in row]

    write_csv(OUT, action_rows, NEXT_ACTION_FIELDS)
    write_csv(APPROVAL, approval_rows, APPROVAL_FIELDS)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusion_rows, ["exclusion_record_id", "excluded_scope", "excluded_rows", "reason"])
    write_doc(action_rows, approval_rows, rollup_rows)
    append_handoff(action_rows, approval_rows)


if __name__ == "__main__":
    main()
