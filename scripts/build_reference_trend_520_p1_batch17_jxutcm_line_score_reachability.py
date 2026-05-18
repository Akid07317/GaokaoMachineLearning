#!/usr/bin/env python3
"""Build marker 124 JXUTCM official line-score reachability packet.

This records an official Guangxi exam-authority投档最低分 candidate for
10412-101 while keeping rank join, reference-trend intake, calibration,
canonical, ML, and decision-pool entry closed.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

READINESS_CSV = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_group_join_readiness.csv"

OUT_PREFIX = "reference_trend_520_p1_batch17_jxutcm_line_score_reachability"
OUT_CSV = SEED_DIR / f"{OUT_PREFIX}.csv"
ROLLUP_CSV = REPORTS_DIR / f"{OUT_PREFIX}_rollup.csv"
QA_CSV = REPORTS_DIR / f"{OUT_PREFIX}_qa.csv"
EXCLUSION_CSV = REPORTS_DIR / f"{OUT_PREFIX}_exclusion_log.csv"
DOC_MD = DOCS_DIR / f"{OUT_PREFIX}.md"
HANDOFF_MD = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

LINE_SOURCE_URL = "https://www.gxeea.cn/view/content_1013_31850.htm"
LINE_SOURCE_TITLE = "2025年本科普通批院校专业组投档最低分数线（首选物理科目组）"
LINE_SOURCE_OWNER = "广西招生考试院"


def read_readiness_rows() -> list[dict[str, str]]:
    with READINESS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs() -> None:
    readiness = read_readiness_rows()
    target = [row for row in readiness if row["source_group_code"] == "01" and row["queue_group_code"] == "101"]
    adjacent = [row for row in readiness if row["source_group_code"] != "01"]
    if len(target) != 1:
        raise SystemExit("Expected exactly one JXUTCM 01 -> 101 suffix candidate row")

    source = target[0]
    out_rows = [{
        "line_score_reachability_id": "reference_trend_520_p1_batch17_jxutcm_line_0001",
        "group_readiness_id": source["group_readiness_id"],
        "university_code": "10412",
        "university_name": "江西中医药大学",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "queue_group_code": "101",
        "source_plan_group_code": "01",
        "exam_authority_group_code": "101",
        "group_mapping_status": "score_line_confirms_exam_authority_group_101_plan_group_01_still_suffix_candidate",
        "min_score": "527",
        "min_rank": "",
        "score_source_type": "official_exam_authority_line_score_page",
        "score_source_owner": LINE_SOURCE_OWNER,
        "score_source_title": LINE_SOURCE_TITLE,
        "score_source_url": LINE_SOURCE_URL,
        "score_source_access_status": "web_search_open_snippet_official_page_identified",
        "score_source_contains_group_code": "true",
        "score_source_contains_min_score": "true",
        "score_source_contains_min_rank": "false",
        "rank_join_status": "blocked_need_official_one_score_one_rank_for_527_or_exam_authority_rank_source",
        "plan_count_from_marker_123": source["plan_count_sum"],
        "plan_source_url": source["source_url"],
        "plan_source_group_note": source["group_mapping_note"],
        "adjacent_plan_groups_held": "|".join(sorted(row["source_group_code"] for row in adjacent)),
        "special_type_boundary_status": "ordinary_batch_score_row_no_remark_adjacent_sports_rows_excluded",
        "confidence_tier": "T1_official_exam_authority_min_score_rank_missing",
        "source_packet_preview_eligible": "true",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "required_resolution": "join official 2025 Guangxi one-score-one-rank or authoritative rank source for score 527 before intake/calibration",
        "evidence_note": "Official Guangxi exam-authority search result shows 10412 江西中医药大学 101 527 on the 2025本科普通批首选物理科目组投档最低分 page; page table schema has no min-rank column.",
    }]

    fields = [
        "line_score_reachability_id",
        "group_readiness_id",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "queue_group_code",
        "source_plan_group_code",
        "exam_authority_group_code",
        "group_mapping_status",
        "min_score",
        "min_rank",
        "score_source_type",
        "score_source_owner",
        "score_source_title",
        "score_source_url",
        "score_source_access_status",
        "score_source_contains_group_code",
        "score_source_contains_min_score",
        "score_source_contains_min_rank",
        "rank_join_status",
        "plan_count_from_marker_123",
        "plan_source_url",
        "plan_source_group_note",
        "adjacent_plan_groups_held",
        "special_type_boundary_status",
        "confidence_tier",
        "source_packet_preview_eligible",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]
    write_csv(OUT_CSV, out_rows, fields)

    rollup = [
        {"metric": "line_score_reachability_rows", "value": 1, "note": "Official score candidate only."},
        {"metric": "official_exam_authority_score_rows", "value": 1, "note": LINE_SOURCE_URL},
        {"metric": "target_group", "value": "10412-101", "note": "JXUTCM Guangxi 2025 physical ordinary batch."},
        {"metric": "min_score_found_rows", "value": 1, "note": "min_score=527"},
        {"metric": "min_rank_found_rows", "value": 0, "note": "Official line page does not expose rank."},
        {"metric": "plan_group_suffix_candidate_rows", "value": 1, "note": "source plan group 01 remains candidate for exam group 101."},
        {"metric": "adjacent_plan_groups_held", "value": 4, "note": "02,04,06,08 remain adjacent source-packet context."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Missing min rank."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Rank join not done."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    write_csv(ROLLUP_CSV, rollup, ["metric", "value", "note"])

    qa = [
        {
            "check": "marker_123_target_row_present",
            "status": "PASS",
            "detail": f"Mapped score candidate to {source['group_readiness_id']}.",
        },
        {
            "check": "official_exam_authority_source_only",
            "status": "PASS",
            "detail": LINE_SOURCE_URL,
        },
        {
            "check": "score_not_rank_claimed",
            "status": "PASS",
            "detail": "Recorded min_score=527; min_rank remains blank because the official投档最低分 page has no rank column.",
        },
        {
            "check": "group_mapping_not_overclaimed",
            "status": "PASS",
            "detail": "Exam authority group 101 found; plan source short group 01 remains suffix candidate pending mapping QA.",
        },
        {
            "check": "no_reference_trend_pool_intake",
            "status": "PASS",
            "detail": "No intake/calibration rows opened.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS",
            "detail": "Canonical/ML and decision-pool entry remain closed.",
        },
    ]
    write_csv(QA_CSV, qa, ["check", "status", "detail"])

    exclusion = [{
        "line_score_reachability_id": out_rows[0]["line_score_reachability_id"],
        "university_code": "10412",
        "university_name": "江西中医药大学",
        "group_code": "101",
        "min_score": "527",
        "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
        "reason": "official_min_score_found_but_min_rank_missing_and_plan_group_mapping_still_QA_hold",
        "safe_next_action": out_rows[0]["required_resolution"],
    }]
    write_csv(EXCLUSION_CSV, exclusion, [
        "line_score_reachability_id",
        "university_code",
        "university_name",
        "group_code",
        "min_score",
        "excluded_from",
        "reason",
        "safe_next_action",
    ])

    doc = f"""# Reference trend 520 P1 batch17 JXUTCM line score reachability

Generated: 2026-05-17

## Scope

This packet records an official Guangxi exam-authority投档最低分 candidate for江西中医药大学 `10412-101`.

## Outputs

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`

## Source

- {LINE_SOURCE_OWNER}: {LINE_SOURCE_URL}

## Result

- Official exam-authority group: `10412-101`
- 投档最低分: 527
- 最低位次: not available on this source
- Plan-source short group `01` remains a suffix candidate for `101`, not an accepted mapping.

## Boundary

- This is score reachability only, not reference-trend intake.
- Rank join remains blocked pending official一分一档 or another authoritative rank source.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""
    DOC_MD.write_text(doc, encoding="utf-8")

    marker = f"""

## 124. 2026-05-17 P1 batch17 JXUTCM line score reachability

已新增江西中医药大学官方投档最低分 reachability：

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`
- `docs/{OUT_PREFIX}.md`

覆盖结果：定位到广西招生考试院 2025 本科普通批首选物理科目组投档最低分页面中的 `10412 江西中医药大学 101 527`，生成 1 条 official exam-authority line-score candidate；最低位次未在该源页提供，rank join rows 仍为 0。QA PASS。

准入边界：本轮只生成 score reachability，不做位次换算、不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool；`01 -> 101` 仍为源计划短组到考试院专业组的候选映射，需后续官方一分一档/位次来源与映射 QA。
"""
    existing = HANDOFF_MD.read_text(encoding="utf-8") if HANDOFF_MD.exists() else ""
    if "## 124. 2026-05-17 P1 batch17 JXUTCM line score reachability" not in existing:
        with HANDOFF_MD.open("a", encoding="utf-8") as f:
            f.write(marker)


if __name__ == "__main__":
    build_outputs()
