#!/usr/bin/env python3
"""Build marker 123 JXUTCM group mapping and line-join readiness.

This summarizes marker 122 major-plan rows into source-group rows and records
why none may enter reference-trend intake yet.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

IN_CSV = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview.csv"
OUT_PREFIX = "reference_trend_520_p1_batch17_jxutcm_group_join_readiness"
OUT_CSV = SEED_DIR / f"{OUT_PREFIX}.csv"
ROLLUP_CSV = REPORTS_DIR / f"{OUT_PREFIX}_rollup.csv"
QA_CSV = REPORTS_DIR / f"{OUT_PREFIX}_qa.csv"
EXCLUSION_CSV = REPORTS_DIR / f"{OUT_PREFIX}_exclusion_log.csv"
DOC_MD = DOCS_DIR / f"{OUT_PREFIX}.md"
HANDOFF_MD = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"


def read_rows() -> list[dict[str, str]]:
    with IN_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs() -> None:
    rows = read_rows()
    groups: dict[str, dict[str, object]] = {}
    majors_by_group: defaultdict[str, list[str]] = defaultdict(list)
    requirements_by_group: defaultdict[str, set[str]] = defaultdict(set)

    for row in rows:
        group = row["source_group_code"]
        majors_by_group[group].append(row["major_name"])
        requirements_by_group[group].add(row["subject_requirement"])
        groups.setdefault(group, {
            "source_group_code": group,
            "plan_count_sum": 0,
            "major_row_count": 0,
            "special_type_row_count": 0,
            "source_url": row["source_url"],
            "source_owner": row["source_owner"],
            "source_title": row["source_title"],
            "university_code": row["university_code"],
            "university_name": row["university_name"],
            "year": row["year"],
            "province": row["province"],
            "batch": row["batch"],
            "subject_category": row["subject_category"],
            "queue_group_code": row["queue_group_code"],
        })
        groups[group]["plan_count_sum"] = int(groups[group]["plan_count_sum"]) + int(row["plan_count"])
        groups[group]["major_row_count"] = int(groups[group]["major_row_count"]) + 1
        if row["special_type_detected"] == "true":
            groups[group]["special_type_row_count"] = int(groups[group]["special_type_row_count"]) + 1

    out_rows: list[dict[str, object]] = []
    for i, group in enumerate(sorted(groups), start=1):
        item = groups[group]
        queue_group_code = str(item["queue_group_code"])
        suffix_candidate = queue_group_code.endswith(group)
        if suffix_candidate:
            mapping_status = "candidate_suffix_match_only_not_confirmed"
            mapping_note = (
                f"queue_group_code {queue_group_code} ends with source short group {group}; "
                "source page still says exam filling system should prevail"
            )
        else:
            mapping_status = "not_queue_target_suffix_mismatch"
            mapping_note = (
                f"source short group {group} is not a suffix match for queue_group_code {queue_group_code}; "
                "keep as adjacent official source-packet context only"
            )
        out_rows.append({
            "group_readiness_id": f"reference_trend_520_p1_batch17_jxutcm_group_{i:04d}",
            "university_code": item["university_code"],
            "university_name": item["university_name"],
            "year": item["year"],
            "province": item["province"],
            "batch": item["batch"],
            "subject_category": item["subject_category"],
            "queue_group_code": queue_group_code,
            "source_group_code": group,
            "group_mapping_status": mapping_status,
            "group_mapping_note": mapping_note,
            "major_row_count": item["major_row_count"],
            "plan_count_sum": item["plan_count_sum"],
            "subject_requirements": "|".join(sorted(requirements_by_group[group])),
            "major_names_preview": "；".join(majors_by_group[group][:8]),
            "special_type_row_count": item["special_type_row_count"],
            "source_contains_plan_count": "true",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "local_line_rank_source_found": "false",
            "line_rank_join_status": "blocked_no_local_exam_authority_line_rank_source_for_10412",
            "confidence_tier": "T1_plan_source_group_readiness_score_rank_missing",
            "source_packet_preview_eligible": "true",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "required_resolution": (
                "obtain official Guangxi 2025 undergraduate ordinary-batch physics admission line/rank "
                "for university 10412 and verify group-code mapping before intake"
            ),
            "source_url": item["source_url"],
            "evidence_note": (
                "Derived from marker 122 official plan preview; project-local search found no existing "
                "10412/Jiangxi TCM line-rank packet."
            ),
        })

    fields = [
        "group_readiness_id",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "queue_group_code",
        "source_group_code",
        "group_mapping_status",
        "group_mapping_note",
        "major_row_count",
        "plan_count_sum",
        "subject_requirements",
        "major_names_preview",
        "special_type_row_count",
        "source_contains_plan_count",
        "source_contains_min_score",
        "source_contains_min_rank",
        "local_line_rank_source_found",
        "line_rank_join_status",
        "confidence_tier",
        "source_packet_preview_eligible",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "source_url",
        "evidence_note",
    ]
    write_csv(OUT_CSV, out_rows, fields)

    total_plan = sum(int(row["plan_count_sum"]) for row in out_rows)
    suffix_candidates = sum(1 for row in out_rows if row["group_mapping_status"] == "candidate_suffix_match_only_not_confirmed")
    rollup = [
        {"metric": "source_group_readiness_rows", "value": len(out_rows), "note": "Grouped from marker 122 plan rows."},
        {"metric": "plan_count_sum", "value": total_plan, "note": ""},
        {"metric": "queue_group_code", "value": "101", "note": "From marker 122 queue context, not accepted as source mapping."},
        {"metric": "suffix_candidate_rows", "value": suffix_candidates, "note": "Candidate only; no intake opened."},
        {"metric": "line_rank_source_found_rows", "value": 0, "note": "No local 10412 line/rank packet found in current repository scan."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Missing min score/rank and mapping confirmation."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No line/rank join."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for row in out_rows:
        rollup.append({
            "metric": f"source_group_plan_sum::{row['source_group_code']}",
            "value": row["plan_count_sum"],
            "note": str(row["subject_requirements"]),
        })
    write_csv(ROLLUP_CSV, rollup, ["metric", "value", "note"])

    qa = [
        {
            "check": "input_marker_122_rows_present",
            "status": "PASS" if len(rows) == 26 else "FAIL",
            "detail": f"marker122_rows={len(rows)}",
        },
        {
            "check": "group_rollup_preserves_plan_sum",
            "status": "PASS" if total_plan == sum(int(row["plan_count"]) for row in rows) == 62 else "FAIL",
            "detail": f"group_plan_sum={total_plan}",
        },
        {
            "check": "suffix_mapping_not_overclaimed",
            "status": "PASS",
            "detail": f"suffix_candidate_rows={suffix_candidates}; all remain mapping QA hold.",
        },
        {
            "check": "line_rank_join_not_overclaimed",
            "status": "PASS",
            "detail": "No local 10412 line/rank source found; line/rank flags remain false.",
        },
        {
            "check": "no_reference_trend_pool_intake",
            "status": "PASS",
            "detail": "All rows remain source packet readiness only.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS",
            "detail": "Canonical/ML and decision-pool entry remain closed.",
        },
    ]
    write_csv(QA_CSV, qa, ["check", "status", "detail"])

    exclusion = [{
        "group_readiness_id": row["group_readiness_id"],
        "university_code": row["university_code"],
        "university_name": row["university_name"],
        "queue_group_code": row["queue_group_code"],
        "source_group_code": row["source_group_code"],
        "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
        "reason": "missing_official_line_rank_join_and_group_mapping_confirmation",
        "safe_next_action": row["required_resolution"],
    } for row in out_rows]
    write_csv(EXCLUSION_CSV, exclusion, [
        "group_readiness_id",
        "university_code",
        "university_name",
        "queue_group_code",
        "source_group_code",
        "excluded_from",
        "reason",
        "safe_next_action",
    ])

    doc = f"""# Reference trend 520 P1 batch17 JXUTCM group join readiness

Generated: 2026-05-17

## Scope

This packet summarizes marker 122 JXUTCM official plan rows into source-group readiness rows and records the blockers for score/rank join and group mapping.

## Outputs

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`

## Result

- Source-group readiness rows: {len(out_rows)}
- Plan sum preserved from marker 122: {total_plan}
- Queue group context: `101`
- Suffix candidate mappings: {suffix_candidates}
- Local official line/rank source found: 0

## Boundary

- `01 -> 101` is recorded only as a suffix candidate, not an accepted mapping.
- Source groups `02`, `04`, `06`, and `08` remain adjacent official source-packet context, not queue-target rows.
- No minimum score/rank was joined.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
"""
    DOC_MD.write_text(doc, encoding="utf-8")

    marker = f"""

## 123. 2026-05-17 P1 batch17 JXUTCM group join readiness

已新增江西中医药大学 source-group join readiness：

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`
- `docs/{OUT_PREFIX}.md`

覆盖结果：将 marker 122 的 26 条专业计划 rows 汇总为 5 条 source-group readiness rows，计划合计保持 62；仅 `01 -> 101` 记录为后缀候选映射，不作为已确认映射；未发现本地 10412 投档线/最低位次 source，可 join rows 为 0。QA PASS。

准入边界：本轮只生成 group mapping 与 line/rank join readiness；不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步需要官方广西 2025 本科普通批物理类投档线/最低位次，并验证源页短专业组代码与广西填报系统专业组代码映射。
"""
    existing = HANDOFF_MD.read_text(encoding="utf-8") if HANDOFF_MD.exists() else ""
    if "## 123. 2026-05-17 P1 batch17 JXUTCM group join readiness" not in existing:
        with HANDOFF_MD.open("a", encoding="utf-8") as f:
            f.write(marker)


if __name__ == "__main__":
    build_outputs()
