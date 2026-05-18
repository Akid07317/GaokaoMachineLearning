from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


SOURCE_DIR = Path("raw_data") / "official_followup" / "xinan_jiaoda_211"
PLAN_SOURCES = ["plan_gx_2025.html", "plan_gx_2024.html"]
PLAN_SOURCE_URL = "https://cjcx.swjtu.edu.cn/plan/"
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
SCHOOL_NAME = "西南交通大学"
SCHOOL_KEY = "xinan_jiaoda_211"
INTRO_URL = "https://cjcx.swjtu.edu.cn/plan/"


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


def strip_tags(text: str) -> str:
    cleaned = re.sub(r"<br\\s*/?>", " ", text, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return " ".join(html.unescape(cleaned).replace("\xa0", " ").split())


def parse_table_rows(path: Path) -> list[list[str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    table_match = re.search(r"<table class='tab'.*?</table>", text, flags=re.I | re.S)
    if not table_match:
        return []
    rows: list[list[str]] = []
    for tr_html in re.findall(r"<tr[^>]*>(.*?)</tr>", table_match.group(0), flags=re.I | re.S):
        values = [strip_tags(cell) for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr_html, flags=re.I | re.S)]
        if values:
            rows.append(values)
    return rows


def normalize_plan_rows(paths: list[Path]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for path in paths:
        rows = parse_table_rows(path)
        for values in rows[1:]:
            if len(values) < 9:
                continue
            _, major_code, major_name, plan_count, subject_type, plan_nature, plan_category, campus, province = values[:9]
            if province != "广西壮族自治区" or subject_type != "物理类" or plan_category != "普通类":
                continue
            year_match = re.search(r"(20\d{2})", path.name)
            year = year_match.group(1) if year_match else ""
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": "广西",
                    "type": "本科普通批",
                    "subject_type": "物理类",
                    "college": "",
                    "specialty": major_name,
                    "plan_count": plan_count,
                    "requirement": "物理类",
                    "selection_group": "物理类",
                    "campus": campus,
                    "remarks": f"专业代码={major_code}" if major_code else "",
                    "weight": "",
                    "record_id": f"swjtu-plan-{year}-{major_code}-{major_name}",
                    "source_url": f"{PLAN_SOURCE_URL}{path.name}",
                    "introduction_link": INTRO_URL,
                    "source_slug": "swjtu-plan-pages",
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Southwest Jiaotong Guangxi physics plan rows from official static HTML pages."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SOURCE_DIR,
        help="Directory containing Southwest Jiaotong Guangxi plan pages.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "xinan_jiaoda_guangxi_plan_rows.csv",
        help="Structured Southwest Jiaotong plan output CSV.",
    )
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
        help="Merged Guangxi physics plan seed CSV.",
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
    source_paths = [args.source_dir / name for name in PLAN_SOURCES]
    plan_rows = normalize_plan_rows([path for path in source_paths if path.exists()])
    write_rows(plan_rows, args.output, PLAN_FIELDS)

    merged_plan_rows = merge_rows(
        drop_school_rows(read_rows(args.plan_merged), SCHOOL_KEY),
        plan_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    write_rows(merged_plan_rows, args.plan_merged, PLAN_FIELDS)

    by_year: dict[str, int] = {}
    for row in plan_rows:
        by_year[row["year"]] = by_year.get(row["year"], 0) + 1
    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "plan_rows_total": str(len(plan_rows)),
            "plan_rows_by_year": "|".join(f"{year}:{count}" for year, count in sorted(by_year.items())),
            "plan_source_url": PLAN_SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(plan_rows)} Southwest Jiaotong Guangxi physics plan rows.")


if __name__ == "__main__":
    main()
