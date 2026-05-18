from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_TOTAL = 32
READY_BANDS = {"M1_ready_for_pre_ml_review", "M2_comparable_ready_with_note"}
FIELDS = [
    "school_key",
    "school_name",
    "readiness_band",
    "handoff_bucket",
    "engineering_tier",
    "pipeline_status",
    "operating_lane",
    "operating_priority",
    "review_priority",
    "actionability_band",
    "reference_year",
    "latest_year_available",
    "latest_year",
    "year_gap_from_latest",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "evidence_quality",
    "plan_source_resolution",
    "score_source_resolution",
    "resolution_status",
    "plan_source_url",
    "score_source_url",
    "next_action",
    "handoff_notes",
    "record_id",
    "source_record_id",
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
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def handoff_bucket(readiness_band: str) -> str:
    if readiness_band == "M1_ready_for_pre_ml_review":
        return "H1_ready_now"
    if readiness_band == "M2_comparable_ready_with_note":
        return "H2_ready_with_note"
    return "H9_out_of_scope"


def build_handoff_notes(
    readiness_band: str,
    profile_row: dict[str, str],
    signal_row: dict[str, str],
    resolution_row: dict[str, str],
) -> str:
    notes = []
    if readiness_band == "M2_comparable_ready_with_note":
        notes.append("使用最近可比记录而非严格最新记录")
    if normalize_text(profile_row.get("year_gap_from_latest", "")) not in {"", "0"}:
        notes.append(f"与最新年份相差 {normalize_text(profile_row.get('year_gap_from_latest', ''))} 年")
    if normalize_text(signal_row.get("trend_available", "")) != "true":
        notes.append("暂无真实趋势")
    resolution_status = normalize_text(resolution_row.get("resolution_status", ""))
    if resolution_status == "fallback_ready":
        notes.append("来源仍有 fallback 成分")
    elif resolution_status == "mixed_ready":
        notes.append("计划/分数来源精度不完全一致")
    if not notes:
        notes.append("已达到 pre-ML 复核前置要求")
    return "；".join(notes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a pre-ML handoff pack for M1/M2 Guangxi engineering schools."
    )
    parser.add_argument(
        "--readiness",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_model_readiness_merged.csv",
        help="Pre-ML readiness matrix CSV.",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_profile_merged.csv",
        help="Best comparable profile CSV.",
    )
    parser.add_argument(
        "--signal",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_signal_merged.csv",
        help="Best comparable signal CSV.",
    )
    parser.add_argument(
        "--board",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_master_operating_board_merged.csv",
        help="Master operating board CSV.",
    )
    parser.add_argument(
        "--resolution",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_source_resolution_matrix_merged.csv",
        help="Source resolution matrix CSV.",
    )
    parser.add_argument(
        "--evidence-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_actionable_evidence_pack_merged.csv",
        help="Actionable evidence pack CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_handoff_pack_merged.csv",
        help="Output handoff pack CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_handoff_pack_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_handoff_pack_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    readiness_rows = read_rows(args.readiness)
    profile_rows = read_rows(args.profile)
    signal_rows = read_rows(args.signal)
    board_rows = read_rows(args.board)
    resolution_rows = read_rows(args.resolution)
    evidence_rows = read_rows(args.evidence_pack)

    profile_by_key = {normalize_text(row.get("school_key", "")): row for row in profile_rows}
    signal_by_key = {normalize_text(row.get("school_key", "")): row for row in signal_rows}
    board_by_key = {normalize_text(row.get("school_key", "")): row for row in board_rows}
    resolution_by_key = {normalize_text(row.get("school_key", "")): row for row in resolution_rows}
    evidence_by_key = {normalize_text(row.get("school_key", "")): row for row in evidence_rows}

    handoff_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    m1_count = 0
    m2_count = 0
    with_plan_source = 0
    with_score_source = 0
    exact_ready = 0
    mixed_ready = 0
    fallback_ready = 0

    for ready_row in readiness_rows:
        school_key = normalize_text(ready_row.get("school_key", ""))
        band = normalize_text(ready_row.get("readiness_band", ""))
        if school_key == "" or band not in READY_BANDS:
            continue

        profile = profile_by_key.get(school_key, {})
        signal = signal_by_key.get(school_key, {})
        board = board_by_key.get(school_key, {})
        resolution = resolution_by_key.get(school_key, {})
        evidence = evidence_by_key.get(school_key, {})

        plan_source_url = normalize_text(
            profile.get("reference_plan_source_url", "")
            or evidence.get("plan_source_url", "")
            or board.get("plan_source_url", "")
        )
        score_source_url = normalize_text(
            profile.get("reference_score_source_url", "")
            or evidence.get("score_source_url", "")
            or board.get("score_source_url", "")
        )
        if band == "M1_ready_for_pre_ml_review":
            m1_count += 1
        elif band == "M2_comparable_ready_with_note":
            m2_count += 1
        if plan_source_url:
            with_plan_source += 1
        if score_source_url:
            with_score_source += 1
        resolution_status = normalize_text(resolution.get("resolution_status", ""))
        if resolution_status == "exact_ready":
            exact_ready += 1
        elif resolution_status == "mixed_ready":
            mixed_ready += 1
        elif resolution_status == "fallback_ready":
            fallback_ready += 1

        handoff_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(ready_row.get("school_name", school_key)),
                "readiness_band": band,
                "handoff_bucket": handoff_bucket(band),
                "engineering_tier": normalize_text(ready_row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(ready_row.get("pipeline_status", "")),
                "operating_lane": normalize_text(board.get("operating_lane", ready_row.get("operating_lane", ""))),
                "operating_priority": normalize_text(board.get("operating_priority", "")),
                "review_priority": normalize_text(signal.get("review_priority", "")),
                "actionability_band": normalize_text(evidence.get("actionability_band", "")),
                "reference_year": normalize_text(profile.get("reference_year", ready_row.get("reference_year", ""))),
                "latest_year_available": normalize_text(profile.get("latest_year_available", "")),
                "latest_year": normalize_text(board.get("latest_year", ready_row.get("latest_year", ""))),
                "year_gap_from_latest": normalize_text(profile.get("year_gap_from_latest", "")),
                "data_completeness": normalize_text(
                    profile.get("reference_data_completeness", ready_row.get("data_completeness", ""))
                ),
                "total_plan_count": normalize_text(
                    profile.get("reference_total_plan_count", ready_row.get("total_plan_count", ""))
                ),
                "minimum_score": normalize_text(
                    profile.get("reference_minimum_score", ready_row.get("minimum_score", ""))
                ),
                "minimum_rank": normalize_text(
                    profile.get("reference_minimum_rank", ready_row.get("minimum_rank", ""))
                ),
                "trend_available": normalize_text(profile.get("trend_available", ready_row.get("trend_available", ""))),
                "trend_signal": normalize_text(signal.get("trend_signal", ready_row.get("trend_signal", ""))),
                "evidence_quality": normalize_text(signal.get("evidence_quality", "")),
                "plan_source_resolution": normalize_text(resolution.get("plan_source_resolution", "")),
                "score_source_resolution": normalize_text(resolution.get("score_source_resolution", "")),
                "resolution_status": resolution_status,
                "plan_source_url": plan_source_url,
                "score_source_url": score_source_url,
                "next_action": normalize_text(board.get("next_action", ready_row.get("pre_ml_next_gate", ""))),
                "handoff_notes": build_handoff_notes(band, profile, signal, resolution),
                "record_id": f"{school_key}-pre-ml-handoff",
                "source_record_id": normalize_text(ready_row.get("record_id", "")),
                "source_slug": "pre_ml_handoff_pack",
            }
        )
        school_summary_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(ready_row.get("school_name", school_key)),
                "pre_ml_handoff_pack_rows": "1",
            }
        )

    handoff_rows.sort(key=lambda item: (item["handoff_bucket"], item["engineering_tier"], item["school_key"]))
    school_summary_rows.sort(key=lambda item: item["school_key"])

    write_rows(args.output, handoff_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "pre_ml_handoff_pack_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "pre_ml_handoff_pack_schools", "value": str(len(handoff_rows))},
        {"metric": "pre_ml_handoff_pack_coverage_ratio", "value": f"{len(handoff_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "pre_ml_handoff_pack_M1_schools", "value": str(m1_count)},
        {"metric": "pre_ml_handoff_pack_M2_schools", "value": str(m2_count)},
        {"metric": "pre_ml_handoff_pack_with_plan_source_schools", "value": str(with_plan_source)},
        {"metric": "pre_ml_handoff_pack_with_score_source_schools", "value": str(with_score_source)},
        {"metric": "pre_ml_handoff_pack_exact_ready_schools", "value": str(exact_ready)},
        {"metric": "pre_ml_handoff_pack_mixed_ready_schools", "value": str(mixed_ready)},
        {"metric": "pre_ml_handoff_pack_fallback_ready_schools", "value": str(fallback_ready)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(
        f"Wrote pre-ML handoff pack for {len(handoff_rows)} schools "
        f"({m1_count} M1, {m2_count} M2) to {args.output}."
    )


if __name__ == "__main__":
    main()
