from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build target-pool structured coverage metrics for engineering schools."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="Target-pool school matrix CSV.",
    )
    parser.add_argument(
        "--structured-summary",
        type=Path,
        default=Path("reports") / "engineering_structured_coverage_summary.csv",
        help="Structured coverage summary CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_structured_target_coverage.csv",
        help="Target-level coverage detail CSV.",
    )
    parser.add_argument(
        "--rollup-output",
        type=Path,
        default=Path("reports") / "engineering_structured_target_coverage_rollup.csv",
        help="Target-level coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    matrix_rows = read_rows(args.matrix)
    structured_rows = read_rows(args.structured_summary) if args.structured_summary.exists() else []
    structured_by_key = {row["school_key"]: row for row in structured_rows}

    output_rows: list[dict[str, str]] = []
    plan_count = 0
    score_count = 0
    for row in matrix_rows:
        key = row["seed_id"]
        structured = structured_by_key.get(key, {})
        has_plan = structured.get("has_structured_plan", "false")
        has_score = structured.get("has_structured_score", "false")
        if has_plan == "true":
            plan_count += 1
        if has_score == "true":
            score_count += 1
        output_rows.append(
            {
                "school_key": key,
                "school_name": row["source_name"],
                "engineering_tier": row["engineering_tier"],
                "has_structured_plan": has_plan,
                "has_structured_score": has_score,
                "total_structured_plan_rows": structured.get("total_structured_plan_rows", "0"),
                "api_score_major_rows": structured.get("api_score_major_rows", "0"),
                "structured_source_mix": structured.get("structured_source_mix", "none"),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    target_total = len(output_rows)
    rollup_rows = [
        {"metric": "target_pool_schools", "value": str(target_total)},
        {"metric": "structured_plan_schools", "value": str(plan_count)},
        {"metric": "structured_score_schools", "value": str(score_count)},
        {"metric": "structured_plan_coverage_ratio", "value": f"{(plan_count / target_total):.4f}" if target_total else "0.0000"},
        {"metric": "structured_score_coverage_ratio", "value": f"{(score_count / target_total):.4f}" if target_total else "0.0000"},
    ]
    with args.rollup_output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rollup_rows)

    print(
        f"Wrote target-pool structured coverage for {target_total} schools to {args.output}."
    )


if __name__ == "__main__":
    main()
