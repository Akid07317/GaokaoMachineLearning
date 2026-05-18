#!/usr/bin/env python3
"""Build rank-band coverage and 2024-2025 group delta previews.

Inputs are the isolated reference trend intake preview rows. Outputs are
non-baseline, non-canonical, non-ML reports for trend-pool diagnostics.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

INTAKE = SEED_DIR / "reference_trend_intake_preview.csv"
DELTA_OUT = SEED_DIR / "reference_trend_2024_2025_matched_group_delta_preview.csv"
BAND_COVERAGE_OUT = REPORT_DIR / "reference_trend_rank_band_coverage.csv"
DELTA_SUMMARY_OUT = REPORT_DIR / "reference_trend_rank_delta_summary.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_rank_band_delta_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_rank_band_delta.md"

BANDS = [
    ("R00_000001_001000", 1, 1000),
    ("R01_001001_003000", 1001, 3000),
    ("R02_003001_005000", 3001, 5000),
    ("R03_005001_010000", 5001, 10000),
    ("R04_010001_020000", 10001, 20000),
    ("R05_020001_040000", 20001, 40000),
    ("R06_040001_070000", 40001, 70000),
    ("R07_070001_100000", 70001, 100000),
    ("R08_100001_plus", 100001, 10**9),
]

DELTA_FIELDS = [
    "delta_record_id",
    "university_code",
    "university_name_2024",
    "university_name_2025",
    "group_code",
    "group_pair_key",
    "score_2024",
    "score_2025",
    "score_delta_2025_minus_2024",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "rank_band_2024",
    "rank_band_2025",
    "trend_direction",
    "calibration_eligible_pair",
    "has_plan_count_2024",
    "has_plan_count_2025",
    "source_id_2024",
    "source_id_2025",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

BAND_FIELDS = [
    "year",
    "rank_band",
    "rank_low",
    "rank_high",
    "eligible_group_year_rows",
    "unique_university_codes",
    "min_score_lowest",
    "min_score_highest",
    "median_min_score",
    "plan_count_available_rows",
    "canonical_ml_entry_open",
]

SUMMARY_FIELDS = ["metric", "bucket", "value"]


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


def rank_band(rank: int) -> str:
    if rank <= 0:
        return "R99_missing_or_invalid"
    for name, low, high in BANDS:
        if low <= rank <= high:
            return name
    return "R99_missing_or_invalid"


def trend_direction(rank_delta: int, score_delta: int) -> str:
    if rank_delta == 0 and score_delta == 0:
        return "flat_same_rank_and_score"
    # Rank is worse when number increases.
    if rank_delta > 0 and score_delta <= 0:
        return "cooler_or_lower_selectivity"
    if rank_delta < 0 and score_delta >= 0:
        return "hotter_or_higher_selectivity"
    if rank_delta > 0 and score_delta > 0:
        return "mixed_score_up_rank_worse"
    if rank_delta < 0 and score_delta < 0:
        return "mixed_score_down_rank_better"
    return "mixed_small_or_ambiguous"


def eligible_rows() -> list[dict[str, str]]:
    return [
        row
        for row in read_csv(INTAKE)
        if row.get("calibration_eligible") == "true" and row.get("year") in {"2024", "2025"}
    ]


def build_band_coverage(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        band = rank_band(parse_int(row.get("min_rank_est")))
        grouped[(row.get("year", ""), band)].append(row)

    output: list[dict[str, object]] = []
    for year in ["2024", "2025"]:
        for band_name, low, high in BANDS:
            band_rows = grouped.get((year, band_name), [])
            scores = [parse_int(row.get("min_score")) for row in band_rows if parse_int(row.get("min_score"))]
            output.append(
                {
                    "year": year,
                    "rank_band": band_name,
                    "rank_low": low,
                    "rank_high": "" if high == 10**9 else high,
                    "eligible_group_year_rows": len(band_rows),
                    "unique_university_codes": len(
                        {row.get("university_code", "") for row in band_rows if row.get("university_code")}
                    ),
                    "min_score_lowest": min(scores) if scores else "",
                    "min_score_highest": max(scores) if scores else "",
                    "median_min_score": median(scores) if scores else "",
                    "plan_count_available_rows": sum(1 for row in band_rows if row.get("has_plan_count") == "true"),
                    "canonical_ml_entry_open": "false",
                }
            )
    return output


def build_delta(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_pair: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        key = (row.get("university_code", ""), row.get("group_code", ""))
        if key[0] and key[1]:
            by_pair[key][row.get("year", "")] = row

    output: list[dict[str, object]] = []
    for (university_code, group_code), years in sorted(by_pair.items()):
        if "2024" not in years or "2025" not in years:
            continue
        row_2024 = years["2024"]
        row_2025 = years["2025"]
        score_2024 = parse_int(row_2024.get("min_score"))
        score_2025 = parse_int(row_2025.get("min_score"))
        rank_2024 = parse_int(row_2024.get("min_rank_est"))
        rank_2025 = parse_int(row_2025.get("min_rank_est"))
        score_delta = score_2025 - score_2024
        rank_delta = rank_2025 - rank_2024
        output.append(
            {
                "delta_record_id": f"reference_trend_delta_{len(output) + 1:05d}",
                "university_code": university_code,
                "university_name_2024": row_2024.get("university_name", ""),
                "university_name_2025": row_2025.get("university_name", ""),
                "group_code": group_code,
                "group_pair_key": f"{university_code}-{group_code}",
                "score_2024": score_2024,
                "score_2025": score_2025,
                "score_delta_2025_minus_2024": score_delta,
                "rank_2024": rank_2024,
                "rank_2025": rank_2025,
                "rank_delta_2025_minus_2024": rank_delta,
                "rank_band_2024": rank_band(rank_2024),
                "rank_band_2025": rank_band(rank_2025),
                "trend_direction": trend_direction(rank_delta, score_delta),
                "calibration_eligible_pair": "true",
                "has_plan_count_2024": row_2024.get("has_plan_count", "false"),
                "has_plan_count_2025": row_2025.get("has_plan_count", "false"),
                "source_id_2024": row_2024.get("source_id", ""),
                "source_id_2025": row_2025.get("source_id", ""),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_delta_preview_only_not_decision_pool",
            }
        )
    return output


def build_summary(rows: list[dict[str, str]], deltas: list[dict[str, object]]) -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []
    years = Counter(row.get("year", "") for row in rows)
    summary.append({"metric": "eligible_group_year_rows", "bucket": "all", "value": len(rows)})
    for year in ["2024", "2025"]:
        summary.append({"metric": "eligible_group_year_rows", "bucket": year, "value": years.get(year, 0)})
    summary.append({"metric": "matched_2024_2025_group_pairs", "bucket": "all", "value": len(deltas)})
    summary.append(
        {
            "metric": "unique_university_codes_in_matched_pairs",
            "bucket": "all",
            "value": len({row.get("university_code") for row in deltas}),
        }
    )
    for direction, count in sorted(Counter(row.get("trend_direction", "") for row in deltas).items()):
        summary.append({"metric": "trend_direction_rows", "bucket": direction, "value": count})
    for band, count in sorted(Counter(row.get("rank_band_2024", "") for row in deltas).items()):
        summary.append({"metric": "matched_pair_2024_rank_band_rows", "bucket": band, "value": count})
    return summary


def write_doc(band_rows: list[dict[str, object]], delta_rows: list[dict[str, object]]) -> None:
    direction_counts = Counter(row.get("trend_direction", "") for row in delta_rows)
    band_2025 = {
        row.get("rank_band"): row.get("eligible_group_year_rows")
        for row in band_rows
        if row.get("year") == "2025"
    }
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend Rank Band And Delta Preview",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已基于 `reference_trend_intake_preview.csv` 中的 strict eligible 记录生成位次带覆盖和 2024-2025 同院校专业组 delta 预览。该结果只用于趋势池诊断，不写 canonical/ML，也不并入 32 所 decision_pool。",
                "",
                "## 覆盖",
                "",
                f"- matched 2024/2025 group pairs: {len(delta_rows)}",
                f"- hotter/higher selectivity pairs: {direction_counts.get('hotter_or_higher_selectivity', 0)}",
                f"- cooler/lower selectivity pairs: {direction_counts.get('cooler_or_lower_selectivity', 0)}",
                f"- mixed pairs: {sum(count for key, count in direction_counts.items() if key.startswith('mixed'))}",
                "",
                "## 2025 位次带样本量",
                "",
                *[
                    f"- {band}: {band_2025.get(band, 0)}"
                    for band, _, _ in BANDS
                ],
                "",
                "## 边界",
                "",
                "- `rank_delta_2025_minus_2024 > 0` 表示最低位次数字变大，通常代表相对降温或门槛下降。",
                "- 当前 `plan_count_available_rows = 0`，所以本轮不能做计划数变化结论。",
                "- 专业组代码跨年沿用不必然代表专业组内专业构成完全一致，后续需要 plan_count/group structure source packet 补厚。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = eligible_rows()
    band_rows = build_band_coverage(rows)
    delta_rows = build_delta(rows)
    summary_rows = build_summary(rows, delta_rows)
    rollup = [
        {"metric": "eligible_group_year_rows", "value": len(rows)},
        {"metric": "rank_band_coverage_rows", "value": len(band_rows)},
        {"metric": "matched_2024_2025_group_delta_rows", "value": len(delta_rows)},
        {"metric": "plan_count_available_in_delta_rows", "value": 0},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(BAND_COVERAGE_OUT, band_rows, BAND_FIELDS)
    write_csv(DELTA_OUT, delta_rows, DELTA_FIELDS)
    write_csv(DELTA_SUMMARY_OUT, summary_rows, SUMMARY_FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(band_rows, delta_rows)
    print(f"eligible_rows={len(rows)}")
    print(f"matched_delta_rows={len(delta_rows)}")


if __name__ == "__main__":
    main()
