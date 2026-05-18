from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


TARGET_TOTAL = 32
INFERENCE_MARKER = "最低位次=按同年广西物理类一分一档保守换算(rank_end)"


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
        .strip()
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build school-level coverage for Guangxi score-summary rank inference rows."
    )
    parser.add_argument(
        "--score-summary",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_summary_seed_merged.csv",
        help="Merged Guangxi score-summary seed CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_score_summary_rank_enrichment_merged.csv",
        help="Per-row rank enrichment extraction output CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_score_summary_rank_enrichment_school_summary.csv",
        help="School-level rank enrichment summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_score_summary_rank_enrichment_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.score_summary)

    enriched_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    school_names: dict[str, str] = {}
    years_by_school: defaultdict[str, set[str]] = defaultdict(set)
    types_by_school: defaultdict[str, set[str]] = defaultdict(set)

    for row in rows:
        remarks = normalize_text(row.get("remarks"))
        if INFERENCE_MARKER not in remarks:
            continue
        enriched_rows.append(row)
        school_key = normalize_text(row.get("school_key"))
        school_counter[school_key] += 1
        school_names[school_key] = normalize_text(row.get("school_name"))
        if normalize_text(row.get("year")):
            years_by_school[school_key].add(normalize_text(row.get("year")))
        if normalize_text(row.get("type")):
            types_by_school[school_key].add(normalize_text(row.get("type")))

    enriched_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("record_id", "")))
    if enriched_rows:
        write_rows(args.output, enriched_rows, list(enriched_rows[0].keys()))
    else:
        write_rows(args.output, [], [])

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": school_names.get(school_key, ""),
            "score_summary_rank_enriched_rows": str(count),
            "years": "|".join(sorted(years_by_school.get(school_key, set()))),
            "types": "|".join(sorted(types_by_school.get(school_key, set()))),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "score_summary_rank_enriched_rows", "years", "types"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "score_summary_rank_enriched_schools", "value": str(len(school_counter))},
        {
            "metric": "score_summary_rank_enriched_coverage_ratio",
            "value": f"{len(school_counter) / TARGET_TOTAL:.4f}",
        },
        {
            "metric": "score_summary_rank_enriched_total_rows",
            "value": str(sum(school_counter.values())),
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote Guangxi score-summary rank enrichment rows for "
        f"{len(school_counter)} schools ({sum(school_counter.values())} rows)."
    )


if __name__ == "__main__":
    main()
