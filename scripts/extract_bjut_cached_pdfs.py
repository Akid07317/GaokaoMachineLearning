from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from pypdf import PdfReader


PROVINCES = [
    "北京",
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
]

GROUP_LABELS = ("普通专业", "中外合作办学专业", "艺术类专业")
ROW_PATTERN = re.compile(
    r"^(?:(普通专业|中外合作办学专业|艺术类专业)\s+)?(.+?)\s+([文理])\s+([四五六]年)\s*$"
)
YEAR_RE = re.compile(r"(20\d{2})年")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def extract_layout_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text(extraction_mode="layout") or "")
    return "\n".join(parts)


def find_header_line(lines: list[str]) -> str:
    for line in lines:
        if "备注" in line and "专" in line and "学制" in line:
            return line
    raise ValueError("Could not find province header line.")


def province_spans(header_line: str) -> tuple[list[tuple[str, int, int]], int]:
    positions = [(province, header_line.find(province)) for province in PROVINCES if header_line.find(province) >= 0]
    positions.sort(key=lambda item: item[1])
    remarks_start = header_line.find("备注")
    spans: list[tuple[str, int, int]] = []
    for index, (province, start) in enumerate(positions):
        end = positions[index + 1][1] if index + 1 < len(positions) else remarks_start
        spans.append((province, start, end))
    return spans, remarks_start


def parse_pdf_rows(pdf_path: Path) -> list[dict[str, str]]:
    text = extract_layout_text(pdf_path)
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    title_line = lines[0]
    year_match = YEAR_RE.search(title_line)
    plan_year = year_match.group(1) if year_match else ""
    header_line = find_header_line(lines)
    spans, remarks_start = province_spans(header_line)
    left_end = spans[0][1]

    rows: list[dict[str, str]] = []
    current_group = ""
    for line in lines[lines.index(header_line) + 1 :]:
        if line.startswith("备注："):
            break
        left = line[:left_end].rstrip()
        match = ROW_PATTERN.match(left.strip())
        if not match:
            continue
        group_label, major_name, subject_type, duration = match.groups()
        if group_label:
            current_group = group_label
        remarks = line[remarks_start:].strip() if remarks_start >= 0 and len(line) > remarks_start else ""
        for province, start, end in spans:
            raw = line[start:end].strip()
            if raw == "":
                continue
            rows.append(
                {
                    "school_key": "beijing_gongye_211",
                    "school_name": "北京工业大学",
                    "plan_year": plan_year,
                    "group_label": current_group or group_label or "",
                    "major_name": major_name,
                    "subject_type": subject_type,
                    "duration": duration,
                    "province": province,
                    "plan_count_raw": raw,
                    "plan_count_numeric": raw if raw.isdigit() else "",
                    "remarks": remarks,
                    "source_pdf": str(pdf_path),
                    "source_pdf_name": pdf_path.name,
                }
            )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract BJUT province plan rows from cached PDF files using layout text."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("reports") / "cached_pdf_inventory.csv",
        help="Cached PDF inventory CSV.",
    )
    parser.add_argument(
        "--output-all",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_province_plan_rows.csv",
        help="Output CSV for all extracted BJUT province plan rows.",
    )
    parser.add_argument(
        "--output-guangxi",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_guangxi_plan_rows.csv",
        help="Output CSV for Guangxi-only extracted rows.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "beijing_gongye_cached_pdf_summary.csv",
        help="Summary CSV path.",
    )
    return parser


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = build_parser().parse_args()
    inventory_rows = read_rows(args.inventory)
    target_paths: list[Path] = []
    seen_names: set[str] = set()
    for row in inventory_rows:
        if row.get("school_key") != "beijing_gongye_211":
            continue
        if row.get("has_guangxi") != "true":
            continue
        pdf_path = Path(row["pdf_path"])
        if pdf_path.name in seen_names:
            continue
        seen_names.add(pdf_path.name)
        target_paths.append(pdf_path)

    all_rows: list[dict[str, str]] = []
    summary_rows: list[dict[str, str | int]] = []
    for pdf_path in target_paths:
        rows = parse_pdf_rows(pdf_path)
        all_rows.extend(rows)
        guangxi_rows = [row for row in rows if row["province"] == "广西"]
        summary_rows.append(
            {
                "source_pdf_name": pdf_path.name,
                "plan_year": guangxi_rows[0]["plan_year"] if guangxi_rows else "",
                "row_count_all": len(rows),
                "row_count_guangxi": len(guangxi_rows),
                "distinct_majors_guangxi": len({row["major_name"] for row in guangxi_rows}),
            }
        )

    guangxi_only = [row for row in all_rows if row["province"] == "广西"]
    write_rows(all_rows, args.output_all)
    write_rows(guangxi_only, args.output_guangxi)
    write_rows(summary_rows, args.summary_output)
    print(
        f"Wrote {len(all_rows)} BJUT province-plan rows and {len(guangxi_only)} Guangxi rows."
    )


if __name__ == "__main__":
    main()
