from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "pypdf is required for this script. Run it with the bundled runtime Python from load_workspace_dependencies."
    ) from exc


TARGET_PDF = Path("raw_data") / "official_followup" / "beijing_gongye_211" / "score_pdf_2025.pdf"
TARGET_TITLE = "2025年北京工业大学京外省份普通类录取分数统计"
SOURCE_URL = "https://admissions.bjut.edu.cn/lnlqfs/1776.htm"
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
PROVINCES = [
    "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "上海", "江苏", "浙江", "安徽", "福建",
    "江西", "山东", "河南", "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州", "云南", "西藏",
    "陕西", "甘肃", "青海", "宁夏", "新疆",
]
TYPE_LABELS = ["普通类", "中外合作办学", "国家专项", "高校专项"]


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


def extract_lines(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text(extraction_mode="layout") or ""
        lines.extend([line.rstrip() for line in text.splitlines() if line.strip()])
    return lines


def parse_rows(lines: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current_province = ""
    current_type = ""
    score_re = re.compile(r"^(?P<major>.+?)\s+(?P<highest>\d+)\s+(?P<lowest>\d+)\s+(?P<average>\d+\.\d+|\d+)$")
    for raw_line in lines:
        line = " ".join(raw_line.split())
        if not line or TARGET_TITLE in line or line.startswith("省份 招生类型"):
            continue
        for province in PROVINCES:
            if line.startswith(province):
                current_province = province
                line = line[len(province):].strip()
                break
        for label in TYPE_LABELS:
            if line.startswith(label):
                current_type = label
                line = line[len(label):].strip()
                break
        match = score_re.match(line)
        if not match or current_province != "广西":
            continue
        rows.append(
            {
                "school_name": "北京工业大学",
                "school_key": "beijing_gongye_211",
                "year": "2025",
                "province": "广西",
                "type": "本科普通批",
                "science_category": "物理类",
                "major": match.group("major").strip(),
                "requirement": "",
                "campus": "",
                "remarks": f"招生类型={current_type};平均分={match.group('average')}",
                "highest_score": match.group("highest"),
                "minimum_score": match.group("lowest"),
                "lowest_score_ranking": "",
                "record_id": f"bjut-score-2025-{current_type}-{match.group('major').strip()}",
                "source_url": SOURCE_URL,
            }
        )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract BJUT Guangxi ordinary-batch score rows from official PDF."
    )
    parser.add_argument("--pdf", type=Path, default=TARGET_PDF, help="BJUT score PDF path.")
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_guangxi_score_rows.csv",
        help="Structured BJUT Guangxi score output CSV.",
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
        default=Path("reports") / "beijing_gongye_official_score_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = parse_rows(extract_lines(args.pdf))
    write_rows(rows, args.score_output, SCORE_FIELDS)

    merged_score_rows = merge_rows(
        drop_school_rows(read_rows(args.score_major_merged), "beijing_gongye_211"),
        rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": "beijing_gongye_211",
            "school_name": "北京工业大学",
            "score_rows_total": str(len(rows)),
            "province": "广西",
            "year": "2025",
            "source_url": SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(rows)} BJUT Guangxi score rows.")


if __name__ == "__main__":
    main()
