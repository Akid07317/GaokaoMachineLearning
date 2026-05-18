#!/usr/bin/env python3
"""Build SCUEC source-packet group mapping workbench.

This joins 中南民族大学 official source-packet parse rows against existing
Guangxi exam-authority group-year rows. It produces a QA workbench only and
does not create canonical, ML, or decision-pool records.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

SOURCE_PARSE = SEED_DIR / "reference_trend_scuec_source_packet_parse_preview.csv"
WINDOW = SEED_DIR / "reference_trend_520_rank_window_preview.csv"
DELTA = SEED_DIR / "reference_trend_520_rank_window_delta_preview.csv"

OUT = SEED_DIR / "reference_trend_scuec_group_mapping_workbench.csv"
QA_OUT = REPORT_DIR / "reference_trend_scuec_group_mapping_qa.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_scuec_group_mapping_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_scuec_group_mapping.md"

FIELDS = [
    "record_id",
    "source_record_id",
    "source_id",
    "source_url",
    "year",
    "university_code",
    "university_name",
    "source_row_label",
    "group_or_selection_label",
    "source_min_score",
    "source_plan_count",
    "exam_group_code_candidate",
    "exam_score",
    "exam_rank",
    "exam_source_type",
    "delta_pair_key",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "mapping_status",
    "mapping_confidence",
    "field_gaps_after_mapping",
    "source_packet_next_action",
    "eligible_for_trend_record",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_rows() -> list[dict[str, object]]:
    source_rows = read_csv(SOURCE_PARSE)
    window_rows = [
        row
        for row in read_csv(WINDOW)
        if row.get("university_code") == "10524" and row.get("year") == "2024"
    ]
    delta_by_group = {
        row.get("group_code", ""): row
        for row in read_csv(DELTA)
        if row.get("university_code") == "10524"
    }

    exam_by_score: dict[str, list[dict[str, str]]] = {}
    for row in window_rows:
        exam_by_score.setdefault(row.get("min_score", ""), []).append(row)

    output: list[dict[str, object]] = []
    for source in source_rows:
        if source.get("special_type_detected") != "ordinary_candidate":
            continue
        if source.get("source_contains_min_score") == "true" and source.get("min_score"):
            matches = exam_by_score.get(source.get("min_score", ""), [])
            if len(matches) == 1:
                exam = matches[0]
                delta = delta_by_group.get(exam.get("group_code", ""), {})
                output.append(
                    {
                        "source_record_id": source.get("record_id", ""),
                        "source_id": source.get("source_id", ""),
                        "source_url": source.get("source_url", ""),
                        "year": source.get("year", ""),
                        "university_code": source.get("university_code", ""),
                        "university_name": source.get("university_name", ""),
                        "source_row_label": source.get("source_row_label", ""),
                        "group_or_selection_label": source.get("group_or_selection_label", ""),
                        "source_min_score": source.get("min_score", ""),
                        "source_plan_count": "",
                        "exam_group_code_candidate": exam.get("group_code", ""),
                        "exam_score": exam.get("min_score", ""),
                        "exam_rank": exam.get("min_rank", ""),
                        "exam_source_type": exam.get("source_type", ""),
                        "delta_pair_key": delta.get("group_pair_key", ""),
                        "rank_delta_2025_minus_2024": delta.get("rank_delta_2025_minus_2024", ""),
                        "trend_direction": delta.get("trend_direction", ""),
                        "mapping_status": "score_exact_single_exam_group_match",
                        "mapping_confidence": "T1_school_score_matches_exam_authority_group",
                        "field_gaps_after_mapping": "plan_count|2025_same_group_plan_mapping",
                        "source_packet_next_action": "use_as_group_mapping_evidence_only_then_seek_2025_plan_group_code_or_exam_plan_source",
                        "eligible_for_trend_record": "false",
                        "calibration_eligible": "false",
                        "canonical_ml_entry_open": "false",
                        "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
                    }
                )
            else:
                output.append(
                    {
                        "source_record_id": source.get("record_id", ""),
                        "source_id": source.get("source_id", ""),
                        "source_url": source.get("source_url", ""),
                        "year": source.get("year", ""),
                        "university_code": source.get("university_code", ""),
                        "university_name": source.get("university_name", ""),
                        "source_row_label": source.get("source_row_label", ""),
                        "group_or_selection_label": source.get("group_or_selection_label", ""),
                        "source_min_score": source.get("min_score", ""),
                        "source_plan_count": "",
                        "mapping_status": "score_match_ambiguous_or_missing",
                        "mapping_confidence": "T3_requires_manual_group_mapping",
                        "field_gaps_after_mapping": "explicit_group_code|plan_count|min_rank",
                        "source_packet_next_action": "manual_review_required_before_group_mapping",
                        "eligible_for_trend_record": "false",
                        "calibration_eligible": "false",
                        "canonical_ml_entry_open": "false",
                        "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
                    }
                )
        elif source.get("source_contains_plan_count") == "true" and source.get("plan_count"):
            output.append(
                {
                    "source_record_id": source.get("record_id", ""),
                    "source_id": source.get("source_id", ""),
                    "source_url": source.get("source_url", ""),
                    "year": source.get("year", ""),
                    "university_code": source.get("university_code", ""),
                    "university_name": source.get("university_name", ""),
                    "source_row_label": source.get("source_row_label", ""),
                    "group_or_selection_label": "",
                    "source_min_score": "",
                    "source_plan_count": source.get("plan_count", ""),
                    "mapping_status": "plan_row_unmapped_no_group_code",
                    "mapping_confidence": "T2_official_plan_count_but_group_unmapped",
                    "field_gaps_after_mapping": "explicit_group_code|min_score|min_rank",
                    "source_packet_next_action": "aggregate_or_map_majors_to_exam_group_only_after_official_group_structure_found",
                    "eligible_for_trend_record": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "reference_trend_group_mapping_workbench_only_not_decision_pool",
                }
            )

    for index, row in enumerate(output, start=1):
        row["record_id"] = f"reference_trend_scuec_group_mapping_{index:04d}"
    return output


def write_doc(rows: list[dict[str, object]]) -> None:
    status = Counter(row.get("mapping_status", "") for row in rows)
    confidence = Counter(row.get("mapping_confidence", "") for row in rows)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend SCUEC Group Mapping Workbench",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已将中南民族大学 source packet 解析结果与广西考试院 520 位次窗口数据做组映射 QA。2024 校方分数页的 3 个普通物理组分数可一一匹配考试院 group code 103/104/105；2025 计划页的 32 条普通计划行仍无显式组代码，只能作为计划数/专业结构候选，不能进入院校专业组-year。",
                "",
                "## 覆盖",
                "",
                f"- workbench rows: {len(rows)}",
                f"- score exact single-group matches: {status.get('score_exact_single_exam_group_match', 0)}",
                f"- plan rows still unmapped: {status.get('plan_row_unmapped_no_group_code', 0)}",
                f"- mapping status counts: {dict(status)}",
                f"- confidence counts: {dict(confidence)}",
                "- trend record eligible rows: 0",
                "- calibration eligible rows: 0",
                "",
                "## 下一步",
                "",
                "- 把 2024 三个分数组映射作为 QA 证据保留，不直接生成趋势样本。",
                "- 继续寻找 2025 官方院校专业组结构或考试院计划来源，解决 2025 计划行无法落到 group code 的问题。",
                "- 继续保持 canonical/ML 和 32 所 decision_pool 入口关闭。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    qa_rows = []
    for row in rows:
        qa_rows.append(
            {
                "record_id": row.get("record_id", ""),
                "source_record_id": row.get("source_record_id", ""),
                "mapping_status": row.get("mapping_status", ""),
                "mapping_confidence": row.get("mapping_confidence", ""),
                "blocking_issues": row.get("field_gaps_after_mapping", ""),
                "next_action": row.get("source_packet_next_action", ""),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": row.get("decision_pool_boundary", ""),
            }
        )
    write_csv(
        QA_OUT,
        qa_rows,
        [
            "record_id",
            "source_record_id",
            "mapping_status",
            "mapping_confidence",
            "blocking_issues",
            "next_action",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    status = Counter(row.get("mapping_status", "") for row in rows)
    confidence = Counter(row.get("mapping_confidence", "") for row in rows)
    rollup = [
        {"metric": "scuec_group_mapping_workbench_rows", "value": len(rows)},
        {"metric": "score_exact_single_group_match_rows", "value": status.get("score_exact_single_exam_group_match", 0)},
        {"metric": "plan_row_unmapped_no_group_code_rows", "value": status.get("plan_row_unmapped_no_group_code", 0)},
        {"metric": "t1_mapping_evidence_rows", "value": confidence.get("T1_school_score_matches_exam_authority_group", 0)},
        {"metric": "t2_unmapped_plan_candidate_rows", "value": confidence.get("T2_official_plan_count_but_group_unmapped", 0)},
        {"metric": "trend_record_eligible_rows", "value": 0},
        {"metric": "calibration_eligible_rows", "value": 0},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"scuec_group_mapping_workbench_rows={len(rows)}")
    print(f"score_exact_single_group_match_rows={status.get('score_exact_single_exam_group_match', 0)}")


if __name__ == "__main__":
    main()
