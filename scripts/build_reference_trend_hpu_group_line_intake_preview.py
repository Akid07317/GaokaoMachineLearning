#!/usr/bin/env python3
"""Create HPU plan-enrichment intake preview candidates.

The global reference_trend_intake_preview already contains Guangxi exam-line
group-year rows. This script creates a school-source enrichment preview instead
of appending duplicate rows to the global intake file.
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

WORKBENCH = SEED_DIR / "reference_trend_hpu_group_line_workbench.csv"
GLOBAL_INTAKE = SEED_DIR / "reference_trend_intake_preview.csv"

OUT = SEED_DIR / "reference_trend_hpu_group_line_intake_preview.csv"
ROLLUP = REPORT_DIR / "reference_trend_hpu_group_line_intake_preview_rollup.csv"
QA = REPORT_DIR / "reference_trend_hpu_group_line_intake_preview_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_hpu_group_line_intake_preview_exclusion_log.csv"
DOC = DOC_DIR / "reference_trend_hpu_group_line_intake_preview.md"
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


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def main() -> None:
    workbench_rows = read_csv(WORKBENCH)
    global_rows = read_csv(GLOBAL_INTAKE)
    global_by_key = {row.get("group_year_key", ""): row for row in global_rows}

    candidate_rows = [
        row
        for row in workbench_rows
        if row.get("reference_trend_intake_candidate") == "true"
        and row.get("join_status") == "ordinary_physics_group_line_plan_verified_intake_candidate"
    ]

    fields = [
        "candidate_record_id",
        "group_year_key",
        "existing_reference_trend_intake_record_id",
        "existing_global_intake_found",
        "enrichment_action",
        "year",
        "province",
        "batch",
        "subject_category",
        "university_code",
        "university_name",
        "group_code",
        "min_score",
        "min_rank_est",
        "min_rank_low",
        "min_rank_high",
        "rank_source_method",
        "plan_count",
        "has_plan_count",
        "plan_count_source_status",
        "elective_requirement",
        "major_count",
        "major_structure",
        "special_type_detected",
        "confidence_tier",
        "trend_pool_role_candidate",
        "calibration_eligible_candidate",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "qa_status",
        "qa_flags",
        "exam_line_source_id",
        "official_score_source_url",
        "official_plan_source_url",
        "official_raw_files",
        "score_rank_match_status",
        "rank_delta_school_minus_exam",
        "score_delta_2025_minus_2024",
        "rank_delta_2025_minus_2024",
        "trend_direction",
        "rank_band_2024",
        "rank_band_2025",
        "decision_pool_boundary",
        "canonical_ml_entry_open",
        "required_resolution",
        "notes",
    ]

    out: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, row in enumerate(candidate_rows, start=1):
        group_key = f"{row['university_code']}-{row['group_code']}-2025"
        existing = global_by_key.get(group_key, {})
        global_found = bool(existing)
        score_match = clean(existing.get("min_score")) == clean(row.get("exam_score_2025"))
        rank_match = clean(existing.get("min_rank_est")) == clean(row.get("exam_rank_2025"))
        qa_flags: list[str] = []
        if not global_found:
            qa_flags.append("missing_existing_global_intake_record")
        if global_found and not score_match:
            qa_flags.append("global_exam_score_mismatch")
        if global_found and not rank_match:
            qa_flags.append("global_exam_rank_mismatch")
        if clean(row.get("rank_delta_school_minus_exam")):
            qa_flags.append(f"school_rank_offset_{row['rank_delta_school_minus_exam']}")
        if not clean(row.get("score_delta_2025_minus_2024")):
            qa_flags.append("no_same_code_2024_delta_pair")

        qa_status = "qa_pass_plan_enrichment_candidate"
        if "missing_existing_global_intake_record" in qa_flags or "global_exam_score_mismatch" in qa_flags:
            qa_status = "qa_review_before_enrichment"

        out.append(
            {
                "candidate_record_id": f"reference_trend_hpu_group_line_intake_candidate_{idx:04d}",
                "group_year_key": group_key,
                "existing_reference_trend_intake_record_id": existing.get("trend_record_id", ""),
                "existing_global_intake_found": bool_text(global_found),
                "enrichment_action": "enrich_existing_reference_trend_group_year_with_official_plan_and_major_structure"
                if global_found
                else "hold_missing_global_group_year",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "group_code": row.get("group_code", ""),
                "min_score": row.get("exam_score_2025", ""),
                "min_rank_est": row.get("exam_rank_2025", ""),
                "min_rank_low": row.get("exam_rank_low_2025", ""),
                "min_rank_high": row.get("exam_rank_high_2025", ""),
                "rank_source_method": "gx_exam_authority_min_rank_est_with_school_floor_qa",
                "plan_count": row.get("plan_count_2025", ""),
                "has_plan_count": "true",
                "plan_count_source_status": "school_official_plan_and_score_page_consistent",
                "elective_requirement": row.get("elective_requirement", ""),
                "major_count": row.get("group_major_count", ""),
                "major_structure": row.get("major_or_group", ""),
                "special_type_detected": "",
                "confidence_tier": "T1_exam_line_plus_school_official_plan_major_structure",
                "trend_pool_role_candidate": "plan_enriched_2025_group_year_candidate",
                "calibration_eligible_candidate": "true",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "qa_status": qa_status,
                "qa_flags": "|".join(qa_flags) if qa_flags else "none",
                "exam_line_source_id": row.get("exam_line_source_id_2025", ""),
                "official_score_source_url": row.get("official_score_source_url", ""),
                "official_plan_source_url": row.get("official_plan_source_url", ""),
                "official_raw_files": row.get("official_raw_files", ""),
                "score_rank_match_status": row.get("score_rank_match_status", ""),
                "rank_delta_school_minus_exam": row.get("rank_delta_school_minus_exam", ""),
                "score_delta_2025_minus_2024": row.get("score_delta_2025_minus_2024", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "rank_band_2024": row.get("rank_band_2024", ""),
                "rank_band_2025": row.get("rank_band_2025", ""),
                "decision_pool_boundary": "reference_trend_enrichment_preview_only_not_decision_pool",
                "canonical_ml_entry_open": "false",
                "required_resolution": "batch acceptance required before merging enrichment into global reference_trend intake; no canonical/ML write",
                "notes": "Candidate enriches an existing Guangxi exam-authority group-year with school official plan count and major composition.",
            }
        )

    for row in workbench_rows:
        if row.get("reference_trend_intake_candidate") != "true":
            exclusions.append(
                {
                    "record_id": row.get("record_id", ""),
                    "university_code": row.get("university_code", ""),
                    "university_name": row.get("university_name", ""),
                    "group_code": row.get("group_code", ""),
                    "exclusion_reason": row.get("special_type_detected") or row.get("join_status", ""),
                    "required_resolution": row.get("required_resolution", ""),
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "reference_trend_enrichment_preview_only_not_decision_pool",
                }
            )

    status_counts = Counter(row["qa_status"] for row in out)
    direction_counts = Counter(row["trend_direction"] for row in out)
    rollup_rows = [
        {"metric": "hpu_enrichment_intake_candidate_rows", "value": len(out), "note": "HPU 101-105 ordinary physics groups."},
        {"metric": "existing_global_intake_found_rows", "value": sum(1 for row in out if row["existing_global_intake_found"] == "true"), "note": "Prevents duplicate append to global intake preview."},
        {"metric": "candidate_plan_total", "value": sum(int(row["plan_count"]) for row in out if clean(row["plan_count"])), "note": ""},
        {"metric": "qa_pass_candidate_rows", "value": status_counts["qa_pass_plan_enrichment_candidate"], "note": ""},
        {"metric": "qa_review_candidate_rows", "value": status_counts["qa_review_before_enrichment"], "note": ""},
        {"metric": "boundary_or_hold_rows", "value": len(exclusions), "note": "History/sino-foreign/historical-only groups remain excluded."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Preview only; needs batch acceptance."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Candidate flag only; final calibration remains closed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": ""},
    ]
    for direction, count in sorted(direction_counts.items()):
        rollup_rows.append({"metric": f"trend_direction::{direction or 'blank'}", "value": count, "note": ""})

    qa_rows = [
        {
            "qa_check": "candidate_count_101_105",
            "status": "pass" if len(out) == 5 else "review",
            "value": len(out),
            "note": "Expected HPU ordinary physics groups 101-105.",
        },
        {
            "qa_check": "global_intake_dedupe",
            "status": "pass" if all(row["existing_global_intake_found"] == "true" for row in out) else "review",
            "value": f"{sum(1 for row in out if row['existing_global_intake_found'] == 'true')}/{len(out)}",
            "note": "Rows should enrich existing group-year records, not duplicate them.",
        },
        {
            "qa_check": "plan_total",
            "status": "pass" if sum(int(row["plan_count"]) for row in out if clean(row["plan_count"])) == 50 else "review",
            "value": sum(int(row["plan_count"]) for row in out if clean(row["plan_count"])),
            "note": "Ordinary physical groups only.",
        },
        {
            "qa_check": "all_candidates_have_candidate_flag",
            "status": "pass" if all(row["calibration_eligible_candidate"] == "true" for row in out) else "review",
            "value": f"{sum(1 for row in out if row['calibration_eligible_candidate'] == 'true')}/{len(out)}",
            "note": "Candidate flag is not final calibration eligibility.",
        },
        {
            "qa_check": "final_pool_and_ml_closed",
            "status": "pass",
            "value": "closed",
            "note": "reference_trend_pool_eligible=false, calibration_eligible=false, canonical_ml_entry_open=false for all rows.",
        },
    ]

    write_csv(OUT, out, fields)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(
        EXCLUSION,
        exclusions,
        ["record_id", "university_code", "university_name", "group_code", "exclusion_reason", "required_resolution", "canonical_ml_entry_open", "decision_pool_boundary"],
    )

    doc = f"""# 河南理工大学 Group-Line Intake Preview

Generated: {datetime.now().isoformat(timespec="seconds")}

## Result

- Enrichment intake candidates: {len(out)}
- Existing global intake records found: {sum(1 for row in out if row['existing_global_intake_found'] == 'true')}
- Candidate plan total: {sum(int(row['plan_count']) for row in out if clean(row['plan_count']))}
- Boundary / hold rows: {len(exclusions)}

## Boundary

This file does not append to `reference_trend_intake_preview.csv`. It is an enrichment preview for existing HPU group-year rows, adding official school plan counts and major structure. `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` remain closed until batch acceptance.
"""
    DOC.write_text(doc, encoding="utf-8")

    marker = "## 29. 2026-05-16 河南理工大学 group-line intake preview"
    section = f"""
{marker}

已新增河南理工大学 group-line intake preview 候选层：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：101-105 五个普通物理组均找到既有全局 `reference_trend_intake_preview` group-year 记录，因此本轮不追加全局 intake，改为生成 plan/major-structure enrichment preview。候选计划合计 50；101/102 为 higher selectivity，104/105 为 lower selectivity，103 为 2025-only 无同码 delta。

准入边界：本轮仅 `calibration_eligible_candidate=true`，正式 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可批量接受该 enrichment，或继续处理下一个 P0/P1 官方计划源。
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
