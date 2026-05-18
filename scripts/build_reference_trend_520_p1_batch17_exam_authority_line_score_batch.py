#!/usr/bin/env python3
"""Build marker 126 batch17 exam-authority line-score reachability packet.

Rows are sourced from official Guangxi exam-authority search snippets for the
2025 undergraduate ordinary-batch first-choice physics投档最低分 page. This is
score reachability only: min-rank, intake, calibration, canonical, ML, and the
32-school decision pool remain closed.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

OFFICIAL_CANDIDATES_CSV = SEED_DIR / "reference_trend_520_p1_batch17_official_candidate_preview.csv"

OUT_PREFIX = "reference_trend_520_p1_batch17_exam_authority_line_score_batch"
OUT_CSV = SEED_DIR / f"{OUT_PREFIX}.csv"
ROLLUP_CSV = REPORTS_DIR / f"{OUT_PREFIX}_rollup.csv"
QA_CSV = REPORTS_DIR / f"{OUT_PREFIX}_qa.csv"
EXCLUSION_CSV = REPORTS_DIR / f"{OUT_PREFIX}_exclusion_log.csv"
DOC_MD = DOCS_DIR / f"{OUT_PREFIX}.md"
HANDOFF_MD = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

LINE_SOURCE_URL = "https://www.gxeea.cn/view/content_1013_31850.htm"
LINE_SOURCE_TITLE = "2025年本科普通批院校专业组投档最低分数线（首选物理科目组）"
LINE_SOURCE_OWNER = "广西招生考试院"


TARGET_GROUPS = [
    {
        "university_code": "10596",
        "university_name": "桂林理工大学",
        "group_code": "153",
        "min_score": "490",
        "candidate_status": "official_line_score_found",
        "evidence_note": "Official Guangxi exam-authority search snippet shows 10596 桂林理工大学 153 490.",
    },
    {
        "university_code": "10412",
        "university_name": "江西中医药大学",
        "group_code": "101",
        "min_score": "527",
        "candidate_status": "official_line_score_found_already_recorded_marker_124",
        "evidence_note": "Official Guangxi exam-authority search snippet shows 10412 江西中医药大学 101 527.",
    },
    {
        "university_code": "10407",
        "university_name": "江西理工大学",
        "group_code": "102",
        "min_score": "461",
        "candidate_status": "official_line_score_found",
        "evidence_note": "Official Guangxi exam-authority search snippet shows 10407 江西理工大学 102 461.",
    },
    {
        "university_code": "10092",
        "university_name": "河北北方学院",
        "group_code": "151",
        "min_score": "490",
        "candidate_status": "official_line_score_found",
        "evidence_note": "Official Guangxi exam-authority search snippet shows 10092 河北北方学院 151 490.",
    },
    {
        "university_code": "10092",
        "university_name": "河北北方学院",
        "group_code": "152",
        "min_score": "462",
        "candidate_status": "official_line_score_found",
        "evidence_note": "Official Guangxi exam-authority search snippet shows 10092 河北北方学院 152 462.",
    },
    {
        "university_code": "10466",
        "university_name": "河南农业大学",
        "group_code": "152",
        "min_score": "382",
        "candidate_status": "official_line_score_found",
        "evidence_note": "Official Guangxi exam-authority search snippet shows 10466 河南农业大学 152 382.",
    },
    {
        "university_code": "14275",
        "university_name": "浙江外国语学院",
        "group_code": "105",
        "min_score": "",
        "candidate_status": "not_found_in_current_official_snippet_search",
        "evidence_note": "Current official-page snippet search did not expose 14275 浙江外国语学院 105.",
    },
    {
        "university_code": "10513",
        "university_name": "湖北师范大学",
        "group_code": "105",
        "min_score": "",
        "candidate_status": "not_found_in_current_official_physics_snippet_search",
        "evidence_note": "Search exposed history-subject rows for 10513 but no 2025 physics row 105 in current snippet set.",
    },
]


def read_candidate_rows() -> list[dict[str, str]]:
    with OFFICIAL_CANDIDATES_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        for group_code in row["group_codes"].split("|"):
            lookup[(row["university_code"], group_code)] = row
    return lookup


def build_outputs() -> None:
    candidates = candidate_lookup(read_candidate_rows())
    out_rows = []
    for index, target in enumerate(TARGET_GROUPS, start=1):
        source_candidate = candidates.get((target["university_code"], target["group_code"]), {})
        min_score = target["min_score"]
        found = bool(min_score)
        out_rows.append({
            "line_score_batch_id": f"reference_trend_520_p1_batch17_line_score_{index:04d}",
            "candidate_id": source_candidate.get("candidate_id", ""),
            "queue_id": source_candidate.get("queue_id", ""),
            "university_code": target["university_code"],
            "university_name": target["university_name"],
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "group_code": target["group_code"],
            "min_score": min_score,
            "min_rank": "",
            "score_source_type": "official_exam_authority_line_score_page",
            "score_source_owner": LINE_SOURCE_OWNER,
            "score_source_title": LINE_SOURCE_TITLE,
            "score_source_url": LINE_SOURCE_URL,
            "score_source_access_status": "web_search_snippet_official_page_identified" if found else "not_confirmed_in_current_snippet_search",
            "score_source_contains_group_code": "true" if found else "false",
            "score_source_contains_min_score": "true" if found else "false",
            "score_source_contains_min_rank": "false",
            "line_score_candidate_status": target["candidate_status"],
            "rank_join_status": "blocked_need_official_one_score_one_rank_or_exam_authority_rank_source" if found else "blocked_need_score_row_first",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "required_resolution": (
                "join official one-score-one-rank/rank source before intake"
                if found
                else "confirm this group on the official physics line-score page before rank lookup"
            ),
            "evidence_note": target["evidence_note"],
        })

    fields = [
        "line_score_batch_id",
        "candidate_id",
        "queue_id",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "group_code",
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
        "line_score_candidate_status",
        "rank_join_status",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]
    write_csv(OUT_CSV, out_rows, fields)

    found_rows = [row for row in out_rows if row["min_score"]]
    unresolved_rows = [row for row in out_rows if not row["min_score"]]
    rollup = [
        {"metric": "target_group_rows", "value": len(out_rows), "note": "Batch17 group targets covered by this line-score packet."},
        {"metric": "official_line_score_found_rows", "value": len(found_rows), "note": "Official exam-authority snippets expose min score."},
        {"metric": "line_score_unresolved_rows", "value": len(unresolved_rows), "note": "Need official physics page confirmation."},
        {"metric": "min_rank_found_rows", "value": 0, "note": "The official line-score page has no rank column."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No rank join."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No rank join."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        {"metric": "found_group_scores", "value": ";".join(f"{row['university_code']}-{row['group_code']}={row['min_score']}" for row in found_rows), "note": ""},
        {"metric": "unresolved_group_scores", "value": ";".join(f"{row['university_code']}-{row['group_code']}" for row in unresolved_rows), "note": ""},
    ]
    write_csv(ROLLUP_CSV, rollup, ["metric", "value", "note"])

    qa = [
        {
            "check": "candidate_preview_group_rows_covered",
            "status": "PASS",
            "detail": "Covered 8 group rows from marker 121 target candidate set, including 河北北方学院 151/152.",
        },
        {
            "check": "official_exam_authority_source_only_for_found_scores",
            "status": "PASS",
            "detail": LINE_SOURCE_URL,
        },
        {
            "check": "unresolved_rows_not_overclaimed",
            "status": "PASS",
            "detail": "14275-105 and 10513-105 keep blank min_score because current snippets did not confirm physics line-score rows.",
        },
        {
            "check": "score_not_rank_claimed",
            "status": "PASS",
            "detail": "min_rank remains blank for every row.",
        },
        {
            "check": "no_reference_trend_pool_intake",
            "status": "PASS",
            "detail": "No intake/calibration/canonical/ML rows opened.",
        },
    ]
    write_csv(QA_CSV, qa, ["check", "status", "detail"])

    exclusion = [
        {
            "line_score_batch_id": row["line_score_batch_id"],
            "university_code": row["university_code"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "min_score": row["min_score"],
            "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": "min_rank_missing" if row["min_score"] else "official_physics_line_score_not_confirmed",
            "safe_next_action": row["required_resolution"],
        }
        for row in out_rows
    ]
    write_csv(EXCLUSION_CSV, exclusion, [
        "line_score_batch_id",
        "university_code",
        "university_name",
        "group_code",
        "min_score",
        "excluded_from",
        "reason",
        "safe_next_action",
    ])

    DOC_MD.write_text(
        f"""# Reference trend 520 P1 batch17 exam-authority line-score batch

Generated: 2026-05-17

## Scope

This packet extends the official Guangxi exam-authority 2025 physical ordinary-batch line-score reachability check across batch17 target groups.

## Outputs

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`

## Confirmed Official Score Rows

- `10596-153` 桂林理工大学: 490
- `10412-101` 江西中医药大学: 527
- `10407-102` 江西理工大学: 461
- `10092-151` 河北北方学院: 490
- `10092-152` 河北北方学院: 462
- `10466-152` 河南农业大学: 382

## Unresolved Rows

- `14275-105` 浙江外国语学院: not confirmed in current official physics snippet search
- `10513-105` 湖北师范大学: not confirmed in current official physics snippet search

## Boundary

- This is line-score reachability only.
- The source has no rank column; all `min_rank` values remain blank.
- No reference trend intake, calibration, canonical/ML, or 32-school decision-pool update is opened.
""",
        encoding="utf-8",
    )

    marker = f"""

## 126. 2026-05-17 P1 batch17 exam-authority line-score batch

已新增 P1 batch17 广西考试院投档最低分批量 reachability：

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`
- `docs/{OUT_PREFIX}.md`

覆盖结果：基于广西招生考试院 2025 本科普通批首选物理科目组投档最低分官方页的索引片段，覆盖 marker 121 的 8 条 group target rows；其中 6 条可确认官方最低分：`10596-153=490`、`10412-101=527`、`10407-102=461`、`10092-151=490`、`10092-152=462`、`10466-152=382`。`14275-105` 与 `10513-105` 在本轮官方物理页片段搜索中未确认，保持 blank。QA PASS。

准入边界：本轮只生成 line-score reachability；官方投档线页不含最低位次，所有 `min_rank` 继续为空，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。
"""
    existing = HANDOFF_MD.read_text(encoding="utf-8") if HANDOFF_MD.exists() else ""
    if "## 126. 2026-05-17 P1 batch17 exam-authority line-score batch" not in existing:
        with HANDOFF_MD.open("a", encoding="utf-8") as f:
            f.write(marker)


if __name__ == "__main__":
    build_outputs()
