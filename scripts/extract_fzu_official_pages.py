from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


PLAN_SOURCE_GLOB = "plan_gx_2025_physics_p*.html"
SCORE_SOURCE_GLOBS = ["score_gx_2025_physics_p*.html", "score_gx_2024_physics_p*.html"]
SOURCE_DIR = Path("raw_data") / "official_followup" / "fuzhou_daxue_211"
PLAN_SOURCE_URL = "https://zsks2.fzu.edu.cn/zhaosheng/?zsnf-1,syssmc-6,jhlbmc-1,klmc-1"
SCORE_SOURCE_URL = "https://zsks2.fzu.edu.cn/linianluqu/"
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
SCHOOL_NAME = "福州大学"
SCHOOL_KEY = "fuzhou_daxue_211"
INTRO_URL = "https://zsb.fzu.edu.cn/zscx/jhcx.htm"


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


def normalize_name(text: str) -> str:
    return (
        str(text)
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def strip_tags(text: str) -> str:
    cleaned = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return " ".join(html.unescape(cleaned).replace("\xa0", " ").split())


def parse_table_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    table_match = re.search(
        r'<table class="mart_20 sub_tab sort-table">(.*?)</table>',
        text,
        re.I | re.S,
    )
    if not table_match:
        return [], []
    table_html = table_match.group(1)
    headers = [strip_tags(item) for item in re.findall(r"<th[^>]*>(.*?)</th>", table_html, re.I | re.S)]
    body_match = re.search(r"<tbody>(.*?)</tbody>", table_html, re.I | re.S)
    if not body_match:
        return headers, []
    rows: list[list[str]] = []
    for tr_html in re.findall(r"<tr[^>]*>(.*?)</tr>", body_match.group(1), re.I | re.S):
        values = [strip_tags(item) for item in re.findall(r"<td[^>]*>(.*?)</td>", tr_html, re.I | re.S)]
        if values:
            rows.append(values)
    return headers, rows


def normalize_plan_rows(paths: list[Path]) -> tuple[list[dict[str, str]], dict[str, str]]:
    output: list[dict[str, str]] = []
    requirement_map: dict[str, str] = {}
    row_index = 0
    for path in paths:
        _, rows = parse_table_rows(path)
        for values in rows:
            if len(values) < 10:
                continue
            year, province, category, subject, batch, major_code, major_name, plan_count, requirement, remarks = values[:10]
            if province != "广西" or category != "普通类" or "物理" not in subject:
                continue
            row_index += 1
            normalized_major = normalize_name(major_name)
            requirement_map[normalized_major] = requirement
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": province,
                    "type": batch or "本科普通批",
                    "subject_type": "物理类",
                    "college": "",
                    "specialty": major_name,
                    "plan_count": plan_count,
                    "requirement": requirement,
                    "selection_group": requirement,
                    "campus": "",
                    "remarks": remarks,
                    "weight": "",
                    "record_id": f"fzu-plan-{year}-{row_index}",
                    "source_url": PLAN_SOURCE_URL,
                    "introduction_link": INTRO_URL,
                    "source_slug": "fzu-official-pages",
                }
            )
    return output, requirement_map


def normalize_score_rows(paths: list[Path], requirement_map: dict[str, str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    row_index = 0
    for path in paths:
        _, rows = parse_table_rows(path)
        for values in rows:
            if len(values) < 11:
                continue
            year, province, category, subject, selection, major_name, admit_count, highest, minimum, average, remarks = values[:11]
            if province != "广西" or category != "普通类" or "物理" not in subject:
                continue
            row_index += 1
            normalized_major = normalize_name(major_name)
            requirement = requirement_map.get(normalized_major, selection.replace(" ", ""))
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": province,
                    "type": "本科普通批",
                    "science_category": "物理类",
                    "major": major_name,
                    "requirement": requirement,
                    "campus": "",
                    "remarks": remarks,
                    "highest_score": highest,
                    "minimum_score": minimum,
                    "lowest_score_ranking": "",
                    "record_id": f"fzu-score-{year}-{row_index}",
                    "source_url": SCORE_SOURCE_URL,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Fuzhou University Guangxi physics plan and score rows from official paginated HTML pages."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SOURCE_DIR,
        help="Directory containing cached Fuzhou follow-up HTML pages.",
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "fzu_guangxi_plan_rows.csv",
        help="Structured Fuzhou plan output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "fzu_guangxi_score_rows.csv",
        help="Structured Fuzhou score output CSV.",
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
        help="Merged Guangxi physics score seed CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "fzu_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_paths = sorted(args.source_dir.glob(PLAN_SOURCE_GLOB))
    score_paths: list[Path] = []
    for pattern in SCORE_SOURCE_GLOBS:
        score_paths.extend(sorted(args.source_dir.glob(pattern)))

    plan_rows, requirement_map = normalize_plan_rows(plan_paths)
    score_rows = normalize_score_rows(score_paths, requirement_map)

    write_rows(plan_rows, args.plan_output, PLAN_FIELDS)
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    merged_plan_rows = merge_rows(
        drop_school_rows(read_rows(args.plan_merged), SCHOOL_KEY),
        plan_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    write_rows(merged_plan_rows, args.plan_merged, PLAN_FIELDS)

    merged_score_rows = merge_rows(
        drop_school_rows(read_rows(args.score_major_merged), SCHOOL_KEY),
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "plan_rows": str(len(plan_rows)),
            "score_rows_total": str(len(score_rows)),
            "plan_source_url": PLAN_SOURCE_URL,
            "score_source_url": SCORE_SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))


if __name__ == "__main__":
    main()
