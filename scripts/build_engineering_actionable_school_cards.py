from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "engineering_tier",
    "actionability_band",
    "queue_source",
    "pipeline_status",
    "reference_year",
    "latest_year_available",
    "year_gap_from_latest",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_from_year",
    "trend_to_year",
    "trend_signal",
    "evidence_quality",
    "recommended_next_action",
    "card_notes",
    "record_id",
    "source_record_id",
    "source_slug",
]

TARGET_TOTAL = 32


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build actionable Guangxi admissions school cards from unified review operating queue."
    )
    parser.add_argument(
        "--unified-queue",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_unified_review_operating_queue_merged.csv",
        help="Unified review operating queue CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_actionable_school_cards_merged.csv",
        help="Actionable school cards output CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_actionable_school_cards_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_actionable_school_cards_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    queue_rows = read_rows(args.unified_queue)

    actionable_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    a1_count = 0
    a2_count = 0

    for row in queue_rows:
        band = normalize_text(row.get("actionability_band", ""))
        if band not in {"A1_action_now", "A2_action_with_note"}:
            continue
        if band == "A1_action_now":
            a1_count += 1
        if band == "A2_action_with_note":
            a2_count += 1

        school_key = normalize_text(row.get("school_key", ""))
        latest_year = normalize_text(row.get("latest_year_available", ""))
        reference_year = normalize_text(row.get("reference_year", ""))
        actionable_rows.append(
            {
                "school_name": normalize_text(row.get("school_name", "")),
                "school_key": school_key,
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "actionability_band": band,
                "queue_source": normalize_text(row.get("queue_source", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "reference_year": reference_year,
                "latest_year_available": latest_year,
                "year_gap_from_latest": str(max((int(latest_year) if latest_year else 0) - (int(reference_year) if reference_year else 0), 0)) if latest_year and reference_year else "",
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "trend_from_year": normalize_text(row.get("trend_from_year", "")),
                "trend_to_year": normalize_text(row.get("trend_to_year", "")),
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "evidence_quality": normalize_text(row.get("evidence_quality", "")),
                "recommended_next_action": normalize_text(row.get("recommended_next_action", "")),
                "card_notes": "行动学校卡由统一预审操作队列派生，只保留当前可直接预审或带备注可预审的学校，方便继续补数和人工核对",
                "record_id": f"{school_key}-actionable-school-card-{reference_year or latest_year}",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "official_actionable_school_card",
            }
        )
        school_counter[school_key] += 1

    actionable_rows.sort(key=lambda item: (item["actionability_band"], item["engineering_tier"], item["school_key"]))
    write_rows(args.output, actionable_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in actionable_rows if row["school_key"] == school_key), ""),
            "actionable_school_card_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "actionable_school_card_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "actionable_school_card_schools", "value": str(len(school_counter))},
        {"metric": "actionable_school_card_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "actionable_school_card_a1_schools", "value": str(a1_count)},
        {"metric": "actionable_school_card_a2_schools", "value": str(a2_count)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote actionable school cards for "
        f"{len(school_counter)} schools ({a1_count} A1, {a2_count} A2)."
    )


if __name__ == "__main__":
    main()
