#!/usr/bin/env python3
"""Build a CSUFT group mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch8_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_csuft_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_csuft_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_csuft_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_csuft_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_csuft_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_csuft_mapping_review_packet.md"
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
            "plan_count_selection_available_group_mapping_hold",
            "manual_accept_group_mapping_or_keep_school_level_selection_summary",
            "Official 2025 plan source has plan counts and selection requirements but does not print Guangxi group code.",
        )
    if status == "school_plan_total_unassigned_to_group":
        return (
            "school_plan_total_unassigned_selection_summary",
            "keep_as_school_level_field_thickness_until_group_split_is_confirmed",
            "Official total is deliberately unassigned because the source lacks Guangxi group code.",
        )
    return "hold_unclassified", "manual_review", "Unclassified CSUFT row."


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action, exclusion_reason = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_csuft_review_{idx:04d}",
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
                "official_selection_plan_breakdown_2025": row.get("official_selection_plan_breakdown_2025", ""),
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
                "suggested_decision_options": "accept_group_mapping|keep_school_level_selection_summary|request_official_group_split|reject",
                "selected_decision": "",
                "selected_group_code": "",
                "reviewer": "",
                "decision_notes": "",
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "csuft_mapping_review_packet_only_not_decision_pool",
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
                "official_total_plan_2025_max": max((to_int(row.get("official_total_plan_2025")) for row in group), default=0),
                "rows_with_official_plan_source": sum(1 for row in group if str(row.get("official_plan_source_url", "")).strip()),
                "rows_with_same_code_delta": sum(1 for row in group if is_true(row.get("has_2024_same_code_delta"))),
                "selection_breakdown_seen": "|".join(sorted({str(row.get("official_selection_plan_breakdown_2025", "")) for row in group if str(row.get("official_selection_plan_breakdown_2025", ""))})),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    total_plan = max((to_int(row.get("official_total_plan_2025")) for row in rows), default=0)
    major_rows = max((to_int(row.get("official_major_rows_2025")) for row in rows), default=0)
    selection_breakdowns = sorted({str(row.get("official_selection_plan_breakdown_2025", "")) for row in rows if str(row.get("official_selection_plan_breakdown_2025", ""))})
    groups_seen = sorted({str(row.get("group_code", "")) for row in rows if str(row.get("group_code", ""))})
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from CSUFT batch8 group mapping workbench."},
        {"metric": "universities_covered", "value": len({row.get("university_name") for row in rows}), "note": "|".join(sorted({str(row.get("university_name", "")) for row in rows}))},
        {"metric": "candidate_group_codes_seen", "value": "|".join(groups_seen), "note": "Includes unassigned summary if present."},
        {"metric": "official_total_plan_2025", "value": total_plan, "note": "Official plan total after source packet parse."},
        {"metric": "official_major_rows_2025", "value": major_rows, "note": "Official major-plan rows parsed."},
        {"metric": "official_selection_plan_breakdown_2025", "value": "|".join(selection_breakdowns), "note": "Selection requirement field thickness; group code still absent."},
        {"metric": "historical_context_rows", "value": actions.get("historical_context_only", 0), "note": "Exam-authority historical trend context only."},
        {"metric": "plan_count_selection_available_group_mapping_hold_rows", "value": actions.get("plan_count_selection_available_group_mapping_hold", 0), "note": "Official plan total and selection requirements exist but group split is missing."},
        {"metric": "school_plan_total_unassigned_selection_summary_rows", "value": actions.get("school_plan_total_unassigned_selection_summary", 0), "note": "School-level plan total summary row."},
        {"metric": "rows_with_official_plan_source", "value": sum(1 for row in rows if str(row.get("official_plan_source_url", "")).strip()), "note": "Rows carrying official source URL."},
        {"metric": "rows_with_same_code_delta", "value": sum(1 for row in rows if is_true(row.get("has_2024_same_code_delta"))), "note": "Rows with 2024 to 2025 same-code rank delta."},
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
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 7 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "historical_context_rows_expected", "status": "PASS" if actions.get("historical_context_only", 0) == 3 else "WARN", "detail": str(actions.get("historical_context_only", 0))},
        {"check": "regular_group_mapping_hold_rows_expected", "status": "PASS" if actions.get("plan_count_selection_available_group_mapping_hold", 0) == 3 else "WARN", "detail": str(actions.get("plan_count_selection_available_group_mapping_hold", 0))},
        {"check": "school_total_summary_rows_expected", "status": "PASS" if actions.get("school_plan_total_unassigned_selection_summary", 0) == 1 else "WARN", "detail": str(actions.get("school_plan_total_unassigned_selection_summary", 0))},
        {"check": "official_plan_total_carried", "status": "PASS" if max(to_int(row.get("official_total_plan_2025")) for row in rows) == 150 else "WARN", "detail": "expected 150"},
        {"check": "official_major_rows_carried", "status": "PASS" if max(to_int(row.get("official_major_rows_2025")) for row in rows) == 41 else "WARN", "detail": "expected 41"},
        {"check": "source_missing_group_code", "status": "PASS" if not any(is_true(row.get("official_source_contains_group_code")) for row in rows) else "WARN", "detail": "official_source_contains_group_code checked"},
        {"check": "selection_breakdown_present", "status": "PASS" if any(str(row.get("official_selection_plan_breakdown_2025", "")).strip() for row in rows) else "WARN", "detail": "selection plan breakdown checked"},
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
    total_plan = max((to_int(row.get("official_total_plan_2025")) for row in rows), default=0)
    major_rows = max((to_int(row.get("official_major_rows_2025")) for row in rows), default=0)
    selection_breakdowns = sorted({str(row.get("official_selection_plan_breakdown_2025", "")) for row in rows if str(row.get("official_selection_plan_breakdown_2025", ""))})
    lines = [
        "# CSUFT Mapping Review Packet",
        "",
        "Scope: 中南林业科技大学 2025 official plan evidence joined only to Guangxi exam-authority group-line context.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Historical context rows: {sum(1 for row in rows if row['action_class'] == 'historical_context_only')}",
        f"- Regular plan-count and selection available but group-mapping hold rows: {sum(1 for row in rows if row['action_class'] == 'plan_count_selection_available_group_mapping_hold')}",
        f"- School-level unassigned plan summary rows: {sum(1 for row in rows if row['action_class'] == 'school_plan_total_unassigned_selection_summary')}",
        f"- Official 2025 plan total: {total_plan}",
        f"- Official major rows: {major_rows}",
        f"- Selection breakdown: {'|'.join(selection_breakdowns)}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(
            f"- {row['mapping_status']} -> {row['action_class']}: {row['rows']} rows, "
            f"groups={row['group_codes_seen']}, source_rows={row['rows_with_official_plan_source']}"
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
    marker = "## 97. 2026-05-16 CSUFT mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增中南林业科技大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_csuft_mapping_review_packet.csv`
- `reports/reference_trend_520_csuft_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_csuft_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_csuft_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_csuft_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_csuft_mapping_review_packet.md`

覆盖结果：从既有 CSUFT batch8 group mapping workbench 派生 {values.get('packet_rows')} 行审核包；历史考试院趋势 context {values.get('historical_context_rows')} 行；官方计划数和选科拆分可用但广西专业组映射缺失 hold {values.get('plan_count_selection_available_group_mapping_hold_rows')} 行；学校级计划总数 summary {values.get('school_plan_total_unassigned_selection_summary_rows')} 行。2025 官方计划总数 {values.get('official_total_plan_2025')}，官方专业 rows {values.get('official_major_rows_2025')}，选科拆分：{values.get('official_selection_plan_breakdown_2025')}。

准入边界：本轮只做官方计划总数、选科拆分、考试院组线趋势和人工组映射待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No CSUFT workbench rows found.")
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
    print(f"wrote {len(rows)} CSUFT mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
