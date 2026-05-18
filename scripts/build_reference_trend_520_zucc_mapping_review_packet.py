#!/usr/bin/env python3
"""Build a ZUCC image-plan group mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_zucc_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_zucc_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_zucc_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_zucc_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_zucc_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_zucc_mapping_review_packet.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: object) -> int:
    try:
        return int(float(str(value or "").strip() or "0"))
    except ValueError:
        return 0


def classify(row: dict[str, str]) -> tuple[str, str, str]:
    status = row.get("mapping_status", "")
    if status == "historical_exam_line_context_only":
        return (
            "historical_context_only",
            "use_as_2024_exam_authority_context_only",
            "Historical row supports trend context only; it cannot allocate 2025 school plan.",
        )
    if status == "candidate_2025_exam_group_without_school_plan_split":
        return (
            "exam_group_plan_split_missing_hold",
            "request_official_group_split_or_major_to_group_mapping",
            "2025 exam group exists, but official school image only provides combined Guangxi physics plan total.",
        )
    if status == "candidate_same_code_group_but_reject_full_80_plan_assignment":
        return (
            "reject_full_school_plan_assignment_same_code_context_hold",
            "do_not_assign_full_80_to_single_group_without_split",
            "Same-code trend context exists, but 2025 has multiple physical groups; assigning all 80 plans to one group would be wrong.",
        )
    if status == "school_plan_total_unassigned_to_group":
        return (
            "school_plan_total_unassigned_summary",
            "keep_as_school_level_field_thickness_until_group_split_is_confirmed",
            "Official image plan total is deliberately unassigned because group boundaries are absent.",
        )
    return "hold_unclassified", "manual_review", "Unclassified ZUCC row."


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action, exclusion_reason = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_zucc_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "row_scope": row.get("row_scope", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "group_code": row.get("group_code", ""),
                "group_year_key": row.get("group_year_key", ""),
                "min_score": row.get("min_score", ""),
                "min_rank_est": row.get("min_rank_est", ""),
                "school_plan_physics_total_2025": row.get("school_plan_physics_total_2025", ""),
                "school_plan_history_total_2025": row.get("school_plan_history_total_2025", ""),
                "school_plan_major_rows_2025": row.get("school_plan_major_rows_2025", ""),
                "source_url": row.get("source_url", ""),
                "source_owner": row.get("source_owner", ""),
                "source_title": row.get("source_title", ""),
                "source_confidence_tier": row.get("source_confidence_tier", ""),
                "same_code_delta_rank_2025_minus_2024": row.get("same_code_delta_rank_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "mapping_status": row.get("mapping_status", ""),
                "qa_status": row.get("qa_status", ""),
                "action_class": action_class,
                "next_action": next_action,
                "suggested_decision_options": "accept_group_split|keep_school_level_only|request_official_group_split|reject_full_plan_assignment|reject",
                "selected_decision": "",
                "selected_group_code": "",
                "reviewer": "",
                "decision_notes": "",
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "zucc_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
                "exclusion_reason": exclusion_reason,
                "evidence_note": row.get("evidence_note", ""),
            }
        )
    return packet


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["mapping_status"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (status, action), group in sorted(grouped.items()):
        out.append(
            {
                "mapping_status": status,
                "action_class": action,
                "rows": len(group),
                "group_codes_seen": "|".join(sorted({str(row.get("group_code", "")) for row in group if str(row.get("group_code", ""))})),
                "physics_plan_total_max": max((to_int(row.get("school_plan_physics_total_2025")) for row in group), default=0),
                "history_plan_total_max": max((to_int(row.get("school_plan_history_total_2025")) for row in group), default=0),
                "school_plan_major_rows_max": max((to_int(row.get("school_plan_major_rows_2025")) for row in group), default=0),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    groups_2025 = sorted({str(row.get("group_code", "")) for row in rows if row.get("year") == "2025" and row.get("row_scope") == "exam_authority_group_line_mapping_context"})
    physics_total = max((to_int(row.get("school_plan_physics_total_2025")) for row in rows), default=0)
    history_total = max((to_int(row.get("school_plan_history_total_2025")) for row in rows), default=0)
    major_rows = max((to_int(row.get("school_plan_major_rows_2025")) for row in rows), default=0)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from ZUCC group mapping workbench."},
        {"metric": "universities_covered", "value": len({row.get("university_name") for row in rows}), "note": "|".join(sorted({str(row.get("university_name", "")) for row in rows}))},
        {"metric": "zucc_2025_exam_authority_physics_groups", "value": len(groups_2025), "note": "|".join(groups_2025)},
        {"metric": "official_image_physics_plan_total", "value": physics_total, "note": "School official image combined Guangxi physics total."},
        {"metric": "official_image_history_plan_total", "value": history_total, "note": "School official image combined Guangxi history total."},
        {"metric": "official_image_major_rows", "value": major_rows, "note": "Major rows parsed from official image."},
        {"metric": "historical_context_rows", "value": actions.get("historical_context_only", 0), "note": "2024 exam-authority context rows."},
        {"metric": "exam_group_plan_split_missing_hold_rows", "value": actions.get("exam_group_plan_split_missing_hold", 0), "note": "2025 group exists but plan split is missing."},
        {"metric": "reject_full_school_plan_assignment_rows", "value": actions.get("reject_full_school_plan_assignment_same_code_context_hold", 0), "note": "Explicitly blocks assigning all 80 physics plans to one group."},
        {"metric": "school_plan_total_unassigned_summary_rows", "value": actions.get("school_plan_total_unassigned_summary", 0), "note": "School-level official image total row."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        *[
            {"metric": f"mapping_status::{key}", "value": value, "note": "Source workbench mapping status."}
            for key, value in sorted(statuses.items())
        ],
        *[
            {"metric": f"action_class::{key}", "value": value, "note": "Packet classification."}
            for key, value in sorted(actions.items())
        ],
    ]


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    actions = Counter(str(row["action_class"]) for row in rows)
    groups_2025 = {str(row.get("group_code", "")) for row in rows if row.get("year") == "2025" and row.get("row_scope") == "exam_authority_group_line_mapping_context"}
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 5 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "multiple_2025_physics_groups_confirmed", "status": "PASS" if groups_2025 == {"101", "102"} else "WARN", "detail": "|".join(sorted(groups_2025))},
        {"check": "physics_plan_total_carried", "status": "PASS" if max(to_int(row.get("school_plan_physics_total_2025")) for row in rows) == 80 else "WARN", "detail": "expected 80"},
        {"check": "history_plan_total_carried", "status": "PASS" if max(to_int(row.get("school_plan_history_total_2025")) for row in rows) == 10 else "WARN", "detail": "expected 10"},
        {"check": "major_rows_carried", "status": "PASS" if max(to_int(row.get("school_plan_major_rows_2025")) for row in rows) == 17 else "WARN", "detail": "expected 17"},
        {"check": "reject_full_80_assignment_present", "status": "PASS" if actions.get("reject_full_school_plan_assignment_same_code_context_hold", 0) == 1 else "WARN", "detail": str(actions.get("reject_full_school_plan_assignment_same_code_context_hold", 0))},
        {"check": "manual_decision_fields_blank", "status": "PASS" if not any(str(row.get("selected_decision", "")).strip() or str(row.get("selected_group_code", "")).strip() or str(row.get("reviewer", "")).strip() or str(row.get("decision_notes", "")).strip() for row in rows) else "WARN", "detail": "selected_decision/selected_group_code/reviewer/decision_notes checked"},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "source_workbench_record_id": row["source_workbench_record_id"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "mapping_status": row["mapping_status"],
            "action_class": row["action_class"],
            "exclusion_reason": row["exclusion_reason"],
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    physics_total = max((to_int(row.get("school_plan_physics_total_2025")) for row in rows), default=0)
    history_total = max((to_int(row.get("school_plan_history_total_2025")) for row in rows), default=0)
    major_rows = max((to_int(row.get("school_plan_major_rows_2025")) for row in rows), default=0)
    lines = [
        "# ZUCC Mapping Review Packet",
        "",
        "Scope: 浙大城市学院 official image-plan evidence joined only to Guangxi exam-authority group-line context.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Official image physics plan total: {physics_total}",
        f"- Official image history plan total: {history_total}",
        f"- Official image major rows: {major_rows}",
        f"- Historical context rows: {sum(1 for row in rows if row['action_class'] == 'historical_context_only')}",
        f"- 2025 group plan-split missing holds: {sum(1 for row in rows if row['action_class'] == 'exam_group_plan_split_missing_hold')}",
        f"- Explicit reject-full-plan-assignment rows: {sum(1 for row in rows if row['action_class'] == 'reject_full_school_plan_assignment_same_code_context_hold')}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(
            f"- {row['mapping_status']} -> {row['action_class']}: {row['rows']} rows, "
            f"groups={row['group_codes_seen']}, physics_total={row['physics_plan_total_max']}"
        )
    lines.extend(
        [
            "",
            "QA:",
            *[f"- {item['check']}: {item['status']} ({item['detail']})" for item in qa],
            "",
            "Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def append_handoff(rollup: list[dict[str, object]]) -> None:
    marker = "## 98. 2026-05-16 ZUCC mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增浙大城市学院 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_zucc_mapping_review_packet.csv`
- `reports/reference_trend_520_zucc_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_zucc_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_zucc_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_zucc_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_zucc_mapping_review_packet.md`

覆盖结果：从既有 ZUCC group mapping workbench 派生 {values.get('packet_rows')} 行审核包；2025 考试院物理组 {values.get('zucc_2025_exam_authority_physics_groups')} 个；官方图片计划显示广西物理 {values.get('official_image_physics_plan_total')}、广西历史 {values.get('official_image_history_plan_total')}、专业 rows {values.get('official_image_major_rows')}。本包明确保留“不能把 80 个物理计划整包分配给单一 101/102 组”的 hold 规则。

准入边界：本轮只做官方图片计划总数、考试院组线趋势和组级拆分待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No ZUCC workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(
        EXCLUSION,
        build_exclusion(rows),
        [
            "packet_record_id",
            "source_workbench_record_id",
            "university_name",
            "group_code",
            "mapping_status",
            "action_class",
            "exclusion_reason",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} ZUCC mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
