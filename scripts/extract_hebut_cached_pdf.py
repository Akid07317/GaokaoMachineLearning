from __future__ import annotations

import argparse
import csv
from pathlib import Path


try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "pypdf is required for this script. Run it with the bundled runtime Python from load_workspace_dependencies."
    ) from exc


TARGET_PDF = (
    Path("raw_data")
    / "engineering_520_fullsweep"
    / "hebei_gongye_211"
    / "https_zs.hebut.edu.cn_Upload_file_20250630_1751266683401513.pdf.html"
)
PROVINCES = [
    "河北",
    "天津",
    "北京",
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
    "24民族预科班",
    "内地新疆班",
]


def read_layout_lines(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text(extraction_mode="layout") or ""
        page_lines = [line.rstrip("\n") for line in text.splitlines() if line.strip()]
        lines.extend(page_lines)
    return lines


def parse_header_spans(lines: list[str]) -> tuple[dict[str, tuple[int, int]], int, int]:
    header_index = next(i for i, line in enumerate(lines) if "学院" in line and "专业" in line and "合计" in line)
    upper = lines[header_index]
    lower = lines[header_index + 1]

    positions = [idx for idx in range(len(upper)) if (upper[idx] != " " or lower[idx] != " ") and idx >= 46]
    spans: dict[str, tuple[int, int]] = {}
    parsed_names: list[tuple[str, int]] = []
    for idx in positions:
        name = f"{upper[idx].strip()}{lower[idx].strip()}"
        if not name:
            continue
        parsed_names.append((name, idx))
    for i, (name, start) in enumerate(parsed_names):
        end = parsed_names[i + 1][1] if i + 1 < len(parsed_names) else len(upper)
        spans[name] = (start, end)
    return spans, header_index, upper.find("合计")


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Hebut Guangxi plan rows from the cached 2025 official plan PDF."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=TARGET_PDF,
        help="Cached Hebut plan PDF path.",
    )
    parser.add_argument(
        "--output-guangxi",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "hebei_gongye_guangxi_plan_rows.csv",
        help="Output CSV for Guangxi-only extracted rows.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "hebei_gongye_cached_pdf_summary.csv",
        help="Summary CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    lines = read_layout_lines(args.pdf)
    spans, header_index, total_start = parse_header_spans(lines)
    gx_start, gx_end = spans["广西"]
    total_end = next(start for name, (start, _) in sorted(spans.items(), key=lambda x: x[1][0]) if start > total_start)

    rows: list[dict[str, str]] = []
    current_college = ""
    for line in lines[header_index + 3 :]:
        if line.startswith("注："):
            break
        total_raw = line[total_start:total_end].strip()
        gx_raw = line[gx_start:gx_end].strip()
        left = line[:total_start].rstrip()
        if not total_raw and left.strip() and rows:
            rows[-1]["major_name"] = f"{rows[-1]['major_name']}{left.strip()}"
            continue
        if not total_raw or not gx_raw or not gx_raw.isdigit():
            continue
        college = "".join(line[:17].split())
        major = "".join(line[17:total_start].split())
        if not major or major == "总计":
            continue
        if "专业" in major and "合计" in major:
            continue
        if any(ch.isdigit() for ch in major):
            continue
        if len(major) > 30:
            continue
        if college and not college.endswith(("学院", "校区")):
            continue
        if college:
            current_college = college
        rows.append(
            {
                "school_key": "hebei_gongye_211",
                "school_name": "河北工业大学",
                "plan_year": "2025",
                "college_name": current_college,
                "major_name": major,
                "province": "广西",
                "plan_count_raw": gx_raw,
                "plan_count_numeric": gx_raw if gx_raw.isdigit() else "",
                "subject_type": "",
                "remarks": "",
                "source_pdf": str(args.pdf),
                "source_pdf_name": args.pdf.name,
            }
        )

    write_rows(rows, args.output_guangxi)
    summary_rows = [
        {
            "source_pdf_name": args.pdf.name,
            "plan_year": "2025",
            "row_count_guangxi": len(rows),
            "distinct_majors_guangxi": len({row["major_name"] for row in rows}),
        }
    ]
    write_rows(summary_rows, args.summary_output)
    print(f"Wrote {len(rows)} Hebut Guangxi plan rows.")


if __name__ == "__main__":
    main()
