#!/usr/bin/env python3
"""Build marker 125 JXUTCM score-rank backoff candidate QA packet.

This records non-official mirror candidates for score 527 rank lookup while
keeping rank join, reference-trend intake, calibration, canonical, ML, and the
32-school decision pool closed.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

LINE_CSV = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_line_score_reachability.csv"

OUT_PREFIX = "reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates"
OUT_CSV = SEED_DIR / f"{OUT_PREFIX}.csv"
ROLLUP_CSV = REPORTS_DIR / f"{OUT_PREFIX}_rollup.csv"
QA_CSV = REPORTS_DIR / f"{OUT_PREFIX}_qa.csv"
EXCLUSION_CSV = REPORTS_DIR / f"{OUT_PREFIX}_exclusion_log.csv"
DOC_MD = DOCS_DIR / f"{OUT_PREFIX}.md"
HANDOFF_MD = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"


CANDIDATES = [
    {
        "score_total_policy": "total_score_plus_national_bonus",
        "score_rank_title": "2025年广西高考物理类一分一档表（总分=总成绩+全国性加分）",
        "mirror_owner": "高考直通车",
        "mirror_url": "https://app.gaokaozhitongche.com/news/h/p2NMBb1w",
        "mirror_access_status": "web_search_snippet_open_result",
        "source_claims_original_owner": "广西招生考试院",
        "score": "527",
        "same_score_people": "617",
        "cumulative_people": "37907",
        "rank_value": "37291",
    },
    {
        "score_total_policy": "total_score_plus_highest_of_national_or_local_bonus",
        "score_rank_title": "2025年广西高考物理类一分一档表（总成绩+全国性加分和地方性加分的最高分）",
        "mirror_owner": "高考直通车",
        "mirror_url": "https://app.gaokaozhitongche.com/news/h/gzQejEjz",
        "mirror_access_status": "web_search_snippet_open_result",
        "source_claims_original_owner": "广西招生考试院",
        "score": "527",
        "same_score_people": "616",
        "cumulative_people": "37987",
        "rank_value": "37372",
    },
]


def read_one_row(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise SystemExit(f"Expected exactly one line-score reachability row in {path}")
    return rows[0]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs() -> None:
    line = read_one_row(LINE_CSV)
    if line["university_code"] != "10412" or line["queue_group_code"] != "101":
        raise SystemExit("Line-score packet is not the expected JXUTCM 10412-101 row")
    if line["min_score"] != "527" or line["min_rank"]:
        raise SystemExit("Expected min_score=527 and blank min_rank before backoff QA")

    out_rows = []
    for index, candidate in enumerate(CANDIDATES, start=1):
        out_rows.append({
            "rank_backoff_candidate_id": f"reference_trend_520_p1_batch17_jxutcm_rank_backoff_{index:04d}",
            "line_score_reachability_id": line["line_score_reachability_id"],
            "university_code": line["university_code"],
            "university_name": line["university_name"],
            "year": line["year"],
            "province": line["province"],
            "batch": line["batch"],
            "subject_category": line["subject_category"],
            "group_code": line["queue_group_code"],
            "min_score": line["min_score"],
            "candidate_rank": candidate["rank_value"],
            "candidate_cumulative_people": candidate["cumulative_people"],
            "candidate_same_score_people": candidate["same_score_people"],
            "score_total_policy": candidate["score_total_policy"],
            "rank_source_type": "third_party_mirror_of_exam_authority_table",
            "rank_source_owner": candidate["mirror_owner"],
            "rank_source_title": candidate["score_rank_title"],
            "rank_source_url": candidate["mirror_url"],
            "rank_source_access_status": candidate["mirror_access_status"],
            "rank_source_claims_original_owner": candidate["source_claims_original_owner"],
            "official_raw_cache_status": "not_cached_official_fine_page_terminal_blocked",
            "official_verification_status": "blocked_need_official_gxeea_or_browser_state_cache",
            "rank_choice_status": "unresolved_multiple_score_total_policies",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "required_resolution": (
                "verify the 527 rank against an official Guangxi exam-authority one-score-one-rank "
                "page/cache and select the correct score-total policy before intake"
            ),
            "evidence_note": (
                f"Mirror snippet reports 527 -> rank {candidate['rank_value']} under "
                f"{candidate['score_total_policy']}; retained as backoff QA only."
            ),
        })

    fields = [
        "rank_backoff_candidate_id",
        "line_score_reachability_id",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "group_code",
        "min_score",
        "candidate_rank",
        "candidate_cumulative_people",
        "candidate_same_score_people",
        "score_total_policy",
        "rank_source_type",
        "rank_source_owner",
        "rank_source_title",
        "rank_source_url",
        "rank_source_access_status",
        "rank_source_claims_original_owner",
        "official_raw_cache_status",
        "official_verification_status",
        "rank_choice_status",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]
    write_csv(OUT_CSV, out_rows, fields)

    rollup = [
        {"metric": "rank_backoff_candidate_rows", "value": 2, "note": "Two mirror-only score-rank candidates for score 527."},
        {"metric": "official_rank_source_rows", "value": 0, "note": "No official raw table/page cached this round."},
        {"metric": "score_527_candidate_rows", "value": 2, "note": "Both candidates are for score 527."},
        {"metric": "candidate_rank_values", "value": "37291|37372", "note": "Different score-total policies; no rank selected."},
        {"metric": "selected_rank_rows", "value": 0, "note": "Rank choice blocked pending official verification."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Mirror-only rank candidates are not intake-ready."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No official rank join."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    write_csv(ROLLUP_CSV, rollup, ["metric", "value", "note"])

    qa = [
        {
            "check": "line_score_packet_present",
            "status": "PASS",
            "detail": f"Backoff candidates attach to {line['line_score_reachability_id']}.",
        },
        {
            "check": "no_official_rank_claim",
            "status": "PASS",
            "detail": "Both rows are explicitly third-party mirror candidates; official raw cache remains missing.",
        },
        {
            "check": "score_policy_ambiguity_retained",
            "status": "PASS",
            "detail": "527 has two candidate rank values: national bonus=37291; national/local highest=37372.",
        },
        {
            "check": "rank_not_selected",
            "status": "PASS",
            "detail": "No candidate rank is copied into the line-score packet or reference trend intake.",
        },
        {
            "check": "no_reference_trend_pool_intake",
            "status": "PASS",
            "detail": "Reference trend pool, calibration, canonical/ML, and decision pool are closed.",
        },
    ]
    write_csv(QA_CSV, qa, ["check", "status", "detail"])

    exclusion = [
        {
            "rank_backoff_candidate_id": row["rank_backoff_candidate_id"],
            "university_code": row["university_code"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "min_score": row["min_score"],
            "candidate_rank": row["candidate_rank"],
            "excluded_from": "rank_join|reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": "third_party_mirror_only_and_score_total_policy_unresolved",
            "safe_next_action": row["required_resolution"],
        }
        for row in out_rows
    ]
    write_csv(EXCLUSION_CSV, exclusion, [
        "rank_backoff_candidate_id",
        "university_code",
        "university_name",
        "group_code",
        "min_score",
        "candidate_rank",
        "excluded_from",
        "reason",
        "safe_next_action",
    ])

    DOC_MD.write_text(
        f"""# Reference trend 520 P1 batch17 JXUTCM rank backoff candidates

Generated: 2026-05-17

## Scope

This packet records mirror-only score-rank candidates for江西中医药大学 `10412-101` at score `527`.

## Outputs

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`

## Candidates

- 总分=总成绩+全国性加分: candidate rank `37291`, cumulative people `37907`, mirror: https://app.gaokaozhitongche.com/news/h/p2NMBb1w
- 总分=总成绩+全国性加分和地方性加分的最高分: candidate rank `37372`, cumulative people `37987`, mirror: https://app.gaokaozhitongche.com/news/h/gzQejEjz

## Boundary

- These rows are backoff QA only.
- No official Guangxi exam-authority raw fine page was cached or parsed this round.
- No rank is selected for intake.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
""",
        encoding="utf-8",
    )

    marker = f"""

## 125. 2026-05-17 P1 batch17 JXUTCM rank backoff candidates

已新增江西中医药大学 527 分位次 backoff QA 候选包：

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`
- `docs/{OUT_PREFIX}.md`

覆盖结果：在官方细分页仍未缓存/解析的前提下，记录两个第三方镜像候选位次，仅用于 QA backoff：`总分=总成绩+全国性加分` 口径下 527 分候选名次 `37291`，`总成绩+全国性加分和地方性加分的最高分` 口径下候选名次 `37372`。由于来源不是已缓存官方页，且总分口径未选择，selected rank rows 仍为 0。QA PASS。

准入边界：本轮不把 37291/37372 写入最低位次，不做位次 join，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步需要官方广西招生考试院一分一档细页浏览器态缓存或其他可审计官方表格来确认 527 的正确位次口径。
"""
    existing = HANDOFF_MD.read_text(encoding="utf-8") if HANDOFF_MD.exists() else ""
    if "## 125. 2026-05-17 P1 batch17 JXUTCM rank backoff candidates" not in existing:
        with HANDOFF_MD.open("a", encoding="utf-8") as f:
            f.write(marker)


if __name__ == "__main__":
    build_outputs()
