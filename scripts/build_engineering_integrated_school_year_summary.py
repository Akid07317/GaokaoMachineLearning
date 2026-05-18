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
    "subject_type",
    "data_completeness",
    "plan_type_count",
    "score_type_count",
    "plan_specialty_count_total",
    "plan_selection_group_count_total",
    "plan_campus_count_total",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "maximum_score",
    "plan_types",
    "score_types",
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


def normalize_subject_type(value: str) -> str:
    text = normalize_text(value)
    if text == "物理":
        return "物理类"
    return text


def parse_int(value: str) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def join_sources(values: list[str]) -> str:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in values:
        for piece in normalize_text(raw).split("|"):
            piece = piece.strip()
            if piece and piece not in seen:
                seen.add(piece)
                ordered.append(piece)
    return "|".join(ordered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build school-year Guangxi integrated summaries from official plan and score summary layers."
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
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_school_year_integrated_summary_merged.csv",
        help="Integrated school-year Guangxi summary CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_integrated_school_summary.csv",
        help="Integrated school summary counts CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_guangxi_integrated_coverage_rollup.csv",
        help="Integrated coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_integrated_summary_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows = read_rows(args.plan_summary_source)
    score_rows = read_rows(args.score_summary_source)

    grouped_plan: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    grouped_score: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)

    for row in plan_rows:
        grouped_plan[
            (
                normalize_text(row.get("school_key", "")),
                normalize_text(row.get("year", "")),
                normalize_text(row.get("province", "")),
                normalize_subject_type(row.get("subject_type", "")),
            )
        ].append(row)
    for row in score_rows:
        grouped_score[
            (
                normalize_text(row.get("school_key", "")),
                normalize_text(row.get("year", "")),
                normalize_text(row.get("province", "")),
                normalize_subject_type(row.get("subject_type", "")),
            )
        ].append(row)

    all_keys = sorted(set(grouped_plan) | set(grouped_score))
    integrated_rows: list[dict[str, str]] = []
    per_school_counter: Counter[str] = Counter()

    for school_key, year, province, subject_type in all_keys:
        plan_subset = grouped_plan.get((school_key, year, province, subject_type), [])
        score_subset = grouped_score.get((school_key, year, province, subject_type), [])
        school_name = normalize_text(
            (score_subset[0].get("school_name") if score_subset else "")
            or (plan_subset[0].get("school_name") if plan_subset else "")
        )

        if plan_subset and score_subset:
            completeness = "plan_and_score"
        elif plan_subset:
            completeness = "plan_only"
        else:
            completeness = "score_only"

        plan_types = sorted({normalize_text(row.get("type", "")) for row in plan_subset if normalize_text(row.get("type", ""))})
        score_types = sorted({normalize_text(row.get("type", "")) for row in score_subset if normalize_text(row.get("type", ""))})
        plan_source_url = join_sources([row.get("source_url", "") for row in plan_subset])
        score_source_url = join_sources([row.get("source_url", "") for row in score_subset])

        total_plan_count = 0
        specialty_total = 0
        selection_total = 0
        campus_total = 0
        for row in plan_subset:
            total_plan_count += parse_int(row.get("total_plan_count", "")) or 0
            specialty_total += parse_int(row.get("specialty_count", "")) or 0
            selection_total += parse_int(row.get("selection_group_count", "")) or 0
            campus_total += parse_int(row.get("campus_count", "")) or 0

        min_score: int | None = None
        max_score: int | None = None
        conservative_rank: int | None = None
        for row in score_subset:
            score_value = parse_int(row.get("minimum_score", ""))
            if score_value is not None and (min_score is None or score_value < min_score):
                min_score = score_value
            max_value = parse_int(row.get("maximum_score", ""))
            if max_value is not None and (max_score is None or max_value > max_score):
                max_score = max_value
            rank_value = parse_int(row.get("minimum_rank", ""))
            if rank_value is not None and (conservative_rank is None or rank_value > conservative_rank):
                conservative_rank = rank_value

        remarks_parts = [
            "学校-年份级广西综合摘要由官方计划摘要与/或官方分数摘要保守整合",
            f"数据完整性={completeness}",
        ]
        if plan_types:
            remarks_parts.append(f"计划类型={'|'.join(plan_types)}")
        if score_types:
            remarks_parts.append(f"分数类型={'|'.join(score_types)}")
        if score_subset:
            remarks_parts.append("最低位次采用各摘要行中最宽松(数值最大)的最低位次")
        remarks = ";".join(remarks_parts)

        integrated_rows.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": year,
                "province": province,
                "subject_type": subject_type,
                "data_completeness": completeness,
                "plan_type_count": str(len(plan_types)),
                "score_type_count": str(len(score_types)),
                "plan_specialty_count_total": str(specialty_total),
                "plan_selection_group_count_total": str(selection_total),
                "plan_campus_count_total": str(campus_total),
                "total_plan_count": str(total_plan_count),
                "minimum_score": "" if min_score is None else str(min_score),
                "minimum_rank": "" if conservative_rank is None else str(conservative_rank),
                "maximum_score": "" if max_score is None else str(max_score),
                "plan_types": "|".join(plan_types),
                "score_types": "|".join(score_types),
                "remarks": remarks,
                "record_id": f"{school_key}-integrated-summary-{year}-{subject_type}",
                "plan_source_url": plan_source_url,
                "score_source_url": score_source_url,
                "source_slug": "official_integrated_school_year_summary",
            }
        )
        per_school_counter[school_key] += 1

    write_rows(args.output, integrated_rows, FIELDS)

    school_names = {row["school_key"]: row["school_name"] for row in integrated_rows}
    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": school_names.get(school_key, ""),
            "integrated_summary_rows": str(count),
        }
        for school_key, count in sorted(per_school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "integrated_summary_rows"],
    )

    completeness_counter = Counter(row["data_completeness"] for row in integrated_rows)
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "structured_integrated_schools", "value": str(len(per_school_counter))},
        {
            "metric": "structured_integrated_coverage_ratio",
            "value": f"{len(per_school_counter) / TARGET_TOTAL:.4f}",
        },
        {"metric": "plan_and_score_rows", "value": str(completeness_counter.get("plan_and_score", 0))},
        {"metric": "plan_only_rows", "value": str(completeness_counter.get("plan_only", 0))},
        {"metric": "score_only_rows", "value": str(completeness_counter.get("score_only", 0))},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "derived_integrated_rows": row["integrated_summary_rows"],
        }
        for row in school_summary_rows
    ]
    write_rows(args.round_summary_output, round_rows, ["school_key", "school_name", "derived_integrated_rows"])

    print(f"Wrote Guangxi integrated school-year summaries for {len(per_school_counter)} schools.")


if __name__ == "__main__":
    main()
