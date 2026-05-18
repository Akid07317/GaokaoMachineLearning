from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "readiness_band",
    "handoff_bucket",
    "review_lane",
    "review_risk_score",
    "review_focus_flags",
    "engineering_tier",
    "pipeline_status",
    "operating_lane",
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
    "gap_count",
    "gap_signature",
    "blocker_class",
    "plan_source_url",
    "score_source_url",
    "pre_ml_gate",
    "review_prompt",
    "review_notes",
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


def parse_int(value: str) -> int:
    text = normalize_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def derive_focus_flags(
    row: dict[str, str],
    gap_row: dict[str, str],
) -> list[str]:
    flags: list[str] = []
    readiness_band = normalize_text(row.get("readiness_band", ""))
    data_completeness = normalize_text(row.get("data_completeness", ""))
    resolution_status = normalize_text(row.get("resolution_status", ""))
    trend_available = normalize_text(row.get("trend_available", ""))
    year_gap = parse_int(row.get("year_gap_from_latest", ""))
    gap_signature = normalize_text(gap_row.get("gap_signature", ""))
    blocker_class = normalize_text(gap_row.get("blocker_class", ""))

    if readiness_band == "M2_comparable_ready_with_note":
        flags.append("comparable_note_required")
    if year_gap > 0:
        flags.append("reference_year_not_latest")
    if data_completeness != "plan_and_score":
        flags.append("score_only_or_partial_plan")
    if trend_available != "true":
        flags.append("trend_missing_or_unverified")
    if resolution_status == "mixed_ready":
        flags.append("mixed_source_resolution")
    elif resolution_status == "fallback_ready":
        flags.append("fallback_source_resolution")
    if gap_signature and gap_signature != "complete_enough":
        flags.append(gap_signature)
    if blocker_class and blocker_class != "none":
        flags.append(f"blocker:{blocker_class}")
    return flags or ["clean_pre_ml_review"]


def derive_risk_score(row: dict[str, str], gap_row: dict[str, str], flags: list[str]) -> int:
    score = 0
    if normalize_text(row.get("readiness_band", "")) == "M2_comparable_ready_with_note":
        score += 1
    if parse_int(row.get("year_gap_from_latest", "")) > 0:
        score += 1
    if normalize_text(row.get("data_completeness", "")) != "plan_and_score":
        score += 1
    if normalize_text(row.get("trend_available", "")) != "true":
        score += 1

    resolution_status = normalize_text(row.get("resolution_status", ""))
    if resolution_status == "mixed_ready":
        score += 1
    elif resolution_status == "fallback_ready":
        score += 2

    gap_signature = normalize_text(gap_row.get("gap_signature", ""))
    if gap_signature and gap_signature != "complete_enough":
        score += max(parse_int(gap_row.get("gap_count", "")), 1)
    if normalize_text(gap_row.get("blocker_class", "")) not in {"", "none"}:
        score += 1
    if "clean_pre_ml_review" in flags:
        return 0
    return score


def derive_review_lane(risk_score: int) -> str:
    if risk_score == 0:
        return "R1_clean_ready"
    if risk_score <= 2:
        return "R2_light_note_review"
    if risk_score <= 4:
        return "R3_caution_review"
    return "R4_high_caution_review"


def build_review_prompt(row: dict[str, str], flags: list[str]) -> str:
    if flags == ["clean_pre_ml_review"]:
        return "核对学校名、年份、计划数、最低分/位次和官方来源后，可进入人工/GPT 复核闸门。"
    prompt_parts = []
    if "comparable_note_required" in flags:
        prompt_parts.append("明确标注该校使用可比记录而非无备注直入模型")
    if "reference_year_not_latest" in flags:
        prompt_parts.append("核对参考年份与最新可用年份差异")
    if "score_only_or_partial_plan" in flags:
        prompt_parts.append("确认计划侧缺口不会被误当作完整计划")
    if "trend_missing_or_unverified" in flags:
        prompt_parts.append("趋势不可用时只保留静态信号")
    if "mixed_source_resolution" in flags or "fallback_source_resolution" in flags:
        prompt_parts.append("复查计划/分数来源精度与回链")
    if any(flag.startswith("missing_") or "|missing_" in flag for flag in flags):
        prompt_parts.append("按字段缺口矩阵复核缺字段")
    return "；".join(prompt_parts) or "按 review_focus_flags 逐项复核。"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a compact pre-ML human review workbench from local handoff artifacts."
    )
    parser.add_argument(
        "--handoff-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_handoff_pack_merged.csv",
        help="Pre-ML handoff pack CSV.",
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
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_workbench_merged.csv",
        help="Output pre-ML review workbench CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_workbench_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_workbench_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    handoff_rows = read_rows(args.handoff_pack)
    gap_rows = read_rows(args.field_gap_matrix)
    gap_by_key = {normalize_text(row.get("school_key", "")): row for row in gap_rows}

    workbench_rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    readiness_counts: Counter[str] = Counter()
    resolution_counts: Counter[str] = Counter()

    for row in handoff_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        gap_row = gap_by_key.get(school_key, {})
        flags = derive_focus_flags(row, gap_row)
        risk_score = derive_risk_score(row, gap_row, flags)
        review_lane = derive_review_lane(risk_score)

        lane_counts[review_lane] += 1
        readiness_counts[normalize_text(row.get("readiness_band", ""))] += 1
        resolution_counts[normalize_text(row.get("resolution_status", ""))] += 1

        workbench_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "readiness_band": normalize_text(row.get("readiness_band", "")),
                "handoff_bucket": normalize_text(row.get("handoff_bucket", "")),
                "review_lane": review_lane,
                "review_risk_score": str(risk_score),
                "review_focus_flags": "|".join(flags),
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "operating_lane": normalize_text(row.get("operating_lane", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "latest_year_available": normalize_text(row.get("latest_year_available", "")),
                "latest_year": normalize_text(row.get("latest_year", "")),
                "year_gap_from_latest": normalize_text(row.get("year_gap_from_latest", "")),
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "evidence_quality": normalize_text(row.get("evidence_quality", "")),
                "plan_source_resolution": normalize_text(row.get("plan_source_resolution", "")),
                "score_source_resolution": normalize_text(row.get("score_source_resolution", "")),
                "resolution_status": normalize_text(row.get("resolution_status", "")),
                "gap_count": normalize_text(gap_row.get("gap_count", "")),
                "gap_signature": normalize_text(gap_row.get("gap_signature", "")),
                "blocker_class": normalize_text(gap_row.get("blocker_class", "")),
                "plan_source_url": normalize_text(row.get("plan_source_url", "")),
                "score_source_url": normalize_text(row.get("score_source_url", "")),
                "pre_ml_gate": "human_or_gpt_review_before_ml",
                "review_prompt": build_review_prompt(row, flags),
                "review_notes": normalize_text(row.get("handoff_notes", "")),
                "record_id": f"{school_key}-pre-ml-review-workbench",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "pre_ml_review_workbench",
            }
        )

    workbench_rows.sort(
        key=lambda item: (
            item["review_lane"],
            parse_int(item["review_risk_score"]),
            item["readiness_band"],
            item["school_key"],
        )
    )
    write_rows(args.output, workbench_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "review_lane": row["review_lane"],
            "review_risk_score": row["review_risk_score"],
            "readiness_band": row["readiness_band"],
            "resolution_status": row["resolution_status"],
            "review_focus_flags": row["review_focus_flags"],
        }
        for row in workbench_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "review_lane",
            "review_risk_score",
            "readiness_band",
            "resolution_status",
            "review_focus_flags",
        ],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "pre_ml_review_workbench_schools", "value": str(len(workbench_rows))},
        {"metric": "pre_ml_review_workbench_coverage_ratio", "value": f"{len(workbench_rows) / TARGET_TOTAL:.4f}"},
    ]
    for band, count in sorted(readiness_counts.items()):
        coverage_rows.append({"metric": f"{band}_schools", "value": str(count)})
    for lane, count in sorted(lane_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    for status, count in sorted(resolution_counts.items()):
        coverage_rows.append({"metric": f"{status}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(
        "Wrote pre-ML review workbench for "
        f"{len(workbench_rows)} schools to {args.output}."
    )


if __name__ == "__main__":
    main()
