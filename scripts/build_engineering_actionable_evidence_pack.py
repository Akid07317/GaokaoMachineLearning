from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "actionability_band",
    "queue_source",
    "engineering_tier",
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
    "plan_source_url",
    "score_source_url",
    "profile_source_record_id",
    "trend_source_record_id",
    "recommended_next_action",
    "evidence_pack_notes",
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


def read_registry(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    registry: dict[str, dict[str, str]] = {}
    for row in rows:
        school_key = normalize_text(row.get("school_key", ""))
        if school_key:
            registry[school_key] = row
    return registry


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
        description="Build actionable evidence pack with source URLs for Guangxi target schools."
    )
    parser.add_argument(
        "--actionable-cards",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_actionable_school_cards_merged.csv",
        help="Actionable school cards CSV.",
    )
    parser.add_argument(
        "--latest-profile",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_profile_merged.csv",
        help="Latest profile CSV.",
    )
    parser.add_argument(
        "--best-comparable-profile",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_profile_merged.csv",
        help="Best comparable profile CSV.",
    )
    parser.add_argument(
        "--canonical-snapshot",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_canonical_snapshot_merged.csv",
        help="Canonical snapshot CSV.",
    )
    parser.add_argument(
        "--source-registry",
        type=Path,
        default=Path("configs") / "actionable_source_fallback_registry.csv",
        help="Fallback registry for actionable evidence plan/score source URLs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_actionable_evidence_pack_merged.csv",
        help="Evidence pack output CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_actionable_evidence_pack_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_actionable_evidence_pack_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    card_rows = read_rows(args.actionable_cards)
    latest_profile_rows = read_rows(args.latest_profile)
    best_profile_rows = read_rows(args.best_comparable_profile)
    canonical_rows = read_rows(args.canonical_snapshot)
    source_registry = read_registry(args.source_registry)

    latest_profile_by_key = {normalize_text(row.get("school_key", "")): row for row in latest_profile_rows}
    best_profile_by_key = {normalize_text(row.get("school_key", "")): row for row in best_profile_rows}
    canonical_by_record = {normalize_text(row.get("record_id", "")): row for row in canonical_rows}

    evidence_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    a1_count = 0
    a2_count = 0

    for row in card_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        band = normalize_text(row.get("actionability_band", ""))
        if band == "A1_action_now":
            a1_count += 1
        elif band == "A2_action_with_note":
            a2_count += 1

        if normalize_text(row.get("queue_source", "")) == "strict_queue":
            profile = latest_profile_by_key.get(school_key, {})
            plan_source_url = normalize_text(profile.get("latest_plan_source_url", ""))
            score_source_url = normalize_text(profile.get("latest_score_source_url", ""))
            profile_source_record_id = normalize_text(profile.get("latest_source_record_id", ""))
            trend_source_record_id = normalize_text(profile.get("trend_source_record_id", ""))
        else:
            profile = best_profile_by_key.get(school_key, {})
            profile_source_record_id = normalize_text(profile.get("reference_source_record_id", ""))
            trend_source_record_id = normalize_text(profile.get("trend_source_record_id", ""))
            canonical = canonical_by_record.get(profile_source_record_id, {})
            plan_source_url = normalize_text(canonical.get("plan_source_url", ""))
            score_source_url = normalize_text(canonical.get("score_source_url", ""))

        registry_row = source_registry.get(school_key, {})
        if not plan_source_url:
            plan_source_url = normalize_text(registry_row.get("plan_source_url", ""))
        if not score_source_url:
            score_source_url = normalize_text(registry_row.get("score_source_url", ""))

        evidence_rows.append(
            {
                "school_name": normalize_text(row.get("school_name", "")),
                "school_key": school_key,
                "actionability_band": band,
                "queue_source": normalize_text(row.get("queue_source", "")),
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "latest_year_available": normalize_text(row.get("latest_year_available", "")),
                "year_gap_from_latest": normalize_text(row.get("year_gap_from_latest", "")),
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "trend_from_year": normalize_text(row.get("trend_from_year", "")),
                "trend_to_year": normalize_text(row.get("trend_to_year", "")),
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "evidence_quality": normalize_text(row.get("evidence_quality", "")),
                "plan_source_url": plan_source_url,
                "score_source_url": score_source_url,
                "profile_source_record_id": profile_source_record_id,
                "trend_source_record_id": trend_source_record_id,
                "recommended_next_action": normalize_text(row.get("recommended_next_action", "")),
                "evidence_pack_notes": "行动证据包由行动学校卡与主口径画像回连得到，用于快速打开官方计划/分数来源并核对当前可行动学校",
                "record_id": f"{school_key}-actionable-evidence-pack-{normalize_text(row.get('reference_year', ''))}",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "official_actionable_evidence_pack",
            }
        )
        school_counter[school_key] += 1

    evidence_rows.sort(key=lambda item: (item["actionability_band"], item["engineering_tier"], item["school_key"]))
    write_rows(args.output, evidence_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in evidence_rows if row["school_key"] == school_key), ""),
            "actionable_evidence_pack_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "actionable_evidence_pack_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "actionable_evidence_pack_schools", "value": str(len(school_counter))},
        {"metric": "actionable_evidence_pack_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "actionable_evidence_pack_a1_schools", "value": str(a1_count)},
        {"metric": "actionable_evidence_pack_a2_schools", "value": str(a2_count)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote actionable evidence pack for "
        f"{len(school_counter)} schools ({a1_count} A1, {a2_count} A2)."
    )


if __name__ == "__main__":
    main()
