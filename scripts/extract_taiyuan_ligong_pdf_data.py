from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "pypdf is required for this script. Run it with the bundled runtime Python from load_workspace_dependencies."
    ) from exc


SOURCE_DIR = Path("raw_data") / "official_followup" / "taiyuan_ligong_211"
PLAN_SPECS = [
    ("2024", SOURCE_DIR / "tyut_plan_2024.pdf", "https://zs.tyut.edu.cn/__local/E/1F/A4/6E74CAF41F36BB48C39E95CBA7E_019BCA19_3B2AF.pdf"),
    ("2025", SOURCE_DIR / "tyut_plan_2025.pdf", "https://zs.tyut.edu.cn/__local/6/E5/19/5342DA63DCE08172C70CE96D984_14FAE149_3B6B9.pdf"),
]
SCORE_2021_PDF = SOURCE_DIR / "tyut_score_2021.pdf"
SCORE_2021_SOURCE_URL = "https://zs.tyut.edu.cn/__local/4/39/2E/BC13AA04709A12EC9E1B3969035_9F7CAEAF_2702F.pdf"
SCHOOL_NAME = "太原理工大学"
SCHOOL_KEY = "taiyuan_ligong_211"
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
SCORE_SUMMARY_FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "science_category",
    "admit_count",
    "province_control_line",
    "highest_score",
    "minimum_score",
    "record_id",
    "source_url",
]
HEADER_POSITIONS = {
    "北京": 305,
    "天津": 313,
    "河北": 323,
    "山西": 337,
    "内蒙古": 350,
    "辽宁": 361,
    "吉林": 374,
    "黑龙江": 387,
    "上海": 400,
    "江苏": 412,
    "浙江": 425,
    "安徽": 438,
    "福建": 450,
    "江西": 462,
    "山东": 474,
    "河南": 485,
    "湖北": 496,
    "湖南": 509,
    "广东": 521,
    "广西": 532,
    "海南": 543,
    "重庆": 555,
    "四川": 566,
    "贵州": 577,
    "云南": 588,
    "西藏": 597,
    "陕西": 606,
    "甘肃": 617,
    "青海": 628,
    "宁夏": 638,
    "新疆": 646,
    "不分省": 654,
}
PROVINCE_ORDER = list(HEADER_POSITIONS)
PLAN_PATTERN = re.compile(
    r"^\((?P<major_code>[^)]+)\)\s*(?P<major>.+?)\s+(?P<requirement>不限|思想政治|物理\+化学)\s+"
    r"(?P<category>文史类\(历史\)|理工类\(物理\)|体育文\(历史\)|体育理\(物理\)|特殊类|理工类)\s+"
    r"(?P<plan_total>\d+)"
)


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
        str(value)
        .replace("（", "(")
        .replace("）", ")")
        .replace("＋", "+")
        .replace(" ", "")
        .strip()
    )


def layout_rows(reader: PdfReader) -> list[str]:
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text(extraction_mode="layout") or ""
        lines.extend([line for line in text.splitlines() if line.strip().startswith("(")])
    return lines


def normal_rows(reader: PdfReader) -> list[str]:
    rows: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        for line in text.splitlines():
            if "(" not in line:
                continue
            for part in re.split(r"(?=\(\d)", line.strip()):
                part = part.strip()
                if part.startswith("("):
                    rows.append(part)
    return rows


def extract_guangxi_plan_rows(year: str, pdf_path: Path, source_url: str) -> list[dict[str, str]]:
    reader = PdfReader(str(pdf_path))
    normal = normal_rows(reader)
    layout = layout_rows(reader)
    output: list[dict[str, str]] = []
    for normal_line, layout_line in zip(normal, layout):
        match = PLAN_PATTERN.match(normal_line)
        if not match:
            continue
        category = match.group("category")
        if category != "理工类(物理)":
            continue
        gx_start = HEADER_POSITIONS["广西"]
        gx_end = HEADER_POSITIONS["海南"]
        gx_raw = layout_line[gx_start:gx_end].strip()
        if not gx_raw.isdigit():
            continue
        major_name = clean_text(match.group("major"))
        requirement = clean_text(match.group("requirement"))
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
                "plan_count": gx_raw,
                "requirement": requirement,
                "selection_group": requirement,
                "campus": "",
                "remarks": f"总计划={match.group('plan_total')}",
                "weight": "",
                "record_id": f"tyut-plan-{year}-{clean_text(match.group('major_code'))}-{major_name}",
                "source_url": source_url,
                "introduction_link": source_url,
                "source_slug": "tyut-official-pdf",
            }
        )
    return output


def extract_score_summary_row() -> list[dict[str, str]]:
    reader = PdfReader(str(SCORE_2021_PDF))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    match = re.search(
        r"广西\s+(\d+)\s+本科第一批\s+理工\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        text,
    )
    if not match:
        return []
    plan_num, admit_num, control_line, highest, minimum = match.groups()
    return [
        {
            "school_name": SCHOOL_NAME,
            "school_key": SCHOOL_KEY,
            "year": "2021",
            "province": "广西",
            "type": "本科第一批",
            "science_category": "理工类",
            "admit_count": admit_num,
            "province_control_line": control_line,
            "highest_score": highest,
            "minimum_score": minimum,
            "record_id": "tyut-score-summary-2021-guangxi",
            "source_url": SCORE_2021_SOURCE_URL,
        }
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract TYUT Guangxi plan rows from official PDFs and 2021 score summary row."
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_pdf_structured" / "taiyuan_ligong_guangxi_plan_rows.csv",
        help="Structured Taiyuan Ligong plan output CSV.",
    )
    parser.add_argument(
        "--score-summary-output",
        type=Path,
        default=Path("clean_data") / "official_pdf_structured" / "taiyuan_ligong_guangxi_score_summary_rows.csv",
        help="Structured Taiyuan Ligong score summary output CSV.",
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
        default=Path("reports") / "taiyuan_ligong_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows: list[dict[str, str]] = []
    plan_by_year: dict[str, int] = {}
    for year, pdf_path, source_url in PLAN_SPECS:
        rows = extract_guangxi_plan_rows(year, pdf_path, source_url)
        plan_rows.extend(rows)
        plan_by_year[year] = len(rows)
    score_summary_rows = extract_score_summary_row()

    write_rows(plan_rows, args.plan_output, PLAN_FIELDS)
    write_rows(score_summary_rows, args.score_summary_output, SCORE_SUMMARY_FIELDS)

    merged_plan_rows = merge_rows(
        drop_school_rows(read_rows(args.plan_merged), SCHOOL_KEY),
        plan_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    write_rows(merged_plan_rows, args.plan_merged, PLAN_FIELDS)

    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "plan_rows_total": str(len(plan_rows)),
            "plan_rows_by_year": "|".join(f"{year}:{plan_by_year[year]}" for year in sorted(plan_by_year)),
            "score_summary_rows_total": str(len(score_summary_rows)),
            "score_years": "2021" if score_summary_rows else "",
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(
        f"Extracted {len(plan_rows)} Taiyuan Ligong Guangxi plan rows and {len(score_summary_rows)} score summary rows."
    )


if __name__ == "__main__":
    main()
