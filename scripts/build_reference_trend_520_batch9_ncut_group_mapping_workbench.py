#!/usr/bin/env python3
"""Build group/subject mapping workbench for batch-9 北方工业大学.

The school source provides 2025 Guangxi-column plan counts by major, but no
Guangxi professional-group code and no subject/selection label. This workbench
joins the source packet against local Guangxi exam-authority group lines and
keeps every potential allocation held for explicit mapping.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

PARSE = SEED_DIR / "reference_trend_520_batch9_ncut_source_packet_parse_preview.csv"
INTAKE = SEED_DIR / "reference_trend_intake_preview.csv"
DELTA = SEED_DIR / "reference_trend_2024_2025_matched_group_delta_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch9_ncut_group_mapping_workbench.csv"
ROLLUP = REPORT_DIR / "reference_trend_520_batch9_ncut_group_mapping_rollup.csv"
QA = REPORT_DIR / "reference_trend_520_batch9_ncut_group_mapping_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_520_batch9_ncut_group_mapping_exclusion_log.csv"
DOC = DOCS_DIR / "reference_trend_520_batch9_ncut_group_mapping.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

TARGET_CODE = "10009"
TARGET_NAME = "北方工业大学"

FIELDS = [
    "record_id",
    "row_scope",
    "year",
    "province",
    "batch",
    "subject_category",
    "university_code",
    "university_name",
    "group_code",
    "group_year_key",
    "min_score",
    "min_rank_est",
    "exam_remark",
    "official_plan_source_url",
    "official_raw_files",
    "official_total_plan_2025",
    "official_major_rows_2025",
    "official_ordinary_unmarked_plan_total_2025",
    "official_special_plan_breakdown_2025",
    "official_source_contains_group_code",
    "official_source_contains_subject_label",
    "candidate_group_from_queue",
    "has_2024_same_code_delta",
    "score_2024",
    "score_2025",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "rank_band_2024",
    "rank_band_2025",
    "mapping_status",
    "qa_status",
    "confidence_tier",
    "reference_trend_intake_candidate",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
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


def to_int(value: object) -> int:
    text = "" if value is None else str(value).strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def parse_summary(parse_rows: list[dict[str, str]]) -> dict[str, object]:
    rows = [row for row in parse_rows if row.get("university_code") == TARGET_CODE]
    total_plan = sum(to_int(row.get("plan_count")) for row in rows)
    special_plan = Counter()
    ordinary_unmarked = 0
    for row in rows:
        plan = to_int(row.get("plan_count"))
        special = row.get("special_type_detected") or "false"
        if special == "false":
            ordinary_unmarked += plan
        else:
            special_plan[special] += plan
    return {
        "rows": rows,
        "total_plan": total_plan,
        "major_rows": len(rows),
        "ordinary_unmarked_plan": ordinary_unmarked,
        "special_breakdown": ";".join(f"{key}:{value}" for key, value in sorted(special_plan.items())) or "none",
        "source_url": rows[0].get("source_url", "") if rows else "",
        "raw_files": "|".join(sorted({row.get("raw_file_path", "") for row in rows if row.get("raw_file_path")})),
        "queue_groups": "|".join(sorted({row.get("queue_group_code", "") for row in rows if row.get("queue_group_code")})),
    }


def mapping_status_for(year: str, group_code: str, exam_special: str, group_count_2025: int) -> tuple[str, str, str, str, str]:
    if year != "2025":
        return (
            "historical_exam_line_context_only",
            "context_only_not_plan_mapping",
            "T3_historical_context_only",
            "false",
            "Historical row supports 2024/2025 trend context, not 2025 plan allocation.",
        )
    if exam_special:
        return (
            "special_type_exam_group_hold",
            "hold_special_type_isolation",
            "T4_special_type_group_hold",
            "false",
            "2025 exam-authority group is marked special/mixed; keep it isolated until a source-level special-type mapping is accepted.",
        )
    if group_count_2025 > 1:
        return (
            "multiple_exam_groups_source_no_group_or_subject_hold",
            "hold_group_and_subject_mapping_required",
            "T2_plan_count_available_group_subject_mapping_missing",
            "false",
            "Official plan source provides major-level plan counts but does not print Guangxi group code or subject/selection labels; manual mapping or official group split is required.",
        )
    return (
        "single_exam_group_candidate_needs_acceptance",
        "hold_manual_acceptance_required",
        "T2_plan_count_available_single_group_candidate",
        "false",
        "Only one 2025 physical group is present locally, but explicit acceptance is still required before calibration.",
    )


def build_rows() -> list[dict[str, object]]:
    parse_rows = read_csv(PARSE)
    intake_rows = [
        row
        for row in read_csv(INTAKE)
        if row.get("university_code") == TARGET_CODE
        and row.get("batch") == "本科普通批"
        and row.get("subject_category") == "物理类"
    ]
    delta_by_key = {
        row.get("group_pair_key"): row
        for row in read_csv(DELTA)
        if row.get("university_code") == TARGET_CODE
    }
    summary = parse_summary(parse_rows)
    group_count_2025 = len({row.get("group_code") for row in intake_rows if row.get("year") == "2025"})
    queue_groups = set(str(summary["queue_groups"]).split("|"))

    out: list[dict[str, object]] = []
    record_idx = 1
    for intake in sorted(intake_rows, key=lambda row: (row.get("year", ""), row.get("group_code", ""))):
        year = intake.get("year", "")
        group_code = intake.get("group_code", "")
        delta = delta_by_key.get(f"{TARGET_CODE}-{group_code}", {})
        exam_special = intake.get("special_type_detected", "")
        mapping_status, qa_status, tier, intake_candidate, resolution = mapping_status_for(year, group_code, exam_special, group_count_2025)
        out.append(
            {
                "record_id": f"reference_trend_520_batch9_ncut_group_mapping_{record_idx:04d}",
                "row_scope": "exam_authority_group_line_mapping_context",
                "year": year,
                "province": intake.get("province", ""),
                "batch": intake.get("batch", ""),
                "subject_category": intake.get("subject_category", ""),
                "university_code": TARGET_CODE,
                "university_name": TARGET_NAME,
                "group_code": group_code,
                "group_year_key": intake.get("group_year_key", ""),
                "min_score": intake.get("min_score", ""),
                "min_rank_est": intake.get("min_rank_est", ""),
                "exam_remark": intake.get("qa_flags", "") or exam_special or intake.get("notes", ""),
                "official_plan_source_url": summary["source_url"] if year == "2025" else "",
                "official_raw_files": summary["raw_files"] if year == "2025" else "",
                "official_total_plan_2025": summary["total_plan"] if year == "2025" else "",
                "official_major_rows_2025": summary["major_rows"] if year == "2025" else "",
                "official_ordinary_unmarked_plan_total_2025": summary["ordinary_unmarked_plan"] if year == "2025" else "",
                "official_special_plan_breakdown_2025": summary["special_breakdown"] if year == "2025" else "",
                "official_source_contains_group_code": "false" if year == "2025" else "",
                "official_source_contains_subject_label": "false" if year == "2025" else "",
                "candidate_group_from_queue": "true" if group_code in queue_groups and year == "2025" else "false",
                "has_2024_same_code_delta": str(bool(delta)).lower(),
                "score_2024": delta.get("score_2024", ""),
                "score_2025": delta.get("score_2025", ""),
                "rank_2024": delta.get("rank_2024", ""),
                "rank_2025": delta.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": delta.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": delta.get("trend_direction", "no_same_code_delta" if not delta else ""),
                "rank_band_2024": delta.get("rank_band_2024", ""),
                "rank_band_2025": delta.get("rank_band_2025", ""),
                "mapping_status": mapping_status,
                "qa_status": qa_status,
                "confidence_tier": tier,
                "reference_trend_intake_candidate": intake_candidate,
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
                "required_resolution": resolution,
                "evidence_note": "Exam-authority group line is official score/rank context; school source adds 2025 Guangxi-column plan thickness but no group or subject label.",
            }
        )
        record_idx += 1

    out.append(
        {
            "record_id": f"reference_trend_520_batch9_ncut_group_mapping_{record_idx:04d}",
            "row_scope": "official_school_plan_total_summary",
            "year": "2025",
            "province": "广西",
            "batch": "本科分专业招生计划_广西列",
            "subject_category": "source_not_printed_hold_for_group_mapping",
            "university_code": TARGET_CODE,
            "university_name": TARGET_NAME,
            "group_code": "unassigned",
            "official_plan_source_url": summary["source_url"],
            "official_raw_files": summary["raw_files"],
            "official_total_plan_2025": summary["total_plan"],
            "official_major_rows_2025": summary["major_rows"],
            "official_ordinary_unmarked_plan_total_2025": summary["ordinary_unmarked_plan"],
            "official_special_plan_breakdown_2025": summary["special_breakdown"],
            "official_source_contains_group_code": "false",
            "official_source_contains_subject_label": "false",
            "candidate_group_from_queue": "false",
            "has_2024_same_code_delta": "false",
            "mapping_status": "school_plan_total_unassigned_to_group_and_subject",
            "qa_status": "pass_plan_sum_but_hold_group_subject_split",
            "confidence_tier": "T1_official_plan_count_summary_no_group_or_subject_code",
            "reference_trend_intake_candidate": "false",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
            "required_resolution": "Use as school-level field-thickness evidence only until official group/subject split or manual mapping is accepted.",
            "evidence_note": "Official source total is deliberately unassigned because group code and subject/selection labels are absent.",
        }
    )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summary = next((row for row in rows if row["row_scope"] == "official_school_plan_total_summary"), {})
    groups_2025 = sorted(
        {
            str(row["group_code"])
            for row in rows
            if row["year"] == "2025" and row["row_scope"] == "exam_authority_group_line_mapping_context"
        }
    )
    rollup = [
        {"metric": "workbench_rows", "value": len(rows), "note": ""},
        {"metric": "universities_covered", "value": 1, "note": TARGET_NAME},
        {"metric": "official_total_plan_2025", "value": summary.get("official_total_plan_2025", ""), "note": ""},
        {"metric": "official_major_rows_2025", "value": summary.get("official_major_rows_2025", ""), "note": ""},
        {"metric": "official_ordinary_unmarked_plan_total_2025", "value": summary.get("official_ordinary_unmarked_plan_total_2025", ""), "note": ""},
        {"metric": "official_special_plan_breakdown_2025", "value": summary.get("official_special_plan_breakdown_2025", ""), "note": ""},
        {"metric": "exam_2025_physics_groups", "value": len(groups_2025), "note": "|".join(groups_2025)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group/subject mapping not accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for status, count in sorted(Counter(str(row["mapping_status"]) for row in rows).items()):
        rollup.append({"metric": f"mapping_status::{status}", "value": count, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    source_rows = [row for row in rows if row["row_scope"] == "official_school_plan_total_summary"]
    group_rows = [row for row in rows if row["row_scope"] == "exam_authority_group_line_mapping_context"]
    group_codes = sorted({str(row["group_code"]) for row in group_rows if row["year"] == "2025"})
    special_groups = [row for row in group_rows if row["year"] == "2025" and row["mapping_status"] == "special_type_exam_group_hold"]
    return [
        {
            "qa_check": "official_plan_total_present",
            "status": "pass" if source_rows else "fail",
            "value": len(source_rows),
            "note": "Official 2025 Guangxi-column plan total is visible but intentionally unassigned to group-year rows.",
        },
        {
            "qa_check": "exam_authority_group_context_present",
            "status": "pass" if group_rows else "fail",
            "value": len(group_rows),
            "note": "Workbench includes 2024/2025 exam-authority group lines for context.",
        },
        {
            "qa_check": "multi_group_subject_boundary",
            "status": "pass",
            "value": len(group_codes),
            "note": f"2025 physical groups: {'|'.join(group_codes)}; source has no group or subject label, so no plan is assigned.",
        },
        {
            "qa_check": "special_group_isolation",
            "status": "pass",
            "value": "|".join(str(row["group_code"]) for row in special_groups) or "none",
            "note": "Special/mixed exam-authority groups stay outside ordinary calibration.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
        {
            "qa_check": "decision_pool_boundary",
            "status": "pass",
            "value": "closed",
            "note": "No merge into the 32-school decision_pool.",
        },
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "official_total_plan_2025": row.get("official_total_plan_2025", ""),
            "exclusion_reason": row["mapping_status"],
            "recommended_next_action": row["required_resolution"],
            "canonical_ml_entry_open": "false",
        }
        for row in rows
        if row["mapping_status"] != "historical_exam_line_context_only"
    ]


def write_doc(rows: list[dict[str, object]]) -> None:
    summary = next(row for row in rows if row["row_scope"] == "official_school_plan_total_summary")
    groups_2025 = sorted(
        {
            str(row["group_code"])
            for row in rows
            if row["year"] == "2025" and row["row_scope"] == "exam_authority_group_line_mapping_context"
        }
    )
    text = f"""# Reference Trend 520 Batch 9 北方工业大学 Group Mapping Workbench

Generated: {date.today().isoformat()}

## Scope

This workbench joins the batch9 北方工业大学 official Guangxi-column plan parse with Guangxi exam-authority group lines. It records field-thickness evidence and group/subject mapping blockers only; it does not open reference_trend calibration, canonical, or ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_qa.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_exclusion_log.csv`

## Summary

- Official 2025 Guangxi-column plan total: {summary['official_total_plan_2025']} across {summary['official_major_rows_2025']} major rows.
- Unmarked ordinary-like plan total: {summary['official_ordinary_unmarked_plan_total_2025']}.
- Special rows marked in source packet: {summary['official_special_plan_breakdown_2025']}.
- Guangxi exam-authority 2025 physical groups visible locally: {'、'.join(groups_2025)}.

## Decision Boundary

The official school plan source does not print Guangxi院校专业组 codes or subject/selection labels. The source total remains unassigned to group-year records: `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: obtain official group-code/subject split or manually accept a mapping rule; otherwise continue P0 official source discovery from the next uncovered row.
"""
    DOC.write_text(text, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]]) -> None:
    summary = next(row for row in rows if row["row_scope"] == "official_school_plan_total_summary")
    groups_2025 = sorted(
        {
            str(row["group_code"])
            for row in rows
            if row["year"] == "2025" and row["row_scope"] == "exam_authority_group_line_mapping_context"
        }
    )
    marker = "## 41. 2026-05-16 batch9 北方工业大学 group mapping workbench"
    content = f"""

{marker}

已新增 batch9 北方工业大学 group/subject mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_qa.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch9_ncut_group_mapping.md`

覆盖结果：北方工业大学官方 2025 广西列计划共 {summary['official_major_rows_2025']} 个专业行、计划合计 {summary['official_total_plan_2025']}；其中未标记普通样态计划 {summary['official_ordinary_unmarked_plan_total_2025']}，特殊边界为 `{summary['official_special_plan_breakdown_2025']}`。本地广西考试院 2025 物理类同校有 {'、'.join(groups_2025)} 组，500 组为特殊/混合边界。

准入边界：官方计划源不打印广西院校专业组代码，也不打印选科/物理类标签；所有计划数仍未分配到 group-year，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可继续找北方工业大学官方组码/选科映射，或推进下一个 P0 官方来源发现批次。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP, build_rollup(rows), ["metric", "value", "note"])
    write_csv(QA, build_qa(rows), ["qa_check", "status", "value", "note"])
    write_csv(
        EXCLUSION,
        build_exclusions(rows),
        [
            "record_id",
            "university_name",
            "group_code",
            "official_total_plan_2025",
            "exclusion_reason",
            "recommended_next_action",
            "canonical_ml_entry_open",
        ],
    )
    write_doc(rows)
    write_handoff(rows)

    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    print(f"wrote {ROLLUP.relative_to(ROOT)}")
    print(f"wrote {QA.relative_to(ROOT)}")
    print(f"wrote {EXCLUSION.relative_to(ROOT)}")
    print(f"wrote {DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
