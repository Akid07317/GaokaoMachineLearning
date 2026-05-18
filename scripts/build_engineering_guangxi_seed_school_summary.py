from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build school-level Guangxi seed summary from merged plan and score tables."
    )
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
        help="Merged Guangxi physics plan seed CSV.",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics major-score seed CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_seed_school_summary.csv",
        help="School-level summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows = read_rows(args.plan_merged) if args.plan_merged.exists() else []
    score_rows = read_rows(args.score_major_merged) if args.score_major_merged.exists() else []

    summary: dict[str, dict[str, str | int]] = defaultdict(
        lambda: {"school_name": "", "plan_rows": 0, "score_major_rows": 0}
    )

    for row in plan_rows:
        key = row.get("school_key", "")
        if row.get("school_name"):
            summary[key]["school_name"] = row["school_name"]
        summary[key]["plan_rows"] = int(summary[key]["plan_rows"]) + 1

    for row in score_rows:
        key = row.get("school_key", "")
        if row.get("school_name") and not summary[key]["school_name"]:
            summary[key]["school_name"] = row["school_name"]
        summary[key]["score_major_rows"] = int(summary[key]["score_major_rows"]) + 1

    output_rows = []
    for school_key, counts in summary.items():
        output_rows.append(
            {
                "school_key": school_key,
                "school_name": str(counts["school_name"]),
                "plan_rows": str(counts["plan_rows"]),
                "score_major_rows": str(counts["score_major_rows"]),
            }
        )

    output_rows.sort(key=lambda row: (-int(row["plan_rows"]), row["school_name"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["school_key", "school_name", "plan_rows", "score_major_rows"],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote Guangxi seed school summary for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
