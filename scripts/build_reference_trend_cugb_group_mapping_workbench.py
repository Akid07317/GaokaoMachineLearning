#!/usr/bin/env python3
"""Build a source-packet group-mapping workbench for CUGB Beijing rows."""

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
PLAN_ROWS = REPORTS / "cugb_beijing_guangxi_plan_rows.csv"
SCORE_MAJOR_ROWS = REPORTS / "cugb_beijing_guangxi_score_major_rows.csv"
SCORE_SUMMARY_ROWS = REPORTS / "cugb_beijing_guangxi_score_summary_rows.csv"

OUT_WORKBENCH = CLEAN / "reference_trend_cugb_group_mapping_workbench.csv"
OUT_QA = REPORTS / "reference_trend_cugb_group_mapping_qa.csv"
OUT_ROLLUP = REPORTS / "reference_trend_cugb_group_mapping_rollup.csv"
OUT_DOC = DOCS / "reference_trend_cugb_group_mapping.md"

UNIVERSITY_CODE = "11415"
UNIVERSITY_NAME = "中国地质大学(北京)"


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
    value = re.sub(r"\s+", "", value)
    return value


def group_category(row: dict[str, str]) -> str:
    code = row.get("group_code", "")
    remark = row.get("remark", "")
    if code.startswith("1"):
        return "ordinary"
    if code.startswith("5") or "专项" in remark:
        return "national_special"
    if code.startswith("7") or "民族" in remark:
        return "ethnic_or_other_special"
    return "review"


def load_exam_groups() -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    ordinary: dict[str, list[dict[str, str]]] = defaultdict(list)
    special: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(ADMISSION_LINES):
        if (
            row.get("university_code") != UNIVERSITY_CODE
            or row.get("batch") != "本科普通批"
            or row.get("subject_type") != "物理类"
            or row.get("is_first_round") != "true"
        ):
            continue
        category = group_category(row)
        row = {**row, "group_category": category}
        if category == "ordinary":
            ordinary[row.get("year", "")].append(row)
        else:
            special[row.get("year", "")].append(row)

    for rows in ordinary.values():
        rows.sort(key=lambda r: r.get("group_code", ""))
    for rows in special.values():
        rows.sort(key=lambda r: r.get("group_code", ""))
    return ordinary, special


def groups_line(groups: list[dict[str, str]]) -> str:
    return "|".join(f"{g.get('group_code')}:{g.get('min_score')}/{g.get('min_rank_est')}" for g in groups)


def candidate_groups_for_score(
    min_score: int | None,
    min_rank: int | None,
    ordinary_groups: list[dict[str, str]],
    special_groups: list[dict[str, str]],
) -> tuple[list[str], str, str]:
    if min_score is None:
        return [], "score_missing", ""

    eligible: list[str] = []
    anchors: list[str] = []
    rank_anchors: list[str] = []
    for group in ordinary_groups:
        group_score = to_int(group.get("min_score"))
        group_rank = to_int(group.get("min_rank_est"))
        if group_score is None:
            continue
        if min_score >= group_score:
            eligible.append(group.get("group_code", ""))
        if min_score == group_score:
            anchors.append(group.get("group_code", ""))
        if min_rank is not None and group_rank is not None and min_rank == group_rank:
            rank_anchors.append(group.get("group_code", ""))

    special_hits = []
    for group in special_groups:
        group_score = to_int(group.get("min_score"))
        group_rank = to_int(group.get("min_rank_est"))
        if min_score == group_score or (min_rank is not None and min_rank == group_rank):
            special_hits.append(f"{group.get('group_code')}:{group.get('group_category')}")

    evidence_parts: list[str] = []
    if anchors:
        evidence_parts.append("score_equals_ordinary_group_floor_" + "|".join(anchors))
    if rank_anchors:
        evidence_parts.append("rank_equals_ordinary_group_floor_" + "|".join(rank_anchors))
    if not evidence_parts:
        if len(eligible) == 1:
            evidence_parts.append("single_candidate_by_score_floor")
        elif len(eligible) > 1:
            evidence_parts.append("ambiguous_multiple_ordinary_groups_by_score_floor")
        else:
            evidence_parts.append("below_all_ordinary_group_floors")

    special_context = ""
    if special_hits:
        special_context = "score_or_rank_equals_special_group_floor_context_only_" + "|".join(special_hits)
    return eligible, ";".join(evidence_parts), special_context


def plan_subject_group(row: dict[str, str]) -> str:
    group = row.get("selection_group", "").strip()
    if group:
        return group
    requirement = row.get("requirement", "").strip()
    if "化学" in requirement:
        return "物理+化学_requirement_only"
    if "物理" in requirement:
        return "物理_requirement_only"
    return ""


def main() -> None:
    ordinary_by_year, special_by_year = load_exam_groups()
    score_rows = [
        row
        for row in read_csv(SCORE_MAJOR_ROWS)
        if row.get("province") == "广西"
        and row.get("type") == "普通考生"
        and row.get("subject_type") == "物理类"
        and row.get("year") in ("2024", "2025")
    ]
    plan_rows = [
        row
        for row in read_csv(PLAN_ROWS)
        if row.get("province") == "广西"
        and row.get("type") == "普通考生"
        and row.get("subject_type") == "物理类"
        and row.get("year") in ("2024", "2025")
    ]
    summary_rows = read_csv(SCORE_SUMMARY_ROWS)

    score_by_year_major: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    score_work: list[dict[str, object]] = []
    for idx, row in enumerate(score_rows, start=1):
        year = row.get("year", "")
        min_score = to_int(row.get("minimum_score"))
        min_rank = to_int(row.get("minimum_rank"))
        candidates, evidence, special_context = candidate_groups_for_score(
            min_score,
            min_rank,
            ordinary_by_year.get(year, []),
            special_by_year.get(year, []),
        )
        norm = normalize_major(row.get("major", ""))
        enriched = {
            **row,
            "candidate_groups": "|".join(candidates),
            "mapping_evidence": evidence,
            "special_group_collision_context": special_context,
        }
        score_by_year_major[(year, norm)].append(enriched)
        score_work.append(
            {
                "record_id": f"cugb_group_score_{idx:04d}",
                "source_file": str(SCORE_MAJOR_ROWS.relative_to(ROOT)),
                "source_row_number": idx,
                "row_kind": "score_major_mapping_candidate",
                "year": year,
                "university_code": UNIVERSITY_CODE,
                "university_name": UNIVERSITY_NAME,
                "source_group_label": row.get("selection_group", ""),
                "major_or_group": row.get("major", ""),
                "normalized_major": norm,
                "plan_count": "",
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "exam_ordinary_group_codes": "|".join(g.get("group_code", "") for g in ordinary_by_year.get(year, [])),
                "exam_ordinary_group_floor_scores": groups_line(ordinary_by_year.get(year, [])),
                "exam_special_group_context": groups_line(special_by_year.get(year, [])),
                "candidate_group_codes": "|".join(candidates),
                "candidate_group_count": len(candidates),
                "mapping_evidence": evidence,
                "special_group_collision_context": special_context,
                "mapping_status": "candidate_mapping_only_not_final",
                "confidence_tier": "T2_official_score_floor_candidate_mapping_no_source_group_code",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
                "required_resolution": "manual_or_official_group_structure_confirmation_before_trend_use",
            }
        )

    plan_work: list[dict[str, object]] = []
    for idx, row in enumerate(plan_rows, start=1):
        year = row.get("year", "")
        norm = normalize_major(row.get("specialty", ""))
        matches = score_by_year_major.get((year, norm), [])
        candidate_set = sorted(
            {
                group
                for match in matches
                for group in str(match.get("candidate_groups", "")).split("|")
                if group
            }
        )
        exact_evidence = sorted({str(match.get("mapping_evidence", "")) for match in matches if match.get("mapping_evidence")})
        special_context = sorted(
            {
                str(match.get("special_group_collision_context", ""))
                for match in matches
                if match.get("special_group_collision_context")
            }
        )
        if not matches:
            evidence = "no_matching_major_score_row_same_year"
        elif len(candidate_set) == 1:
            evidence = "single_candidate_from_exact_major_score_match"
        elif candidate_set:
            evidence = "ambiguous_candidates_from_exact_major_score_match"
        else:
            evidence = "matched_score_row_but_no_candidate_group"

        plan_work.append(
            {
                "record_id": f"cugb_group_plan_{idx:04d}",
                "source_file": str(PLAN_ROWS.relative_to(ROOT)),
                "source_row_number": idx,
                "row_kind": "plan_major_mapping_candidate",
                "year": year,
                "university_code": UNIVERSITY_CODE,
                "university_name": UNIVERSITY_NAME,
                "source_group_label": plan_subject_group(row),
                "major_or_group": row.get("specialty", ""),
                "normalized_major": norm,
                "plan_count": row.get("plan_count", ""),
                "minimum_score": "",
                "minimum_rank": "",
                "exam_ordinary_group_codes": "|".join(g.get("group_code", "") for g in ordinary_by_year.get(year, [])),
                "exam_ordinary_group_floor_scores": groups_line(ordinary_by_year.get(year, [])),
                "exam_special_group_context": groups_line(special_by_year.get(year, [])),
                "candidate_group_codes": "|".join(candidate_set),
                "candidate_group_count": len(candidate_set),
                "mapping_evidence": evidence,
                "special_group_collision_context": "|".join(special_context),
                "mapping_status": "candidate_mapping_only_not_final",
                "confidence_tier": "T2_official_plan_candidate_from_major_score_match_no_source_group_code",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
                "required_resolution": "manual_or_official_group_structure_confirmation_before_trend_use",
                "matched_score_evidence": "|".join(exact_evidence),
            }
        )

    workbench = score_work + plan_work
    counts = Counter()
    for row in workbench:
        counts["workbench_rows"] += 1
        counts[f"row_kind:{row['row_kind']}"] += 1
        counts[f"evidence:{row['mapping_evidence']}"] += 1
        if row.get("special_group_collision_context"):
            counts["special_group_collision_context_rows"] += 1
        candidate_count = int(row["candidate_group_count"])
        if candidate_count == 1:
            counts["single_candidate_rows"] += 1
        elif candidate_count > 1:
            counts["ambiguous_candidate_rows"] += 1
        else:
            counts["unmapped_rows"] += 1
        if row.get("source_group_label"):
            counts["rows_with_source_group_label_or_requirement"] += 1

    qa_rows = [
        {
            "record_id": "cugb_group_mapping_qa_0001",
            "check": "exam_authority_ordinary_group_count_2024",
            "value": len(ordinary_by_year.get("2024", [])),
            "result": "pass" if len(ordinary_by_year.get("2024", [])) == 3 else "review",
            "note": groups_line(ordinary_by_year.get("2024", [])),
        },
        {
            "record_id": "cugb_group_mapping_qa_0002",
            "check": "exam_authority_ordinary_group_count_2025",
            "value": len(ordinary_by_year.get("2025", [])),
            "result": "pass" if len(ordinary_by_year.get("2025", [])) == 2 else "review",
            "note": groups_line(ordinary_by_year.get("2025", [])),
        },
        {
            "record_id": "cugb_group_mapping_qa_0003",
            "check": "official_source_group_code_present",
            "value": 0,
            "result": "hold",
            "note": "校方计划/专业分缓存给出选考组或要求，但未直接给广西院校专业组代码。",
        },
        {
            "record_id": "cugb_group_mapping_qa_0004",
            "check": "summary_score_row_boundary",
            "value": len(summary_rows),
            "result": "hold",
            "note": "概览最低分只作边界证据，不是专业组-year 或专业分记录。",
        },
        {
            "record_id": "cugb_group_mapping_qa_0005",
            "check": "trend_pool_eligible_rows",
            "value": 0,
            "result": "pass",
            "note": "本轮只生成 CUGB source-packet mapping workbench，保持 canonical/ML 关闭。",
        },
    ]

    fields = [
        "record_id",
        "source_file",
        "source_row_number",
        "row_kind",
        "year",
        "university_code",
        "university_name",
        "source_group_label",
        "major_or_group",
        "normalized_major",
        "plan_count",
        "minimum_score",
        "minimum_rank",
        "exam_ordinary_group_codes",
        "exam_ordinary_group_floor_scores",
        "exam_special_group_context",
        "candidate_group_codes",
        "candidate_group_count",
        "mapping_evidence",
        "matched_score_evidence",
        "special_group_collision_context",
        "mapping_status",
        "confidence_tier",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
    ]
    write_csv(OUT_WORKBENCH, workbench, fields)
    write_csv(OUT_QA, qa_rows, ["record_id", "check", "value", "result", "note"])

    exact_floor_rows = sum(v for k, v in counts.items() if "score_equals_ordinary_group_floor" in k)
    rollup = [
        ("exam_authority_ordinary_group_rows_2024", len(ordinary_by_year.get("2024", []))),
        ("exam_authority_ordinary_group_rows_2025", len(ordinary_by_year.get("2025", []))),
        ("exam_authority_special_context_rows_2024", len(special_by_year.get("2024", []))),
        ("exam_authority_special_context_rows_2025", len(special_by_year.get("2025", []))),
        ("official_score_major_rows", len(score_rows)),
        ("official_plan_rows", len(plan_rows)),
        ("official_summary_rows_boundary_hold", len(summary_rows)),
        ("workbench_rows", counts["workbench_rows"]),
        ("score_major_mapping_candidate_rows", counts["row_kind:score_major_mapping_candidate"]),
        ("plan_major_mapping_candidate_rows", counts["row_kind:plan_major_mapping_candidate"]),
        ("single_candidate_rows", counts["single_candidate_rows"]),
        ("ambiguous_candidate_rows", counts["ambiguous_candidate_rows"]),
        ("unmapped_rows", counts["unmapped_rows"]),
        ("score_equals_ordinary_group_floor_rows", exact_floor_rows),
        ("special_group_collision_context_rows", counts["special_group_collision_context_rows"]),
        ("rows_with_source_group_label_or_requirement", counts["rows_with_source_group_label_or_requirement"]),
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

    group_lines = []
    for year in ("2024", "2025"):
        for group in ordinary_by_year.get(year, []):
            group_lines.append(
                f"- {year} ordinary group {group.get('group_code')}: "
                f"min_score {group.get('min_score')}, rank {group.get('min_rank_est')}"
            )
    group_text = "\n".join(group_lines)

    OUT_DOC.write_text(
        f"""# Reference Trend CUGB Group Mapping Workbench

日期：{date.today().isoformat()}

## 结论

已基于广西考试院 `2024/2025` 中国地质大学（北京）物理类本科普通批投档线，对校方官方缓存的计划/专业分记录生成候选专业组映射工作台。校方记录有计划数、专业最低分/位次和部分选考组标签，但没有直接给广西院校专业组代码，因此本轮不生成正式 `院校专业组-year` 趋势记录。

## 考试院普通组线

{group_text}

## 覆盖

- workbench rows: {counts['workbench_rows']}
- score-major candidate rows: {counts['row_kind:score_major_mapping_candidate']}
- plan-major candidate rows: {counts['row_kind:plan_major_mapping_candidate']}
- exact ordinary group floor score rows: {exact_floor_rows}
- single-candidate rows: {counts['single_candidate_rows']}
- ambiguous candidate rows: {counts['ambiguous_candidate_rows']}
- unmapped rows: {counts['unmapped_rows']}
- special-group collision context rows: {counts['special_group_collision_context_rows']}
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 使用边界

候选规则只用“专业最低分不低于考试院普通组最低投档线”的必要条件，并额外标注专业最低分/位次是否等于某个普通组线。若分数同时高于多个普通组线，仍保留为 ambiguous；若碰到专项/民族班组线同分同位次，只作为 context 标注，不转为普通组映射。

## 下一步

1. 若要让 CUGB 进入正式 reference trend group-year 层，需要找到官方广西招生计划中的院校专业组代码或人工确认专业组结构。
2. 在未确认前，本文件只作为 32 所 decision_pool 的 source evidence / mapping workbench，不进入统计背景、canonical 或 ML。
3. 下一轮可继续处理最新出现的南京航空航天大学官方缓存行，或回到 P0/P1 非主池官方计划来源发现队列。
""",
        encoding="utf-8",
    )

    print(f"cugb_group_mapping_workbench_rows={counts['workbench_rows']}")
    print(f"score_major_mapping_candidate_rows={counts['row_kind:score_major_mapping_candidate']}")
    print(f"plan_major_mapping_candidate_rows={counts['row_kind:plan_major_mapping_candidate']}")
    print(f"score_equals_ordinary_group_floor_rows={exact_floor_rows}")
    print("reference_trend_pool_eligible_rows=0")


if __name__ == "__main__":
    main()
