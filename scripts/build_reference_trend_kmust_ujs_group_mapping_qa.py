#!/usr/bin/env python3
"""Build KMUST/UJS group-mapping QA workbench from batch4 parsed sources."""

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
OUT = SEED_DIR / "reference_trend_kmust_ujs_group_mapping_qa_workbench.csv"
ROLLUP = REPORT_DIR / "reference_trend_kmust_ujs_group_mapping_qa_rollup.csv"
QA = REPORT_DIR / "reference_trend_kmust_ujs_group_mapping_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_kmust_ujs_group_mapping_qa_exclusion_log.csv"
DOC = DOC_DIR / "reference_trend_kmust_ujs_group_mapping_qa.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"


FIELDS = [
    "record_id",
    "source_record_id",
    "university_code",
    "university_name",
    "year",
    "batch",
    "subject_category",
    "major_or_group",
    "elective_requirement",
    "admission_type",
    "admission_count",
    "source_min_score",
    "source_min_rank",
    "source_max_score",
    "source_max_rank",
    "candidate_group_codes",
    "candidate_group_scores",
    "candidate_group_ranks",
    "candidate_group_count",
    "exact_score_group_codes",
    "single_regular_group_code",
    "mapping_status",
    "confidence_tier",
    "special_type_detected",
    "source_url",
    "raw_file_path",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
]


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


def as_int(value: str) -> int | None:
    if value is None or value == "":
        return None
    return int(float(value))


def join_values(rows: list[dict[str, str]], key: str) -> str:
    return "|".join(row.get(key, "") for row in rows)


def append_handoff(section: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    marker = "## 23. 2026-05-16 昆明理工/江苏大学 group mapping QA"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip()
    HANDOFF.write_text(existing.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")


def build_kmust(rows: list[dict[str, str]], lines: list[dict[str, str]]) -> list[dict[str, object]]:
    source_rows = [
        row for row in rows
        if row.get("university_code") == "10674"
        and row.get("qa_status") in {"score_rank_reference_ready_group_mapping_needed", "non_physics_score_row_hold"}
    ]
    group_lines = [
        row for row in lines
        if row.get("university_code") == "10674"
        and row.get("year") == "2025"
        and row.get("subject_type") == "物理类"
        and row.get("batch") == "本科普通批"
    ]
    group_lines.sort(key=lambda row: int(row["min_score"]), reverse=True)
    out: list[dict[str, object]] = []
    for idx, source in enumerate(source_rows, start=1):
        score = as_int(source.get("min_score", ""))
        rank = as_int(source.get("min_rank", ""))
        is_physics = source.get("subject_category") == "物理类"
        candidates = [row for row in group_lines if score is not None and int(row["min_score"]) <= score]
        exact = [row for row in group_lines if score is not None and int(row["min_score"]) == score]
        if not is_physics:
            status = "non_physics_row_hold"
            confidence = "T4_non_physics_hold"
            required = "exclude history row from physical group mapping"
            candidate_rows: list[dict[str, str]] = []
            exact_rows: list[dict[str, str]] = []
        elif len(exact) == 1:
            status = "score_exact_single_group_floor_candidate"
            confidence = "T2_major_score_equals_exam_group_floor_but_group_code_unconfirmed"
            required = "verify official group membership or plan structure before accepting mapping"
            candidate_rows = candidates
            exact_rows = exact
        elif len(candidates) == 1:
            status = "single_threshold_group_candidate"
            confidence = "T3_single_threshold_candidate_group_code_unconfirmed"
            required = "verify official group membership before accepting mapping"
            candidate_rows = candidates
            exact_rows = exact
        else:
            status = "ambiguous_multi_group_threshold_candidate"
            confidence = "T3_ambiguous_group_mapping_by_score_threshold"
            required = "need official group structure or plan grouping to resolve candidate group"
            candidate_rows = candidates
            exact_rows = exact
        out.append(
            {
                "record_id": f"reference_trend_kmust_group_mapping_qa_{idx:04d}",
                "source_record_id": source.get("record_id", ""),
                "university_code": "10674",
                "university_name": "昆明理工大学",
                "year": "2025",
                "batch": source.get("batch", ""),
                "subject_category": source.get("subject_category", ""),
                "major_or_group": source.get("major_or_group", ""),
                "elective_requirement": source.get("elective_requirement", ""),
                "admission_type": "",
                "admission_count": "",
                "source_min_score": score if score is not None else "",
                "source_min_rank": rank if rank is not None else "",
                "source_max_score": source.get("max_score", ""),
                "source_max_rank": source.get("max_rank", ""),
                "candidate_group_codes": join_values(candidate_rows, "group_code"),
                "candidate_group_scores": join_values(candidate_rows, "min_score"),
                "candidate_group_ranks": join_values(candidate_rows, "min_rank_est"),
                "candidate_group_count": len(candidate_rows),
                "exact_score_group_codes": join_values(exact_rows, "group_code"),
                "single_regular_group_code": "",
                "mapping_status": status,
                "confidence_tier": confidence,
                "special_type_detected": source.get("special_type_detected", ""),
                "source_url": source.get("source_url", ""),
                "raw_file_path": source.get("raw_file_path", ""),
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_mapping_qa_only_not_decision_pool",
                "required_resolution": required,
                "evidence_note": "KMUST official major score/rank row mapped only by score-threshold logic against Guangxi exam-authority group lines; no official group code in source row.",
            }
        )
    return out


def build_ujs(rows: list[dict[str, str]], lines: list[dict[str, str]]) -> list[dict[str, object]]:
    source_rows = [
        row for row in rows
        if row.get("university_code") == "10299"
        and row.get("parser_dataset") == "ujs_2025_guangxi_score_html_table"
    ]
    regular_groups = [
        row for row in lines
        if row.get("university_code") == "10299"
        and row.get("year") == "2025"
        and row.get("subject_type") == "物理类"
        and row.get("batch") == "本科普通批"
        and not row.get("remark")
    ]
    special_groups = [
        row for row in lines
        if row.get("university_code") == "10299"
        and row.get("year") == "2025"
        and row.get("subject_type") == "物理类"
        and row.get("batch") == "本科普通批"
        and row.get("remark")
    ]
    single_regular = regular_groups[0] if len(regular_groups) == 1 else {}
    out: list[dict[str, object]] = []
    for idx, source in enumerate(source_rows, start=1):
        score = as_int(source.get("min_score", ""))
        is_physics = source.get("subject_category") == "物理类"
        is_special = bool(source.get("special_type_detected"))
        if is_physics and not is_special and single_regular:
            status = "single_regular_exam_group_candidate_no_rank"
            confidence = "T2_single_regular_group_score_reference_rank_missing"
            candidate_rows = regular_groups
            exact_rows = [row for row in regular_groups if score is not None and int(row["min_score"]) == score]
            required = "derive/verify min rank and group structure before calibration"
        elif is_physics and is_special:
            status = "national_special_score_row_hold"
            confidence = "T4_special_type_hold"
            candidate_rows = special_groups
            exact_rows = [row for row in special_groups if score is not None and int(row["min_score"]) == score]
            required = "keep national-special rows isolated"
        else:
            status = "non_physics_score_row_hold"
            confidence = "T4_non_physics_hold"
            candidate_rows = []
            exact_rows = []
            required = "exclude history rows from physical group mapping"
        out.append(
            {
                "record_id": f"reference_trend_ujs_group_mapping_qa_{idx:04d}",
                "source_record_id": source.get("record_id", ""),
                "university_code": "10299",
                "university_name": "江苏大学",
                "year": "2025",
                "batch": source.get("batch", ""),
                "subject_category": source.get("subject_category", ""),
                "major_or_group": source.get("major_or_group", ""),
                "elective_requirement": source.get("elective_requirement", ""),
                "admission_type": "国家专项" if is_special else "普通类",
                "admission_count": source.get("admission_count", ""),
                "source_min_score": score if score is not None else "",
                "source_min_rank": "",
                "source_max_score": source.get("max_score", ""),
                "source_max_rank": "",
                "candidate_group_codes": join_values(candidate_rows, "group_code"),
                "candidate_group_scores": join_values(candidate_rows, "min_score"),
                "candidate_group_ranks": join_values(candidate_rows, "min_rank_est"),
                "candidate_group_count": len(candidate_rows),
                "exact_score_group_codes": join_values(exact_rows, "group_code"),
                "single_regular_group_code": single_regular.get("group_code", ""),
                "mapping_status": status,
                "confidence_tier": confidence,
                "special_type_detected": source.get("special_type_detected", ""),
                "source_url": source.get("source_url", ""),
                "raw_file_path": source.get("raw_file_path", ""),
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_mapping_qa_only_not_decision_pool",
                "required_resolution": required,
                "evidence_note": "UJS official Guangxi score HTML gives major min scores/admission counts but no rank. Ordinary physical rows are assigned only as single-regular-group candidates.",
            }
        )
    return out


def main() -> None:
    rows = read_csv(PARSE_PREVIEW)
    lines = read_csv(ADMISSION_LINES)
    workbench = build_kmust(rows, lines) + build_ujs(rows, lines)
    exclusions = [
        row for row in workbench
        if row["mapping_status"] not in {
            "score_exact_single_group_floor_candidate",
            "single_threshold_group_candidate",
            "single_regular_exam_group_candidate_no_rank",
        }
    ]
    status_counts = Counter(row["mapping_status"] for row in workbench)
    university_counts = Counter(row["university_name"] for row in workbench)
    rollup = [
        {"metric": "workbench_rows", "value": len(workbench), "note": ""},
        {"metric": "kmust_rows", "value": university_counts["昆明理工大学"], "note": ""},
        {"metric": "ujs_rows", "value": university_counts["江苏大学"], "note": ""},
        {"metric": "hold_or_exclusion_rows", "value": len(exclusions), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Mapping QA only; group assignment not formally accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for status, count in sorted(status_counts.items()):
        rollup.append({"metric": f"mapping_status::{status}", "value": count, "note": ""})
    qa = [
        {
            "qa_check": "kmust_exact_score_group_floor_candidates",
            "status": "info",
            "value": status_counts["score_exact_single_group_floor_candidate"],
            "note": "Exact score-to-group-floor rows are useful QA but not accepted mappings without group structure.",
        },
        {
            "qa_check": "kmust_ambiguous_threshold_candidates",
            "status": "review",
            "value": status_counts["ambiguous_multi_group_threshold_candidate"],
            "note": "Need official group structure or plan grouping.",
        },
        {
            "qa_check": "ujs_single_regular_group_candidates",
            "status": "info",
            "value": status_counts["single_regular_exam_group_candidate_no_rank"],
            "note": "UJS has one regular physical exam group line in 2025, but source rows lack rank.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]
    write_csv(OUT, workbench, FIELDS)
    write_csv(EXCLUSION, exclusions, FIELDS)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["qa_check", "status", "value", "note"])

    doc = f"""# Reference Trend KMUST/UJS Group Mapping QA

Run time: {datetime.now().isoformat(timespec="seconds")}

## Result

- Workbench rows: {len(workbench)}
- KMUST rows: {university_counts['昆明理工大学']}
- UJS rows: {university_counts['江苏大学']}
- KMUST exact score group-floor candidates: {status_counts['score_exact_single_group_floor_candidate']}
- KMUST ambiguous threshold candidates: {status_counts['ambiguous_multi_group_threshold_candidate']}
- UJS single regular-group candidates: {status_counts['single_regular_exam_group_candidate_no_rank']}
- Reference trend eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry: closed

## Boundary

KMUST has official major-level score/rank evidence, but no official Guangxi group code per row. UJS ordinary physical rows can be associated with the only regular physical exam group in 2025, but the source lacks min rank. Both are QA workbench assets rather than accepted group-year records.

## Next Step

Continue searching for official plan/group structure for KMUST and plan/rank source for UJS. If no safe source appears, continue P0/P1 discovery for the next queue items.
"""
    DOC.write_text(doc, encoding="utf-8")

    handoff = f"""## 23. 2026-05-16 昆明理工/江苏大学 group mapping QA

已新增 KMUST/UJS group mapping QA 工作台：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：workbench {len(workbench)} 行，其中昆明理工大学 {university_counts['昆明理工大学']} 行、江苏大学 {university_counts['江苏大学']} 行。昆明理工有 {status_counts['score_exact_single_group_floor_candidate']} 条分数等于考试院组线的 floor 候选，{status_counts['ambiguous_multi_group_threshold_candidate']} 条多组阈值候选；江苏大学有 {status_counts['single_regular_exam_group_candidate_no_rank']} 条普通物理单一组候选。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。KMUST 缺官方组代码，UJS 缺位次/组结构，全部只作为 mapping QA。

下一轮优先级：继续寻找 KMUST 官方分组计划/组结构或 UJS 计划/位次来源；若无安全来源，回到 P0/P1 官方来源发现队列。
"""
    append_handoff(handoff)

    print(f"wrote {OUT}")
    print(f"wrote {ROLLUP}")
    print(f"wrote {QA}")
    print(f"wrote {EXCLUSION}")
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
