from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "engineering_tier",
    "pipeline_status",
    "operating_lane",
    "source_track",
    "latest_year",
    "reference_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "has_plan_source",
    "has_score_source",
    "readiness_band",
    "critical_gap_signature",
    "pre_ml_next_gate",
    "readiness_notes",
    "record_id",
    "source_slug",
]


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
    return str(value or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a conservative pre-ML readiness matrix for the 32-school Guangxi engineering pool."
    )
    parser.add_argument(
        "--board",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_master_operating_board_merged.csv",
        help="Master operating board CSV.",
    )
    parser.add_argument(
        "--source-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_official_source_pack_merged.csv",
        help="Official source pack CSV.",
    )
    parser.add_argument(
        "--field-gap-matrix",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_field_gap_matrix_merged.csv",
        help="Primary field gap matrix CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_model_readiness_merged.csv",
        help="Output readiness CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_model_readiness_school_summary.csv",
        help="School summary CSV output.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_model_readiness_coverage_rollup.csv",
        help="Coverage rollup CSV output.",
    )
    return parser


def derive_readiness(
    operating_lane: str,
    data_completeness: str,
    minimum_rank: str,
    trend_available: str,
    has_plan_source: str,
    has_score_source: str,
    blocker_class: str,
) -> tuple[str, str, str]:
    missing = []
    if data_completeness != "plan_and_score":
        missing.append("not_full_plan_and_score")
    if not minimum_rank:
        missing.append("missing_rank")
    if trend_available != "true":
        missing.append("missing_trend")
    if has_plan_source != "true":
        missing.append("missing_plan_source")
    if has_score_source != "true":
        missing.append("missing_score_source")

    if operating_lane == "A1_action_now" and not missing:
        return (
            "M1_ready_for_pre_ml_review",
            "gpt_review_before_ml",
            "已具备最新主口径、计划、分数、位次、趋势和官方来源，可在进入机器学习前先做人工/GPT 复核",
        )
    if operating_lane == "A2_action_with_note" and "missing_score_source" not in missing and "missing_rank" not in missing:
        return (
            "M2_comparable_ready_with_note",
            "review_note_then_gpt_review",
            "可比记录已可用，但需要明确备注非严格最新或存在轻微口径差异，再进入机器学习前复核",
        )
    if operating_lane.startswith("P"):
        return (
            "M4_blocked_or_manual_route",
            "stay_in_data_collection",
            "仍处于冷队列或人工路线，优先补官方入口、参数字典或稳定可比记录，不进入机器学习",
        )
    if blocker_class:
        return (
            "M3_fill_gaps_then_review",
            "fill_critical_gaps",
            "已进入主链但仍有关键字段缺口，先补最低位次/计划/趋势或来源，再考虑进入机器学习前复核",
        )
    return (
        "M3_fill_gaps_then_review",
        "fill_critical_gaps",
        "当前已有一定主链数据，但仍需补关键缺口后再进入机器学习前复核",
    )


def main() -> None:
    args = build_parser().parse_args()
    board_rows = read_rows(args.board)
    source_rows = read_rows(args.source_pack)
    gap_rows = read_rows(args.field_gap_matrix)

    source_by_key = {normalize_text(row.get("school_key", "")): row for row in source_rows}
    gap_by_key = {normalize_text(row.get("school_key", "")): row for row in gap_rows}

    merged_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    band_counts: dict[str, int] = {}

    for row in board_rows:
        school_key = normalize_text(row.get("school_key", ""))
        source = source_by_key.get(school_key, {})
        gap = gap_by_key.get(school_key, {})

        operating_lane = normalize_text(row.get("operating_lane", ""))
        data_completeness = normalize_text(row.get("data_completeness", ""))
        minimum_rank = normalize_text(row.get("minimum_rank", ""))
        trend_available = normalize_text(row.get("trend_available", ""))
        has_plan_source = normalize_text(source.get("has_plan_source", "false"))
        has_score_source = normalize_text(source.get("has_score_source", "false"))
        blocker_class = normalize_text(row.get("blocker_class", gap.get("blocker_class", "")))

        band, next_gate, notes = derive_readiness(
            operating_lane,
            data_completeness,
            minimum_rank,
            trend_available,
            has_plan_source,
            has_score_source,
            blocker_class,
        )
        band_counts[band] = band_counts.get(band, 0) + 1

        gap_signature = normalize_text(gap.get("gap_signature", ""))
        if not gap_signature:
            gap_signature = "none" if band.startswith("M1") else "implicit_gap"

        merged_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "operating_lane": operating_lane,
                "source_track": normalize_text(source.get("source_track", "")),
                "latest_year": normalize_text(row.get("latest_year", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "data_completeness": data_completeness,
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": minimum_rank,
                "trend_available": trend_available,
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "has_plan_source": has_plan_source,
                "has_score_source": has_score_source,
                "readiness_band": band,
                "critical_gap_signature": gap_signature,
                "pre_ml_next_gate": next_gate,
                "readiness_notes": notes,
                "record_id": f"{school_key}-pre-ml-model-readiness",
                "source_slug": "pre_ml_model_readiness",
            }
        )
        school_summary_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "pre_ml_model_readiness_rows": "1",
            }
        )

    merged_rows.sort(key=lambda item: (item["readiness_band"], item["engineering_tier"], item["school_key"]))
    school_summary_rows.sort(key=lambda item: item["school_key"])

    write_rows(args.output, merged_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "pre_ml_model_readiness_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "pre_ml_model_readiness_schools", "value": str(len(merged_rows))},
        {"metric": "pre_ml_model_readiness_coverage_ratio", "value": f"{len(merged_rows) / TARGET_TOTAL:.4f}"},
    ]
    for band, count in sorted(band_counts.items()):
        coverage_rows.append({"metric": f"{band}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML model readiness matrix for {len(merged_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
