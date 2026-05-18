from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


SOURCE_DIR = Path("raw_data") / "official_followup" / "xinan_jiaoda_211"
SOURCE_SPECS = [
    (
        "2024",
        SOURCE_DIR / "admission_gx_2024.html",
        "https://cjcx.swjtu.edu.cn/admission/admission_2024_ANXIZHUANGZUZIZHIOU.html",
    ),
    (
        "2025",
        SOURCE_DIR / "admission_gx_2025.html",
        "https://cjcx.swjtu.edu.cn/admission/admission_2025_ANXIZHUANGZUZIZHIOU.html",
    ),
]
SCHOOL_NAME = "西南交通大学"
SCHOOL_KEY = "xinan_jiaoda_211"
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


def drop_school_rows(rows: list[dict[str, str]], school_key: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("school_key", "") != school_key]


def clean_text(value: str) -> str:
    return (
        value.replace("&nbsp;", " ")
        .replace("（", "(")
        .replace("）", ")")
        .replace("＋", "+")
        .replace("\xa0", " ")
        .strip()
    )


def parse_table_rows(path: Path) -> list[list[str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    body_match = re.search(r"<table class='tab'.*?<tbody>(.*?)</tbody>", text, re.I | re.S)
    if not body_match:
        body_match = re.search(r"<table class='tab'.*?>(.*?)</table>", text, re.I | re.S)
    if not body_match:
        return []
    rows: list[list[str]] = []
    for tr_html in re.findall(r"<tr[^>]*>(.*?)</tr>", body_match.group(1), re.I | re.S):
        values = [
            clean_text(re.sub(r"<[^>]+>", "", item))
            for item in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr_html, re.I | re.S)
        ]
        if values:
            rows.append(values)
    return rows


def is_physics_ordinary(category: str) -> bool:
    return "物理" in category and "历史" not in category and "预科" not in category and "国家专项" not in category


def normalize_rows() -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for year, path, source_url in SOURCE_SPECS:
        for values in parse_table_rows(path):
            if len(values) < 11 or values[0] == "序号":
                continue
            _, campus, category, major, admit_count, province_line, highest, minimum, average, province, rank = values[:11]
            if province != "广西壮族自治区" or not is_physics_ordinary(category):
                continue
            major_name = clean_text(major)
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": "广西",
                    "type": "本科普通批",
                    "science_category": "物理类",
                    "major": major_name,
                    "requirement": "",
                    "campus": clean_text(campus),
                    "remarks": f"类别名称={clean_text(category)};录取数={clean_text(admit_count)};省控线={clean_text(province_line)};平均分={clean_text(average)}",
                    "highest_score": clean_text(highest),
                    "minimum_score": clean_text(minimum),
                    "lowest_score_ranking": clean_text(rank),
                    "record_id": f"swjtu-score-{year}-{major_name}-{clean_text(campus)}-{clean_text(category)}",
                    "source_url": source_url,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Southwest Jiaotong Guangxi physics score rows from official admission pages."
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "xinan_jiaoda_guangxi_score_rows.csv",
        help="Structured Southwest Jiaotong score output CSV.",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics score seed CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "xinan_jiaoda_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    score_rows = normalize_rows()
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    merged_score_rows = merge_rows(
        drop_school_rows(read_rows(args.score_major_merged), SCHOOL_KEY),
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    by_year: dict[str, int] = {}
    for row in score_rows:
        by_year[row["year"]] = by_year.get(row["year"], 0) + 1
    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "score_rows_total": str(len(score_rows)),
            "score_rows_by_year": "|".join(f"{year}:{by_year[year]}" for year in sorted(by_year)),
            "score_source_urls": "|".join(url for _, _, url in SOURCE_SPECS),
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(score_rows)} Southwest Jiaotong Guangxi physics score rows.")


if __name__ == "__main__":
    main()
