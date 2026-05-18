#!/usr/bin/env python3
"""Build a ZUCC group-mapping workbench from official image plan + GX lines.

This does not promote rows to canonical/ML. It only records whether the
official school plan image can safely thicken group-year reference rows.
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

INTAKE = SEED_DIR / "reference_trend_intake_preview.csv"
IMAGE_PARSE = SEED_DIR / "reference_trend_zucc_2025_plan_image_parse_preview.csv"
DELTA = SEED_DIR / "reference_trend_2024_2025_matched_group_delta_preview.csv"

OUT = SEED_DIR / "reference_trend_zucc_group_mapping_workbench.csv"
ROLLUP = REPORT_DIR / "reference_trend_zucc_group_mapping_rollup.csv"
QA = REPORT_DIR / "reference_trend_zucc_group_mapping_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_zucc_group_mapping_exclusion_log.csv"
DOC = DOCS_DIR / "reference_trend_zucc_group_mapping.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

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
    "plan_count_from_exam_line",
    "school_plan_physics_total_2025",
    "school_plan_history_total_2025",
    "school_plan_major_rows_2025",
    "source_url",
    "source_owner",
    "source_title",
    "source_confidence_tier",
    "same_code_delta_rank_2025_minus_2024",
    "trend_direction",
    "mapping_status",
    "qa_status",
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


def int_value(value: str) -> int:
    return int(value) if str(value).strip().isdigit() else 0


def main() -> None:
    intake = read_csv(INTAKE)
    image_rows = read_csv(IMAGE_PARSE)
    delta_rows = read_csv(DELTA)

    zucc_intake = [
        row
        for row in intake
        if row.get("university_code") == "13021"
        and row.get("university_name") == "浙大城市学院"
        and row.get("subject_category") == "物理类"
        and row.get("batch") == "本科普通批"
    ]
    zucc_delta = {
        row.get("group_pair_key"): row
        for row in delta_rows
        if row.get("university_code") == "13021"
        and row.get("university_name_2025") == "浙大城市学院"
    }
    major_rows = [row for row in image_rows if row.get("row_scope") == "official_plan_image_major_row"]
    summary = next((row for row in image_rows if row.get("row_scope") == "official_plan_image_summary_row"), {})
    physics_total = sum(int_value(row.get("physics_plan_count", "")) for row in major_rows)
    history_total = sum(int_value(row.get("history_plan_count", "")) for row in major_rows)
    source_url = summary.get("source_url") or (major_rows[0].get("source_url", "") if major_rows else "")

    workbench: list[dict[str, object]] = []

    for idx, row in enumerate(sorted(zucc_intake, key=lambda r: (r.get("year", ""), r.get("group_code", ""))), start=1):
        year = row.get("year", "")
        group_code = row.get("group_code", "")
        group_pair_key = f"13021-{group_code}"
        delta = zucc_delta.get(group_pair_key, {})
        is_2025 = year == "2025"
        if is_2025:
            if group_code == "102":
                mapping_status = "candidate_same_code_group_but_reject_full_80_plan_assignment"
                required = "Need official group-level plan split or defensible major-to-group mapping before assigning any part of the 80 physical plan total to 13021-102."
            else:
                mapping_status = "candidate_2025_exam_group_without_school_plan_split"
                required = "Need official group-level plan split or major-to-group mapping; 2025 has more than one physical group."
            qa_status = "hold_group_plan_split_required"
        else:
            mapping_status = "historical_exam_line_context_only"
            qa_status = "context_only_not_plan_mapping"
            required = "Historical group line supports trend context, not 2025 plan allocation."

        workbench.append(
            {
                "record_id": f"reference_trend_zucc_group_mapping_{idx:04d}",
                "row_scope": "exam_authority_group_line_mapping_context",
                "year": year,
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "group_code": group_code,
                "group_year_key": row.get("group_year_key", ""),
                "min_score": row.get("min_score", ""),
                "min_rank_est": row.get("min_rank_est", ""),
                "plan_count_from_exam_line": row.get("plan_count", ""),
                "school_plan_physics_total_2025": physics_total if is_2025 else "",
                "school_plan_history_total_2025": history_total if is_2025 else "",
                "school_plan_major_rows_2025": len(major_rows) if is_2025 else "",
                "source_url": source_url if is_2025 else row.get("source_url", ""),
                "source_owner": "浙大城市学院本科招生网" if is_2025 else row.get("source_owner", ""),
                "source_title": "浙大城市学院2025年广西招生计划" if is_2025 else row.get("source_title", ""),
                "source_confidence_tier": "T1_official_image_plan_count_plus_T1_exam_authority_line" if is_2025 else row.get("confidence_tier", ""),
                "same_code_delta_rank_2025_minus_2024": delta.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": delta.get("trend_direction", ""),
                "mapping_status": mapping_status,
                "qa_status": qa_status,
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
                "required_resolution": required,
                "evidence_note": (
                    "2025 exam-authority intake has two physical groups for ZUCC (101 and 102), while the official school image only gives one combined 广西物 plan total of 80."
                    if is_2025
                    else "Historical exam-authority row retained to show that 2024 had different group codes in the same rank window."
                ),
            }
        )

    # Add an explicit source-summary row so the rejection of 80 -> 102 is visible.
    workbench.append(
        {
            "record_id": "reference_trend_zucc_group_mapping_source_summary_0001",
            "row_scope": "official_school_plan_total_summary",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "university_code": "13021",
            "university_name": "浙大城市学院",
            "group_code": "unassigned",
            "group_year_key": "",
            "min_score": "",
            "min_rank_est": "",
            "plan_count_from_exam_line": "",
            "school_plan_physics_total_2025": physics_total,
            "school_plan_history_total_2025": history_total,
            "school_plan_major_rows_2025": len(major_rows),
            "source_url": source_url,
            "source_owner": "浙大城市学院本科招生网",
            "source_title": "浙大城市学院2025年广西招生计划",
            "source_confidence_tier": "T1_official_image_plan_count_visual_parse",
            "same_code_delta_rank_2025_minus_2024": "",
            "trend_direction": "",
            "mapping_status": "school_plan_total_unassigned_to_group",
            "qa_status": "pass_plan_sum_but_hold_group_split",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
            "required_resolution": "Use this as school-level field-thickness evidence only until official group-level plan split or major-to-group mapping is found.",
            "evidence_note": "Parsed official image total: 广西物=80, 广西史=10. The image does not print 101/102 group boundaries.",
        }
    )

    counts = Counter(row["mapping_status"] for row in workbench)
    group_2025 = sorted(row.get("group_code") for row in zucc_intake if row.get("year") == "2025")
    rollup = [
        {"metric": "workbench_rows", "value": len(workbench), "note": ""},
        {"metric": "zucc_2025_exam_authority_physics_groups", "value": len(group_2025), "note": "|".join(group_2025)},
        {"metric": "official_image_physics_plan_total", "value": physics_total, "note": "School official image combined 广西物 column."},
        {"metric": "official_image_history_plan_total", "value": history_total, "note": "School official image combined 广西史 column."},
        {"metric": "reject_full_80_to_13021_102", "value": "true", "note": "2025 has groups 101 and 102; school image lacks split."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group mapping unresolved."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Group mapping unresolved."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for key, value in sorted(counts.items()):
        rollup.append({"metric": f"mapping_status::{key}", "value": value, "note": ""})

    qa = [
        {
            "qa_check": "zucc_2025_physics_group_count",
            "status": "hold",
            "value": len(group_2025),
            "note": "Multiple 2025 physical groups mean the official image total cannot be assigned wholesale to 13021-102.",
        },
        {
            "qa_check": "official_image_plan_sum",
            "status": "pass",
            "value": physics_total,
            "note": "Official image major rows sum to 广西物=80.",
        },
        {
            "qa_check": "plan_to_group_mapping",
            "status": "hold",
            "value": "unresolved",
            "note": "Need official group split or major-to-group mapping.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]

    write_csv(OUT, workbench, FIELDS)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, workbench, FIELDS)

    DOC.write_text(
        f"""# ZUCC Group Mapping Workbench

Generated: {date.today().isoformat()}

This workbench checks whether the official ZUCC 2025 Guangxi plan image can safely thicken the `13021-102` group-year trend row.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv`
- `reports/reference_trend_zucc_group_mapping_rollup.csv`
- `reports/reference_trend_zucc_group_mapping_qa.csv`
- `reports/reference_trend_zucc_group_mapping_exclusion_log.csv`

## Finding

Do **not** assign the official image's full 广西物 plan total of {physics_total} to `13021-102`.

Local exam-authority intake rows show that ZUCC has two 2025 Guangxi physical groups: `{', '.join(group_2025)}`. The school official image only provides a combined 广西物 column and does not print group code boundaries. Therefore the official image can thicken school-level plan evidence, but it cannot yet thicken group-level plan count for `13021-102`.

## Trend Context

Existing exam-authority rows still keep `13021-102` as a valid score/rank trend pair:

- 2024 `13021-102`: 518 / rank 44178
- 2025 `13021-102`: 502 / rank 54559
- Rank delta: +10381, direction cooler/lower selectivity

This trend evidence remains score/rank-only because plan-count split is unresolved.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. This workbench does not alter the global intake preview, canonical/ML inputs, or the 32-school decision pool.
""",
        encoding="utf-8",
    )

    append_handoff_once(
        "## 31. ",
        f"""

## 31. {date.today().isoformat()} 浙大城市学院 group mapping workbench

已新增 ZUCC group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv`
- `reports/reference_trend_zucc_group_mapping_rollup.csv`
- `reports/reference_trend_zucc_group_mapping_qa.csv`
- `reports/reference_trend_zucc_group_mapping_exclusion_log.csv`
- `docs/reference_trend_zucc_group_mapping.md`

覆盖结果：本地考试院 intake 显示浙大城市学院 2025 广西物理类有 101、102 两个专业组；官网图片只有合并的“广西物”计划总数 80，不打印专业组边界。因此明确禁止把 80 人整包挂到 `13021-102`。`13021-102` 的 2024/2025 分数位次趋势仍可保留为 score/rank-only：518/44178 -> 502/54559，rank delta +10381，方向 cooler/lower selectivity。

准入边界：本轮仅 group-mapping workbench，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮继续找 ZUCC 官方组内计划拆分/专业到组映射；若找不到，则回到下一个 P0/P1 官方计划源。
""",
    )

    for path in [OUT, ROLLUP, QA, EXCLUSION, DOC]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
