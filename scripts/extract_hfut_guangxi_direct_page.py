from __future__ import annotations

import argparse
import csv
from pathlib import Path


try:
    import pandas as pd
except Exception as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "pandas is required for this script. Run it with the bundled runtime Python from load_workspace_dependencies."
    ) from exc


SOURCE_HTML = (
    Path("raw_data")
    / "engineering_core_missing_supplemental"
    / "hefei_gongda_211"
    / "http_bkzs.hfut.edu.cn_f_zsjhAndLqfs_guangxi.html"
)
SOURCE_URL = "http://bkzs.hfut.edu.cn/f/zsjhAndLqfs/广西"
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


def clean_cell(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    return " ".join(text.split())


def normalize_detail_table(df: "pd.DataFrame") -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    df.columns = [
        "science_category",
        "specialty",
        "plan_count_2025",
        "admission_type",
        "score_2024_high",
        "score_2024_low",
        "score_2023_high",
        "score_2023_low",
        "score_2022_high",
        "score_2022_low",
    ]
    df = df.applymap(clean_cell)
    df = df[df["science_category"] == "物理类"].copy()

    plan_rows: list[dict[str, str]] = []
    score_rows: list[dict[str, str]] = []
    for idx, row in df.iterrows():
        specialty = row["specialty"]
        plan_count = row["plan_count_2025"]
        admission_type = row["admission_type"] or "普通批"
        if specialty and plan_count not in {"", "-"}:
            plan_rows.append(
                {
                    "school_name": "合肥工业大学",
                    "school_key": "hefei_gongda_211",
                    "year": "2025",
                    "province": "广西",
                    "type": admission_type,
                    "subject_type": "物理类",
                    "college": "",
                    "specialty": specialty,
                    "plan_count": plan_count,
                    "requirement": "",
                    "selection_group": "",
                    "campus": "",
                    "remarks": "",
                    "weight": "",
                    "record_id": f"hfut-plan-{idx}",
                    "source_url": SOURCE_URL,
                    "introduction_link": "",
                    "source_slug": "hfut-direct-guangxi",
                }
            )

        for year in ("2024", "2023", "2022"):
            highest = row[f"score_{year}_high"]
            lowest = row[f"score_{year}_low"]
            if lowest in {"", "-"}:
                continue
            score_rows.append(
                {
                    "school_name": "合肥工业大学",
                    "school_key": "hefei_gongda_211",
                    "year": year,
                    "province": "广西",
                    "type": admission_type,
                    "science_category": "物理类",
                    "major": specialty,
                    "requirement": "",
                    "campus": "",
                    "remarks": "",
                    "highest_score": highest if highest not in {"", "-"} else "",
                    "minimum_score": lowest,
                    "lowest_score_ranking": "",
                    "record_id": f"hfut-score-{year}-{idx}",
                    "source_url": SOURCE_URL,
                }
            )
    return plan_rows, score_rows


def normalize_overview_table(df: "pd.DataFrame") -> list[dict[str, str]]:
    df.columns = [
        "year",
        "physics_type",
        "physics_control_line",
        "physics_minimum_score",
        "history_type",
        "history_control_line",
        "history_minimum_score",
    ]
    df = df.applymap(clean_cell)
    rows: list[dict[str, str]] = []
    for _, row in df.iterrows():
        rows.append(
            {
                "province": "广西",
                "year": row["year"].replace("年", ""),
                "physics_type": row["physics_type"],
                "physics_control_line": row["physics_control_line"],
                "physics_minimum_score": row["physics_minimum_score"],
                "history_type": row["history_type"],
                "history_control_line": row["history_control_line"],
                "history_minimum_score": row["history_minimum_score"],
                "source_url": SOURCE_URL,
            }
        )
    return rows


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Guangxi plan and score seeds from the direct HFUT province detail page."
    )
    parser.add_argument("--source-html", type=Path, default=SOURCE_HTML, help="Cached HFUT Guangxi direct page HTML.")
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
        help="Merged Guangxi physics plan seed CSV to update.",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics major-score seed CSV to update.",
    )
    parser.add_argument(
        "--overview-output",
        type=Path,
        default=Path("clean_data") / "direct_page_structured" / "hfut_guangxi_overview_rows.csv",
        help="Overview table output CSV.",
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "direct_page_structured" / "hfut_guangxi_plan_rows.csv",
        help="HFUT Guangxi plan rows output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "direct_page_structured" / "hfut_guangxi_score_rows.csv",
        help="HFUT Guangxi expanded score rows output CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "hfut_guangxi_direct_page_summary.csv",
        help="HFUT direct page extraction summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    tables = pd.read_html(str(args.source_html))
    overview_rows = normalize_overview_table(tables[0])
    plan_rows, score_rows = normalize_detail_table(tables[1])

    write_rows(overview_rows, args.overview_output, list(overview_rows[0].keys()))
    write_rows(plan_rows, args.plan_output, PLAN_FIELDS)
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    merged_plan = merge_rows(
        read_rows(args.plan_merged),
        plan_rows,
        ["school_key", "year", "province", "type", "subject_type", "specialty", "plan_count", "source_url"],
    )
    merged_score = merge_rows(
        read_rows(args.score_major_merged),
        score_rows,
        ["school_key", "year", "province", "type", "science_category", "major", "minimum_score", "source_url"],
    )
    merged_plan.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    merged_score.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_plan, args.plan_merged, PLAN_FIELDS)
    write_rows(merged_score, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": "hefei_gongda_211",
            "school_name": "合肥工业大学",
            "overview_rows": str(len(overview_rows)),
            "plan_rows_2025_physics": str(len(plan_rows)),
            "score_rows_physics_expanded": str(len(score_rows)),
            "distinct_physics_majors_2025": str(len({row["specialty"] for row in plan_rows})),
            "source_url": SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(
        f"Extracted HFUT Guangxi direct page: {len(plan_rows)} plan rows and {len(score_rows)} physics score rows."
    )


if __name__ == "__main__":
    main()
