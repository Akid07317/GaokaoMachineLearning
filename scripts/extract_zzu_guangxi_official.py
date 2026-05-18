from __future__ import annotations

import argparse
import csv
import re
from io import StringIO
from pathlib import Path

try:
    import pandas as pd
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "This script requires the bundled runtime Python with pandas and pypdf available."
    ) from exc


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
SCHOOL_NAME = "郑州大学"
SCHOOL_KEY = "zhengzhou_daxue_211"
PLAN_PAGE_URL = "https://ao.zzu.edu.cn/xxgk/zsjh_/gx/a2025.htm"
PLAN_SOURCE_URL = "https://ao.zzu.edu.cn/__local/B/26/EB/BA1AA1F04FE2D060489EB73C48F_613A53AF_E94F.pdf"
SCORE_SOURCE_2024 = "https://ao.zzu.edu.cn/xxgk/lnlq/gx/a2024.htm"
SCORE_SOURCE_2025 = "https://ao.zzu.edu.cn/xxgk/lnlq/gx/a2025.htm"


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
        .replace("　", "")
        .strip()
    )


def repair_mojibake(text: str) -> str:
    fixed = text
    for _ in range(3):
        try:
            candidate = fixed.encode("latin1").decode("utf-8")
        except UnicodeError:
            break
        if candidate == fixed:
            break
        fixed = candidate
    return fixed.lstrip("\ufeff")


def read_pdf_lines(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text(extraction_mode="layout") or ""
        lines.extend(line.rstrip("\n") for line in text.splitlines() if line.strip())
    return lines


def parse_plan_code_and_length(raw_text: str) -> tuple[str, str]:
    match = re.match(r"(?P<code>\d+)\s*(?P<length>[一二三四五六七八九十]年)$", raw_text)
    if match:
        return match.group("code"), match.group("length")
    return raw_text.strip(), ""


def find_campus_index(parts: list[str]) -> int:
    for index in range(len(parts) - 1, 4, -1):
        token = parts[index]
        if token.endswith("校区"):
            return index
    raise ValueError(f"Could not find campus token in plan row: {parts}")


def normalize_plan_rows(pdf_path: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    lines = read_pdf_lines(pdf_path)
    output: list[dict[str, str]] = []
    requirement_map: dict[str, str] = {}

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped.startswith("广西"):
            continue
        parts = [part.strip() for part in re.split(r"\s{2,}", stripped) if part.strip()]
        if len(parts) < 9 or parts[1] != "物理类":
            continue

        province, subject_type, batch_type, plan_count, specialty = parts[:5]
        campus_index = find_campus_index(parts)
        tuition = parts[campus_index - 1]
        campus = parts[campus_index]
        requirement = "".join(parts[campus_index + 1 :])
        code_tokens = parts[5 : campus_index - 1]
        if len(code_tokens) == 1:
            code, length = parse_plan_code_and_length(code_tokens[0])
        else:
            code = code_tokens[0] if code_tokens else ""
            length = "".join(code_tokens[1:])

        requirement = requirement.replace(" ", "")
        remarks_parts = []
        if code:
            remarks_parts.append(f"国标代码:{code}")
        if length:
            remarks_parts.append(f"学制:{length}")
        if tuition:
            remarks_parts.append(f"收费标准:{tuition}")
        remarks = "; ".join(remarks_parts)

        normalized_specialty = normalize_name(specialty)
        requirement_map[normalized_specialty] = requirement
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": "2025",
                "province": province,
                "type": "本科普通批" if batch_type == "本科" else batch_type,
                "subject_type": subject_type,
                "college": "",
                "specialty": specialty,
                "plan_count": plan_count,
                "requirement": requirement,
                "selection_group": requirement,
                "campus": campus,
                "remarks": remarks,
                "weight": "",
                "record_id": f"zzu-plan-2025-{index}",
                "source_url": PLAN_SOURCE_URL,
                "introduction_link": PLAN_PAGE_URL,
                "source_slug": "zzu-plan-pdf",
            }
        )

    return output, requirement_map


def read_html_table(path: Path) -> pd.DataFrame:
    fixed_html = repair_mojibake(path.read_text(encoding="utf-8", errors="ignore"))
    tables = pd.read_html(StringIO(fixed_html))
    if not tables:
        raise ValueError(f"No tables found in {path}")
    table = tables[0].fillna("")
    table.columns = [str(column) for column in table.columns]
    return table


def as_int_string(value: object) -> str:
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    match = re.search(r"\d+", text.replace(",", ""))
    return match.group(0) if match else ""


def normalize_score_rows(
    table: pd.DataFrame,
    year: str,
    source_url: str,
    requirement_map: dict[str, str],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for _, row in table.iterrows():
        category = str(row.iloc[0]).strip()
        if "物理类" not in category:
            continue
        major = str(row.iloc[1]).strip()
        if not major or "总共" in major or (major.startswith("共") and "专业" in major):
            continue

        highest_score = as_int_string(row.iloc[2])
        minimum_score = as_int_string(row.iloc[3])
        lowest_score_ranking = as_int_string(row.iloc[5]) if len(row) > 5 else ""
        if not minimum_score:
            continue

        normalized_major = normalize_name(major)
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": year,
                "province": "广西",
                "type": "本科普通批",
                "science_category": "物理类",
                "major": major,
                "requirement": requirement_map.get(normalized_major, "物理类"),
                "campus": "",
                "remarks": "",
                "highest_score": highest_score,
                "minimum_score": minimum_score,
                "lowest_score_ranking": lowest_score_ranking,
                "record_id": f"zzu-score-{year}-{normalized_major}",
                "source_url": source_url,
            }
        )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Zhengzhou University Guangxi physics plan and score rows from official cached sources."
    )
    parser.add_argument(
        "--plan-pdf",
        type=Path,
        default=Path("raw_data") / "zhengzhou_direct" / "zzzu_gx_plan_2025.pdf",
        help="Cached 2025 Guangxi plan PDF.",
    )
    parser.add_argument(
        "--score-2024-html",
        type=Path,
        default=Path("raw_data") / "zhengzhou_direct" / "zzzu_lnlq_gx_a2024.html",
        help="Cached 2024 Guangxi score HTML page.",
    )
    parser.add_argument(
        "--score-2025-html",
        type=Path,
        default=Path("raw_data") / "zhengzhou_direct" / "zzzu_lnlq_gx_a2025.html",
        help="Cached 2025 Guangxi score HTML page.",
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_pdf_structured" / "zzu_guangxi_plan_rows.csv",
        help="Structured Guangxi plan output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "zzu_guangxi_score_rows.csv",
        help="Structured Guangxi score output CSV.",
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
        default=Path("reports") / "zzu_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    plan_rows, requirement_map = normalize_plan_rows(args.plan_pdf)
    score_2024_table = read_html_table(args.score_2024_html)
    score_2025_table = read_html_table(args.score_2025_html)
    score_rows = normalize_score_rows(score_2024_table, "2024", SCORE_SOURCE_2024, requirement_map)
    score_rows.extend(normalize_score_rows(score_2025_table, "2025", SCORE_SOURCE_2025, requirement_map))

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
            "score_rows_2024": str(sum(1 for row in score_rows if row["year"] == "2024")),
            "score_rows_2025": str(sum(1 for row in score_rows if row["year"] == "2025")),
            "score_rows_total": str(len(score_rows)),
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(
        f"Wrote {len(plan_rows)} Zhengzhou Guangxi plan rows and {len(score_rows)} score rows."
    )


if __name__ == "__main__":
    main()
