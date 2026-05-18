#!/usr/bin/env python3
"""Build a 520-score rank-window preview for the reference trend pool.

This isolates the target-score context without writing canonical/ML artifacts.
The project has used a 520 score floor in the engineering focus files; here we
derive year-specific rank anchors from official admission-line preview rows.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

INTAKE = SEED_DIR / "reference_trend_intake_preview.csv"
DELTA = SEED_DIR / "reference_trend_2024_2025_matched_group_delta_preview.csv"

WINDOW_OUT = SEED_DIR / "reference_trend_520_rank_window_preview.csv"
DELTA_OUT = SEED_DIR / "reference_trend_520_rank_window_delta_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_rank_window_rollup.csv"
SUMMARY_OUT = REPORT_DIR / "reference_trend_520_rank_window_summary.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_rank_window.md"

TARGET_SCORE = 520
WINDOW = 20_000

WINDOW_FIELDS = [
    "window_record_id",
    "year",
    "target_score",
    "target_rank_anchor",
    "rank_window_low",
    "rank_window_high",
    "university_code",
    "university_name",
    "group_code",
    "min_score",
    "min_rank_est",
    "rank_distance_from_anchor",
    "window_bucket",
    "has_plan_count",
    "confidence_tier",
    "source_id",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

DELTA_FIELDS = [
    "delta_window_record_id",
    "group_pair_key",
    "university_code",
    "university_name_2024",
    "university_name_2025",
    "group_code",
    "score_2024",
    "score_2025",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "in_2024_520_window",
    "in_2025_520_window",
    "has_plan_count_2024",
    "has_plan_count_2025",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def parse_int(value: object) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def eligible_intake() -> list[dict[str, str]]:
    return [
        row
        for row in read_csv(INTAKE)
        if row.get("calibration_eligible") == "true" and row.get("year") in {"2024", "2025"}
    ]


def target_rank_anchors(rows: list[dict[str, str]]) -> dict[str, int]:
    anchors: dict[str, int] = {}
    for year in ["2024", "2025"]:
        ranks = [
            parse_int(row.get("min_rank_est"))
            for row in rows
            if row.get("year") == year
            and parse_int(row.get("min_score")) == TARGET_SCORE
            and parse_int(row.get("min_rank_est"))
        ]
        anchors[year] = int(median(ranks)) if ranks else 0
    return anchors


def window_bucket(distance: int) -> str:
    abs_distance = abs(distance)
    if abs_distance <= 5_000:
        return "near_anchor_0_5000"
    if abs_distance <= 10_000:
        return "adjacent_5001_10000"
    if abs_distance <= 20_000:
        return "outer_10001_20000"
    return "outside_window"


def build_window_rows(rows: list[dict[str, str]], anchors: dict[str, int]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        year = row.get("year", "")
        anchor = anchors.get(year, 0)
        rank = parse_int(row.get("min_rank_est"))
        if not anchor or not rank:
            continue
        low = max(1, anchor - WINDOW)
        high = anchor + WINDOW
        if not (low <= rank <= high):
            continue
        distance = rank - anchor
        output.append(
            {
                "window_record_id": f"reference_trend_520_window_{len(output) + 1:05d}",
                "year": year,
                "target_score": TARGET_SCORE,
                "target_rank_anchor": anchor,
                "rank_window_low": low,
                "rank_window_high": high,
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "group_code": row.get("group_code", ""),
                "min_score": row.get("min_score", ""),
                "min_rank_est": rank,
                "rank_distance_from_anchor": distance,
                "window_bucket": window_bucket(distance),
                "has_plan_count": row.get("has_plan_count", "false"),
                "confidence_tier": row.get("confidence_tier", ""),
                "source_id": row.get("source_id", ""),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_520_window_only_not_decision_pool",
            }
        )
    return output


def in_window(rank: int, anchor: int) -> bool:
    return bool(anchor and rank and max(1, anchor - WINDOW) <= rank <= anchor + WINDOW)


def build_delta_rows(anchors: dict[str, int]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in read_csv(DELTA):
        rank_2024 = parse_int(row.get("rank_2024"))
        rank_2025 = parse_int(row.get("rank_2025"))
        in_2024 = in_window(rank_2024, anchors.get("2024", 0))
        in_2025 = in_window(rank_2025, anchors.get("2025", 0))
        if not (in_2024 or in_2025):
            continue
        output.append(
            {
                "delta_window_record_id": f"reference_trend_520_window_delta_{len(output) + 1:05d}",
                "group_pair_key": row.get("group_pair_key", ""),
                "university_code": row.get("university_code", ""),
                "university_name_2024": row.get("university_name_2024", ""),
                "university_name_2025": row.get("university_name_2025", ""),
                "group_code": row.get("group_code", ""),
                "score_2024": row.get("score_2024", ""),
                "score_2025": row.get("score_2025", ""),
                "rank_2024": rank_2024,
                "rank_2025": rank_2025,
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "in_2024_520_window": "true" if in_2024 else "false",
                "in_2025_520_window": "true" if in_2025 else "false",
                "has_plan_count_2024": row.get("has_plan_count_2024", "false"),
                "has_plan_count_2025": row.get("has_plan_count_2025", "false"),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_520_window_delta_only_not_decision_pool",
            }
        )
    return output


def write_doc(anchors: dict[str, int], window_rows: list[dict[str, object]], delta_rows: list[dict[str, object]]) -> None:
    by_year = Counter(row.get("year", "") for row in window_rows)
    by_bucket = Counter(row.get("window_bucket", "") for row in window_rows)
    by_direction = Counter(row.get("trend_direction", "") for row in delta_rows)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 520 Rank Window Preview",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已按项目既有 520 分数线口径，从 reference trend pool 中抽取目标位次上下 20,000 位的趋势窗口。该结果只用于趋势背景和抽样优先级，不写 canonical/ML，也不并入 32 所 decision_pool。",
                "",
                "## 位次锚点",
                "",
                f"- 2024 score 520 rank anchor: {anchors.get('2024', 0)}",
                f"- 2025 score 520 rank anchor: {anchors.get('2025', 0)}",
                "",
                "## 覆盖",
                "",
                f"- window group-year rows: {len(window_rows)}",
                f"- 2024 rows: {by_year.get('2024', 0)}",
                f"- 2025 rows: {by_year.get('2025', 0)}",
                f"- matched delta rows in window: {len(delta_rows)}",
                f"- hotter/higher selectivity rows: {by_direction.get('hotter_or_higher_selectivity', 0)}",
                f"- cooler/lower selectivity rows: {by_direction.get('cooler_or_lower_selectivity', 0)}",
                "",
                "## 窗口分层",
                "",
                f"- near anchor 0-5,000: {by_bucket.get('near_anchor_0_5000', 0)}",
                f"- adjacent 5,001-10,000: {by_bucket.get('adjacent_5001_10000', 0)}",
                f"- outer 10,001-20,000: {by_bucket.get('outer_10001_20000', 0)}",
                "",
                "## 边界",
                "",
                "- 这是趋势参考窗口，不是报考推荐清单。",
                "- 当前计划数字段仍缺失，不能解释计划数变化。",
                "- 后续应优先对窗口内 hotter/cooler 且接近目标位次的组补 plan/source packet。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = eligible_intake()
    anchors = target_rank_anchors(rows)
    window_rows = build_window_rows(rows, anchors)
    delta_rows = build_delta_rows(anchors)
    by_year = Counter(row.get("year", "") for row in window_rows)
    by_direction = Counter(row.get("trend_direction", "") for row in delta_rows)
    summary = [
        {"metric": "target_score", "bucket": "all", "value": TARGET_SCORE},
        {"metric": "window_size_each_side", "bucket": "all", "value": WINDOW},
        {"metric": "target_rank_anchor", "bucket": "2024", "value": anchors.get("2024", 0)},
        {"metric": "target_rank_anchor", "bucket": "2025", "value": anchors.get("2025", 0)},
        {"metric": "window_group_year_rows", "bucket": "all", "value": len(window_rows)},
        {"metric": "window_group_year_rows", "bucket": "2024", "value": by_year.get("2024", 0)},
        {"metric": "window_group_year_rows", "bucket": "2025", "value": by_year.get("2025", 0)},
        {"metric": "matched_delta_rows_in_window", "bucket": "all", "value": len(delta_rows)},
    ]
    for direction, count in sorted(by_direction.items()):
        summary.append({"metric": "trend_direction_rows", "bucket": direction, "value": count})
    rollup = [
        {"metric": "target_score", "value": TARGET_SCORE},
        {"metric": "target_rank_anchor_2024", "value": anchors.get("2024", 0)},
        {"metric": "target_rank_anchor_2025", "value": anchors.get("2025", 0)},
        {"metric": "window_group_year_rows", "value": len(window_rows)},
        {"metric": "matched_delta_rows_in_window", "value": len(delta_rows)},
        {"metric": "plan_count_available_rows", "value": 0},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(WINDOW_OUT, window_rows, WINDOW_FIELDS)
    write_csv(DELTA_OUT, delta_rows, DELTA_FIELDS)
    write_csv(SUMMARY_OUT, summary, ["metric", "bucket", "value"])
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(anchors, window_rows, delta_rows)
    print(f"window_rows={len(window_rows)}")
    print(f"delta_rows={len(delta_rows)}")


if __name__ == "__main__":
    main()
