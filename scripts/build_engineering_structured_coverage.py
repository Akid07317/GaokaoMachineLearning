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
        description="Build a merged structured-coverage summary for engineering target schools."
    )
    parser.add_argument(
        "--api-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_seed_school_summary.csv",
        help="School summary from API-derived Guangxi seeds.",
    )
    parser.add_argument(
        "--bjut-pdf-rows",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_guangxi_plan_rows.csv",
        help="Structured Guangxi rows extracted from BJUT cached PDFs.",
    )
    parser.add_argument(
        "--hebut-pdf-rows",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "hebei_gongye_guangxi_plan_rows.csv",
        help="Structured Guangxi rows extracted from Hebut cached PDF.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_structured_coverage_summary.csv",
        help="Output structured coverage summary CSV.",
    )
    parser.add_argument(
        "--rollup-output",
        type=Path,
        default=Path("reports") / "engineering_structured_coverage_rollup.csv",
        help="Output rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    api_rows = read_rows(args.api_summary) if args.api_summary.exists() else []
    bjut_rows = read_rows(args.bjut_pdf_rows) if args.bjut_pdf_rows.exists() else []
    hebut_rows = read_rows(args.hebut_pdf_rows) if args.hebut_pdf_rows.exists() else []

    merged: dict[str, dict[str, str | int]] = {}
    for row in api_rows:
        merged[row["school_key"]] = {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "api_plan_rows": int(row.get("plan_rows", "0") or 0),
            "api_score_major_rows": int(row.get("score_major_rows", "0") or 0),
            "pdf_plan_rows": 0,
            "pdf_plan_years": "",
        }

    if bjut_rows:
        years = sorted({row["plan_year"] for row in bjut_rows if row.get("plan_year")})
        key = "beijing_gongye_211"
        if key not in merged:
            merged[key] = {
                "school_key": key,
                "school_name": "北京工业大学",
                "api_plan_rows": 0,
                "api_score_major_rows": 0,
                "pdf_plan_rows": 0,
                "pdf_plan_years": "",
            }
        merged[key]["pdf_plan_rows"] = len(bjut_rows)
        merged[key]["pdf_plan_years"] = "|".join(years)

    if hebut_rows:
        years = sorted({row["plan_year"] for row in hebut_rows if row.get("plan_year")})
        key = "hebei_gongye_211"
        if key not in merged:
            merged[key] = {
                "school_key": key,
                "school_name": "河北工业大学",
                "api_plan_rows": 0,
                "api_score_major_rows": 0,
                "pdf_plan_rows": 0,
                "pdf_plan_years": "",
            }
        merged[key]["pdf_plan_rows"] = len(hebut_rows)
        merged[key]["pdf_plan_years"] = "|".join(years)

    output_rows: list[dict[str, str | int]] = []
    for row in merged.values():
        api_plan_rows = int(row["api_plan_rows"])
        api_score_major_rows = int(row["api_score_major_rows"])
        pdf_plan_rows = int(row["pdf_plan_rows"])
        output_rows.append(
            {
                "school_key": row["school_key"],
                "school_name": row["school_name"],
                "api_plan_rows": api_plan_rows,
                "api_score_major_rows": api_score_major_rows,
                "pdf_plan_rows": pdf_plan_rows,
                "pdf_plan_years": row["pdf_plan_years"],
                "total_structured_plan_rows": api_plan_rows + pdf_plan_rows,
                "has_structured_plan": str((api_plan_rows + pdf_plan_rows) > 0).lower(),
                "has_structured_score": str(api_score_major_rows > 0).lower(),
                "structured_source_mix": (
                    "api+pdf"
                    if api_plan_rows > 0 and pdf_plan_rows > 0
                    else "api"
                    if api_plan_rows > 0 or api_score_major_rows > 0
                    else "pdf"
                    if pdf_plan_rows > 0
                    else "none"
                ),
            }
        )

    output_rows.sort(key=lambda row: (-int(row["total_structured_plan_rows"]), row["school_name"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    plan_only_count = sum(1 for row in output_rows if row["has_structured_plan"] == "true")
    score_count = sum(1 for row in output_rows if row["has_structured_score"] == "true")
    mix_counts = defaultdict(int)
    for row in output_rows:
        mix_counts[str(row["structured_source_mix"])] += 1
    rollup_rows = [
        {"metric": "schools_with_structured_plan", "value": plan_only_count},
        {"metric": "schools_with_structured_score", "value": score_count},
        {"metric": "schools_total_in_summary", "value": len(output_rows)},
        {"metric": "source_mix_api", "value": mix_counts["api"]},
        {"metric": "source_mix_pdf", "value": mix_counts["pdf"]},
        {"metric": "source_mix_api+pdf", "value": mix_counts["api+pdf"]},
    ]
    with args.rollup_output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rollup_rows)

    print(
        f"Wrote structured coverage summary for {len(output_rows)} schools to {args.output}."
    )


if __name__ == "__main__":
    main()
