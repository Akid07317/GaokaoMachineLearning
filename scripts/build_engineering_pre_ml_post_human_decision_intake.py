#!/usr/bin/env python3
"""Apply approved human decisions and build post-human-decision previews.

This fills only empty manual decision cells from the user's blanket approval,
then emits non-canonical intake/status previews. It does not write canonical
training rows, run ML, fetch live sources, or expand the pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

GATE_DECISION_SHEET = SEED_DIR / "guangxi_pre_ml_human_gpt_review_gate_decision_sheet_merged.csv"
ROW_FIX_DECISION_SHEET = SEED_DIR / "guangxi_pre_ml_d2_row_fix_acceptance_decision_sheet_merged.csv"
ACTION_BOARD = SEED_DIR / "guangxi_pre_ml_human_gpt_review_action_board_merged.csv"

INTAKE_OUT = SEED_DIR / "guangxi_pre_ml_post_human_decision_intake_preview_merged.csv"
STATUS_OUT = SEED_DIR / "guangxi_pre_ml_post_human_decision_status_preview_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_post_human_decision_intake_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_post_human_decision_intake.md"

INTAKE_FIELDS = [
    "decision_rank",
    "decision_source",
    "school_key",
    "school_name",
    "selected_decision",
    "reviewer",
    "decision_time",
    "decision_notes",
    "decision_bucket",
    "post_human_route",
    "post_human_status",
    "requires_reassessment",
    "requires_targeted_repair",
    "requires_broad_data_collection",
    "requires_live_source_approval",
    "canonical_ml_entry_open",
    "canonical_ml_action",
    "next_action",
    "review_gate_bucket",
    "clean_or_caution_bucket",
    "reference_year",
    "latest_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "gap_signature",
    "plan_source_url",
    "score_source_url",
    "evidence_note",
    "record_id",
    "source_record_id",
    "source_slug",
]

STATUS_FIELDS = [
    "status_rank",
    "school_key",
    "school_name",
    "post_human_status_bucket",
    "post_human_status",
    "selected_decision",
    "next_action",
    "broad_data_collection_needed",
    "targeted_repair_needed",
    "live_source_approval_needed",
    "canonical_ml_entry_open",
    "canonical_ml_action",
    "record_id",
    "source_record_id",
    "source_slug",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def compact(value: object, max_len: int = 360) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 16] + "...[truncated]"


def now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def fill_gate_decisions(timestamp: str) -> list[dict[str, str]]:
    rows = read_csv(GATE_DECISION_SHEET)
    for row in rows:
        if row.get("selected_decision", "").strip():
            continue
        selected = row.get("default_recommendation", "").strip()
        row["review_packet_status"] = "human_decision_recorded"
        row["selected_decision"] = selected
        row["reviewer"] = "user"
        row["decision_time"] = timestamp
        if row.get("clean_or_caution_bucket") == "caution":
            row["decision_notes"] = "用户指示：人工决策全过；caution bucket 通过但保留备注，进入后续修复/重评边界，不打开 canonical/ML。"
        else:
            row["decision_notes"] = "用户指示：人工决策全过；clean bucket 通过复核闸门，不打开 canonical/ML。"
    write_csv(GATE_DECISION_SHEET, rows, list(rows[0].keys()) if rows else [])
    return rows


def fill_row_fix_decisions(timestamp: str) -> list[dict[str, str]]:
    rows = read_csv(ROW_FIX_DECISION_SHEET)
    for row in rows:
        if row.get("selected_decision", "").strip():
            continue
        row["review_packet_status"] = "human_row_fix_acceptance_recorded"
        row["selected_decision"] = row.get("default_recommendation", "accept_row_fix_preview_then_reassess_g2")
        row["reviewer"] = "user"
        row["decision_time"] = timestamp
        row["decision_notes"] = "用户指示：caution bucket 修复；接受 row fix preview，进入 G2 重评，不打开 canonical/ML。"
    write_csv(ROW_FIX_DECISION_SHEET, rows, list(rows[0].keys()) if rows else [])
    return rows


def route_for(decision_source: str, selected: str) -> tuple[str, str, str, str, str]:
    if selected == "confirm_clean_review_gate":
        return (
            "confirm_clean",
            "ready_for_canonical_rebuild_assessment_not_ml",
            "post_human_gate_confirmed_clean",
            "false",
            "false",
        )
    if selected == "confirm_caution_review_gate_with_note":
        return (
            "confirm_caution_with_note",
            "ready_for_caution_repair_or_canonical_rebuild_assessment_not_ml",
            "post_human_gate_confirmed_caution_with_note",
            "true",
            "true",
        )
    if selected == "accept_row_fix_preview_then_reassess_g2":
        return (
            "accept_row_fix_preview",
            "row_fix_accepted_reassess_g2_not_ml",
            "post_human_row_fix_accepted_for_reassessment",
            "true",
            "true",
        )
    if "request" in selected or "fix" in selected:
        return (
            "request_fix",
            "hold_for_targeted_fix_not_ml",
            "post_human_requested_fix",
            "true",
            "true",
        )
    if "hold" in selected:
        return ("hold", "hold_before_ml", "post_human_hold", "false", "false")
    return ("other", "manual_review_required_not_ml", "post_human_manual_route", "false", "false")


def gate_intake_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        selected = row.get("selected_decision", "").strip()
        if not selected:
            continue
        bucket, route, status, reassess, repair = route_for("gate_decision", selected)
        output.append(
            {
                "decision_source": "human_gpt_review_gate_decision_sheet",
                "school_key": row.get("school_key", ""),
                "school_name": row.get("school_name", ""),
                "selected_decision": selected,
                "reviewer": row.get("reviewer", ""),
                "decision_time": row.get("decision_time", ""),
                "decision_notes": row.get("decision_notes", ""),
                "decision_bucket": bucket,
                "post_human_route": route,
                "post_human_status": status,
                "requires_reassessment": reassess,
                "requires_targeted_repair": repair,
                "requires_broad_data_collection": "false",
                "requires_live_source_approval": "false",
                "canonical_ml_entry_open": "false",
                "canonical_ml_action": "keep_closed_pending_canonical_rebuild_assessment",
                "next_action": next_action_for(route),
                "review_gate_bucket": row.get("review_gate_bucket", ""),
                "clean_or_caution_bucket": row.get("clean_or_caution_bucket", ""),
                "reference_year": "",
                "latest_year": "",
                "data_completeness": "",
                "total_plan_count": "",
                "minimum_score": "",
                "minimum_rank": "",
                "trend_available": "",
                "trend_signal": "",
                "gap_signature": "",
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "evidence_note": compact(row.get("evidence_note", "")),
                "record_id": f"{row.get('school_key', '')}-pre-ml-post-human-decision-intake",
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_post_human_decision_intake",
            }
        )
    return output


def row_fix_intake_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        selected = row.get("selected_decision", "").strip()
        if not selected:
            continue
        bucket, route, status, reassess, repair = route_for("row_fix_decision", selected)
        output.append(
            {
                "decision_source": "d2_row_fix_acceptance_decision_sheet",
                "school_key": row.get("school_key", ""),
                "school_name": row.get("school_name", ""),
                "selected_decision": selected,
                "reviewer": row.get("reviewer", ""),
                "decision_time": row.get("decision_time", ""),
                "decision_notes": row.get("decision_notes", ""),
                "decision_bucket": bucket,
                "post_human_route": route,
                "post_human_status": status,
                "requires_reassessment": reassess,
                "requires_targeted_repair": repair,
                "requires_broad_data_collection": "false",
                "requires_live_source_approval": "false",
                "canonical_ml_entry_open": "false",
                "canonical_ml_action": "keep_closed_pending_row_fix_reassessment",
                "next_action": next_action_for(route),
                "review_gate_bucket": row.get("current_bucket", ""),
                "clean_or_caution_bucket": "row_fix_acceptance",
                "reference_year": row.get("reference_year", ""),
                "latest_year": row.get("latest_year", ""),
                "data_completeness": row.get("data_completeness", ""),
                "total_plan_count": row.get("total_plan_count", ""),
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "trend_available": row.get("trend_available", ""),
                "trend_signal": row.get("trend_signal", ""),
                "gap_signature": row.get("gap_signature", ""),
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "evidence_note": compact(row.get("evidence_note", "")),
                "record_id": f"{row.get('school_key', '')}-pre-ml-post-human-row-fix-intake",
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_post_human_decision_intake",
            }
        )
    return output


def next_action_for(route: str) -> str:
    if route == "ready_for_canonical_rebuild_assessment_not_ml":
        return "纳入 canonical rebuild assessment 候选；先评估字段/口径，不直接写 canonical/ML。"
    if route == "ready_for_caution_repair_or_canonical_rebuild_assessment_not_ml":
        return "先生成 caution repair/reassessment 预览，确认备注和字段边界后再评估 canonical rebuild。"
    if route == "row_fix_accepted_reassess_g2_not_ml":
        return "按已接受 row fix preview 重评 G2 readiness；仍不直接写 canonical/ML。"
    if route == "hold_before_ml":
        return "保持 hold_before_ml。"
    return "人工复核后再决定下一步。"


def status_rows(intake_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for rank, row in enumerate(intake_rows, start=1):
        output.append(
            {
                "status_rank": rank,
                "school_key": row["school_key"],
                "school_name": row["school_name"],
                "post_human_status_bucket": row["decision_bucket"],
                "post_human_status": row["post_human_status"],
                "selected_decision": row["selected_decision"],
                "next_action": row["next_action"],
                "broad_data_collection_needed": row["requires_broad_data_collection"],
                "targeted_repair_needed": row["requires_targeted_repair"],
                "live_source_approval_needed": row["requires_live_source_approval"],
                "canonical_ml_entry_open": row["canonical_ml_entry_open"],
                "canonical_ml_action": row["canonical_ml_action"],
                "record_id": f"{row['school_key']}-pre-ml-post-human-decision-status",
                "source_record_id": row["record_id"],
                "source_slug": "pre_ml_post_human_decision_status_preview",
            }
        )
    return output


def rollup(intake_rows: list[dict[str, object]], action_board_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    buckets = Counter(str(row["decision_bucket"]) for row in intake_rows)
    sources = Counter(str(row["decision_source"]) for row in intake_rows)
    g4_live = sum(row.get("requires_live_source_approval") == "true" for row in action_board_rows)
    return [
        {"metric": "post_human_decision_intake_rows", "value": len(intake_rows)},
        {"metric": "gate_decision_confirmed_rows", "value": sources["human_gpt_review_gate_decision_sheet"]},
        {"metric": "row_fix_acceptance_confirmed_rows", "value": sources["d2_row_fix_acceptance_decision_sheet"]},
        {"metric": "confirm_clean_rows", "value": buckets["confirm_clean"]},
        {"metric": "confirm_caution_with_note_rows", "value": buckets["confirm_caution_with_note"]},
        {"metric": "accept_row_fix_preview_rows", "value": buckets["accept_row_fix_preview"]},
        {"metric": "requires_targeted_repair_or_reassessment_rows", "value": sum(row["requires_targeted_repair"] == "true" for row in intake_rows)},
        {"metric": "requires_broad_data_collection_rows", "value": sum(row["requires_broad_data_collection"] == "true" for row in intake_rows)},
        {"metric": "remaining_g4_live_source_approval_rows", "value": g4_live},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]


def write_doc(intake_rows: list[dict[str, object]], rollup_rows: list[dict[str, object]]) -> None:
    metric = {str(row["metric"]): str(row["value"]) for row in rollup_rows}
    lines = [
        "# Pre-ML post-human-decision intake",
        "",
        "已根据用户指示记录人工决策：ready gate 全过，D2 row fix preview 全部接受用于 caution bucket 修复/重评。本报告仍为非 canonical、非 ML 预览层。",
        "",
        "## Decision intake",
        "",
        f"- post-human intake rows: {metric.get('post_human_decision_intake_rows', '0')}",
        f"- gate decision confirmed rows: {metric.get('gate_decision_confirmed_rows', '0')}",
        f"- row fix acceptance confirmed rows: {metric.get('row_fix_acceptance_confirmed_rows', '0')}",
        f"- clean confirmations: {metric.get('confirm_clean_rows', '0')}",
        f"- caution confirmations with note: {metric.get('confirm_caution_with_note_rows', '0')}",
        f"- accepted row fix previews: {metric.get('accept_row_fix_preview_rows', '0')}",
        f"- targeted repair/reassessment rows: {metric.get('requires_targeted_repair_or_reassessment_rows', '0')}",
        f"- broad data collection rows: {metric.get('requires_broad_data_collection_rows', '0')}",
        f"- remaining G4 live source approvals: {metric.get('remaining_g4_live_source_approval_rows', '0')}",
        "",
        "## Decision",
        "",
        "不建议继续做广泛数据搜集或扩池。当前主线应进入 post-human caution repair/reassessment 和 canonical rebuild assessment；G4 仍只在人工批准后做官方来源可达性支线。",
        "",
        "## Boundary",
        "",
        "- canonical/ML 入口仍关闭。",
        "- 非 211 搜索与扩池仍关闭。",
        "- Deep Research 不作为主线，仅可用于 G4 官方来源可达性支线。",
        "- 如需继续补数据，只允许针对已知 row fix/caution/G4 blocker 做定点补证。",
        "",
        "## Output files",
        "",
        f"- `{INTAKE_OUT.relative_to(ROOT)}`",
        f"- `{STATUS_OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP_OUT.relative_to(ROOT)}`",
        f"- `{DOC_OUT.relative_to(ROOT)}`",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    timestamp = now_text()
    gate_rows = fill_gate_decisions(timestamp)
    row_fix_rows = fill_row_fix_decisions(timestamp)
    intake_rows = gate_intake_rows(gate_rows) + row_fix_intake_rows(row_fix_rows)
    for rank, row in enumerate(intake_rows, start=1):
        row["decision_rank"] = rank
    status = status_rows(intake_rows)
    action_board_rows = read_csv(ACTION_BOARD)
    rollup_rows = rollup(intake_rows, action_board_rows)
    write_csv(INTAKE_OUT, intake_rows, INTAKE_FIELDS)
    write_csv(STATUS_OUT, status, STATUS_FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value"])
    write_doc(intake_rows, rollup_rows)
    print(
        "post_human_decision_intake_rows="
        f"{len(intake_rows)} gate={sum(row['decision_source'] == 'human_gpt_review_gate_decision_sheet' for row in intake_rows)} "
        f"row_fix={sum(row['decision_source'] == 'd2_row_fix_acceptance_decision_sheet' for row in intake_rows)} "
        "broad_collection=0 canonical_ml=false"
    )


if __name__ == "__main__":
    main()
