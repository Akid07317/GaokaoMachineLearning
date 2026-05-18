#!/usr/bin/env python3
"""Build boundary QA for newly landed official cache rows.

This batch covers newly materialized official source rows for Beijing
University of Technology, Donghua University, and CUGB. These are treated as
source-packet evidence only because they belong to the 32-school decision-pool
orbit or need group/batch review before any trend use.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

OUT_PREVIEW = CLEAN / "reference_trend_new_official_cache_batch_qa_preview.csv"
OUT_ROLLUP = REPORTS / "reference_trend_new_official_cache_batch_qa_rollup.csv"
OUT_EXCLUSION = REPORTS / "reference_trend_new_official_cache_batch_exclusion_log.csv"
OUT_DOC = DOCS / "reference_trend_new_official_cache_batch_qa.md"


INPUTS = [
    ("bjut_plan", REPORTS / "bjut_guangxi_plan_rows.csv", "official_plan_row"),
    ("bjut_score", REPORTS / "bjut_guangxi_score_rows.csv", "official_major_score_row"),
    ("dhu_score", REPORTS / "dhu_guangxi_score_rows.csv", "official_major_score_row"),
    ("cugb_plan", REPORTS / "cugb_beijing_guangxi_plan_rows.csv", "official_plan_row"),
    ("cugb_score_major", REPORTS / "cugb_beijing_guangxi_score_major_rows.csv", "official_major_score_row"),
    ("cugb_score_summary", REPORTS / "cugb_beijing_guangxi_score_summary_rows.csv", "official_summary_score_row"),
]


SPECIAL_MARKERS = ("专项", "预科", "民族", "中外", "合作", "艺术", "体育", "提前")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def first(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name, "")
        if value not in ("", None):
            return str(value).strip()
    return ""


def normalize_subject(value: str) -> str:
    value = value.strip()
    if value in ("物理", "物理类", "理工", "理"):
        return "物理类" if value != "理" else "旧理科"
    if value in ("历史", "历史类", "文史", "文"):
        return "历史类" if value != "文" else "旧文科"
    if value.startswith("物化"):
        return value
    return value


def has_special(*values: str) -> bool:
    text = " ".join(v for v in values if v)
    return any(marker in text for marker in SPECIAL_MARKERS)


def infer_row(dataset: str, role: str, row: dict[str, str], source_file: Path, index: int) -> dict[str, object]:
    school_key = first(row, "school_key") or ("zhongguo_dizhi_beijing_211" if dataset.startswith("cugb") else "")
    school_name = first(row, "school_name") or ("中国地质大学北京" if dataset.startswith("cugb") else "")
    year = first(row, "year", "plan_year")
    province = first(row, "province")
    batch = first(row, "type", "group_label")
    raw_subject = first(row, "subject_type", "science_category")
    subject = normalize_subject(raw_subject)
    major = first(row, "major", "major_name", "specialty")
    group_label = first(row, "selection_group", "group_label", "science_category", "requirement")
    plan_count = first(row, "plan_count", "plan_count_numeric")
    min_score = first(row, "minimum_score")
    min_rank = first(row, "minimum_rank", "lowest_score_ranking")
    max_score = first(row, "maximum_score", "highest_score")
    avg_score = first(row, "average_score")
    source_url = first(row, "source_url")
    source_pdf = first(row, "source_pdf")
    source_payload = first(row, "source_payload", "source_pdf_name")
    requirement = first(row, "requirement", "reselect_requirement")
    remarks = first(row, "remarks")
    special = has_special(batch, major, remarks, group_label)

    strict_year = year in ("2024", "2025")
    strict_subject = subject == "物理类" or subject.startswith("物化")
    strict_batch = any(token in batch for token in ("普通", "本科一批", "普通考生")) or batch == ""
    strict_candidate = province == "广西" and strict_year and strict_subject and strict_batch and not special

    if year == "2023" or subject == "旧理科":
        qa_status = "bridge_2023_old_science_hold"
        required_resolution = "keep_as_bridge_background_not_strict_2024_2025_group_year"
    elif not strict_candidate:
        qa_status = "not_strict_guangxi_physics_hold"
        required_resolution = "exclude_or_reclassify_before_intake"
    elif role == "official_plan_row" and not group_label:
        qa_status = "source_packet_ready_group_mapping_needed"
        required_resolution = "map_plan_major_rows_to_exam_authority_group_before_trend_use"
    elif role == "official_major_score_row" and not min_rank:
        qa_status = "source_packet_ready_rank_missing_or_batch_review"
        required_resolution = "derive_rank_from_score_rank_table_or_hold_for_decision_pool_evidence"
    elif role == "official_summary_score_row":
        qa_status = "summary_score_boundary_hold"
        required_resolution = "summary_row_not_major_or_group_year_record"
    else:
        qa_status = "source_packet_ready_boundary_hold"
        required_resolution = "keep_as_decision_pool_source_packet_or_explicitly_approve_trend_use"

    return {
        "record_id": f"new_official_cache_{dataset}_{index:04d}",
        "dataset": dataset,
        "source_file": str(source_file.relative_to(ROOT)),
        "source_row_number": index,
        "school_key": school_key,
        "school_name": school_name,
        "year": year,
        "province": province,
        "batch": batch,
        "subject_category": subject,
        "source_role": role,
        "major_or_group": major,
        "group_label": group_label,
        "plan_count": plan_count,
        "minimum_score": min_score,
        "minimum_rank": min_rank,
        "maximum_score": max_score,
        "average_score": avg_score,
        "requirement": requirement,
        "remarks": remarks,
        "source_url": source_url or source_pdf,
        "source_payload": source_payload,
        "source_contains_group_code": "false",
        "source_contains_plan_count": str(bool(plan_count)).lower(),
        "source_contains_min_score": str(bool(min_score)).lower(),
        "source_contains_min_rank": str(bool(min_rank)).lower(),
        "special_type_detected": str(special).lower(),
        "strict_2024_2025_candidate": str(strict_candidate).lower(),
        "qa_status": qa_status,
        "collector_confidence": "T2_official_cache_or_pdf_extract",
        "intended_layer": "source_packet_preview_only",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
        "required_resolution": required_resolution,
    }


def main() -> None:
    preview: list[dict[str, object]] = []
    exclusion: list[dict[str, object]] = []
    counts = Counter()

    for dataset, path, role in INPUTS:
        rows = read_csv(path)
        counts["input_files_present"] += int(path.exists())
        counts["input_rows"] += len(rows)
        for idx, row in enumerate(rows, start=1):
            record = infer_row(dataset, role, row, path, idx)
            preview.append(record)
            counts[f"dataset:{dataset}"] += 1
            counts[f"role:{role}"] += 1
            counts[f"qa:{record['qa_status']}"] += 1
            if record["strict_2024_2025_candidate"] == "true":
                counts["strict_candidate_rows"] += 1
            if record["source_contains_plan_count"] == "true":
                counts["rows_with_plan_count"] += 1
            if record["source_contains_min_score"] == "true":
                counts["rows_with_min_score"] += 1
            if record["source_contains_min_rank"] == "true":
                counts["rows_with_min_rank"] += 1

            if record["qa_status"] != "source_packet_ready_boundary_hold":
                exclusion.append(
                    {
                        "record_id": f"new_official_cache_exclusion_{len(exclusion) + 1:04d}",
                        "source_record_id": record["record_id"],
                        "dataset": dataset,
                        "school_name": record["school_name"],
                        "qa_status": record["qa_status"],
                        "exclusion_or_hold_reason": record["required_resolution"],
                        "canonical_ml_entry_open": "false",
                        "reference_trend_pool_eligible": "false",
                    }
                )

    fields = [
        "record_id",
        "dataset",
        "source_file",
        "source_row_number",
        "school_key",
        "school_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "source_role",
        "major_or_group",
        "group_label",
        "plan_count",
        "minimum_score",
        "minimum_rank",
        "maximum_score",
        "average_score",
        "requirement",
        "remarks",
        "source_url",
        "source_payload",
        "source_contains_group_code",
        "source_contains_plan_count",
        "source_contains_min_score",
        "source_contains_min_rank",
        "special_type_detected",
        "strict_2024_2025_candidate",
        "qa_status",
        "collector_confidence",
        "intended_layer",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
    ]
    write_csv(OUT_PREVIEW, preview, fields)
    write_csv(
        OUT_EXCLUSION,
        exclusion,
        [
            "record_id",
            "source_record_id",
            "dataset",
            "school_name",
            "qa_status",
            "exclusion_or_hold_reason",
            "canonical_ml_entry_open",
            "reference_trend_pool_eligible",
        ],
    )

    rollup = [
        ("input_files_present", counts["input_files_present"]),
        ("input_rows", counts["input_rows"]),
        ("preview_rows", len(preview)),
        ("official_plan_rows", counts["role:official_plan_row"]),
        ("official_major_score_rows", counts["role:official_major_score_row"]),
        ("official_summary_score_rows", counts["role:official_summary_score_row"]),
        ("strict_2024_2025_candidate_rows", counts["strict_candidate_rows"]),
        ("source_packet_ready_boundary_hold_rows", counts["qa:source_packet_ready_boundary_hold"]),
        ("source_packet_ready_group_mapping_needed_rows", counts["qa:source_packet_ready_group_mapping_needed"]),
        ("source_packet_ready_rank_missing_or_batch_review_rows", counts["qa:source_packet_ready_rank_missing_or_batch_review"]),
        ("bridge_2023_old_science_hold_rows", counts["qa:bridge_2023_old_science_hold"]),
        ("summary_score_boundary_hold_rows", counts["qa:summary_score_boundary_hold"]),
        ("rows_with_plan_count", counts["rows_with_plan_count"]),
        ("rows_with_min_score", counts["rows_with_min_score"]),
        ("rows_with_min_rank", counts["rows_with_min_rank"]),
        ("reference_trend_pool_eligible_rows", 0),
        ("calibration_eligible_rows", 0),
        ("canonical_ml_entry_open", "false"),
        ("decision_pool_expansion_performed", "false"),
    ]
    write_csv(
        OUT_ROLLUP,
        [{"metric": metric, "value": value} for metric, value in rollup],
        ["metric", "value"],
    )

    dataset_lines = "\n".join(
        f"- {key.removeprefix('dataset:')}: {value} rows"
        for key, value in sorted(counts.items())
        if key.startswith("dataset:")
    )
    OUT_DOC.write_text(
        f"""# New Official Cache Batch QA

日期：{date.today().isoformat()}

## 结论

已将新增落地的北京工业大学、东华大学、中国地质大学北京官方缓存/官方文章行统一做 source-packet 边界 QA。该批数据仍属于 32 所 decision-pool 证据线或需要 group/rank/batch 复核，因此本轮不进入 `reference_trend_pool`，不写 canonical，不打开 ML。

## 覆盖

- input rows: {counts['input_rows']}
- preview rows: {len(preview)}
- official plan rows: {counts['role:official_plan_row']}
- official major score rows: {counts['role:official_major_score_row']}
- strict 2024/2025 candidate rows: {counts['strict_candidate_rows']}
- group mapping needed rows: {counts['qa:source_packet_ready_group_mapping_needed']}
- rank missing / batch review rows: {counts['qa:source_packet_ready_rank_missing_or_batch_review']}
- bridge 2023 old science hold rows: {counts['qa:bridge_2023_old_science_hold']}
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 数据集

{dataset_lines}

## 下一步

1. 北京工业大学：2025 计划/分数可作证据，但需与考试院专业组线做映射；2023 旧理科只放 bridge 背景。
2. 东华大学：2025 文章有 `物化1/物化2` 组标签但缺最低位次，需用一分一档换算或继续查官方位次/考试院组线。
3. 中国地质大学北京：官方 AJAX 源质量较好，可继续做 group mapping workbench，但仍不自动进入 trend/canonical/ML。
""",
        encoding="utf-8",
    )

    print(f"new_official_cache_preview_rows={len(preview)}")
    print(f"strict_2024_2025_candidate_rows={counts['strict_candidate_rows']}")
    print("reference_trend_pool_eligible_rows=0")


if __name__ == "__main__":
    main()
