from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PLAN_SOURCE = Path("raw_data") / "official_api" / "nanli_211" / "njust_guangxi_2025_plan.json"
SCORE_SOURCE = Path("raw_data") / "official_api" / "nanli_211" / "njust_guangxi_score.json"
PLAN_SOURCE_URL = "https://zsb.njust.edu.cn/lqPain/initDateCon"
SCORE_SOURCE_URL = "https://zsb.njust.edu.cn/lqScore/initDateWebCon"
PLAN_FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "subject_type",
    "college",
    "specialty",
    "plan_count",
    "requirement",
    "selection_group",
    "campus",
    "remarks",
    "weight",
    "record_id",
    "source_url",
    "introduction_link",
    "source_slug",
]
SCORE_FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "science_category",
    "major",
    "requirement",
    "campus",
    "remarks",
    "highest_score",
    "minimum_score",
    "lowest_score_ranking",
    "record_id",
    "source_url",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_name(text: str) -> str:
    return (
        str(text)
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def merge_rows(
    existing_rows: list[dict[str, str]],
    new_rows: list[dict[str, str]],
    key_fields: list[str],
) -> list[dict[str, str]]:
    merged: dict[tuple[str, ...], dict[str, str]] = {}
    for row in existing_rows + new_rows:
        key = tuple(row.get(field, "") for field in key_fields)
        merged[key] = row
    return list(merged.values())


def load_json_rows(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("data", {}).get("list", [])


def normalize_plan_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, str]], set[str], set[str], dict[str, str]]:
    output: list[dict[str, str]] = []
    physics_names: set[str] = set()
    history_names: set[str] = set()
    requirement_map: dict[str, str] = {}
    for row in rows:
        province = str(row.get("province", "")).strip()
        subject = str(row.get("subject", "")).strip()
        specialty = str(row.get("professional_name", "")).strip()
        normalized_specialty = normalize_name(specialty)
        if province != "广西":
            continue
        if "物理" in subject:
            physics_names.add(normalized_specialty)
            requirement_map[normalized_specialty] = subject
            output.append(
                {
                    "school_name": "南京理工大学",
                    "school_key": "nanli_211",
                    "year": str(row.get("year", "")).strip(),
                    "province": province,
                    "type": str(row.get("class_name", "")).strip() or "本科一批",
                    "subject_type": "物理类",
                    "college": "",
                    "specialty": specialty,
                    "plan_count": str(row.get("pain_num", "")).strip(),
                    "requirement": subject,
                    "selection_group": subject,
                    "campus": "",
                    "remarks": "",
                    "weight": "",
                    "record_id": f"njust-plan-{row.get('id', '')}",
                    "source_url": PLAN_SOURCE_URL,
                    "introduction_link": "",
                    "source_slug": "njust-official-api",
                }
            )
        else:
            history_names.add(normalized_specialty)
    return output, physics_names, history_names, requirement_map


def normalize_score_rows(
    rows: list[dict[str, object]],
    physics_names: set[str],
    history_names: set[str],
    requirement_map: dict[str, str],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    year_map = {"year1": "2023", "year2": "2024", "year3": "2025"}
    for row in rows:
        province = str(row.get("province", "")).strip()
        major = str(row.get("professional_name", "")).strip()
        normalized_major = normalize_name(major)
        if province != "广西":
            continue
        if normalized_major in history_names:
            continue
        if "预科" in major:
            continue
        if physics_names and normalized_major not in physics_names:
            # Keep the physics-oriented Guangxi subset aligned to the plan-side major set.
            continue
        for key, year in year_map.items():
            minimum_score = str(row.get(key, "")).strip()
            if minimum_score in {"", "-"}:
                continue
            output.append(
                {
                    "school_name": "南京理工大学",
                    "school_key": "nanli_211",
                    "year": year,
                    "province": province,
                    "type": str(row.get("class_name", "")).strip() or "本科一批",
                    "science_category": "物理类",
                    "major": major,
                    "requirement": requirement_map.get(normalized_major, "物理类"),
                    "campus": "",
                    "remarks": "",
                    "highest_score": "",
                    "minimum_score": minimum_score,
                    "lowest_score_ranking": "",
                    "record_id": f"njust-score-{row.get('id', '')}-{year}",
                    "source_url": SCORE_SOURCE_URL,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Guangxi physics plan and score seed rows from NJUST official JSON."
    )
    parser.add_argument("--plan-source", type=Path, default=PLAN_SOURCE, help="Cached NJUST Guangxi plan JSON.")
    parser.add_argument("--score-source", type=Path, default=SCORE_SOURCE, help="Cached NJUST Guangxi score JSON.")
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
        help="Merged Guangxi physics plan seed CSV to update.",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics major-score seed CSV to update.",
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "njust_guangxi_plan_rows.csv",
        help="Structured NJUST Guangxi plan output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "njust_guangxi_score_rows.csv",
        help="Structured NJUST Guangxi score output CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "njust_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_source_rows = load_json_rows(args.plan_source)
    score_source_rows = load_json_rows(args.score_source)

    plan_rows, physics_names, history_names, requirement_map = normalize_plan_rows(plan_source_rows)
    score_rows = normalize_score_rows(score_source_rows, physics_names, history_names, requirement_map)

    write_rows(plan_rows, args.plan_output, PLAN_FIELDS)
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    merged_plan_rows = merge_rows(
        read_rows(args.plan_merged),
        plan_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    write_rows(merged_plan_rows, args.plan_merged, PLAN_FIELDS)

    merged_score_rows = merge_rows(
        read_rows(args.score_major_merged),
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": "nanli_211",
            "school_name": "南京理工大学",
            "province": "广西",
            "plan_rows": str(len(plan_rows)),
            "score_rows": str(len(score_rows)),
            "physics_plan_majors": str(len(physics_names)),
            "history_plan_majors": str(len(history_names)),
            "plan_source_url": PLAN_SOURCE_URL,
            "score_source_url": SCORE_SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(plan_rows)} NJUST Guangxi physics plan rows and {len(score_rows)} score rows.")


if __name__ == "__main__":
    main()
