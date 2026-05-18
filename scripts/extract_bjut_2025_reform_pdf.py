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


TARGET_PDF = (
    Path("raw_data")
    / "engineering_520_fullsweep"
    / "beijing_gongye_211"
    / "http_admissions.bjut.edu.cn_dfiles_2025_2025gaigeshengfenjh.pdf.html"
)
TARGET_TITLE = "北京工业大学2025年京外本科普通批分省分专业招生计划"
ROW_PATTERN = re.compile(
    r"^\s*(?P<group>.{0,4}?)\s*(?P<subject>物理|不限)\s+(?P<reselect>化学|不限)\s+(?P<major>.+?)\s+(?P<duration>[四五]年)\s*$"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key in seen:
                continue
            seen.add(key)
            fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_layout_lines(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    for candidate in reader.pages:
        text = candidate.extract_text(extraction_mode="layout") or ""
        if TARGET_TITLE in text:
            return [line.rstrip("\n") for line in text.splitlines() if line.strip()]
    raise ValueError(f"Could not find target title in {pdf_path}.")


def province_spans(lines: list[str]) -> tuple[dict[str, tuple[int, int]], int]:
    line_upper = lines[1]
    line_lower = lines[2]
    line_tail = lines[3]

    starts: list[int] = []
    for index in range(58, 160):
        if not any((line[index] if index < len(line) else " ").strip() for line in (line_upper, line_lower, line_tail)):
            continue
        if not starts or index - starts[-1] > 1:
            starts.append(index)

    spans: dict[str, tuple[int, int]] = {}
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else 160
        name = "".join(
            [
                (line_upper[start] if start < len(line_upper) else " ").strip(),
                (line_lower[start] if start < len(line_lower) else " ").strip(),
                (line_tail[start] if start < len(line_tail) else " ").strip(),
            ]
        )
        spans[name] = (start, end)
    return spans, 160


def normalize_group(current_group: str, fragment: str) -> str:
    frag = "".join(fragment.split())
    if not frag:
        return current_group
    if "普通" in frag or (frag == "专业" and current_group.startswith("普通")):
        return "普通专业"
    if "中外" in frag or "作办学" in frag or (frag == "专业" and current_group.startswith("中外合作办学")):
        return "中外合作办学专业"
    if "艺术" in frag or (frag == "专业" and current_group.startswith("艺术类")):
        return "艺术类专业"
    return current_group


def parse_guangxi_rows(pdf_path: Path) -> list[dict[str, str]]:
    lines = extract_layout_lines(pdf_path)
    spans, remarks_start = province_spans(lines)
    gx_start, gx_end = spans["广西"]

    rows: list[dict[str, str]] = []
    current_group = ""
    for line in lines[4:]:
        if line.startswith("备注："):
            break
        match = ROW_PATTERN.match(line[:58])
        if not match:
            continue
        current_group = normalize_group(current_group, match.group("group"))
        gx_raw = line[gx_start:gx_end].strip()
        if not gx_raw or not gx_raw.isdigit():
            continue
        rows.append(
            {
                "school_key": "beijing_gongye_211",
                "school_name": "北京工业大学",
                "plan_year": "2025",
                "group_label": current_group,
                "major_name": match.group("major").strip(),
                "subject_type": match.group("subject"),
                "reselect_requirement": match.group("reselect"),
                "duration": match.group("duration"),
                "province": "广西",
                "plan_count_raw": gx_raw,
                "plan_count_numeric": gx_raw,
                "remarks": line[remarks_start:].strip(),
                "source_pdf": str(pdf_path),
                "source_pdf_name": pdf_path.name,
            }
        )
    return rows


def merge_rows(existing_rows: list[dict[str, str]], new_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in existing_rows + new_rows:
        key = (
            row.get("source_pdf_name", ""),
            row.get("plan_year", ""),
            row.get("major_name", ""),
            row.get("plan_count_raw", ""),
        )
        merged[key] = row
    return sorted(
        merged.values(),
        key=lambda row: (
            row.get("plan_year", ""),
            row.get("source_pdf_name", ""),
            row.get("major_name", ""),
        ),
    )


def merge_summary(existing_rows: list[dict[str, str]], new_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for row in existing_rows + new_rows:
        merged[row.get("source_pdf_name", "")] = row
    return sorted(merged.values(), key=lambda row: (row.get("plan_year", ""), row.get("source_pdf_name", "")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract BJUT 2025 reform-province Guangxi plan rows from cached PDF."
    )
    parser.add_argument("--pdf", type=Path, default=TARGET_PDF, help="Cached BJUT 2025 reform-province PDF path.")
    parser.add_argument(
        "--existing-guangxi",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_guangxi_plan_rows.csv",
        help="Existing BJUT Guangxi rows CSV to merge into.",
    )
    parser.add_argument(
        "--existing-summary",
        type=Path,
        default=Path("reports") / "beijing_gongye_cached_pdf_summary.csv",
        help="Existing BJUT PDF summary CSV to merge into.",
    )
    parser.add_argument(
        "--output-guangxi",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_guangxi_plan_rows.csv",
        help="Merged BJUT Guangxi plan rows output CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "beijing_gongye_cached_pdf_summary.csv",
        help="Merged BJUT PDF summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    new_rows = parse_guangxi_rows(args.pdf)
    merged_rows = merge_rows(read_rows(args.existing_guangxi), new_rows)
    write_rows(merged_rows, args.output_guangxi)

    new_summary = [
        {
            "source_pdf_name": args.pdf.name,
            "plan_year": "2025",
            "row_count_all": str(len(new_rows)),
            "row_count_guangxi": str(len(new_rows)),
            "distinct_majors_guangxi": str(len({row["major_name"] for row in new_rows})),
        }
    ]
    merged_summary = merge_summary(read_rows(args.existing_summary), new_summary)
    write_rows(merged_summary, args.summary_output)
    print(
        f"Merged {len(new_rows)} new BJUT 2025 Guangxi plan rows; total BJUT Guangxi rows now {len(merged_rows)}."
    )


if __name__ == "__main__":
    main()
