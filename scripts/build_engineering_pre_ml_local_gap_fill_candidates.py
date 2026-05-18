from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


TARGET_TOTAL = 32
SPECIAL_REMARK_KEYWORDS = (
    "专项",
    "预科",
    "民族",
    "中外",
    "合作",
    "定向",
)
FIELDS = [
    "school_key",
    "school_name",
    "backlog_lane",
    "gate_status",
    "latest_year",
    "current_data_completeness",
    "current_minimum_score",
    "current_minimum_rank",
    "missing_field_flags",
    "candidate_year",
    "candidate_subject_type",
    "candidate_batch",
    "candidate_group_count",
    "candidate_group_codes",
    "candidate_minimum_score",
    "candidate_minimum_rank",
    "candidate_min_rank_low",
    "candidate_min_rank_high",
    "candidate_source_ids",
    "candidate_data_quality",
    "candidate_fill_fields",
    "candidate_use_scope",
    "candidate_notes",
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


def is_ordinary_row(row: dict[str, str]) -> bool:
    remark = normalize_text(row.get("remark", ""))
    if any(keyword in remark for keyword in SPECIAL_REMARK_KEYWORDS):
        return False
    return normalize_text(row.get("is_first_round", "")) == "true"


def canonical_school_name(value: str) -> str:
    text = normalize_text(value)
    for suffix in (
        "本科招生信息网",
        "本科招生网",
        "本科生招生信息公开",
        "招生与就业工作处",
        "本科招生",
    ):
        text = text.replace(suffix, "")
    return text.strip()


def target_name_matches(school_name: str, university_name: str) -> bool:
    # Use exact canonical names to avoid pulling independent colleges with the same prefix.
    return canonical_school_name(school_name) == canonical_school_name(university_name)


def summarize_admission_rows(rows: list[dict[str, str]]) -> dict[str, str]:
    if not rows:
        return {}
    # School-level conservative summary: lowest score, widest conservative rank.
    min_score = min(parse_int(row.get("min_score", "")) for row in rows if parse_int(row.get("min_score", "")) > 0)
    max_rank_row = max(rows, key=lambda row: parse_int(row.get("min_rank_est", "")))
    group_codes = sorted({normalize_text(row.get("group_code", "")) for row in rows if row.get("group_code")})
    source_ids = sorted({normalize_text(row.get("source_id", "")) for row in rows if row.get("source_id")})
    data_quality = sorted({normalize_text(row.get("data_quality", "")) for row in rows if row.get("data_quality")})
    return {
        "candidate_year": normalize_text(max_rank_row.get("year", "")),
        "candidate_subject_type": normalize_text(max_rank_row.get("subject_type", "")),
        "candidate_batch": normalize_text(max_rank_row.get("batch", "")),
        "candidate_group_count": str(len(group_codes)),
        "candidate_group_codes": "|".join(group_codes),
        "candidate_minimum_score": str(min_score),
        "candidate_minimum_rank": normalize_text(max_rank_row.get("min_rank_est", "")),
        "candidate_min_rank_low": normalize_text(max_rank_row.get("min_rank_low", "")),
        "candidate_min_rank_high": normalize_text(max_rank_row.get("min_rank_high", "")),
        "candidate_source_ids": "|".join(source_ids),
        "candidate_data_quality": "|".join(data_quality),
    }


def candidate_fill_fields(backlog_row: dict[str, str], summary: dict[str, str]) -> str:
    fields = []
    missing = normalize_text(backlog_row.get("missing_field_flags", ""))
    if "missing_score" in missing and summary.get("candidate_minimum_score"):
        fields.append("minimum_score")
    if "missing_rank" in missing and summary.get("candidate_minimum_rank"):
        fields.append("minimum_rank")
    if "not_fresh_2025" in missing and summary.get("candidate_year") == "2025":
        fields.append("latest_year")
    if "missing_trend" in missing:
        fields.append("trend_seed_possible_from_2024_2025_admission_lines")
    return "|".join(fields) if fields else "none"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build local-only gap-fill candidates from official Guangxi admission-line seed data."
    )
    parser.add_argument(
        "--remaining-backlog",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_remaining_action_backlog_merged.csv",
        help="Pre-ML remaining action backlog CSV.",
    )
    parser.add_argument(
        "--admission-lines",
        type=Path,
        default=Path("clean_data") / "admission_line_table_seed.csv",
        help="Official admission line seed CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_local_gap_fill_candidates_merged.csv",
        help="Output local gap-fill candidates CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_local_gap_fill_candidates_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_local_gap_fill_candidates_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    backlog_rows = read_rows(args.remaining_backlog)
    admission_rows = read_rows(args.admission_lines)

    admission_by_year: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in admission_rows:
        if normalize_text(row.get("subject_type", "")) != "物理类":
            continue
        if normalize_text(row.get("batch", "")) != "本科普通批":
            continue
        if not is_ordinary_row(row):
            continue
        admission_by_year[normalize_text(row.get("year", ""))].append(row)

    output_rows: list[dict[str, str]] = []
    fill_counter: Counter[str] = Counter()
    lane_counter: Counter[str] = Counter()

    for backlog_row in backlog_rows:
        if normalize_text(backlog_row.get("backlog_lane", "")) != "B2_local_gap_fill":
            continue
        school_key = normalize_text(backlog_row.get("school_key", ""))
        school_name = normalize_text(backlog_row.get("school_name", ""))

        # Prefer latest local official admission seed, then fall back to the row's latest year.
        candidate_rows = [
            row
            for row in admission_by_year.get("2025", [])
            if target_name_matches(school_name, row.get("university_name", ""))
        ]
        if not candidate_rows:
            latest_year = normalize_text(backlog_row.get("latest_year", ""))
            candidate_rows = [
                row
                for row in admission_by_year.get(latest_year, [])
                if target_name_matches(school_name, row.get("university_name", ""))
            ]
        summary = summarize_admission_rows(candidate_rows)
        fill_fields = candidate_fill_fields(backlog_row, summary)
        fill_counter[fill_fields] += 1
        lane_counter[normalize_text(backlog_row.get("backlog_lane", ""))] += 1

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": school_name,
                "backlog_lane": normalize_text(backlog_row.get("backlog_lane", "")),
                "gate_status": normalize_text(backlog_row.get("gate_status", "")),
                "latest_year": normalize_text(backlog_row.get("latest_year", "")),
                "current_data_completeness": normalize_text(backlog_row.get("data_completeness", "")),
                "current_minimum_score": normalize_text(backlog_row.get("minimum_score", "")),
                "current_minimum_rank": normalize_text(backlog_row.get("minimum_rank", "")),
                "missing_field_flags": normalize_text(backlog_row.get("missing_field_flags", "")),
                "candidate_year": summary.get("candidate_year", ""),
                "candidate_subject_type": summary.get("candidate_subject_type", ""),
                "candidate_batch": summary.get("candidate_batch", ""),
                "candidate_group_count": summary.get("candidate_group_count", "0"),
                "candidate_group_codes": summary.get("candidate_group_codes", ""),
                "candidate_minimum_score": summary.get("candidate_minimum_score", ""),
                "candidate_minimum_rank": summary.get("candidate_minimum_rank", ""),
                "candidate_min_rank_low": summary.get("candidate_min_rank_low", ""),
                "candidate_min_rank_high": summary.get("candidate_min_rank_high", ""),
                "candidate_source_ids": summary.get("candidate_source_ids", ""),
                "candidate_data_quality": summary.get("candidate_data_quality", ""),
                "candidate_fill_fields": fill_fields,
                "candidate_use_scope": "local_gap_fill_candidate_only_not_auto_ml_input",
                "candidate_notes": (
                    "候选值来自本地广西官方投档线种子，按普通批、物理类、第一次正式投档、排除特殊备注后汇总；"
                    "用于补洞审计或人工复核，不自动进入机器学习。"
                ),
                "record_id": f"{school_key}-pre-ml-local-gap-fill-candidate",
                "source_record_id": normalize_text(backlog_row.get("record_id", "")),
                "source_slug": "pre_ml_local_gap_fill_candidate",
            }
        )

    output_rows.sort(key=lambda row: (row["school_key"], row["candidate_year"]))
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "candidate_year": row["candidate_year"],
            "candidate_minimum_score": row["candidate_minimum_score"],
            "candidate_minimum_rank": row["candidate_minimum_rank"],
            "candidate_fill_fields": row["candidate_fill_fields"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "candidate_year",
            "candidate_minimum_score",
            "candidate_minimum_rank",
            "candidate_fill_fields",
        ],
    )

    candidate_with_rank = sum(1 for row in output_rows if row["candidate_minimum_rank"])
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "local_gap_fill_candidate_schools", "value": str(len(output_rows))},
        {"metric": "local_gap_fill_candidate_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "local_gap_fill_candidates_with_rank", "value": str(candidate_with_rank)},
    ]
    for lane, count in sorted(lane_counter.items()):
        coverage_rows.append({"metric": f"{lane}_candidate_schools", "value": str(count)})
    for fields, count in sorted(fill_counter.items()):
        coverage_rows.append({"metric": f"fill_{fields}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote local gap-fill candidates for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
