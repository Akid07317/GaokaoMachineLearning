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
    "plan_specialty_count",
    "plan_selection_group_count",
    "plan_campus_count",
    "total_plan_count",
    "score_campus",
    "minimum_score",
    "minimum_rank",
    "average_score",
    "maximum_score",
    "remarks",
    "record_id",
    "plan_source_url",
    "score_source_url",
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


def normalize_type(value: str) -> str:
    text = normalize_text(value)
    replacements = {
        "普通批": "本科普通批",
    }
    return replacements.get(text, text)


def normalize_subject_type(value: str) -> str:
    text = normalize_text(value)
    if text == "物理":
        return "物理类"
    return text


def join_sources(*values: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for raw in values:
        for piece in normalize_text(raw).split("|"):
            piece = piece.strip()
            if piece and piece not in seen:
                seen.add(piece)
                parts.append(piece)
    return "|".join(parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build school-level Guangxi overview rows by combining official plan and score summaries."
    )
    parser.add_argument(
        "--plan-summary-source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_summary_seed_merged.csv",
        help="Merged Guangxi plan-summary seed CSV.",
    )
    parser.add_argument(
        "--score-summary-source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_summary_seed_merged.csv",
        help="Merged Guangxi score-summary seed CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_overview_seed_merged.csv",
        help="Merged school-level Guangxi overview CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_overview_school_summary.csv",
        help="School-level overview counts CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_overview_coverage_rollup.csv",
        help="Overview coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_overview_summary_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows = read_rows(args.plan_summary_source)
    score_rows = read_rows(args.score_summary_source)

    plan_by_key: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in plan_rows:
        plan_by_key[
            (
                normalize_text(row.get("school_key", "")),
                normalize_text(row.get("year", "")),
                normalize_text(row.get("province", "")),
                normalize_type(row.get("type", "")),
                normalize_subject_type(row.get("subject_type", "")),
            )
        ] = row

    score_by_key: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in score_rows:
        score_by_key[
            (
                normalize_text(row.get("school_key", "")),
                normalize_text(row.get("year", "")),
                normalize_text(row.get("province", "")),
                normalize_type(row.get("type", "")),
                normalize_subject_type(row.get("subject_type", "")),
            )
        ] = row

    shared_keys = sorted(set(plan_by_key) & set(score_by_key))
    overview_rows: list[dict[str, str]] = []
    per_school_counter: Counter[str] = Counter()
    for school_key, year, province, row_type, subject_type in shared_keys:
        plan_row = plan_by_key[(school_key, year, province, row_type, subject_type)]
        score_row = score_by_key[(school_key, year, province, row_type, subject_type)]
        school_name = normalize_text(score_row.get("school_name") or plan_row.get("school_name"))
        remarks = ";".join(
            part
            for part in [
                "学校级广西概览由官方计划摘要与官方分数摘要合并",
                normalize_text(plan_row.get("remarks", "")),
                normalize_text(score_row.get("remarks", "")),
            ]
            if part
        )
        overview_rows.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": year,
                "province": province,
                "type": row_type,
                "subject_type": subject_type,
                "plan_specialty_count": normalize_text(plan_row.get("specialty_count", "")),
                "plan_selection_group_count": normalize_text(plan_row.get("selection_group_count", "")),
                "plan_campus_count": normalize_text(plan_row.get("campus_count", "")),
                "total_plan_count": normalize_text(plan_row.get("total_plan_count", "")),
                "score_campus": normalize_text(score_row.get("campus", "")),
                "minimum_score": normalize_text(score_row.get("minimum_score", "")),
                "minimum_rank": normalize_text(score_row.get("minimum_rank", "")),
                "average_score": normalize_text(score_row.get("average_score", "")),
                "maximum_score": normalize_text(score_row.get("maximum_score", "")),
                "remarks": remarks,
                "record_id": f"{school_key}-overview-{year}-{subject_type}-{row_type}",
                "plan_source_url": join_sources(plan_row.get("source_url", "")),
                "score_source_url": join_sources(score_row.get("source_url", "")),
                "source_slug": "official_plan_score_overview",
            }
        )
        per_school_counter[school_key] += 1

    write_rows(args.output, overview_rows, FIELDS)

    school_names = {row["school_key"]: row["school_name"] for row in overview_rows}
    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": school_names.get(school_key, ""),
            "overview_summary_rows": str(count),
        }
        for school_key, count in sorted(per_school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "overview_summary_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "structured_overview_schools", "value": str(len(per_school_counter))},
        {
            "metric": "structured_overview_coverage_ratio",
            "value": f"{len(per_school_counter) / TARGET_TOTAL:.4f}",
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "derived_overview_rows": row["overview_summary_rows"],
        }
        for row in school_summary_rows
    ]
    write_rows(args.round_summary_output, round_rows, ["school_key", "school_name", "derived_overview_rows"])

    print(f"Wrote Guangxi overview rows for {len(per_school_counter)} schools.")


if __name__ == "__main__":
    main()
