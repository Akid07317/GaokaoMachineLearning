#!/usr/bin/env python3
"""Build the ready-school human/GPT review gate packet and decision sheets.

The outputs are non-canonical review artifacts. Manual decision columns are
preserved across reruns so the heartbeat cannot overwrite human work.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

ACTION_BOARD = SEED_DIR / "guangxi_pre_ml_human_gpt_review_action_board_merged.csv"
D1_DECISIONS = SEED_DIR / "guangxi_pre_ml_d1_g1_gpt_review_decisions_merged.csv"
D2_DECISIONS = SEED_DIR / "guangxi_pre_ml_d2_g2_gpt_review_decisions_merged.csv"
D3_D4_DECISIONS = SEED_DIR / "guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv"

GATE_PACKET_OUT = SEED_DIR / "guangxi_pre_ml_human_gpt_review_gate_packet_merged.csv"
GATE_DECISION_OUT = SEED_DIR / "guangxi_pre_ml_human_gpt_review_gate_decision_sheet_merged.csv"
ROW_FIX_ACCEPTANCE_OUT = SEED_DIR / "guangxi_pre_ml_d2_row_fix_acceptance_decision_sheet_merged.csv"
GATE_ROLLUP = REPORT_DIR / "engineering_pre_ml_human_gpt_review_gate_packet_coverage_rollup.csv"
ROW_FIX_ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_row_fix_acceptance_decision_sheet_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_human_gpt_review_gate_packet.md"

MANUAL_FIELDS = [
    "review_packet_status",
    "selected_decision",
    "reviewer",
    "decision_time",
    "decision_notes",
]

GATE_PACKET_FIELDS = [
    "packet_rank",
    "school_key",
    "school_name",
    "review_gate_bucket",
    "clean_or_caution_bucket",
    "source_layer",
    "final_gate_bucket",
    "review_decision",
    "source_gate_status",
    "source_readiness_band",
    "review_lane",
    "review_risk_score",
    "reference_year",
    "latest_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "gap_signature",
    "resolution_status",
    "plan_source_resolution",
    "score_source_resolution",
    "plan_source_url",
    "score_source_url",
    "evidence_note",
    "required_checks",
    "optional_decisions",
    "default_recommendation",
    "caution_or_boundary_notes",
    "canonical_ml_entry_open",
    "canonical_ml_closed_reason",
    "record_id",
    "source_record_id",
    "source_slug",
]

GATE_DECISION_FIELDS = [
    "decision_rank",
    "school_key",
    "school_name",
    "review_gate_bucket",
    "clean_or_caution_bucket",
    "review_packet_status",
    "selected_decision",
    "reviewer",
    "decision_time",
    "decision_notes",
    "optional_decisions",
    "default_recommendation",
    "required_checks",
    "plan_source_url",
    "score_source_url",
    "evidence_note",
    "canonical_ml_entry_open",
    "ml_boundary_note",
    "record_id",
    "source_record_id",
    "source_slug",
]

ROW_FIX_FIELDS = [
    "queue_rank",
    "school_key",
    "school_name",
    "fix_priority",
    "row_fix_status",
    "row_fix_exit_condition",
    "current_bucket",
    "review_packet_status",
    "selected_decision",
    "reviewer",
    "decision_time",
    "decision_notes",
    "acceptance_options",
    "default_recommendation",
    "recommended_action",
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
    "post_acceptance_route",
    "canonical_ml_entry_open",
    "ml_boundary_note",
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


def by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("school_key", ""): row for row in rows if row.get("school_key", "")}


def compact(value: object, max_len: int = 360) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 16] + "...[truncated]"


def first_value(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def manual_by_key(path: Path) -> dict[str, dict[str, str]]:
    existing = by_key(read_csv(path))
    preserved: dict[str, dict[str, str]] = {}
    for key, row in existing.items():
        preserved[key] = {field: row.get(field, "") for field in MANUAL_FIELDS}
    return preserved


def source_decision_lookup() -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for rows in (read_csv(D1_DECISIONS), read_csv(D2_DECISIONS), read_csv(D3_D4_DECISIONS)):
        for row in rows:
            key = row.get("school_key", "")
            if key:
                merged[key] = row
    return merged


def gate_bucket(row: dict[str, str]) -> str:
    return "caution" if row.get("final_gate_bucket") == "B2_ready_caution_review_gate" else "clean"


def required_checks(row: dict[str, str], decision: dict[str, str]) -> str:
    if decision.get("required_checks"):
        checks = decision["required_checks"]
    elif row.get("source_layer") == "D3_D4_gap_fill_application":
        checks = (
            "核对学校名|核对本地补洞来源为广西官方投档线|核对物理类/本科普通批/第一次正式投档"
            "|核对计划数/最低分/最低位次|确认复核通过前不进ML"
        )
    else:
        checks = "核对学校名|核对计划数|核对最低分/位次|核对来源回链|确认复核通过前不进ML"
    if gate_bucket(row) == "caution":
        checks = f"{checks}|核对 caution 备注是否足以隔离风险"
    return checks


def optional_decisions(row: dict[str, str]) -> str:
    if gate_bucket(row) == "caution":
        return "confirm_caution_review_gate_with_note|request_row_fix|hold_before_ml"
    return "confirm_clean_review_gate|request_row_fix|hold_before_ml"


def default_recommendation(row: dict[str, str]) -> str:
    if gate_bucket(row) == "caution":
        return "confirm_caution_review_gate_with_note"
    return "confirm_clean_review_gate"


def boundary_notes(row: dict[str, str], decision: dict[str, str]) -> str:
    notes = [
        row.get("next_action", ""),
        decision.get("residual_followups", ""),
        decision.get("required_followups", ""),
        decision.get("blocking_issues", ""),
    ]
    return compact("|".join(note for note in notes if note))


def build_gate_packet() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    board_rows = [
        row for row in read_csv(ACTION_BOARD) if row.get("ready_for_human_gpt_review_gate") == "true"
    ]
    decisions = source_decision_lookup()
    existing_decisions = manual_by_key(GATE_DECISION_OUT)
    packet_rows: list[dict[str, object]] = []
    decision_rows: list[dict[str, object]] = []

    for rank, row in enumerate(board_rows, start=1):
        key = row.get("school_key", "")
        source_decision = decisions.get(key, {})
        clean_caution = gate_bucket(row)
        checks = required_checks(row, source_decision)
        options = optional_decisions(row)
        recommendation = default_recommendation(row)
        evidence = compact(first_value(row.get("evidence_summary"), source_decision.get("acceptance_basis")))
        note = boundary_notes(row, source_decision)
        packet_id = f"{key}-pre-ml-human-gpt-review-gate-packet"
        decision_id = f"{key}-pre-ml-human-gpt-review-gate-decision-sheet"

        packet_rows.append(
            {
                "packet_rank": rank,
                "school_key": key,
                "school_name": row.get("school_name", ""),
                "review_gate_bucket": row.get("final_gate_bucket", ""),
                "clean_or_caution_bucket": clean_caution,
                "source_layer": row.get("source_layer", ""),
                "final_gate_bucket": row.get("final_gate_bucket", ""),
                "review_decision": row.get("review_decision", ""),
                "source_gate_status": row.get("source_gate_status", ""),
                "source_readiness_band": row.get("source_readiness_band", ""),
                "review_lane": row.get("review_lane", ""),
                "review_risk_score": row.get("review_risk_score", ""),
                "reference_year": row.get("reference_year", ""),
                "latest_year": row.get("latest_year", ""),
                "data_completeness": row.get("data_completeness", ""),
                "total_plan_count": row.get("total_plan_count", ""),
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "trend_available": row.get("trend_available", ""),
                "trend_signal": row.get("trend_signal", ""),
                "gap_signature": row.get("gap_signature", ""),
                "resolution_status": row.get("resolution_status", ""),
                "plan_source_resolution": row.get("plan_source_resolution", ""),
                "score_source_resolution": row.get("score_source_resolution", ""),
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "evidence_note": evidence,
                "required_checks": checks,
                "optional_decisions": options,
                "default_recommendation": recommendation,
                "caution_or_boundary_notes": note,
                "canonical_ml_entry_open": "false",
                "canonical_ml_closed_reason": row.get("canonical_ml_closed_reason", ""),
                "record_id": packet_id,
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_human_gpt_review_gate_packet",
            }
        )

        preserved = existing_decisions.get(key, {})
        decision_rows.append(
            {
                "decision_rank": rank,
                "school_key": key,
                "school_name": row.get("school_name", ""),
                "review_gate_bucket": row.get("final_gate_bucket", ""),
                "clean_or_caution_bucket": clean_caution,
                "review_packet_status": preserved.get("review_packet_status") or "pending_human_gpt_review_gate_decision",
                "selected_decision": preserved.get("selected_decision", ""),
                "reviewer": preserved.get("reviewer", ""),
                "decision_time": preserved.get("decision_time", ""),
                "decision_notes": preserved.get("decision_notes", ""),
                "optional_decisions": options,
                "default_recommendation": recommendation,
                "required_checks": checks,
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "evidence_note": evidence,
                "canonical_ml_entry_open": "false",
                "ml_boundary_note": "decision sheet only; canonical/ML remain closed until separately approved",
                "record_id": decision_id,
                "source_record_id": packet_id,
                "source_slug": "pre_ml_human_gpt_review_gate_decision_sheet",
            }
        )
    return packet_rows, decision_rows


def build_row_fix_acceptance_sheet() -> list[dict[str, object]]:
    board_rows = [
        row for row in read_csv(ACTION_BOARD) if row.get("requires_row_fix") == "true"
    ]
    existing = manual_by_key(ROW_FIX_ACCEPTANCE_OUT)
    output_rows: list[dict[str, object]] = []
    for rank, row in enumerate(board_rows, start=1):
        key = row.get("school_key", "")
        preserved = existing.get(key, {})
        acceptance_id = f"{key}-pre-ml-d2-row-fix-acceptance-decision-sheet"
        output_rows.append(
            {
                "queue_rank": rank,
                "school_key": key,
                "school_name": row.get("school_name", ""),
                "fix_priority": row.get("row_fix_priority", ""),
                "row_fix_status": row.get("row_fix_status", ""),
                "row_fix_exit_condition": row.get("row_fix_exit_condition", ""),
                "current_bucket": row.get("final_gate_bucket", ""),
                "review_packet_status": preserved.get("review_packet_status") or "pending_row_fix_acceptance_decision",
                "selected_decision": preserved.get("selected_decision", ""),
                "reviewer": preserved.get("reviewer", ""),
                "decision_time": preserved.get("decision_time", ""),
                "decision_notes": preserved.get("decision_notes", ""),
                "acceptance_options": "accept_row_fix_preview_then_reassess_g2|reject_row_fix_preview|hold_before_ml|request_more_local_evidence",
                "default_recommendation": "accept_row_fix_preview_then_reassess_g2",
                "recommended_action": compact(row.get("next_action", "")),
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
                "evidence_note": compact(row.get("evidence_summary", "")),
                "post_acceptance_route": row.get("row_fix_exit_condition", ""),
                "canonical_ml_entry_open": "false",
                "ml_boundary_note": "row fix acceptance sheet only; no canonical/ML write",
                "record_id": acceptance_id,
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_d2_row_fix_acceptance_decision_sheet",
            }
        )
    return output_rows


def selected_count(rows: list[dict[str, object]]) -> int:
    return sum(bool(str(row.get("selected_decision", "")).strip()) for row in rows)


def gate_rollup(packet_rows: list[dict[str, object]], decision_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    buckets = Counter(str(row["clean_or_caution_bucket"]) for row in packet_rows)
    source_layers = Counter(str(row["source_layer"]) for row in packet_rows)
    statuses = Counter(str(row["review_packet_status"]) for row in decision_rows)
    rows: list[dict[str, object]] = [
        {"metric": "review_gate_packet_school_count", "value": len(packet_rows)},
        {"metric": "clean_bucket_count", "value": buckets["clean"]},
        {"metric": "caution_bucket_count", "value": buckets["caution"]},
        {"metric": "decision_sheet_rows", "value": len(decision_rows)},
        {"metric": "selected_decision_count", "value": selected_count(decision_rows)},
        {"metric": "pending_decision_count", "value": len(decision_rows) - selected_count(decision_rows)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for name, count in sorted(source_layers.items()):
        rows.append({"metric": f"source_layer::{name}", "value": count})
    for name, count in sorted(statuses.items()):
        rows.append({"metric": f"review_packet_status::{name}", "value": count})
    return rows


def row_fix_rollup(rows_in: list[dict[str, object]]) -> list[dict[str, object]]:
    priorities = Counter(str(row["fix_priority"]) for row in rows_in)
    statuses = Counter(str(row["review_packet_status"]) for row in rows_in)
    rows: list[dict[str, object]] = [
        {"metric": "row_fix_acceptance_sheet_rows", "value": len(rows_in)},
        {"metric": "selected_decision_count", "value": selected_count(rows_in)},
        {"metric": "pending_decision_count", "value": len(rows_in) - selected_count(rows_in)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for name, count in sorted(priorities.items()):
        rows.append({"metric": f"fix_priority::{name}", "value": count})
    for name, count in sorted(statuses.items()):
        rows.append({"metric": f"review_packet_status::{name}", "value": count})
    return rows


def write_doc(
    packet_rows: list[dict[str, object]],
    decision_rows: list[dict[str, object]],
    row_fix_rows: list[dict[str, object]],
) -> None:
    clean_rows = [row for row in packet_rows if row["clean_or_caution_bucket"] == "clean"]
    caution_rows = [row for row in packet_rows if row["clean_or_caution_bucket"] == "caution"]
    lines = [
        "# Pre-ML human/GPT review gate packet",
        "",
        "本报告从全项目 action board 抽取 `ready_for_human_gpt_review_gate = true` 的学校，生成复核包和人工决策表。未联网，未运行 Deep Research，未写 canonical，未打开 ML。",
        "",
        "## Coverage",
        "",
        f"- review gate packet 学校数：{len(packet_rows)}",
        f"- clean bucket：{len(clean_rows)}",
        f"- caution bucket：{len(caution_rows)}",
        f"- decision sheet 待人工决策：{len(decision_rows) - selected_count(decision_rows)}",
        f"- D2 row fix acceptance sheet：{len(row_fix_rows)}",
        "- canonical/ML 入口：关闭",
        "- 扩池 / 非 211 搜索 / Deep Research 主线：关闭",
        "",
        "## Clean bucket",
        "",
    ]
    for row in clean_rows:
        lines.append(
            f"- {row['school_name']}：计划 {row['total_plan_count']}，最低分 {row['minimum_score']}，最低位次 {row['minimum_rank']}，趋势 {row['trend_signal']}"
        )
    lines.extend(["", "## Caution bucket", ""])
    for row in caution_rows:
        lines.append(
            f"- {row['school_name']}：计划 {row['total_plan_count']}，最低分 {row['minimum_score']}，最低位次 {row['minimum_rank']}，备注 {row['gap_signature']}"
        )
    lines.extend(["", "## D2 row fix acceptance sheet", ""])
    for row in row_fix_rows:
        lines.append(
            f"- {row['school_name']}：{row['fix_priority']} / {row['post_acceptance_route']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- 复核包只用于人工/GPT 闸门确认。",
            "- row fix acceptance sheet 只用于接受/驳回修复预览。",
            "- 所有表都保留 manual decision columns；脚本重跑会保留人工填写内容。",
            "- 禁止直接写 canonical/ML、扩池、非 211 搜索或把 Deep Research 当主线。",
            "",
            "## Output files",
            "",
            f"- `{GATE_PACKET_OUT.relative_to(ROOT)}`",
            f"- `{GATE_DECISION_OUT.relative_to(ROOT)}`",
            f"- `{ROW_FIX_ACCEPTANCE_OUT.relative_to(ROOT)}`",
            f"- `{GATE_ROLLUP.relative_to(ROOT)}`",
            f"- `{ROW_FIX_ROLLUP.relative_to(ROOT)}`",
            f"- `{DOC_OUT.relative_to(ROOT)}`",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    packet_rows, decision_rows = build_gate_packet()
    row_fix_rows = build_row_fix_acceptance_sheet()
    write_csv(GATE_PACKET_OUT, packet_rows, GATE_PACKET_FIELDS)
    write_csv(GATE_DECISION_OUT, decision_rows, GATE_DECISION_FIELDS)
    write_csv(ROW_FIX_ACCEPTANCE_OUT, row_fix_rows, ROW_FIX_FIELDS)
    write_csv(GATE_ROLLUP, gate_rollup(packet_rows, decision_rows), ["metric", "value"])
    write_csv(ROW_FIX_ROLLUP, row_fix_rollup(row_fix_rows), ["metric", "value"])
    write_doc(packet_rows, decision_rows, row_fix_rows)
    print(
        "review_gate_packet_rows="
        f"{len(packet_rows)} clean="
        f"{sum(row['clean_or_caution_bucket'] == 'clean' for row in packet_rows)} "
        "caution="
        f"{sum(row['clean_or_caution_bucket'] == 'caution' for row in packet_rows)} "
        "row_fix_acceptance_rows="
        f"{len(row_fix_rows)}"
    )


if __name__ == "__main__":
    main()
