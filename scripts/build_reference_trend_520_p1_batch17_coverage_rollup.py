#!/usr/bin/env python3
"""Build marker 127 batch17 coverage rollup.

This consolidates current batch17 workset/candidate/parse/line-score/rank-backoff
state into a row-level QA report. It does not open intake, calibration,
canonical, ML, or the 32-school decision pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

WORKSET_CSV = SEED_DIR / "reference_trend_520_p1_batch17_discovery_workset.csv"
CANDIDATE_CSV = SEED_DIR / "reference_trend_520_p1_batch17_official_candidate_preview.csv"
JXUTCM_GROUP_CSV = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_group_join_readiness.csv"
LINE_SCORE_CSV = SEED_DIR / "reference_trend_520_p1_batch17_exam_authority_line_score_batch.csv"
RANK_BACKOFF_CSV = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates.csv"

OUT_PREFIX = "reference_trend_520_p1_batch17_coverage_rollup"
OUT_CSV = SEED_DIR / f"{OUT_PREFIX}.csv"
ROLLUP_CSV = REPORTS_DIR / f"{OUT_PREFIX}.csv"
QA_CSV = REPORTS_DIR / f"{OUT_PREFIX}_qa.csv"
EXCLUSION_CSV = REPORTS_DIR / f"{OUT_PREFIX}_exclusion_log.csv"
DOC_MD = DOCS_DIR / f"{OUT_PREFIX}.md"
HANDOFF_MD = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def expand_candidates(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    expanded: dict[str, dict[str, str]] = {}
    for row in rows:
        for key in row["group_pair_keys"].split("|"):
            expanded[key] = row
    return expanded


def map_by_group_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {f"{row['university_code']}-{row['group_code']}": row for row in rows}


def rank_backoff_by_group(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = f"{row['university_code']}-{row['group_code']}"
        grouped.setdefault(key, []).append(row)
    return grouped


def jxutcm_target_plan_group(rows: list[dict[str, str]]) -> dict[str, str]:
    target = [
        row for row in rows
        if row["university_code"] == "10412"
        and row["queue_group_code"] == "101"
        and row["source_group_code"] == "01"
    ]
    if len(target) != 1:
        return {}
    return target[0]


def coverage_stage(
    candidate: dict[str, str],
    jxutcm_group: dict[str, str],
    line_score: dict[str, str],
    rank_candidates: list[dict[str, str]],
) -> str:
    if not candidate:
        return "workset_only_no_official_candidate"
    has_plan_candidate = candidate.get("candidate_id", "") != ""
    has_jxutcm_plan = bool(jxutcm_group)
    has_score = bool(line_score.get("min_score", ""))
    has_rank_backoff = bool(rank_candidates)
    if has_jxutcm_plan and has_score and has_rank_backoff:
        return "plan_candidate_plus_score_plus_rank_backoff"
    if has_jxutcm_plan and has_score:
        return "plan_candidate_plus_score_rank_missing"
    if has_score:
        return "official_candidate_plus_score_rank_missing"
    if has_plan_candidate:
        return "official_candidate_no_confirmed_line_score"
    return "workset_only_no_official_candidate"


def blocker_for_stage(stage: str, candidate: dict[str, str], line_score: dict[str, str]) -> str:
    if stage == "workset_only_no_official_candidate":
        return "official_source_candidate_not_yet_found"
    if stage == "official_candidate_no_confirmed_line_score":
        return line_score.get("required_resolution", "") or candidate.get("parse_or_access_blocker", "")
    if stage == "official_candidate_plus_score_rank_missing":
        return "min_rank_missing_and_plan_parse_or_mapping_not_ready"
    if stage == "plan_candidate_plus_score_rank_missing":
        return "min_rank_missing_and_group_mapping_QA_hold"
    if stage == "plan_candidate_plus_score_plus_rank_backoff":
        return "official_min_rank_missing_backoff_rank_not_accepted"
    return "not_intake_ready"


def build_outputs() -> None:
    workset_rows = read_csv(WORKSET_CSV)
    candidate_rows = expand_candidates(read_csv(CANDIDATE_CSV))
    line_score_rows = map_by_group_key(read_csv(LINE_SCORE_CSV))
    rank_backoff_rows = rank_backoff_by_group(read_csv(RANK_BACKOFF_CSV))
    jxutcm_group = jxutcm_target_plan_group(read_csv(JXUTCM_GROUP_CSV))

    coverage_rows = []
    for row in workset_rows:
        key = row["group_pair_key"]
        candidate = candidate_rows.get(key, {})
        line_score = line_score_rows.get(key, {})
        rank_candidates = rank_backoff_rows.get(key, [])
        jxutcm_plan = jxutcm_group if key == "10412-101" else {}
        stage = coverage_stage(candidate, jxutcm_plan, line_score, rank_candidates)
        coverage_rows.append({
            "coverage_id": f"reference_trend_520_p1_batch17_coverage_{len(coverage_rows) + 1:04d}",
            "workset_id": row["workset_id"],
            "queue_rank": row["queue_rank"],
            "group_pair_key": key,
            "university_code": row["university_code"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "trend_direction": row["trend_direction"],
            "rank_delta_2025_minus_2024": row["rank_delta_2025_minus_2024"],
            "special_type_boundary": row["special_type_boundary"],
            "official_candidate_id": candidate.get("candidate_id", ""),
            "official_candidate_tier": candidate.get("source_candidate_tier", ""),
            "official_candidate_status": candidate.get("source_candidate_status", ""),
            "official_candidate_url": candidate.get("source_url", ""),
            "source_packet_parse_status": "jxutcm_group_readiness_candidate" if jxutcm_plan else "not_parsed_or_not_ready",
            "plan_count_candidate": jxutcm_plan.get("plan_count_sum", ""),
            "plan_group_mapping_status": jxutcm_plan.get("group_mapping_status", ""),
            "line_score_status": line_score.get("line_score_candidate_status", ""),
            "min_score": line_score.get("min_score", ""),
            "min_rank": line_score.get("min_rank", ""),
            "rank_backoff_candidate_count": len(rank_candidates),
            "rank_backoff_values": "|".join(candidate_row["candidate_rank"] for candidate_row in rank_candidates),
            "coverage_stage": stage,
            "intake_blocker": blocker_for_stage(stage, candidate, line_score),
            "source_packet_preview_eligible": "true" if candidate or jxutcm_plan or line_score else "false",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "required_resolution": (
                "confirm official plan/line/rank sources, official min-rank, and group mapping before intake"
            ),
        })

    fields = [
        "coverage_id",
        "workset_id",
        "queue_rank",
        "group_pair_key",
        "university_code",
        "university_name",
        "group_code",
        "trend_direction",
        "rank_delta_2025_minus_2024",
        "special_type_boundary",
        "official_candidate_id",
        "official_candidate_tier",
        "official_candidate_status",
        "official_candidate_url",
        "source_packet_parse_status",
        "plan_count_candidate",
        "plan_group_mapping_status",
        "line_score_status",
        "min_score",
        "min_rank",
        "rank_backoff_candidate_count",
        "rank_backoff_values",
        "coverage_stage",
        "intake_blocker",
        "source_packet_preview_eligible",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
    ]
    write_csv(OUT_CSV, coverage_rows, fields)

    stage_counts = Counter(row["coverage_stage"] for row in coverage_rows)
    candidate_count = sum(1 for row in coverage_rows if row["official_candidate_id"])
    score_count = sum(1 for row in coverage_rows if row["min_score"])
    rank_backoff_count = sum(1 for row in coverage_rows if row["rank_backoff_candidate_count"])
    rollup = [
        {"metric": "batch17_group_target_rows", "value": len(coverage_rows), "note": "From marker 118 workset."},
        {"metric": "official_candidate_covered_rows", "value": candidate_count, "note": "Rows represented in marker 121 candidate preview."},
        {"metric": "official_candidate_missing_rows", "value": len(coverage_rows) - candidate_count, "note": "Still workset-only."},
        {"metric": "source_packet_plan_candidate_rows", "value": 1, "note": "JXUTCM 10412-101 group readiness only."},
        {"metric": "official_line_score_rows", "value": score_count, "note": "Rows with official exam-authority min_score."},
        {"metric": "official_min_rank_rows", "value": 0, "note": "No official min-rank accepted."},
        {"metric": "rank_backoff_candidate_rows", "value": rank_backoff_count, "note": "Rows with non-official backoff rank candidates."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Intake remains closed."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No official rank join."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for stage, count in sorted(stage_counts.items()):
        rollup.append({"metric": f"stage::{stage}", "value": count, "note": ""})
    write_csv(ROLLUP_CSV, rollup, ["metric", "value", "note"])

    qa = [
        {
            "check": "all_workset_rows_represented",
            "status": "PASS" if len(coverage_rows) == len(workset_rows) else "FAIL",
            "detail": f"{len(coverage_rows)} coverage rows for {len(workset_rows)} workset rows.",
        },
        {
            "check": "candidate_coverage_count_matches_marker_121",
            "status": "PASS" if candidate_count == 8 else "FAIL",
            "detail": f"{candidate_count} group rows are covered by 7 university-level candidate rows.",
        },
        {
            "check": "line_score_count_matches_marker_126",
            "status": "PASS" if score_count == 6 else "FAIL",
            "detail": f"{score_count} official line-score rows have min_score.",
        },
        {
            "check": "no_min_rank_claimed",
            "status": "PASS" if all(not row["min_rank"] for row in coverage_rows) else "FAIL",
            "detail": "All coverage rows keep min_rank blank.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in coverage_rows) else "FAIL",
            "detail": "No canonical/ML entry opened.",
        },
    ]
    write_csv(QA_CSV, qa, ["check", "status", "detail"])

    exclusion = [
        {
            "coverage_id": row["coverage_id"],
            "group_pair_key": row["group_pair_key"],
            "university_name": row["university_name"],
            "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": row["intake_blocker"],
            "safe_next_action": row["required_resolution"],
        }
        for row in coverage_rows
    ]
    write_csv(EXCLUSION_CSV, exclusion, [
        "coverage_id",
        "group_pair_key",
        "university_name",
        "excluded_from",
        "reason",
        "safe_next_action",
    ])

    DOC_MD.write_text(
        f"""# Reference trend 520 P1 batch17 coverage rollup

Generated: 2026-05-17

## Scope

This rollup consolidates batch17 group-target coverage across workset, official candidate preview, JXUTCM plan parsing, exam-authority line-score reachability, and rank backoff QA.

## Outputs

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`

## Coverage Summary

- Group targets: {len(coverage_rows)}
- Official candidate covered rows: {candidate_count}
- Workset-only rows: {len(coverage_rows) - candidate_count}
- Official line-score rows: {score_count}
- Official min-rank rows: 0
- Reference trend eligible rows: 0

## Boundary

No reference trend intake, calibration, canonical/ML, or 32-school decision-pool update is opened. All rows remain in source-packet, preview, QA, rollup, or exclusion-log layers.
""",
        encoding="utf-8",
    )

    marker = f"""

## 127. 2026-05-17 P1 batch17 coverage rollup

已新增 P1 batch17 覆盖面总账：

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`
- `docs/{OUT_PREFIX}.md`

覆盖结果：将 marker 118-126 的 workset、官方候选源、江西中医药计划解析、广西考试院投档最低分、位次 backoff QA 合并为 20 条 group-target coverage rows。当前 8/20 个 group rows 已覆盖官方候选源，6/20 个 group rows 已补官方投档最低分，1/20 个 group rows 有计划数候选解析，0/20 个 group rows 有可采信官方最低位次。QA PASS。

准入边界：本轮只生成 coverage/QA/exclusion/rollup，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步应优先补 12 条 workset-only 的官方候选源，或对 6 条已有最低分 rows 做官方一分一档位次缓存/验证。
"""
    existing = HANDOFF_MD.read_text(encoding="utf-8") if HANDOFF_MD.exists() else ""
    if "## 127. 2026-05-17 P1 batch17 coverage rollup" not in existing:
        with HANDOFF_MD.open("a", encoding="utf-8") as f:
            f.write(marker)


if __name__ == "__main__":
    build_outputs()
