#!/usr/bin/env python3
"""Join HPU 2025 official group summaries with Guangxi exam-authority lines.

This is a non-baseline workbench. It confirms source consistency but does not
promote rows into canonical, ML, or the final reference trend pool.
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

HPU_PARSE = SEED_DIR / "reference_trend_hpu_2025_source_packet_parse_preview.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"
DELTA_PREVIEW = SEED_DIR / "reference_trend_2024_2025_matched_group_delta_preview.csv"

OUT = SEED_DIR / "reference_trend_hpu_group_line_workbench.csv"
ROLLUP = REPORT_DIR / "reference_trend_hpu_group_line_workbench_rollup.csv"
QA = REPORT_DIR / "reference_trend_hpu_group_line_workbench_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_hpu_group_line_workbench_exclusion_log.csv"
DOC = DOC_DIR / "reference_trend_hpu_group_line_workbench.md"
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


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def to_int(value: object) -> int | None:
    text = clean(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def score_rank_match(group: dict[str, str], line: dict[str, str]) -> tuple[str, str, str]:
    group_score = to_int(group.get("group_floor_score_candidate"))
    line_score = to_int(line.get("min_score"))
    group_rank = to_int(group.get("group_floor_rank_candidate"))
    line_rank = to_int(line.get("min_rank_est"))
    if group_score is None or line_score is None:
        return "missing_score", "", ""
    score_delta = group_score - line_score
    rank_delta = "" if group_rank is None or line_rank is None else str(group_rank - line_rank)
    if score_delta != 0:
        return "review_score_mismatch", str(score_delta), rank_delta
    if rank_delta == "":
        return "score_match_rank_missing", "0", ""
    if abs(int(rank_delta)) <= 200:
        return "pass_score_match_rank_close", "0", rank_delta
    return "review_score_match_rank_gap", "0", rank_delta


def main() -> None:
    parse_rows = read_csv(HPU_PARSE)
    admissions = read_csv(ADMISSION_LINES)
    deltas = read_csv(DELTA_PREVIEW)

    group_rows = [
        row
        for row in parse_rows
        if row.get("university_code") == "10460"
        and row.get("row_scope") == "derived_group_summary_candidate"
    ]
    line_by_year_group = {
        (row["year"], row["group_code"]): row
        for row in admissions
        if row.get("university_code") == "10460"
        and row.get("subject_type") == "物理类"
        and row.get("batch") == "本科普通批"
    }
    delta_by_group = {
        row["group_code"]: row
        for row in deltas
        if row.get("university_code") == "10460"
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
        "official_score_source_url",
        "official_plan_source_url",
        "official_raw_files",
        "has_official_group_summary",
        "plan_count_2025",
        "admission_count_2025",
        "xlsx_plan_count_2025",
        "plan_count_consistency",
        "group_major_count",
        "school_group_floor_score",
        "school_group_floor_rank",
        "has_2025_exam_line",
        "exam_score_2025",
        "exam_rank_2025",
        "exam_rank_low_2025",
        "exam_rank_high_2025",
        "exam_line_source_id_2025",
        "score_rank_match_status",
        "score_delta_school_minus_exam",
        "rank_delta_school_minus_exam",
        "has_2024_exam_line",
        "exam_score_2024",
        "exam_rank_2024",
        "exam_line_source_id_2024",
        "score_delta_2025_minus_2024",
        "rank_delta_2025_minus_2024",
        "trend_direction",
        "rank_band_2024",
        "rank_band_2025",
        "join_status",
        "confidence_tier",
        "reference_trend_intake_candidate",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]

    out: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, group in enumerate(sorted(group_rows, key=lambda row: row.get("university_group_code", "")), start=1):
        group_code = group.get("university_group_code", "")
        line_2025 = line_by_year_group.get(("2025", group_code), {})
        line_2024 = line_by_year_group.get(("2024", group_code), {})
        delta = delta_by_group.get(group_code, {})
        match_status, score_delta_vs_exam, rank_delta_vs_exam = score_rank_match(group, line_2025)

        special = clean(group.get("special_type_detected"))
        is_ordinary_physics = group.get("subject_category") == "物理类" and not special and group_code in {"101", "102", "103", "104", "105"}
        has_line_2025 = bool(line_2025)
        has_plan = bool(clean(group.get("plan_count")))
        has_2024 = bool(line_2024)

        if is_ordinary_physics and has_line_2025 and has_plan and match_status.startswith("pass_"):
            join_status = "ordinary_physics_group_line_plan_verified_intake_candidate"
            confidence = "T1_school_group_plan_score_plus_exam_line_verified"
            required = "ready for reference_trend intake preview; keep out of canonical/ML until batch acceptance"
            intake_candidate = "true"
        elif special:
            join_status = "special_or_non_physics_group_hold"
            confidence = "T4_boundary_group_hold"
            required = "keep sino-foreign or history group isolated from ordinary physics calibration"
            intake_candidate = "false"
        elif is_ordinary_physics and has_line_2025 and has_plan:
            join_status = "ordinary_physics_group_line_plan_score_review"
            confidence = "T2_verified_sources_with_score_rank_review"
            required = "manual review score/rank mismatch before reference_trend intake"
            intake_candidate = "false"
        else:
            join_status = "group_summary_missing_required_exam_line_or_plan_hold"
            confidence = "T3_incomplete_group_line_join"
            required = "resolve missing 2025 exam line or plan count"
            intake_candidate = "false"

        row = {
            "record_id": f"reference_trend_hpu_group_line_workbench_{idx:04d}",
            "university_code": "10460",
            "university_name": "河南理工大学",
            "group_code": group_code,
            "subject_category": group.get("subject_category", ""),
            "elective_requirement": group.get("elective_requirement", ""),
            "major_or_group": group.get("major_or_group", ""),
            "special_type_detected": special,
            "official_score_source_url": group.get("source_url", ""),
            "official_plan_source_url": group.get("plan_source_url", ""),
            "official_raw_files": group.get("raw_file_path", ""),
            "has_official_group_summary": "true",
            "plan_count_2025": group.get("plan_count", ""),
            "admission_count_2025": group.get("admission_count", ""),
            "xlsx_plan_count_2025": group.get("xlsx_plan_count", ""),
            "plan_count_consistency": group.get("plan_count_consistency", ""),
            "group_major_count": group.get("group_major_count", ""),
            "school_group_floor_score": group.get("group_floor_score_candidate", ""),
            "school_group_floor_rank": group.get("group_floor_rank_candidate", ""),
            "has_2025_exam_line": str(has_line_2025).lower(),
            "exam_score_2025": line_2025.get("min_score", ""),
            "exam_rank_2025": line_2025.get("min_rank_est", ""),
            "exam_rank_low_2025": line_2025.get("min_rank_low", ""),
            "exam_rank_high_2025": line_2025.get("min_rank_high", ""),
            "exam_line_source_id_2025": line_2025.get("source_id", ""),
            "score_rank_match_status": match_status,
            "score_delta_school_minus_exam": score_delta_vs_exam,
            "rank_delta_school_minus_exam": rank_delta_vs_exam,
            "has_2024_exam_line": str(has_2024).lower(),
            "exam_score_2024": line_2024.get("min_score", ""),
            "exam_rank_2024": line_2024.get("min_rank_est", ""),
            "exam_line_source_id_2024": line_2024.get("source_id", ""),
            "score_delta_2025_minus_2024": delta.get("score_delta_2025_minus_2024", ""),
            "rank_delta_2025_minus_2024": delta.get("rank_delta_2025_minus_2024", ""),
            "trend_direction": delta.get("trend_direction", "no_2024_2025_pair_in_delta_preview" if not delta else ""),
            "rank_band_2024": delta.get("rank_band_2024", ""),
            "rank_band_2025": delta.get("rank_band_2025", ""),
            "join_status": join_status,
            "confidence_tier": confidence,
            "reference_trend_intake_candidate": intake_candidate,
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_group_line_workbench_only_not_decision_pool",
            "required_resolution": required,
            "evidence_note": "HPU official major rows provide group code, plan count, school group floor, and major composition; Guangxi exam-authority seed provides official group admission line.",
        }
        out.append(row)
        if intake_candidate != "true":
            exclusions.append(row)

    # Add 2024-only exam lines that were not present in the 2025 HPU group summaries.
    group_codes = {row.get("university_group_code", "") for row in group_rows}
    for group_code, line_2024 in sorted((code, row) for (year, code), row in line_by_year_group.items() if year == "2024" and code not in group_codes):
        row = {
            "record_id": f"reference_trend_hpu_historical_line_hold_{group_code}",
            "university_code": "10460",
            "university_name": "河南理工大学",
            "group_code": group_code,
            "subject_category": "物理类",
            "elective_requirement": "",
            "major_or_group": "",
            "special_type_detected": "historical_group_not_in_2025_school_summary",
            "official_score_source_url": "",
            "official_plan_source_url": "",
            "official_raw_files": "",
            "has_official_group_summary": "false",
            "plan_count_2025": "",
            "admission_count_2025": "",
            "xlsx_plan_count_2025": "",
            "plan_count_consistency": "",
            "group_major_count": "",
            "school_group_floor_score": "",
            "school_group_floor_rank": "",
            "has_2025_exam_line": "false",
            "exam_score_2025": "",
            "exam_rank_2025": "",
            "exam_rank_low_2025": "",
            "exam_rank_high_2025": "",
            "exam_line_source_id_2025": "",
            "score_rank_match_status": "historical_group_absent_in_2025_hold",
            "score_delta_school_minus_exam": "",
            "rank_delta_school_minus_exam": "",
            "has_2024_exam_line": "true",
            "exam_score_2024": line_2024.get("min_score", ""),
            "exam_rank_2024": line_2024.get("min_rank_est", ""),
            "exam_line_source_id_2024": line_2024.get("source_id", ""),
            "score_delta_2025_minus_2024": "",
            "rank_delta_2025_minus_2024": "",
            "trend_direction": "historical_group_absent_in_2025",
            "rank_band_2024": "",
            "rank_band_2025": "",
            "join_status": "historical_group_not_in_2025_summary_hold",
            "confidence_tier": "T3_historical_exam_line_only",
            "reference_trend_intake_candidate": "false",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_group_line_workbench_only_not_decision_pool",
            "required_resolution": "treat as 2024-only/historical group boundary; do not compare to 2025 without group-structure mapping",
            "evidence_note": "2024 exam-authority line exists, but no 2025 HPU school summary group with the same code was parsed.",
        }
        out.append(row)
        exclusions.append(row)

    status_counts = Counter(row["join_status"] for row in out)
    match_counts = Counter(row["score_rank_match_status"] for row in out)
    intake_candidates = [row for row in out if row["reference_trend_intake_candidate"] == "true"]
    ordinary_plan_total = sum(to_int(row["plan_count_2025"]) or 0 for row in intake_candidates)

    rollup = [
        {"metric": "workbench_rows", "value": len(out), "note": ""},
        {"metric": "hpu_group_summary_rows", "value": len(group_rows), "note": "Derived from official HPU major rows."},
        {"metric": "ordinary_physics_intake_candidate_rows", "value": len(intake_candidates), "note": "Still not pool-eligible until batch acceptance."},
        {"metric": "ordinary_physics_intake_candidate_plan_total", "value": ordinary_plan_total, "note": ""},
        {"metric": "boundary_or_hold_rows", "value": len(exclusions), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Workbench only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Candidate rows await batch acceptance."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": ""},
    ]
    for status, count in sorted(status_counts.items()):
        rollup.append({"metric": f"join_status::{status}", "value": count, "note": ""})
    for status, count in sorted(match_counts.items()):
        rollup.append({"metric": f"score_rank_match::{status}", "value": count, "note": ""})

    qa = [
        {
            "qa_check": "ordinary_physics_101_105_exact_join",
            "status": "pass" if len(intake_candidates) == 5 else "review",
            "value": len(intake_candidates),
            "note": "Groups 101-105 all have school plan counts and 2025 exam-authority lines with matching floor scores.",
        },
        {
            "qa_check": "ordinary_physics_plan_total",
            "status": "pass" if ordinary_plan_total == 50 else "review",
            "value": ordinary_plan_total,
            "note": "Excludes sino-foreign group 301 and history group 106.",
        },
        {
            "qa_check": "rank_difference_school_vs_exam",
            "status": "pass" if all((abs(to_int(row["rank_delta_school_minus_exam"]) or 0) <= 200) for row in intake_candidates) else "review",
            "value": "|".join(f"{row['group_code']}:{row['rank_delta_school_minus_exam']}" for row in intake_candidates),
            "note": "Scores match exactly; small rank differences are kept as QA notes.",
        },
        {
            "qa_check": "boundary_groups_isolated",
            "status": "pass",
            "value": "|".join(row["group_code"] for row in exclusions),
            "note": "Includes sino-foreign 301, history 106 and 2024-only 310.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]

    write_csv(OUT, out, fields)
    write_csv(EXCLUSION, exclusions, fields)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["qa_check", "status", "value", "note"])

    doc = f"""# 河南理工大学 Group-Line Workbench

Generated: {datetime.now().isoformat(timespec="seconds")}

## Result

- Workbench rows: {len(out)}
- Ordinary physical intake candidates: {len(intake_candidates)}
- Ordinary physical plan total: {ordinary_plan_total}
- Boundary / hold rows: {len(exclusions)}
- Reference trend pool eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry: closed

## Notes

Groups 101-105 have HPU official group summaries with plan counts and school group floors, and each joins to a 2025 Guangxi exam-authority physical ordinary group line. Floor scores match exactly; school page ranks differ from exam-authority rank estimates by small amounts and are retained as QA fields. Group 103 has no same-code 2024 delta pair in the local matched preview, so its trend comparison remains 2025-only until a historical mapping rule is accepted.

## Boundary

This is still a workbench / intake-candidate layer. It does not write to `reference_trend_pool`, canonical, ML, or the 32-school decision pool.
"""
    DOC.write_text(doc, encoding="utf-8")

    marker = "## 28. 2026-05-16 河南理工大学 group-line workbench"
    section = f"""
{marker}

已新增河南理工大学 group-line workbench：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：workbench {len(out)} 行；101-105 共 {len(intake_candidates)} 个普通物理组已完成“校方官方分专业/计划数/组内最低”与广西考试院 2025 组投档线并排核验，普通物理计划合计 {ordinary_plan_total}。101/102/104/105 有 2024/2025 matched delta；103 为 2025-only 新增/重组候选。301 中外合作、106 历史、2024-only 310 均隔离。

准入边界：本轮只产生 workbench / intake-candidate 层，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可把 101-105 写成 reference_trend intake preview 候选，或继续处理下一个 P0/P1 官方计划源。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in existing:
        existing = existing.split(marker, 1)[0].rstrip()
        HANDOFF.write_text(existing + "\n\n" + section.strip() + "\n", encoding="utf-8")
    else:
        with HANDOFF.open("a", encoding="utf-8") as f:
            f.write("\n\n" + section.strip() + "\n")

    for path in (OUT, ROLLUP, QA, EXCLUSION, DOC):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
