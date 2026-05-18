#!/usr/bin/env python3
"""Join GXUST official group structure with Guangxi exam-authority group lines.

This produces a non-baseline workbench only. It does not write canonical/ML
records and does not promote rows into the final reference trend pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

PARSE_PREVIEW = SEED_DIR / "reference_trend_520_batch4_source_packet_parse_preview.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"
DELTA_PREVIEW = SEED_DIR / "reference_trend_520_rank_window_delta_preview.csv"
OUT = SEED_DIR / "reference_trend_gxust_group_line_workbench.csv"
ROLLUP = REPORT_DIR / "reference_trend_gxust_group_line_workbench_rollup.csv"
QA = REPORT_DIR / "reference_trend_gxust_group_line_workbench_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_gxust_group_line_workbench_exclusion_log.csv"
DOC = DOC_DIR / "reference_trend_gxust_group_line_workbench.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_handoff(section: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    marker = "## 22. 2026-05-16 广西科技大学 group-line workbench"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip()
    HANDOFF.write_text(existing.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")


def main() -> None:
    parse_rows = read_csv(PARSE_PREVIEW)
    admissions = read_csv(ADMISSION_LINES)
    deltas = read_csv(DELTA_PREVIEW)

    gxust_groups = [
        row
        for row in parse_rows
        if row.get("university_code") == "10594"
        and row.get("parser_dataset") == "gxust_2025_group_structure_pdf"
    ]
    line_by_year_group = {
        (row["year"], row["group_code"]): row
        for row in admissions
        if row.get("university_code") == "10594"
        and row.get("subject_type") == "物理类"
        and row.get("batch") == "本科普通批"
    }
    delta_by_group = {
        row["group_code"]: row
        for row in deltas
        if row.get("university_code") == "10594"
    }

    fields = [
        "record_id",
        "university_code",
        "university_name",
        "group_code",
        "subject_category",
        "elective_requirement",
        "major_or_group",
        "special_type_detected",
        "official_group_structure_source_url",
        "official_group_structure_raw_file",
        "has_official_group_structure",
        "has_2025_exam_line",
        "score_2025",
        "rank_2025",
        "rank_low_2025",
        "rank_high_2025",
        "exam_line_source_id_2025",
        "has_2024_exam_line",
        "score_2024",
        "rank_2024",
        "rank_low_2024",
        "rank_high_2024",
        "exam_line_source_id_2024",
        "rank_delta_2025_minus_2024",
        "trend_direction",
        "in_520_window_2024",
        "in_520_window_2025",
        "has_plan_count_2025",
        "plan_count_2025",
        "join_status",
        "confidence_tier",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]

    out: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, group in enumerate(gxust_groups, start=1):
        code = group["university_group_code"]
        line_2025 = line_by_year_group.get(("2025", code), {})
        line_2024 = line_by_year_group.get(("2024", code), {})
        delta = delta_by_group.get(code, {})
        is_regular_physics = (
            group.get("subject_category") == "物理类"
            and group.get("qa_status") == "group_structure_ready_exam_line_mapping_needed"
            and not group.get("special_type_detected")
        )
        has_2025 = bool(line_2025)
        has_2024 = bool(line_2024)
        has_delta = bool(delta)
        if is_regular_physics and has_2025:
            join_status = "official_group_structure_joined_to_2025_exam_line_plan_count_missing"
            confidence = "T1_group_structure_plus_exam_line_T2_plan_count_missing"
            required = "find official plan-count source or accept plan_count_missing before trend-pool promotion"
        elif is_regular_physics:
            join_status = "official_group_structure_without_2025_exam_line_hold"
            confidence = "T2_group_structure_only_missing_exam_line"
            required = "resolve missing 2025 exam authority group line"
        else:
            join_status = "excluded_non_regular_or_special_group"
            confidence = "T4_excluded_boundary_group"
            required = "keep non-physics, sino-foreign or preparatory group isolated"

        row: dict[str, object] = {
            "record_id": f"reference_trend_gxust_group_line_workbench_{idx:04d}",
            "university_code": "10594",
            "university_name": "广西科技大学",
            "group_code": code,
            "subject_category": group.get("subject_category", ""),
            "elective_requirement": group.get("elective_requirement", ""),
            "major_or_group": group.get("major_or_group", ""),
            "special_type_detected": group.get("special_type_detected", ""),
            "official_group_structure_source_url": group.get("source_url", ""),
            "official_group_structure_raw_file": group.get("raw_file_path", ""),
            "has_official_group_structure": "true",
            "has_2025_exam_line": str(has_2025).lower(),
            "score_2025": line_2025.get("min_score", ""),
            "rank_2025": line_2025.get("min_rank_est", ""),
            "rank_low_2025": line_2025.get("min_rank_low", ""),
            "rank_high_2025": line_2025.get("min_rank_high", ""),
            "exam_line_source_id_2025": line_2025.get("source_id", ""),
            "has_2024_exam_line": str(has_2024).lower(),
            "score_2024": line_2024.get("min_score", ""),
            "rank_2024": line_2024.get("min_rank_est", ""),
            "rank_low_2024": line_2024.get("min_rank_low", ""),
            "rank_high_2024": line_2024.get("min_rank_high", ""),
            "exam_line_source_id_2024": line_2024.get("source_id", ""),
            "rank_delta_2025_minus_2024": delta.get("rank_delta_2025_minus_2024", ""),
            "trend_direction": delta.get("trend_direction", "not_in_520_delta_window" if not has_delta else ""),
            "in_520_window_2024": delta.get("in_2024_520_window", ""),
            "in_520_window_2025": delta.get("in_2025_520_window", ""),
            "has_plan_count_2025": "false",
            "plan_count_2025": "",
            "join_status": join_status,
            "confidence_tier": confidence,
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_group_line_workbench_only_not_decision_pool",
            "required_resolution": required,
            "evidence_note": "Official GXUST group-structure PDF joined to local Guangxi exam-authority admission-line seed; plan count intentionally blank.",
        }
        out.append(row)
        if join_status != "official_group_structure_joined_to_2025_exam_line_plan_count_missing":
            exclusions.append(row)

    official_codes = {row["group_code"] for row in out}
    unmatched_exam_2025 = [
        row
        for (year, group_code), row in sorted(line_by_year_group.items())
        if year == "2025" and group_code not in official_codes
    ]
    for idx, line in enumerate(unmatched_exam_2025, start=1):
        row = {
            "record_id": f"reference_trend_gxust_unmatched_exam_line_2025_{idx:04d}",
            "university_code": "10594",
            "university_name": "广西科技大学",
            "group_code": line.get("group_code", ""),
            "subject_category": "物理类",
            "elective_requirement": "",
            "major_or_group": "",
            "special_type_detected": line.get("remark", "") or "not_in_official_group_structure_pdf",
            "official_group_structure_source_url": "",
            "official_group_structure_raw_file": "",
            "has_official_group_structure": "false",
            "has_2025_exam_line": "true",
            "score_2025": line.get("min_score", ""),
            "rank_2025": line.get("min_rank_est", ""),
            "rank_low_2025": line.get("min_rank_low", ""),
            "rank_high_2025": line.get("min_rank_high", ""),
            "exam_line_source_id_2025": line.get("source_id", ""),
            "has_2024_exam_line": str(bool(line_by_year_group.get(("2024", line.get("group_code", ""))))).lower(),
            "score_2024": line_by_year_group.get(("2024", line.get("group_code", "")), {}).get("min_score", ""),
            "rank_2024": line_by_year_group.get(("2024", line.get("group_code", "")), {}).get("min_rank_est", ""),
            "rank_low_2024": line_by_year_group.get(("2024", line.get("group_code", "")), {}).get("min_rank_low", ""),
            "rank_high_2024": line_by_year_group.get(("2024", line.get("group_code", "")), {}).get("min_rank_high", ""),
            "exam_line_source_id_2024": line_by_year_group.get(("2024", line.get("group_code", "")), {}).get("source_id", ""),
            "rank_delta_2025_minus_2024": delta_by_group.get(line.get("group_code", ""), {}).get("rank_delta_2025_minus_2024", ""),
            "trend_direction": delta_by_group.get(line.get("group_code", ""), {}).get("trend_direction", "exam_line_not_in_official_group_structure_pdf"),
            "in_520_window_2024": delta_by_group.get(line.get("group_code", ""), {}).get("in_2024_520_window", ""),
            "in_520_window_2025": delta_by_group.get(line.get("group_code", ""), {}).get("in_2025_520_window", ""),
            "has_plan_count_2025": "false",
            "plan_count_2025": "",
            "join_status": "exam_line_without_official_group_structure_hold",
            "confidence_tier": "T3_exam_line_only_missing_official_group_structure",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_group_line_workbench_only_not_decision_pool",
            "required_resolution": "classify whether this group is ethnic, preparatory, precision-special, separate campus, or other boundary before use",
            "evidence_note": "2025 exam-authority line exists but no matching row was parsed from the GXUST group-structure PDF.",
        }
        out.append(row)
        exclusions.append(row)

    status_counts = Counter(row["join_status"] for row in out)
    rollup = [
        {"metric": "workbench_rows", "value": len(out), "note": ""},
        {"metric": "official_group_structure_rows", "value": len(gxust_groups), "note": ""},
        {"metric": "regular_physics_groups_joined_2025_exam_line", "value": status_counts["official_group_structure_joined_to_2025_exam_line_plan_count_missing"], "note": "Still missing plan_count."},
        {"metric": "unmatched_2025_exam_line_rows", "value": len(unmatched_exam_2025), "note": "Exam lines not represented in official PDF parse."},
        {"metric": "hold_or_exclusion_rows", "value": len(exclusions), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Plan count missing and boundary rows unresolved."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Kept as workbench; no final acceptance."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": ""},
    ]
    for status, count in sorted(status_counts.items()):
        rollup.append({"metric": f"join_status::{status}", "value": count, "note": ""})

    qa = [
        {
            "qa_check": "gxust_regular_physics_group_exact_join",
            "status": "pass" if status_counts["official_group_structure_joined_to_2025_exam_line_plan_count_missing"] == 8 else "review",
            "value": status_counts["official_group_structure_joined_to_2025_exam_line_plan_count_missing"],
            "note": "Expected 8 ordinary physical groups from official group-structure PDF.",
        },
        {
            "qa_check": "plan_count_available",
            "status": "hold",
            "value": 0,
            "note": "No official plan-count packet has been parsed for these groups yet.",
        },
        {
            "qa_check": "unmatched_exam_lines_need_boundary_classification",
            "status": "review",
            "value": len(unmatched_exam_2025),
            "note": "Includes ethnic/preparatory/other groups in exam-authority seed that are not in parsed official group rows.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "Workbench only; canonical/ML remains closed.",
        },
    ]

    write_csv(OUT, out, fields)
    write_csv(EXCLUSION, exclusions, fields)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["qa_check", "status", "value", "note"])

    doc = f"""# Reference Trend GXUST Group-Line Workbench

Run time: {datetime.now().isoformat(timespec="seconds")}

## Result

- Workbench rows: {len(out)}
- Official group-structure rows: {len(gxust_groups)}
- Regular physical groups joined to 2025 exam line: {status_counts['official_group_structure_joined_to_2025_exam_line_plan_count_missing']}
- Unmatched 2025 exam-authority lines: {len(unmatched_exam_2025)}
- Reference trend eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry: closed

## Boundary

广西科技大学 now has a strong group-line workbench: official university group structure plus Guangxi exam-authority 2025 score/rank lines. The blocker is plan count. Rows are therefore kept in workbench status, not promoted into canonical, ML, or the 32-school decision pool.

## Next Step

Find or parse an official GXUST 2025 plan-count source by group/professional structure. If plan counts remain unavailable, this school can still serve as a high-confidence group-structure and score/rank background reference, but not as a complete plan-sensitive calibration record.
"""
    DOC.write_text(doc, encoding="utf-8")

    handoff = f"""## 22. 2026-05-16 广西科技大学 group-line workbench

已新增广西科技大学 group-line workbench：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：workbench {len(out)} 行，官方专业组结构 {len(gxust_groups)} 行，其中普通物理组 {status_counts['official_group_structure_joined_to_2025_exam_line_plan_count_missing']} 行已精确 join 到 2025 广西考试院投档线；另有 {len(unmatched_exam_2025)} 条 2025 考试院组线未在当前 PDF 解析出的普通组结构中出现，需要边界分类。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是计划数尚未解析；该表只作为 group-line / source-packet QA 工作台，不进入 canonical、ML 或 32 所 decision_pool。

下一轮优先级：寻找/解析广西科技大学官方 2025 分组计划数；若无安全来源，则继续处理昆明理工大学或江苏大学的 group mapping QA。
"""
    append_handoff(handoff)

    print(f"wrote {OUT}")
    print(f"wrote {ROLLUP}")
    print(f"wrote {QA}")
    print(f"wrote {EXCLUSION}")
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
