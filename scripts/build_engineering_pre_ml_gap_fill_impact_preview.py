from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "current_gate_status",
    "current_readiness_band",
    "current_gap_signature",
    "current_data_completeness",
    "current_latest_year",
    "current_minimum_score",
    "current_minimum_rank",
    "candidate_year",
    "candidate_minimum_score",
    "candidate_minimum_rank",
    "candidate_group_count",
    "candidate_group_codes",
    "candidate_fill_fields",
    "preview_data_completeness",
    "preview_latest_year",
    "preview_minimum_score",
    "preview_minimum_rank",
    "preview_gap_signature",
    "preview_gate_status",
    "preview_readiness_band",
    "promotion_lane",
    "manual_acceptance_required",
    "impact_notes",
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


def split_flags(value: str) -> set[str]:
    return {flag for flag in normalize_text(value).split("|") if flag}


def join_flags(flags: set[str]) -> str:
    if not flags:
        return "complete_enough"
    order = [
        "missing_plan",
        "missing_score",
        "missing_rank",
        "missing_trend",
        "not_fresh_2025",
        "missing_latest_snapshot",
    ]
    return "|".join([flag for flag in order if flag in flags] + sorted(flags - set(order)))


def preview_gap_signature(current_gap_signature: str, candidate_fill_fields: str) -> str:
    gaps = split_flags(current_gap_signature)
    fills = split_flags(candidate_fill_fields)
    if "minimum_score" in fills:
        gaps.discard("missing_score")
    if "minimum_rank" in fills:
        gaps.discard("missing_rank")
    if "latest_year" in fills:
        gaps.discard("not_fresh_2025")
    if "trend_seed_possible_from_2024_2025_admission_lines" in fills:
        gaps.discard("missing_trend")
    return join_flags(gaps)


def preview_data_completeness(current_data_completeness: str, preview_gap: str) -> str:
    current = normalize_text(current_data_completeness)
    gaps = split_flags(preview_gap)
    if "missing_plan" not in gaps and "missing_score" not in gaps and "missing_rank" not in gaps:
        return "plan_and_score"
    if current == "plan_only" and "missing_score" not in gaps and "missing_rank" not in gaps:
        return "plan_and_score"
    if current == "score_only" and "missing_rank" not in gaps:
        return "score_only_with_rank_candidate"
    return current


def preview_status(preview_gap: str, preview_completeness: str) -> tuple[str, str, str]:
    gaps = split_flags(preview_gap)
    completeness = normalize_text(preview_completeness)
    if preview_gap == "complete_enough" and completeness == "plan_and_score":
        return (
            "G1_ready_for_human_gpt_review_gate_candidate",
            "M1_ready_for_pre_ml_review_candidate",
            "P1_candidate_promote_after_manual_acceptance",
        )
    if "missing_plan" in gaps and "missing_rank" not in gaps:
        return (
            "G2_ready_with_caution_for_review_gate_candidate",
            "M2_comparable_ready_with_note_candidate",
            "P2_candidate_review_with_plan_gap_note",
        )
    return (
        "G3_local_gap_fill_still_needed",
        "M3_fill_gaps_then_review",
        "P3_still_needs_local_gap_work",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview the impact of local gap-fill candidates without changing canonical readiness tables."
    )
    parser.add_argument(
        "--gate-status",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gate_status_merged.csv",
        help="Current pre-ML gate status CSV.",
    )
    parser.add_argument(
        "--local-gap-fill-candidates",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_local_gap_fill_candidates_merged.csv",
        help="Local gap-fill candidate CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_gap_fill_impact_preview_merged.csv",
        help="Output impact preview CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_gap_fill_impact_preview_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_gap_fill_impact_preview_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    gate_rows = read_rows(args.gate_status)
    candidate_rows = read_rows(args.local_gap_fill_candidates)

    gate_by_key = {normalize_text(row.get("school_key", "")): row for row in gate_rows}
    output_rows: list[dict[str, str]] = []
    promotion_counts: Counter[str] = Counter()
    preview_gate_counts: Counter[str] = Counter()

    for candidate in candidate_rows:
        school_key = normalize_text(candidate.get("school_key", ""))
        gate = gate_by_key.get(school_key, {})
        current_gap = normalize_text(gate.get("gap_signature", candidate.get("missing_field_flags", "")))
        fill_fields = normalize_text(candidate.get("candidate_fill_fields", ""))
        next_gap = preview_gap_signature(current_gap, fill_fields)
        next_completeness = preview_data_completeness(
            gate.get("data_completeness", candidate.get("current_data_completeness", "")),
            next_gap,
        )
        next_gate, next_readiness, promotion_lane = preview_status(next_gap, next_completeness)
        promotion_counts[promotion_lane] += 1
        preview_gate_counts[next_gate] += 1

        preview_latest_year = normalize_text(candidate.get("candidate_year", "")) or normalize_text(
            gate.get("latest_year", "")
        )
        preview_minimum_score = normalize_text(candidate.get("candidate_minimum_score", "")) or normalize_text(
            gate.get("minimum_score", "")
        )
        preview_minimum_rank = normalize_text(candidate.get("candidate_minimum_rank", "")) or normalize_text(
            gate.get("minimum_rank", "")
        )

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(candidate.get("school_name", school_key)),
                "current_gate_status": normalize_text(gate.get("gate_status", "")),
                "current_readiness_band": normalize_text(gate.get("readiness_band", "")),
                "current_gap_signature": current_gap,
                "current_data_completeness": normalize_text(gate.get("data_completeness", "")),
                "current_latest_year": normalize_text(gate.get("latest_year", "")),
                "current_minimum_score": normalize_text(gate.get("minimum_score", "")),
                "current_minimum_rank": normalize_text(gate.get("minimum_rank", "")),
                "candidate_year": normalize_text(candidate.get("candidate_year", "")),
                "candidate_minimum_score": normalize_text(candidate.get("candidate_minimum_score", "")),
                "candidate_minimum_rank": normalize_text(candidate.get("candidate_minimum_rank", "")),
                "candidate_group_count": normalize_text(candidate.get("candidate_group_count", "")),
                "candidate_group_codes": normalize_text(candidate.get("candidate_group_codes", "")),
                "candidate_fill_fields": fill_fields,
                "preview_data_completeness": next_completeness,
                "preview_latest_year": preview_latest_year,
                "preview_minimum_score": preview_minimum_score,
                "preview_minimum_rank": preview_minimum_rank,
                "preview_gap_signature": next_gap,
                "preview_gate_status": next_gate,
                "preview_readiness_band": next_readiness,
                "promotion_lane": promotion_lane,
                "manual_acceptance_required": "true",
                "impact_notes": (
                    "仅为本地补洞影响预览，不改写 readiness、handoff、workbench 或 ML 输入；"
                    "人工确认候选口径后再决定是否生成正式补洞层。"
                ),
                "record_id": f"{school_key}-pre-ml-gap-fill-impact-preview",
                "source_record_id": normalize_text(candidate.get("record_id", "")),
                "source_slug": "pre_ml_gap_fill_impact_preview",
            }
        )

    output_rows.sort(key=lambda row: (row["promotion_lane"], row["school_key"]))
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "preview_gate_status": row["preview_gate_status"],
            "preview_readiness_band": row["preview_readiness_band"],
            "preview_gap_signature": row["preview_gap_signature"],
            "promotion_lane": row["promotion_lane"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "preview_gate_status",
            "preview_readiness_band",
            "preview_gap_signature",
            "promotion_lane",
        ],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "gap_fill_impact_preview_schools", "value": str(len(output_rows))},
        {"metric": "gap_fill_impact_preview_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
    ]
    for lane, count in sorted(promotion_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    for status, count in sorted(preview_gate_counts.items()):
        coverage_rows.append({"metric": f"{status}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote gap-fill impact preview for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
