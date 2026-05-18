from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "subject_type",
    "specialty_count",
    "selection_group_count",
    "campus_count",
    "total_plan_count",
    "remarks",
    "record_id",
    "source_url",
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


def parse_int(value: str) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build school-level Guangxi plan summary rows from merged official plan seeds."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
        help="Merged Guangxi plan seed CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_summary_seed_merged.csv",
        help="Merged school-level Guangxi plan summary CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_plan_summary_school_summary.csv",
        help="School-level summary counts CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_plan_summary_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_plan_summary_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.source)

    grouped: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                normalize_text(row.get("school_key", "")),
                normalize_text(row.get("year", "")),
                normalize_text(row.get("province", "")),
                normalize_text(row.get("type", "")),
                normalize_text(row.get("subject_type", "")),
            )
        ].append(row)

    merged_rows: list[dict[str, str]] = []
    per_school_counter: Counter[str] = Counter()
    for (school_key, year, province, row_type, subject_type), subset in sorted(grouped.items()):
        school_name = normalize_text(subset[0].get("school_name", ""))
        source_urls = sorted({normalize_text(row.get("source_url", "")) for row in subset if normalize_text(row.get("source_url", ""))})
        source_slugs = sorted({normalize_text(row.get("source_slug", "")) for row in subset if normalize_text(row.get("source_slug", ""))})
        specialty_count = len({normalize_text(row.get("specialty", "")) for row in subset if normalize_text(row.get("specialty", ""))})
        selection_group_count = len({normalize_text(row.get("selection_group", "")) for row in subset if normalize_text(row.get("selection_group", ""))})
        campus_count = len({normalize_text(row.get("campus", "")) for row in subset if normalize_text(row.get("campus", ""))})
        total_plan_count = 0
        missing_plan_count_rows = 0
        for row in subset:
            value = parse_int(row.get("plan_count", ""))
            if value is None:
                missing_plan_count_rows += 1
            else:
                total_plan_count += value
        remarks_parts = [f"学校级摘要由官方招生计划明细推导", f"专业条目数={specialty_count}"]
        if selection_group_count:
            remarks_parts.append(f"选科/分组条目数={selection_group_count}")
        if campus_count:
            remarks_parts.append(f"校区条目数={campus_count}")
        if missing_plan_count_rows:
            remarks_parts.append(f"空计划数条目={missing_plan_count_rows}")
        merged_rows.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": year,
                "province": province,
                "type": row_type,
                "subject_type": subject_type,
                "specialty_count": str(specialty_count),
                "selection_group_count": str(selection_group_count),
                "campus_count": str(campus_count),
                "total_plan_count": str(total_plan_count),
                "remarks": ";".join(remarks_parts),
                "record_id": f"{school_key}-plan-summary-{year}-{subject_type}-{row_type}",
                "source_url": "|".join(source_urls),
                "source_slug": "|".join(source_slugs),
            }
        )
        per_school_counter[school_key] += 1

    write_rows(args.output, merged_rows, FIELDS)

    school_names = {row["school_key"]: row["school_name"] for row in merged_rows}
    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": school_names.get(school_key, ""),
            "plan_summary_rows": str(count),
        }
        for school_key, count in sorted(per_school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(args.school_summary_output, school_summary_rows, ["school_key", "school_name", "plan_summary_rows"])

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "structured_plan_summary_schools", "value": str(len(per_school_counter))},
        {
            "metric": "structured_plan_summary_coverage_ratio",
            "value": f"{len(per_school_counter) / TARGET_TOTAL:.4f}",
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "derived_plan_summary_rows": row["plan_summary_rows"],
        }
        for row in school_summary_rows
    ]
    write_rows(args.round_summary_output, round_rows, ["school_key", "school_name", "derived_plan_summary_rows"])

    print(f"Wrote Guangxi plan-summary seed rows for {len(per_school_counter)} schools.")


if __name__ == "__main__":
    main()
