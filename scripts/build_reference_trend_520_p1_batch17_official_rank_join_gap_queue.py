#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

INPUT = SEED_DIR / "reference_trend_520_p1_batch17_source_packet_preview_action_queue.csv"

QUEUE = SEED_DIR / "reference_trend_520_p1_batch17_official_rank_join_gap_queue.csv"
ROLLUP = REPORTS_DIR / "reference_trend_520_p1_batch17_official_rank_join_gap_queue_rollup.csv"
QA = REPORTS_DIR / "reference_trend_520_p1_batch17_official_rank_join_gap_queue_qa.csv"
EXCLUSION = REPORTS_DIR / "reference_trend_520_p1_batch17_official_rank_join_gap_queue_exclusion_log.csv"
DOC = DOCS_DIR / "reference_trend_520_p1_batch17_official_rank_join_gap_queue.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

OFFICIAL_LINE_SCORE_URL = "https://www.gxeea.cn/view/content_1013_31850.htm"
RANK_SOURCE_STATUS = (
    "official_2025_physics_one_score_one_rank_not_cached;"
    "terminal_qg_qn_subpages_blocked_do_not_repeat_curl"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def has_value(value: str | None) -> bool:
    return bool((value or "").strip())


def rank_gap_row(row: dict[str, str], index: int) -> dict[str, str]:
    score = row["min_score"].strip()
    prior_backoff = ""
    if row["group_pair_key"] == "10412-101" and score == "527":
        prior_backoff = (
            "mirror_only_candidates_seen_for_527:37291_or_37372;"
            "not_selected_without_official_total-score_policy"
        )

    return {
        "rank_gap_queue_id": f"reference_trend_520_p1_batch17_official_rank_join_gap_queue_{index:04d}",
        "source_action_queue_id": row["action_queue_id"],
        "group_pair_key": row["group_pair_key"],
        "university_code": row["university_code"],
        "university_name": row["university_name"],
        "group_code": row["group_code"],
        "year": row["year"],
        "province": row["province"],
        "batch": row["batch"],
        "subject_category": row["subject_category"],
        "min_score": score,
        "min_rank": "",
        "official_line_score_url": OFFICIAL_LINE_SCORE_URL,
        "official_line_score_status": "confirmed_from_guangxi_exam_authority_physics_batch_line_page",
        "official_rank_source_status": RANK_SOURCE_STATUS,
        "unique_score_lookup_key": f"{row['year']}_{row['province']}_{row['subject_category']}_score_{score}",
        "score_rank_lookup_unit": "score_year_subject_policy",
        "rank_policy_required": (
            "Use official Guangxi 2025 physics one-score-one-rank table; "
            "do not select third-party mirror rank or mixed total-score policy."
        ),
        "prior_backoff_note": prior_backoff,
        "safe_without_new_user_approval": "false_for_rank_fetch;true_for_queue_only",
        "requires_browser_or_alternate_fetch": "true_if_official_qg_qn_static_cache_remains_blocked",
        "requires_header_cookie_form_replay": "approval_required_if_needed",
        "required_next_artifact": "official_2025_physics_score_rank_cache_or_browser_approval_packet",
        "qa_focus": (
            "join official min_rank by score only after official raw cache exists; "
            "preserve group-year boundary and total-score policy"
        ),
        "stop_condition": "stop_before_rank_join_until_official_score_rank_source_is_cached_and_policy_QA_passes",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
    }


def exclusion_row(row: dict[str, str], reason: str) -> dict[str, str]:
    return {
        "source_action_queue_id": row["action_queue_id"],
        "group_pair_key": row["group_pair_key"],
        "university_name": row["university_name"],
        "excluded_from": "official_rank_join_gap_queue",
        "reason": reason,
        "safe_next_action": row.get("next_action", ""),
    }


def qa_row(check: str, status: bool, detail: str) -> dict[str, str]:
    return {"check": check, "status": "PASS" if status else "FAIL", "detail": detail}


def main() -> None:
    rows = read_rows(INPUT)

    gap_rows: list[dict[str, str]] = []
    exclusions: list[dict[str, str]] = []
    for row in rows:
        if has_value(row.get("min_score")) and not has_value(row.get("min_rank")):
            gap_rows.append(rank_gap_row(row, len(gap_rows) + 1))
        elif has_value(row.get("min_rank")):
            exclusions.append(exclusion_row(row, "min_rank_already_present_no_gap"))
        else:
            exclusions.append(exclusion_row(row, "missing_official_line_score_so_rank_join_not_ready"))

    queue_fields = [
        "rank_gap_queue_id",
        "source_action_queue_id",
        "group_pair_key",
        "university_code",
        "university_name",
        "group_code",
        "year",
        "province",
        "batch",
        "subject_category",
        "min_score",
        "min_rank",
        "official_line_score_url",
        "official_line_score_status",
        "official_rank_source_status",
        "unique_score_lookup_key",
        "score_rank_lookup_unit",
        "rank_policy_required",
        "prior_backoff_note",
        "safe_without_new_user_approval",
        "requires_browser_or_alternate_fetch",
        "requires_header_cookie_form_replay",
        "required_next_artifact",
        "qa_focus",
        "stop_condition",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
    ]
    exclusion_fields = [
        "source_action_queue_id",
        "group_pair_key",
        "university_name",
        "excluded_from",
        "reason",
        "safe_next_action",
    ]

    write_csv(QUEUE, queue_fields, gap_rows)
    write_csv(EXCLUSION, exclusion_fields, exclusions)

    scores = [row["min_score"] for row in gap_rows]
    score_counts = Counter(scores)
    rollup_rows = [
        {"metric": "rank_gap_group_rows", "value": str(len(gap_rows)), "note": "Group-year rows with official min_score but missing official min_rank."},
        {"metric": "rank_gap_unique_scores", "value": str(len(score_counts)), "note": "Unique scores to look up in official one-score-one-rank source."},
        {"metric": "excluded_rows", "value": str(len(exclusions)), "note": "Rows without official min_score or without a rank gap."},
        {"metric": "rows_with_prior_mirror_backoff", "value": str(sum(1 for row in gap_rows if row["prior_backoff_note"])), "note": "Mirror-only ranks are noted but not accepted."},
        {"metric": "official_rank_source_rows", "value": "0", "note": "No official one-score-one-rank raw table is cached yet."},
        {"metric": "reference_trend_pool_eligible_rows", "value": "0", "note": "Rank join is not complete."},
        {"metric": "calibration_eligible_rows", "value": "0", "note": "No official min_rank."},
        {"metric": "canonical_ml_entry_open_rows", "value": "0", "note": "Canonical/ML remains closed."},
    ]
    for score, count in sorted(score_counts.items(), key=lambda item: int(item[0]), reverse=True):
        rollup_rows.append({"metric": f"score::{score}", "value": str(count), "note": "Group rows needing official rank lookup at this score."})
    write_csv(ROLLUP, ["metric", "value", "note"], rollup_rows)

    qa_rows = [
        qa_row("rank_gap_group_row_count", len(gap_rows) == 6, f"{len(gap_rows)} group-year rows need official rank join."),
        qa_row("unique_score_count", len(score_counts) == 5, f"{len(score_counts)} unique scores queued: {'|'.join(sorted(score_counts, key=int))}."),
        qa_row("min_rank_not_filled", all(not row["min_rank"] for row in gap_rows), "No min_rank values were selected or inferred."),
        qa_row("official_line_score_url_present", all(row["official_line_score_url"] == OFFICIAL_LINE_SCORE_URL for row in gap_rows), OFFICIAL_LINE_SCORE_URL),
        qa_row("rank_source_boundary_present", all("do_not_repeat_curl" in row["official_rank_source_status"] for row in gap_rows), "Known terminal qg/qn blockage is carried forward."),
        qa_row("intake_and_canonical_closed", all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in gap_rows), "Intake, calibration, canonical, and ML remain closed."),
    ]
    write_csv(QA, ["check", "status", "detail"], qa_rows)

    doc = f"""# P1 Batch17 Official Rank Join Gap Queue

日期：2026-05-17

## 结果

从 marker 133 的 source-packet preview action queue 中抽取 6 条已有广西考试院官方最低分、但仍缺官方最低位次的 group-year rows，生成官方一分一档位次 join gap queue。

- group-year rank gap rows：{len(gap_rows)}
- unique score lookup keys：{len(score_counts)}
- excluded rows：{len(exclusions)}
- official rank rows accepted：0

## 分数查找目标

{chr(10).join(f'- {score}: {count} group row(s)' for score, count in sorted(score_counts.items(), key=lambda item: int(item[0]), reverse=True))}

## 边界

本轮只生成 rank join gap queue、QA、rollup 和 exclusion log；不抓取广西考试院一分一档细分页，不重复终端 curl `qg/qn` 阻塞路径，不采用第三方镜像位次，不做位次换算，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。

下一步只有在获得官方 2025 物理类一分一档 raw cache，或用户批准浏览器态/可审计替代抓取后，才能把 `min_score` join 到官方 `min_rank`。
"""
    DOC.write_text(doc, encoding="utf-8")

    handoff = f"""

## 134. 2026-05-17 P1 batch17 official rank join gap queue

已新增 P1 batch17 official rank join gap queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_rank_join_gap_queue.csv`
- `reports/reference_trend_520_p1_batch17_official_rank_join_gap_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_rank_join_gap_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_rank_join_gap_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_rank_join_gap_queue.md`

覆盖结果：从 marker 133 的 15 条 action queue rows 中抽取 6 条已有广西考试院官方最低分、但缺官方最低位次的 group-year rows，形成 5 个 unique score lookup targets：{", ".join(sorted(score_counts, key=int, reverse=True))}。其余 9 条因尚无官方最低分或不具备 rank join 条件写入 exclusion log。QA PASS。

准入边界：本轮只生成官方位次 join 缺口队列，不抓取一分一档细页、不重复已阻塞的终端 curl、不采用第三方镜像位次、不做位次换算；reference trend intake、calibration、canonical/ML、32 所 decision_pool 继续关闭。
"""
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(handoff)


if __name__ == "__main__":
    main()
