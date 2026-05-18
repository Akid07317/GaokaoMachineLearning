#!/usr/bin/env python3
"""Build a batch7 SHZU/FJUT group mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch7_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch7_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_batch7_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_batch7_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_batch7_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_batch7_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_batch7_mapping_review_packet.md"
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


def classify(row: dict[str, str]) -> tuple[str, str, str]:
    status = row.get("mapping_status", "")
    if status == "historical_exam_line_context_only":
        return (
            "historical_context_only",
            "use_as_2024_2025_exam_authority_trend_context_only",
            "No 2025 official plan allocation is attached to this historical row.",
        )
    if status == "multiple_exam_groups_source_no_group_code_hold":
        return (
            "plan_count_available_multi_group_mapping_hold",
            "manual_accept_specific_group_mapping_or_keep_school_level_only",
            "Official 2025 plan source has useful school-level/subject-level plan counts but does not print Guangxi group code.",
        )
    if status == "school_plan_total_unassigned_to_group":
        return (
            "school_plan_total_unassigned_summary",
            "keep_as_school_level_field_thickness_until_group_split_is_confirmed",
            "Official total is deliberately unassigned because the source lacks Guangxi group code.",
        )
    if status == "special_type_exam_group_hold":
        return (
            "special_type_exam_group_isolated_hold",
            "keep_outside_regular_physics_calibration",
            "Exam authority seed marks this group as special type; isolate from ordinary trend calibration.",
        )
    return "hold_unclassified", "manual_review", "Unclassified batch7 row."


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action, exclusion_reason = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_batch7_review_{idx:04d}",
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
                "exam_remark": row.get("exam_remark", ""),
                "official_plan_source_url": row.get("official_plan_source_url", ""),
                "official_raw_files": row.get("official_raw_files", ""),
                "official_total_plan_2025": row.get("official_total_plan_2025", ""),
                "official_major_rows_2025": row.get("official_major_rows_2025", ""),
                "official_subject_plan_breakdown_2025": row.get("official_subject_plan_breakdown_2025", ""),
                "official_source_contains_group_code": row.get("official_source_contains_group_code", ""),
                "candidate_group_from_queue": row.get("candidate_group_from_queue", ""),
                "has_2024_same_code_delta": row.get("has_2024_same_code_delta", ""),
                "score_2024": row.get("score_2024", ""),
                "score_2025": row.get("score_2025", ""),
                "rank_2024": row.get("rank_2024", ""),
                "rank_2025": row.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "rank_band_2024": row.get("rank_band_2024", ""),
                "rank_band_2025": row.get("rank_band_2025", ""),
                "mapping_status": row.get("mapping_status", ""),
                "qa_status": row.get("qa_status", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "action_class": action_class,
                "next_action": next_action,
                "suggested_decision_options": "accept_group_mapping|keep_school_level_only|request_official_group_split|hold_special_type|reject",
                "selected_decision": "",
                "selected_group_code": "",
                "reviewer": "",
                "decision_notes": "",
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "batch7_mapping_review_packet_only_not_decision_pool",
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
                "universities_seen": "|".join(sorted({str(row.get("university_name", "")) for row in group if str(row.get("university_name", ""))})),
                "group_codes_seen": "|".join(sorted({str(row.get("group_code", "")) for row in group if str(row.get("group_code", ""))})),
                "official_total_plan_2025_max_sum_by_school": sum(
                    max(to_int(row.get("official_total_plan_2025")) for row in group if row.get("university_name") == school)
                    for school in {str(row.get("university_name", "")) for row in group if str(row.get("university_name", ""))}
                ),
                "rows_with_official_plan_source": sum(1 for row in group if str(row.get("official_plan_source_url", "")).strip()),
                "rows_with_same_code_delta": sum(1 for row in group if is_true(row.get("has_2024_same_code_delta"))),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    school_plan_totals: dict[str, int] = {}
    school_groups: dict[str, set[str]] = defaultdict(set)
    school_breakdowns: dict[str, str] = {}
    for row in rows:
        school = str(row.get("university_name", ""))
        if not school:
            continue
        total = to_int(row.get("official_total_plan_2025"))
        if total:
            school_plan_totals[school] = max(total, school_plan_totals.get(school, 0))
        group = str(row.get("group_code", ""))
        if group:
            school_groups[school].add(group)
        breakdown = str(row.get("official_subject_plan_breakdown_2025", ""))
        if breakdown:
            school_breakdowns[school] = breakdown

    out = [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from batch7 SHZU/FJUT group mapping workbench."},
        {"metric": "universities_covered", "value": len({row.get("university_name") for row in rows}), "note": "|".join(sorted({str(row.get("university_name", "")) for row in rows}))},
        {"metric": "historical_context_rows", "value": actions.get("historical_context_only", 0), "note": "Exam-authority historical trend context only."},
        {"metric": "plan_count_available_multi_group_mapping_hold_rows", "value": actions.get("plan_count_available_multi_group_mapping_hold", 0), "note": "Official plan total exists but group split is missing."},
        {"metric": "school_plan_total_unassigned_summary_rows", "value": actions.get("school_plan_total_unassigned_summary", 0), "note": "School-level plan total summary rows."},
        {"metric": "special_type_exam_group_isolated_hold_rows", "value": actions.get("special_type_exam_group_isolated_hold", 0), "note": "Special/preparatory group isolated from ordinary calibration."},
        {"metric": "rows_with_official_plan_source", "value": sum(1 for row in rows if str(row.get("official_plan_source_url", "")).strip()), "note": "Rows carrying official source URL."},
        {"metric": "rows_with_same_code_delta", "value": sum(1 for row in rows if is_true(row.get("has_2024_same_code_delta"))), "note": "Rows with 2024 to 2025 same-code rank delta."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for school, total in sorted(school_plan_totals.items()):
        out.append({"metric": f"school::{school}::official_total_plan_2025", "value": total, "note": school_breakdowns.get(school, "")})
        out.append({"metric": f"school::{school}::candidate_groups_seen", "value": "|".join(sorted(school_groups[school])), "note": "Includes unassigned summary if present."})
    out.extend(
        {"metric": f"mapping_status::{key}", "value": value, "note": "Source workbench mapping status."}
        for key, value in sorted(statuses.items())
    )
    out.extend(
        {"metric": f"action_class::{key}", "value": value, "note": "Packet classification."}
        for key, value in sorted(actions.items())
    )
    return out


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    actions = Counter(str(row["action_class"]) for row in rows)
    schools = Counter(str(row["university_name"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 13 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "university_counts_expected", "status": "PASS" if schools.get("石河子大学", 0) == 6 and schools.get("福建理工大学", 0) == 7 else "WARN", "detail": f"石河子大学={schools.get('石河子大学', 0)}; 福建理工大学={schools.get('福建理工大学', 0)}"},
        {"check": "historical_context_rows_expected", "status": "PASS" if actions.get("historical_context_only", 0) == 5 else "WARN", "detail": str(actions.get("historical_context_only", 0))},
        {"check": "regular_group_mapping_hold_rows_expected", "status": "PASS" if actions.get("plan_count_available_multi_group_mapping_hold", 0) == 5 else "WARN", "detail": str(actions.get("plan_count_available_multi_group_mapping_hold", 0))},
        {"check": "school_total_summary_rows_expected", "status": "PASS" if actions.get("school_plan_total_unassigned_summary", 0) == 2 else "WARN", "detail": str(actions.get("school_plan_total_unassigned_summary", 0))},
        {"check": "special_type_hold_rows_expected", "status": "PASS" if actions.get("special_type_exam_group_isolated_hold", 0) == 1 else "WARN", "detail": str(actions.get("special_type_exam_group_isolated_hold", 0))},
        {"check": "official_plan_totals_carried", "status": "PASS" if max(to_int(row.get("official_total_plan_2025")) for row in rows if row.get("university_name") == "石河子大学") == 100 and max(to_int(row.get("official_total_plan_2025")) for row in rows if row.get("university_name") == "福建理工大学") == 205 else "WARN", "detail": "石河子大学=100; 福建理工大学=205 expected"},
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
    school_totals: dict[str, int] = {}
    school_breakdowns: dict[str, str] = {}
    for row in rows:
        school = str(row.get("university_name", ""))
        total = to_int(row.get("official_total_plan_2025"))
        if school and total:
            school_totals[school] = max(total, school_totals.get(school, 0))
        breakdown = str(row.get("official_subject_plan_breakdown_2025", ""))
        if school and breakdown:
            school_breakdowns[school] = breakdown

    lines = [
        "# Batch7 SHZU/FJUT Mapping Review Packet",
        "",
        "Scope: 石河子大学 and 福建理工大学 2025 official plan-source evidence joined only to Guangxi exam-authority group-line context.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Historical context rows: {sum(1 for row in rows if row['action_class'] == 'historical_context_only')}",
        f"- Regular plan-count available but group-mapping hold rows: {sum(1 for row in rows if row['action_class'] == 'plan_count_available_multi_group_mapping_hold')}",
        f"- School-level unassigned plan summaries: {sum(1 for row in rows if row['action_class'] == 'school_plan_total_unassigned_summary')}",
        f"- Special group isolated holds: {sum(1 for row in rows if row['action_class'] == 'special_type_exam_group_isolated_hold')}",
        "",
        "Official 2025 plan totals:",
    ]
    for school, total in sorted(school_totals.items()):
        lines.append(f"- {school}: {total} ({school_breakdowns.get(school, '')})")
    lines.extend(["", "Status rollup:"])
    for row in status_rows:
        lines.append(
            f"- {row['mapping_status']} -> {row['action_class']}: {row['rows']} rows, "
            f"schools={row['universities_seen']}, groups={row['group_codes_seen']}"
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
    marker = "## 95. 2026-05-16 Batch7 SHZU/FJUT mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增 batch7 石河子大学/福建理工大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_mapping_review_packet.csv`
- `reports/reference_trend_520_batch7_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_batch7_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_batch7_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_batch7_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_batch7_mapping_review_packet.md`

覆盖结果：从既有 batch7 group mapping workbench 派生 {values.get('packet_rows')} 行审核包，覆盖石河子大学与福建理工大学；历史考试院趋势 context {values.get('historical_context_rows')} 行；官方计划数可用但广西专业组映射缺失 hold {values.get('plan_count_available_multi_group_mapping_hold_rows')} 行；学校级计划总数 summary {values.get('school_plan_total_unassigned_summary_rows')} 行；特殊/预科类隔离 {values.get('special_type_exam_group_isolated_hold_rows')} 行。2025 官方计划总数：石河子大学 {values.get('school::石河子大学::official_total_plan_2025')}，福建理工大学 {values.get('school::福建理工大学::official_total_plan_2025')}。

准入边界：本轮只做官方计划总数、考试院组线趋势和人工组映射待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No batch7 workbench rows found.")
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
    print(f"wrote {len(rows)} batch7 SHZU/FJUT mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
