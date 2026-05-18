#!/usr/bin/env python3
"""Build a Guangxi University of Science and Technology group-line review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_gxust_group_line_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_gxust_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_gxust_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_gxust_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_gxust_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_gxust_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_gxust_mapping_review_packet.md"
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


def is_true(value: object) -> bool:
    return str(value or "").strip().lower() == "true"


def classify(row: dict[str, str]) -> tuple[str, str]:
    status = row.get("join_status", "")
    special = row.get("special_type_detected", "")
    if status == "official_group_structure_joined_to_2025_exam_line_plan_count_missing":
        if is_true(row.get("in_520_window_2024")) and is_true(row.get("in_520_window_2025")):
            return "regular_physics_group_line_520_window_plan_missing", "find_or_accept_missing_plan_count_before_any_trend_pool_intake"
        return "regular_physics_group_line_outside_520_window_plan_missing", "keep_as_background_line_evidence_until_plan_count_exists"
    if status == "exam_line_without_official_group_structure_hold":
        if "民族班" in special:
            return "exam_line_only_ethnic_class_hold", "classify_boundary_and_keep_outside_regular_trend"
        return "exam_line_only_missing_official_group_structure_hold", "locate_group_structure_or_keep_boundary_hold"
    if status == "excluded_non_regular_or_special_group":
        if "history" in special:
            return "history_non_physics_isolated_hold", "exclude_from_physics_reference_trend"
        if "sino" in special:
            return "sino_foreign_isolated_hold", "keep_separate_from_regular_ordinary_trend"
        if "preparatory" in special:
            return "ethnic_preparatory_isolated_hold", "keep_separate_from_regular_ordinary_trend"
        return "excluded_boundary_group_hold", "keep_boundary_isolated"
    return "hold_unclassified", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_gxust_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "group_code": row.get("group_code", ""),
                "subject_category": row.get("subject_category", ""),
                "elective_requirement": row.get("elective_requirement", ""),
                "major_or_group": row.get("major_or_group", ""),
                "special_type_detected": row.get("special_type_detected", ""),
                "official_group_structure_source_url": row.get("official_group_structure_source_url", ""),
                "official_group_structure_raw_file": row.get("official_group_structure_raw_file", ""),
                "has_official_group_structure": row.get("has_official_group_structure", ""),
                "has_2025_exam_line": row.get("has_2025_exam_line", ""),
                "score_2025": row.get("score_2025", ""),
                "rank_2025": row.get("rank_2025", ""),
                "rank_low_2025": row.get("rank_low_2025", ""),
                "rank_high_2025": row.get("rank_high_2025", ""),
                "exam_line_source_id_2025": row.get("exam_line_source_id_2025", ""),
                "has_2024_exam_line": row.get("has_2024_exam_line", ""),
                "score_2024": row.get("score_2024", ""),
                "rank_2024": row.get("rank_2024", ""),
                "rank_low_2024": row.get("rank_low_2024", ""),
                "rank_high_2024": row.get("rank_high_2024", ""),
                "exam_line_source_id_2024": row.get("exam_line_source_id_2024", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "in_520_window_2024": row.get("in_520_window_2024", ""),
                "in_520_window_2025": row.get("in_520_window_2025", ""),
                "has_plan_count_2025": row.get("has_plan_count_2025", ""),
                "plan_count_2025": row.get("plan_count_2025", ""),
                "join_status": row.get("join_status", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "action_class": action_class,
                "next_action": next_action,
                "evidence_note": row.get("evidence_note", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "gxust_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
            }
        )
    return packet


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["join_status"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (status, action), group in sorted(grouped.items()):
        out.append(
            {
                "join_status": status,
                "action_class": action,
                "rows": len(group),
                "groups_seen": "|".join(sorted({str(row.get("group_code", "")) for row in group if str(row.get("group_code", ""))})),
                "rows_with_2025_exam_line": sum(1 for row in group if is_true(row.get("has_2025_exam_line"))),
                "rows_with_2024_exam_line": sum(1 for row in group if is_true(row.get("has_2024_exam_line"))),
                "rows_in_520_both_years": sum(1 for row in group if is_true(row.get("in_520_window_2024")) and is_true(row.get("in_520_window_2025"))),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["join_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from GXUST group-line workbench."},
        {"metric": "official_group_structure_joined_to_2025_exam_line_rows", "value": statuses.get("official_group_structure_joined_to_2025_exam_line_plan_count_missing", 0), "note": "Regular physics lines with official group structure and exam line, plan count missing."},
        {"metric": "regular_physics_520_window_rows", "value": sum(1 for row in rows if row["action_class"] == "regular_physics_group_line_520_window_plan_missing"), "note": "Strongest background candidates; still not intake eligible without plan count."},
        {"metric": "regular_physics_outside_520_window_rows", "value": sum(1 for row in rows if row["action_class"] == "regular_physics_group_line_outside_520_window_plan_missing"), "note": "Background line evidence outside target rank window."},
        {"metric": "exam_line_without_official_group_structure_hold_rows", "value": statuses.get("exam_line_without_official_group_structure_hold", 0), "note": "Exam authority line exists but group was not parsed from official structure PDF."},
        {"metric": "excluded_boundary_rows", "value": statuses.get("excluded_non_regular_or_special_group", 0), "note": "History, sino-foreign, preparatory or other isolated boundary groups."},
        {"metric": "rows_with_plan_count_2025", "value": sum(1 for row in rows if is_true(row.get("has_plan_count_2025"))), "note": "Expected zero for this workbench."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        *[
            {"metric": f"action_class::{key}", "value": value, "note": "Packet classification."}
            for key, value in sorted(actions.items())
        ],
    ]


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    statuses = Counter(str(row["join_status"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 17 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "status_counts_match_source_rollup", "status": "PASS" if statuses.get("official_group_structure_joined_to_2025_exam_line_plan_count_missing", 0) == 8 and statuses.get("exam_line_without_official_group_structure_hold", 0) == 5 and statuses.get("excluded_non_regular_or_special_group", 0) == 4 else "WARN", "detail": f"joined={statuses.get('official_group_structure_joined_to_2025_exam_line_plan_count_missing', 0)}; unmatched={statuses.get('exam_line_without_official_group_structure_hold', 0)}; excluded={statuses.get('excluded_non_regular_or_special_group', 0)}"},
        {"check": "regular_520_window_rows_carried", "status": "PASS" if sum(1 for row in rows if row["action_class"] == "regular_physics_group_line_520_window_plan_missing") == 3 else "WARN", "detail": str(sum(1 for row in rows if row["action_class"] == "regular_physics_group_line_520_window_plan_missing"))},
        {"check": "plan_count_still_missing", "status": "PASS" if sum(1 for row in rows if is_true(row.get("has_plan_count_2025"))) == 0 else "WARN", "detail": str(sum(1 for row in rows if is_true(row.get("has_plan_count_2025"))))},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "join_status": row["join_status"],
            "group_code": row["group_code"],
            "action_class": row["action_class"],
            "exclusion_reason": "plan_count_missing_or_boundary_group_unresolved",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# GXUST Mapping Review Packet",
        "",
        "Scope: 广西科技大学 official group-structure lines joined to 2024/2025 Guangxi exam-authority group lines.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Regular physics joined line rows: {sum(1 for row in rows if row['join_status'] == 'official_group_structure_joined_to_2025_exam_line_plan_count_missing')}",
        f"- Regular 520-window line rows: {sum(1 for row in rows if row['action_class'] == 'regular_physics_group_line_520_window_plan_missing')}",
        f"- Exam-line-only holds: {sum(1 for row in rows if row['join_status'] == 'exam_line_without_official_group_structure_hold')}",
        f"- Excluded boundary rows: {sum(1 for row in rows if row['join_status'] == 'excluded_non_regular_or_special_group')}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(f"- {row['join_status']} {row['action_class']}: {row['rows']} rows, groups={row['groups_seen']}, both520={row['rows_in_520_both_years']}")
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
    marker = "## 94. 2026-05-16 GXUST mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增广西科技大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_gxust_mapping_review_packet.csv`
- `reports/reference_trend_520_gxust_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_gxust_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_gxust_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_gxust_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_gxust_mapping_review_packet.md`

覆盖结果：从既有 GXUST group-line workbench 派生 {values.get('packet_rows')} 行审核包，其中官方专业组结构已接上 2025 考试院线但缺计划数 rows {values.get('official_group_structure_joined_to_2025_exam_line_rows')} 行；520 窗口内普通物理线索 {values.get('regular_physics_520_window_rows')} 行；考试院线缺官方组结构 hold {values.get('exam_line_without_official_group_structure_hold_rows')} 行；边界/特殊隔离 {values.get('excluded_boundary_rows')} 行。

准入边界：本轮只做组线证据、缺计划数和边界隔离分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No GXUST workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "join_status", "group_code", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} GXUST mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
