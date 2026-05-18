#!/usr/bin/env python3
"""Build a reference-trend boundary workbench for Nanhang official cache rows."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"
PLAN_ROWS = REPORTS / "nanhang_guangxi_plan_rows.csv"
SCORE_ROWS = REPORTS / "nanhang_guangxi_score_rows.csv"
OVERVIEW_ROWS = REPORTS / "nanhang_guangxi_score_overview_rows.csv"

OUT_WORKBENCH = CLEAN / "reference_trend_nanhang_group_boundary_workbench.csv"
OUT_ROLLUP = REPORTS / "reference_trend_nanhang_group_boundary_rollup.csv"
OUT_QA = REPORTS / "reference_trend_nanhang_group_boundary_qa.csv"
OUT_EXCLUSION = REPORTS / "reference_trend_nanhang_group_boundary_exclusion_log.csv"
OUT_DOC = DOCS / "reference_trend_nanhang_group_boundary_workbench.md"

UNIVERSITY_CODE = "10287"
UNIVERSITY_NAME = "南京航空航天大学"


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


def to_int(value: object) -> int | None:
    if value in ("", None):
        return None
    try:
        return int(float(str(value)))
    except ValueError:
        return None


def normalize_major(value: str) -> str:
    value = str(value or "")
    value = value.replace("（", "(").replace("）", ")")
    value = re.sub(r"\(.*?\)", "", value)
    value = re.sub(r"（.*?）", "", value)
    value = re.sub(r"\s+", "", value)
    return value


def line_category(row: dict[str, str]) -> str:
    code = row.get("group_code", "").strip()
    remark = row.get("remark", "").strip()
    if "国家专项" in remark or code.startswith("5"):
        return "national_special"
    if "预科" in remark or code.startswith("7"):
        return "preparatory_or_other_special"
    if code.startswith("3"):
        return "separate_unlabeled_group_candidate"
    if code.startswith("1"):
        return "ordinary_regular"
    return "review"


def load_exam_lines() -> dict[str, dict[str, list[dict[str, str]]]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in read_csv(ADMISSION_LINES):
        if (
            row.get("university_code") != UNIVERSITY_CODE
            or row.get("batch") != "本科普通批"
            or row.get("subject_type") != "物理类"
            or row.get("is_first_round") != "true"
        ):
            continue
        category = line_category(row)
        grouped[row.get("year", "")][category].append({**row, "line_category": category})
    for by_category in grouped.values():
        for rows in by_category.values():
            rows.sort(key=lambda r: r.get("group_code", ""))
    return grouped


def line_repr(rows: list[dict[str, str]]) -> str:
    return "|".join(f"{r.get('group_code')}:{r.get('min_score')}/{r.get('min_rank_est')}" for r in rows)


def candidate_groups_for_score(min_score: int | None, ordinary_lines: list[dict[str, str]]) -> tuple[list[str], str]:
    if min_score is None:
        return [], "score_missing"
    eligible: list[str] = []
    floor_hits: list[str] = []
    for line in ordinary_lines:
        floor = to_int(line.get("min_score"))
        if floor is None:
            continue
        if min_score >= floor:
            eligible.append(line.get("group_code", ""))
        if min_score == floor:
            floor_hits.append(line.get("group_code", ""))
    if floor_hits:
        return eligible, "score_equals_ordinary_group_floor_" + "|".join(floor_hits)
    if len(eligible) == 1:
        return eligible, "single_candidate_by_score_floor"
    if len(eligible) > 1:
        return eligible, "ambiguous_multiple_ordinary_groups_by_score_floor"
    return eligible, "below_all_ordinary_group_floors"


def main() -> None:
    exam = load_exam_lines()
    ordinary_2024 = exam.get("2024", {}).get("ordinary_regular", [])
    ordinary_2025 = exam.get("2025", {}).get("ordinary_regular", [])
    separate_2025 = exam.get("2025", {}).get("separate_unlabeled_group_candidate", [])
    special_2024 = [
        row
        for category, rows in exam.get("2024", {}).items()
        for row in rows
        if category != "ordinary_regular"
    ]
    special_2025 = [
        row
        for category, rows in exam.get("2025", {}).items()
        for row in rows
        if category not in {"ordinary_regular", "separate_unlabeled_group_candidate"}
    ]

    score_rows = [
        row
        for row in read_csv(SCORE_ROWS)
        if row.get("year") == "2024"
        and row.get("province") == "广西"
        and row.get("type") == "本科普通批"
        and row.get("science_category") == "物理类"
        and "类型=普通类" in row.get("remarks", "")
    ]
    plan_rows = [
        row
        for row in read_csv(PLAN_ROWS)
        if row.get("year") == "2025"
        and row.get("province") == "广西"
        and row.get("type") == "普通类"
        and row.get("subject") == "物理类"
    ]
    overview_rows = [
        row
        for row in read_csv(OVERVIEW_ROWS)
        if row.get("year") == "2024"
        and row.get("province") == "广西"
        and row.get("subject_type") == "物理类"
    ]

    score_by_norm: dict[str, list[dict[str, object]]] = defaultdict(list)
    workbench: list[dict[str, object]] = []

    for idx, row in enumerate(score_rows, start=1):
        min_score = to_int(row.get("minimum_score"))
        candidate_groups, evidence = candidate_groups_for_score(min_score, ordinary_2024)
        norm = normalize_major(row.get("major", ""))
        score_record = {
            **row,
            "candidate_groups": "|".join(candidate_groups),
            "mapping_evidence": evidence,
        }
        score_by_norm[norm].append(score_record)
        rank_missing = not row.get("lowest_score_ranking", "").strip()
        workbench.append(
            {
                "record_id": f"nanhang_boundary_score_{idx:04d}",
                "source_file": str(SCORE_ROWS.relative_to(ROOT)),
                "source_row_number": idx,
                "row_kind": "official_major_score_2024_candidate",
                "year": "2024",
                "comparison_year": "",
                "university_code": UNIVERSITY_CODE,
                "university_name": UNIVERSITY_NAME,
                "college": "",
                "major_or_group": row.get("major", ""),
                "normalized_major": norm,
                "plan_count": "",
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("lowest_score_ranking", ""),
                "rank_status": "rank_missing_in_official_major_score_api" if rank_missing else "rank_present",
                "exam_ordinary_group_codes": "|".join(line.get("group_code", "") for line in ordinary_2024),
                "exam_ordinary_group_floor_scores": line_repr(ordinary_2024),
                "exam_separate_unlabeled_group_context": "",
                "exam_special_group_context": line_repr(special_2024),
                "candidate_group_codes": "|".join(candidate_groups),
                "candidate_group_count": len(candidate_groups),
                "mapping_evidence": evidence,
                "cross_year_match_status": "",
                "qa_status": "boundary_hold_rank_missing_and_no_source_group_code",
                "confidence_tier": "T2_official_major_score_no_rank_group_candidate",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
                "required_resolution": "official_group_code_or_manual_group_structure_and_rank_source_confirmation",
            }
        )

    for idx, row in enumerate(plan_rows, start=1):
        norm = normalize_major(row.get("specialty", ""))
        matches = score_by_norm.get(norm, [])
        candidate_set = sorted(
            {
                group
                for match in matches
                for group in str(match.get("candidate_groups", "")).split("|")
                if group
            }
        )
        if not matches:
            cross_year_status = "no_2024_major_score_match"
        elif len(matches) == 1:
            cross_year_status = "single_2024_major_score_match"
        else:
            cross_year_status = "multiple_2024_major_score_matches_after_major_normalization"
        if separate_2025:
            qa_status = "boundary_hold_2025_group_303_scope_review_required"
        else:
            qa_status = "boundary_hold_no_source_group_code"
        workbench.append(
            {
                "record_id": f"nanhang_boundary_plan_{idx:04d}",
                "source_file": str(PLAN_ROWS.relative_to(ROOT)),
                "source_row_number": idx,
                "row_kind": "official_plan_2025_cross_year_candidate",
                "year": "2025",
                "comparison_year": "2024",
                "university_code": UNIVERSITY_CODE,
                "university_name": UNIVERSITY_NAME,
                "college": row.get("college", ""),
                "major_or_group": row.get("specialty", ""),
                "normalized_major": norm,
                "plan_count": row.get("plan_number", ""),
                "minimum_score": "",
                "minimum_rank": "",
                "rank_status": "not_score_row",
                "exam_ordinary_group_codes": "|".join(line.get("group_code", "") for line in ordinary_2025),
                "exam_ordinary_group_floor_scores": line_repr(ordinary_2025),
                "exam_separate_unlabeled_group_context": line_repr(separate_2025),
                "exam_special_group_context": line_repr(special_2025),
                "candidate_group_codes": "|".join(candidate_set),
                "candidate_group_count": len(candidate_set),
                "mapping_evidence": "candidate_from_2024_major_score_match" if matches else "no_matching_2024_major_score_row",
                "cross_year_match_status": cross_year_status,
                "qa_status": qa_status,
                "confidence_tier": "T3_cross_year_plan_score_candidate_group_scope_unresolved",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
                "required_resolution": "confirm_2025_group_101_vs_303_scope_and_group_code_before_any_trend_use",
            }
        )

    for idx, row in enumerate(overview_rows, start=1):
        overview_type = row.get("type", "")
        is_ordinary = overview_type == "普通类"
        workbench.append(
            {
                "record_id": f"nanhang_boundary_overview_{idx:04d}",
                "source_file": str(OVERVIEW_ROWS.relative_to(ROOT)),
                "source_row_number": idx,
                "row_kind": "official_score_overview_2024_boundary",
                "year": "2024",
                "comparison_year": "",
                "university_code": UNIVERSITY_CODE,
                "university_name": UNIVERSITY_NAME,
                "college": "",
                "major_or_group": overview_type,
                "normalized_major": "",
                "plan_count": "",
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "rank_status": "rank_missing_in_official_overview_api",
                "exam_ordinary_group_codes": "|".join(line.get("group_code", "") for line in ordinary_2024),
                "exam_ordinary_group_floor_scores": line_repr(ordinary_2024),
                "exam_separate_unlabeled_group_context": "",
                "exam_special_group_context": line_repr(special_2024),
                "candidate_group_codes": "101" if is_ordinary and row.get("minimum_score") == "618" else "",
                "candidate_group_count": 1 if is_ordinary and row.get("minimum_score") == "618" else 0,
                "mapping_evidence": "ordinary_overview_min_score_equals_2024_group_101_floor" if is_ordinary else "special_or_nonordinary_overview_boundary_only",
                "cross_year_match_status": "",
                "qa_status": "boundary_hold_overview_not_major_or_group_year_record",
                "confidence_tier": "T3_overview_boundary_not_group_year",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
                "required_resolution": "overview_rows_are_boundary_evidence_only",
            }
        )

    counts = Counter()
    for row in workbench:
        counts["workbench_rows"] += 1
        counts[f"row_kind:{row['row_kind']}"] += 1
        counts[f"qa_status:{row['qa_status']}"] += 1
        counts[f"cross_year:{row['cross_year_match_status']}"] += 1
        counts[f"evidence:{row['mapping_evidence']}"] += 1
        if int(row["candidate_group_count"]) == 1:
            counts["single_candidate_rows"] += 1
        elif int(row["candidate_group_count"]) > 1:
            counts["ambiguous_candidate_rows"] += 1
        else:
            counts["unmapped_rows"] += 1
        if row["rank_status"] == "rank_missing_in_official_major_score_api":
            counts["major_score_rank_missing_rows"] += 1
        if row["reference_trend_pool_eligible"] == "true":
            counts["reference_trend_pool_eligible_rows"] += 1

    exclusion_rows = [
        {
            "record_id": f"nanhang_boundary_exclusion_{idx:04d}",
            "source_record_id": row["record_id"],
            "row_kind": row["row_kind"],
            "qa_status": row["qa_status"],
            "exclusion_or_hold_reason": row["required_resolution"],
            "reference_trend_pool_eligible": row["reference_trend_pool_eligible"],
            "canonical_ml_entry_open": row["canonical_ml_entry_open"],
        }
        for idx, row in enumerate(workbench, start=1)
        if row["reference_trend_pool_eligible"] != "true"
    ]

    qa_rows = [
        {
            "record_id": "nanhang_group_boundary_qa_0001",
            "check": "exam_authority_ordinary_group_count_2024",
            "value": len(ordinary_2024),
            "result": "pass" if len(ordinary_2024) == 1 else "review",
            "note": line_repr(ordinary_2024),
        },
        {
            "record_id": "nanhang_group_boundary_qa_0002",
            "check": "exam_authority_ordinary_group_count_2025",
            "value": len(ordinary_2025),
            "result": "pass" if len(ordinary_2025) == 1 else "review",
            "note": line_repr(ordinary_2025),
        },
        {
            "record_id": "nanhang_group_boundary_qa_0003",
            "check": "exam_authority_separate_unlabeled_group_2025",
            "value": len(separate_2025),
            "result": "hold" if separate_2025 else "pass",
            "note": line_repr(separate_2025) or "none",
        },
        {
            "record_id": "nanhang_group_boundary_qa_0004",
            "check": "official_major_score_rank_fields_2024",
            "value": counts["major_score_rank_missing_rows"],
            "result": "hold" if counts["major_score_rank_missing_rows"] else "pass",
            "note": "南航 2024 专业分 API 未给最低位次。",
        },
        {
            "record_id": "nanhang_group_boundary_qa_0005",
            "check": "trend_pool_eligible_rows",
            "value": counts["reference_trend_pool_eligible_rows"],
            "result": "pass" if counts["reference_trend_pool_eligible_rows"] == 0 else "review",
            "note": "本轮只生成 32 所 decision_pool source evidence 边界工作台。",
        },
    ]

    fields = [
        "record_id",
        "source_file",
        "source_row_number",
        "row_kind",
        "year",
        "comparison_year",
        "university_code",
        "university_name",
        "college",
        "major_or_group",
        "normalized_major",
        "plan_count",
        "minimum_score",
        "minimum_rank",
        "rank_status",
        "exam_ordinary_group_codes",
        "exam_ordinary_group_floor_scores",
        "exam_separate_unlabeled_group_context",
        "exam_special_group_context",
        "candidate_group_codes",
        "candidate_group_count",
        "mapping_evidence",
        "cross_year_match_status",
        "qa_status",
        "confidence_tier",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
    ]
    write_csv(OUT_WORKBENCH, workbench, fields)
    write_csv(OUT_QA, qa_rows, ["record_id", "check", "value", "result", "note"])
    write_csv(
        OUT_EXCLUSION,
        exclusion_rows,
        [
            "record_id",
            "source_record_id",
            "row_kind",
            "qa_status",
            "exclusion_or_hold_reason",
            "reference_trend_pool_eligible",
            "canonical_ml_entry_open",
        ],
    )

    rollup = [
        ("exam_authority_ordinary_group_rows_2024", len(ordinary_2024)),
        ("exam_authority_ordinary_group_rows_2025", len(ordinary_2025)),
        ("exam_authority_separate_unlabeled_group_rows_2025", len(separate_2025)),
        ("exam_authority_special_context_rows_2024", len(special_2024)),
        ("exam_authority_special_context_rows_2025", len(special_2025)),
        ("official_plan_rows_2025", len(plan_rows)),
        ("official_plan_count_total_2025", sum(to_int(row.get("plan_number")) or 0 for row in plan_rows)),
        ("official_major_score_rows_2024", len(score_rows)),
        ("official_overview_rows_2024", len(overview_rows)),
        ("workbench_rows", counts["workbench_rows"]),
        ("single_candidate_rows", counts["single_candidate_rows"]),
        ("ambiguous_candidate_rows", counts["ambiguous_candidate_rows"]),
        ("unmapped_rows", counts["unmapped_rows"]),
        ("score_equals_ordinary_group_floor_rows", counts["evidence:score_equals_ordinary_group_floor_101"]),
        ("major_score_rank_missing_rows", counts["major_score_rank_missing_rows"]),
        ("plan_rows_no_2024_major_score_match", counts["cross_year:no_2024_major_score_match"]),
        ("plan_rows_single_2024_major_score_match", counts["cross_year:single_2024_major_score_match"]),
        ("plan_rows_multiple_2024_major_score_matches", counts["cross_year:multiple_2024_major_score_matches_after_major_normalization"]),
        ("reference_trend_pool_eligible_rows", counts["reference_trend_pool_eligible_rows"]),
        ("calibration_eligible_rows", 0),
        ("canonical_ml_entry_open", "false"),
        ("decision_pool_expansion_performed", "false"),
    ]
    write_csv(
        OUT_ROLLUP,
        [{"metric": metric, "value": value} for metric, value in rollup],
        ["metric", "value"],
    )

    OUT_DOC.write_text(
        f"""# Reference Trend Nanhang Group Boundary Workbench

日期：{date.today().isoformat()}

## 结论

已把南京航空航天大学官方缓存行整理成 reference-trend 边界工作台。该校属于 32 所 `decision_pool`，本轮只形成 source evidence / QA，不进入 `reference_trend_pool`、canonical 或 ML。

关键边界：

- 2024 广西考试院普通组：{line_repr(ordinary_2024)}
- 2025 广西考试院普通组：{line_repr(ordinary_2025)}
- 2025 未备注分组待判定：{line_repr(separate_2025) or "none"}
- 2024 专业分 API 行数：{len(score_rows)}，但最低位次字段缺失
- 2025 计划行数：{len(plan_rows)}，计划数合计 {sum(to_int(row.get("plan_number")) or 0 for row in plan_rows)}

## 覆盖

- workbench rows: {counts['workbench_rows']}
- 2024 score-major rows: {len(score_rows)}
- 2025 plan rows: {len(plan_rows)}
- 2024 overview rows: {len(overview_rows)}
- single-candidate rows: {counts['single_candidate_rows']}
- ambiguous candidate rows: {counts['ambiguous_candidate_rows']}
- unmapped rows: {counts['unmapped_rows']}
- rank-missing major score rows: {counts['major_score_rank_missing_rows']}
- reference trend eligible rows: {counts['reference_trend_pool_eligible_rows']}

## 使用边界

2024 专业分最低分 `618` 与广西考试院 2024 普通组 `101` 最低分一致，可作为强边界证据；但专业分 API 不含最低位次，也不含院校专业组代码。2025 计划侧有 21 行专业计划，但无法直接确认这些专业属于 `101` 还是未备注的 `303` 组，因此全部保持 hold。

## 下一步

1. 若要正式入 reference trend，需要找到南航 2025 广西招生计划中的院校专业组结构，或人工确认 `303` 组性质。
2. 若继续处理 32 所 source evidence，下一轮可审计 `nanhang` 是否有官方 API 参数能返回 group code。
3. 若回到趋势池扩展，优先处理 P0/P1 非主池官方计划来源发现队列。
""",
        encoding="utf-8",
    )

    print(f"nanhang_group_boundary_workbench_rows={counts['workbench_rows']}")
    print(f"official_plan_rows_2025={len(plan_rows)}")
    print(f"official_major_score_rows_2024={len(score_rows)}")
    print(f"major_score_rank_missing_rows={counts['major_score_rank_missing_rows']}")
    print(f"reference_trend_pool_eligible_rows={counts['reference_trend_pool_eligible_rows']}")


if __name__ == "__main__":
    main()
