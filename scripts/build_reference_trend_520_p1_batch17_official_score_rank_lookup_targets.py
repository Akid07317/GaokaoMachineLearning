#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

INPUT = SEED_DIR / "reference_trend_520_p1_batch17_official_rank_join_gap_queue.csv"

TARGETS = SEED_DIR / "reference_trend_520_p1_batch17_official_score_rank_lookup_targets.csv"
ROLLUP = REPORTS_DIR / "reference_trend_520_p1_batch17_official_score_rank_lookup_targets_rollup.csv"
QA = REPORTS_DIR / "reference_trend_520_p1_batch17_official_score_rank_lookup_targets_qa.csv"
EXCLUSION = REPORTS_DIR / "reference_trend_520_p1_batch17_official_score_rank_lookup_targets_exclusion_log.csv"
DOC = DOCS_DIR / "reference_trend_520_p1_batch17_official_score_rank_lookup_targets.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def qa_row(check: str, status: bool, detail: str) -> dict[str, str]:
    return {"check": check, "status": "PASS" if status else "FAIL", "detail": detail}


def main() -> None:
    rows = read_rows(INPUT)
    by_score: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_score[row["min_score"].strip()].append(row)

    target_rows: list[dict[str, str]] = []
    duplicate_rows: list[dict[str, str]] = []
    for index, score in enumerate(sorted(by_score, key=int, reverse=True), start=1):
        consumers = by_score[score]
        consumer_ids = "|".join(row["rank_gap_queue_id"] for row in consumers)
        group_pair_keys = "|".join(row["group_pair_key"] for row in consumers)
        universities = "|".join(row["university_name"] for row in consumers)
        prior_backoff = "|".join(row["prior_backoff_note"] for row in consumers if row["prior_backoff_note"])
        official_line_score_urls = sorted({row["official_line_score_url"] for row in consumers})
        rank_source_statuses = sorted({row["official_rank_source_status"] for row in consumers})

        target_rows.append(
            {
                "score_rank_lookup_target_id": f"reference_trend_520_p1_batch17_official_score_rank_lookup_targets_{index:04d}",
                "year": "2025",
                "province": "广西",
                "subject_category": "物理类",
                "min_score": score,
                "consumer_rank_gap_queue_ids": consumer_ids,
                "consumer_group_pair_keys": group_pair_keys,
                "consumer_universities": universities,
                "consumer_group_year_count": str(len(consumers)),
                "official_line_score_url": "|".join(official_line_score_urls),
                "official_rank_source_status": "|".join(rank_source_statuses),
                "prior_backoff_note": prior_backoff,
                "rank_lookup_policy": (
                    "Single official score-rank lookup may fan out to every listed consumer group-year; "
                    "use only official Guangxi 2025 physics one-score-one-rank raw cache."
                ),
                "required_next_artifact": "official_2025_physics_score_rank_cache_or_browser_approval_packet",
                "stop_condition": "stop_before_selecting_rank_until_official_raw_cache_and_total_score_policy_QA_pass",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

        if len(consumers) > 1:
            duplicate_rows.append(
                {
                    "min_score": score,
                    "excluded_from": "duplicate_official_rank_lookup",
                    "reason": "multiple_group_year_consumers_share_one_score_lookup_target",
                    "consumer_group_pair_keys": group_pair_keys,
                    "safe_next_action": "perform one official score-rank lookup and fan out only after QA",
                }
            )

    if not duplicate_rows:
        duplicate_rows.append(
            {
                "min_score": "",
                "excluded_from": "duplicate_official_rank_lookup",
                "reason": "no_duplicate_score_targets",
                "consumer_group_pair_keys": "",
                "safe_next_action": "none",
            }
        )

    target_fields = [
        "score_rank_lookup_target_id",
        "year",
        "province",
        "subject_category",
        "min_score",
        "consumer_rank_gap_queue_ids",
        "consumer_group_pair_keys",
        "consumer_universities",
        "consumer_group_year_count",
        "official_line_score_url",
        "official_rank_source_status",
        "prior_backoff_note",
        "rank_lookup_policy",
        "required_next_artifact",
        "stop_condition",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
    ]
    write_csv(TARGETS, target_fields, target_rows)
    write_csv(
        EXCLUSION,
        ["min_score", "excluded_from", "reason", "consumer_group_pair_keys", "safe_next_action"],
        duplicate_rows,
    )

    total_consumers = sum(int(row["consumer_group_year_count"]) for row in target_rows)
    duplicate_score_targets = sum(1 for row in target_rows if int(row["consumer_group_year_count"]) > 1)
    rollup_rows = [
        {"metric": "score_rank_lookup_targets", "value": str(len(target_rows)), "note": "Unique official score lookup targets."},
        {"metric": "consumer_group_year_rows", "value": str(total_consumers), "note": "Group-year rows that will consume those official rank lookups."},
        {"metric": "duplicate_score_targets", "value": str(duplicate_score_targets), "note": "Scores shared by more than one group-year consumer."},
        {"metric": "official_rank_source_rows", "value": "0", "note": "No official one-score-one-rank raw table is cached yet."},
        {"metric": "reference_trend_pool_eligible_rows", "value": "0", "note": "Rank lookup has not been completed."},
        {"metric": "calibration_eligible_rows", "value": "0", "note": "No official min_rank is selected."},
        {"metric": "canonical_ml_entry_open_rows", "value": "0", "note": "Canonical/ML remains closed."},
    ]
    for row in target_rows:
        rollup_rows.append(
            {
                "metric": f"target_score::{row['min_score']}",
                "value": row["consumer_group_year_count"],
                "note": row["consumer_group_pair_keys"],
            }
        )
    write_csv(ROLLUP, ["metric", "value", "note"], rollup_rows)

    qa_rows = [
        qa_row("unique_score_target_count", len(target_rows) == 5, f"{len(target_rows)} unique score targets generated."),
        qa_row("consumer_group_year_count", total_consumers == 6, f"{total_consumers} consumer group-year rows preserved."),
        qa_row("duplicate_score_collapsed", any(row["min_score"] == "490" and row["consumer_group_year_count"] == "2" for row in target_rows), "Score 490 collapses two group-year consumers."),
        qa_row("rank_not_selected", all("official_rank_source_rows" not in row for row in target_rows), "No rank values are present in lookup targets."),
        qa_row("blocked_terminal_boundary_carried", all("do_not_repeat_curl" in row["official_rank_source_status"] for row in target_rows), "Known qg/qn terminal blockage is retained."),
        qa_row("intake_and_canonical_closed", all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in target_rows), "Intake, calibration, canonical, and ML remain closed."),
    ]
    write_csv(QA, ["check", "status", "detail"], qa_rows)

    score_lines = "\n".join(
        f"- {row['min_score']}: {row['consumer_group_year_count']} consumer group-year row(s) -> {row['consumer_group_pair_keys']}"
        for row in target_rows
    )
    DOC.write_text(
        f"""# P1 Batch17 Official Score-Rank Lookup Targets

日期：2026-05-17

## 结果

从 marker 134 的 6 条 official rank join gap rows 去重成 5 个 official score-rank lookup targets。后续只需按分数查一次官方 2025 广西物理类一分一档，再在 QA 通过后回填对应 group-year。

{score_lines}

## 边界

本轮只生成去重后的 lookup target 包、QA、rollup 和 duplicate lookup exclusion log；不抓取官方一分一档细页，不重复终端 curl `qg/qn` 阻塞路径，不采用第三方镜像位次，不选择或推断任何 min_rank。

reference trend intake、calibration、canonical/ML 和 32 所 decision_pool 继续关闭。
""",
        encoding="utf-8",
    )

    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

## 135. 2026-05-17 P1 batch17 official score-rank lookup targets

已新增 P1 batch17 official score-rank lookup targets：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_score_rank_lookup_targets.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_lookup_targets_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_lookup_targets_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_lookup_targets_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_score_rank_lookup_targets.md`

覆盖结果：将 marker 134 的 6 条 rank join gap rows 去重为 5 个 official score-rank lookup targets；其中 `490` 一次 lookup 服务 `10596-153` 与 `10092-151` 两条 group-year consumers。QA PASS。

准入边界：本轮只生成去重 lookup target/QA/rollup，不抓取一分一档细页、不重复已阻塞终端 curl、不采用第三方镜像位次、不选择或推断 min_rank；reference trend intake、calibration、canonical/ML、32 所 decision_pool 继续关闭。
"""
        )


if __name__ == "__main__":
    main()
