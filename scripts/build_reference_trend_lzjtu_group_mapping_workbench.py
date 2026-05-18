#!/usr/bin/env python3
"""Build a candidate group-mapping workbench for Lanzhou Jiaotong rows."""

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

SOURCE_PACKET = CLEAN / "reference_trend_lzjtu_source_packet_parse_preview.csv"
TREND_INTAKE = CLEAN / "reference_trend_intake_preview.csv"

OUT_WORKBENCH = CLEAN / "reference_trend_lzjtu_group_mapping_workbench.csv"
OUT_QA = REPORTS / "reference_trend_lzjtu_group_mapping_qa.csv"
OUT_ROLLUP = REPORTS / "reference_trend_lzjtu_group_mapping_rollup.csv"
OUT_DOC = DOCS / "reference_trend_lzjtu_group_mapping.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def to_int(value: str) -> int | None:
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


def load_exam_groups(year: str = "2024") -> list[dict[str, str]]:
    rows = []
    for row in read_csv(TREND_INTAKE):
        if (
            row.get("university_code") == "10732"
            and row.get("year") == year
            and row.get("batch") == "本科普通批"
            and row.get("subject_category") == "物理类"
        ):
            rows.append(row)
    return sorted(rows, key=lambda r: r.get("group_code", ""))


def candidate_groups_for_score(min_score: int | None, groups: list[dict[str, str]]) -> tuple[list[str], str]:
    if min_score is None:
        return [], "score_missing"
    eligible = []
    anchors = []
    for group in groups:
        group_score = to_int(group.get("min_score", ""))
        if group_score is None:
            continue
        if min_score >= group_score:
            eligible.append(group.get("group_code", ""))
        if min_score == group_score:
            anchors.append(group.get("group_code", ""))
    if anchors:
        return eligible, "score_equals_exam_group_floor_" + "|".join(anchors)
    if len(eligible) == 1:
        return eligible, "single_candidate_by_score_floor"
    if len(eligible) > 1:
        return eligible, "ambiguous_multiple_groups_by_score_floor"
    return eligible, "below_all_exam_group_floors"


def main() -> None:
    source_rows = read_csv(SOURCE_PACKET)
    groups_2024 = load_exam_groups("2024")
    groups_2025 = load_exam_groups("2025")

    score_rows = [
        row
        for row in source_rows
        if row.get("source_role") == "official_major_score_row"
        and row.get("ordinary_physics_guangxi") == "true"
    ]
    plan_rows = [
        row
        for row in source_rows
        if row.get("source_role") == "official_plan_row"
        and row.get("ordinary_physics_guangxi") == "true"
    ]

    score_by_norm_major: dict[str, list[dict[str, str]]] = defaultdict(list)
    score_work: list[dict[str, object]] = []
    for row in score_rows:
        min_score = to_int(row.get("minimum_score", ""))
        candidates, evidence = candidate_groups_for_score(min_score, groups_2024)
        norm = normalize_major(row.get("major_or_group", ""))
        score_by_norm_major[norm].append({**row, "candidate_groups": "|".join(candidates), "mapping_evidence": evidence})
        score_work.append(
            {
                "record_id": f"lzjtu_group_score_{len(score_work) + 1:04d}",
                "source_record_id": row.get("record_id", ""),
                "row_kind": "score_major_mapping_candidate",
                "year": row.get("year", ""),
                "university_code": "10732",
                "university_name": "兰州交通大学",
                "major_or_group": row.get("major_or_group", ""),
                "normalized_major": norm,
                "plan_count": "",
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "exam_group_codes_2024": "|".join(g.get("group_code", "") for g in groups_2024),
                "exam_group_floor_scores_2024": "|".join(f"{g.get('group_code')}:{g.get('min_score')}" for g in groups_2024),
                "candidate_group_codes": "|".join(candidates),
                "candidate_group_count": len(candidates),
                "mapping_evidence": evidence,
                "mapping_status": "candidate_mapping_only_not_final",
                "confidence_tier": "T2_score_floor_candidate_mapping_no_source_group_code",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "required_resolution": "manual_or_official_group_structure_confirmation",
            }
        )

    plan_work: list[dict[str, object]] = []
    for row in plan_rows:
        norm = normalize_major(row.get("major_or_group", ""))
        matches = score_by_norm_major.get(norm, [])
        candidate_set = sorted(
            {
                group
                for match in matches
                for group in match.get("candidate_groups", "").split("|")
                if group
            }
        )
        if not matches:
            evidence = "no_matching_major_score_row"
        elif len(candidate_set) == 1:
            evidence = "single_candidate_from_exact_major_score_match"
        elif candidate_set:
            evidence = "ambiguous_candidates_from_exact_major_score_match"
        else:
            evidence = "matched_score_row_but_no_candidate_group"

        plan_work.append(
            {
                "record_id": f"lzjtu_group_plan_{len(plan_work) + 1:04d}",
                "source_record_id": row.get("record_id", ""),
                "row_kind": "plan_major_mapping_candidate",
                "year": row.get("year", ""),
                "university_code": "10732",
                "university_name": "兰州交通大学",
                "major_or_group": row.get("major_or_group", ""),
                "normalized_major": norm,
                "plan_count": row.get("plan_count", ""),
                "minimum_score": "",
                "minimum_rank": "",
                "exam_group_codes_2024": "|".join(g.get("group_code", "") for g in groups_2024),
                "exam_group_floor_scores_2024": "|".join(f"{g.get('group_code')}:{g.get('min_score')}" for g in groups_2024),
                "candidate_group_codes": "|".join(candidate_set),
                "candidate_group_count": len(candidate_set),
                "mapping_evidence": evidence,
                "mapping_status": "candidate_mapping_only_not_final",
                "confidence_tier": "T2_plan_major_candidate_from_score_match_no_source_group_code",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "required_resolution": "manual_or_official_group_structure_confirmation",
            }
        )

    workbench = score_work + plan_work
    counts = Counter()
    for row in workbench:
        counts["workbench_rows"] += 1
        counts[f"row_kind:{row['row_kind']}"] += 1
        counts[f"evidence:{row['mapping_evidence']}"] += 1
        if int(row["candidate_group_count"]) == 1:
            counts["single_candidate_rows"] += 1
        elif int(row["candidate_group_count"]) > 1:
            counts["ambiguous_candidate_rows"] += 1
        else:
            counts["unmapped_rows"] += 1

    qa_rows = [
        {
            "record_id": "lzjtu_group_mapping_qa_0001",
            "check": "exam_authority_group_count_2024",
            "value": len(groups_2024),
            "result": "pass" if len(groups_2024) == 2 else "review",
            "note": ";".join(f"{g.get('group_code')}={g.get('min_score')}/{g.get('min_rank_est')}" for g in groups_2024),
        },
        {
            "record_id": "lzjtu_group_mapping_qa_0002",
            "check": "official_api_group_code_present",
            "value": 0,
            "result": "hold",
            "note": "兰州交通大学官方 API 给出专业/计划/分数/位次，但未给院校专业组代码。",
        },
        {
            "record_id": "lzjtu_group_mapping_qa_0003",
            "check": "trend_pool_eligible_rows",
            "value": 0,
            "result": "pass",
            "note": "候选映射未作为正式专业组-year 记录写入趋势池。",
        },
    ]

    fields = [
        "record_id",
        "source_record_id",
        "row_kind",
        "year",
        "university_code",
        "university_name",
        "major_or_group",
        "normalized_major",
        "plan_count",
        "minimum_score",
        "minimum_rank",
        "exam_group_codes_2024",
        "exam_group_floor_scores_2024",
        "candidate_group_codes",
        "candidate_group_count",
        "mapping_evidence",
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
    rollup = [
        ("exam_authority_2024_group_rows", len(groups_2024)),
        ("exam_authority_2025_group_rows", len(groups_2025)),
        ("workbench_rows", counts["workbench_rows"]),
        ("score_major_mapping_candidate_rows", counts["row_kind:score_major_mapping_candidate"]),
        ("plan_major_mapping_candidate_rows", counts["row_kind:plan_major_mapping_candidate"]),
        ("single_candidate_rows", counts["single_candidate_rows"]),
        ("ambiguous_candidate_rows", counts["ambiguous_candidate_rows"]),
        ("unmapped_rows", counts["unmapped_rows"]),
        ("score_equals_exam_group_floor_rows", sum(v for k, v in counts.items() if k.startswith("evidence:score_equals_exam_group_floor"))),
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

    group_lines = "\n".join(
        f"- 2024 group {g.get('group_code')}: min_score {g.get('min_score')}, rank {g.get('min_rank_est')}"
        for g in groups_2024
    )
    OUT_DOC.write_text(
        f"""# Reference Trend Lanzhou Jiaotong Group Mapping Workbench

日期：{date.today().isoformat()}

## 结论

已基于广西考试院 `2024` 兰州交通大学物理类本科普通批投档线，对校方官方 API 的计划/专业分记录生成候选专业组映射工作台。考试院存在两个专业组：`101` 与 `102`；校方 API 未直接给组代码，因此本轮只生成候选映射，不产生正式 `院校专业组-year` 趋势记录。

## 考试院组线

{group_lines}

## 覆盖

- workbench rows: {counts['workbench_rows']}
- score-major candidate rows: {counts['row_kind:score_major_mapping_candidate']}
- plan-major candidate rows: {counts['row_kind:plan_major_mapping_candidate']}
- single-candidate rows: {counts['single_candidate_rows']}
- ambiguous candidate rows: {counts['ambiguous_candidate_rows']}
- unmapped rows: {counts['unmapped_rows']}
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 使用边界

候选规则只利用“专业最低分不低于组最低投档线”的必要条件，不能替代官方专业组结构。分数低于 `101` 组线且不低于 `102` 组线的专业可形成较强的 `102` 候选；高于 `101` 组线的专业仍可能属于任一组，需要招生计划专业组结构或人工核验。

## 下一步

1. 优先寻找兰州交通大学 `2024/2025` 专业组结构或广西招生计划 PDF/静态表。
2. 若找不到组结构，只能把该校保留为 source-packet + mapping workbench，不能正式进入 group-year trend pool。
3. 下一轮可继续处理新落地的北京工业大学/东华大学等官方缓存行，或推进下一批 P0/P1 非主池发现。
""",
        encoding="utf-8",
    )

    print(f"lzjtu_group_mapping_workbench_rows={counts['workbench_rows']}")
    print(f"single_candidate_rows={counts['single_candidate_rows']}")
    print(f"ambiguous_candidate_rows={counts['ambiguous_candidate_rows']}")
    print("reference_trend_pool_eligible_rows=0")


if __name__ == "__main__":
    main()
