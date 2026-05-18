from __future__ import annotations

import argparse
import csv
from pathlib import Path


try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "pypdf is required for this script. Run it with the bundled runtime Python from load_workspace_dependencies."
    ) from exc


SCHOOL_NAME = "河北工业大学"
SCHOOL_KEY = "hebei_gongye_211"
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


def extract_rows(pdf_path: Path, plan_year: str, source_url: str) -> list[dict[str, str]]:
    lines = read_layout_lines(pdf_path)
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
            rows[-1]["specialty"] = f"{rows[-1]['specialty']}{left.strip()}"
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
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": plan_year,
                "province": "广西",
                "type": "本科普通批",
                "subject_type": "物理类",
                "college": current_college,
                "specialty": major,
                "plan_count": gx_raw,
                "requirement": "",
                "selection_group": "",
                "campus": "",
                "remarks": f"总计划={total_raw}",
                "weight": "",
                "record_id": f"hebut-plan-{plan_year}-{current_college}-{major}",
                "source_url": source_url,
                "introduction_link": source_url,
                "source_slug": "hebut-official-pdf",
            }
        )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Hebut Guangxi plan rows from official plan PDFs."
    )
    parser.add_argument("--pdf", type=Path, required=True, help="Official Hebut plan PDF path.")
    parser.add_argument("--plan-year", required=True, help="Plan year, e.g. 2024 or 2025.")
    parser.add_argument("--source-url", required=True, help="Official source URL for the PDF.")
    parser.add_argument(
        "--output-guangxi",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "hebei_gongye_guangxi_plan_rows.csv",
        help="Output CSV for Guangxi-only extracted rows.",
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
        default=Path("reports") / "hebei_gongye_cached_pdf_summary.csv",
        help="Summary CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    existing_output_rows = [row for row in read_rows(args.output_guangxi) if row.get("year") != args.plan_year]
    new_rows = extract_rows(args.pdf, args.plan_year, args.source_url)
    output_rows = merge_rows(existing_output_rows, new_rows, ["school_key", "year", "province", "record_id"])
    output_rows.sort(key=lambda row: (row.get("year", ""), row.get("college", ""), row.get("specialty", "")))
    write_rows(output_rows, args.output_guangxi, PLAN_FIELDS)

    merged_plan_rows = merge_rows(
        drop_school_rows(read_rows(args.plan_merged), SCHOOL_KEY),
        output_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    write_rows(merged_plan_rows, args.plan_merged, PLAN_FIELDS)

    year_counts: dict[str, int] = {}
    year_sources: dict[str, str] = {}
    for row in output_rows:
        year_counts[row["year"]] = year_counts.get(row["year"], 0) + 1
        year_sources[row["year"]] = row.get("source_url", "")
    summary_rows = [
        {
            "source_pdf_name": year_sources.get(year, "").split("/")[-1],
            "plan_year": year,
            "row_count_guangxi": str(count),
            "distinct_majors_guangxi": str(len({r["specialty"] for r in output_rows if r["year"] == year})),
        }
        for year, count in sorted(year_counts.items())
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Wrote {len(new_rows)} Hebut Guangxi plan rows for {args.plan_year}.")


if __name__ == "__main__":
    main()
