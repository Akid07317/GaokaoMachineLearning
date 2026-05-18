from __future__ import annotations

import argparse
import csv
from io import StringIO
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
    / "donghua_211"
    / "http_zs.dhu.edu.cn_2026_0227_c25199a371750_page.htm.html"
)
SOURCE_URL = "http://zs.dhu.edu.cn/2026/0227/c25199a371750/page.htm"
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


def recover_mojibake(text: str) -> str:
    raw_text = "" if text is None else str(text)
    if not raw_text.strip():
        return ""
    try:
        recovered = raw_text.encode("latin1").decode("utf-8")
    except Exception:
        recovered = raw_text
    return clean_cell(recovered)


def select_score_table(source_html: Path) -> "pd.DataFrame":
    text = source_html.read_text(encoding="utf-8", errors="ignore")
    tables = pd.read_html(StringIO(text))
    for table in tables:
        if table.shape[1] != 6:
            continue
        first_row = [recover_mojibake(str(value)) for value in table.iloc[0].tolist()]
        if first_row == ["省份", "选考科类", "专业", "最高分", "最低分", "平均分"]:
            return table
    raise SystemExit(f"Could not find Donghua Guangxi score table in {source_html}.")


def normalize_score_rows(df: "pd.DataFrame") -> list[dict[str, str]]:
    df.columns = ["province", "science_category", "major", "highest_score", "minimum_score", "average_score"]
    rows: list[dict[str, str]] = []
    for idx, row in df.iloc[1:].iterrows():
        province = recover_mojibake(str(row["province"]))
        science_category = recover_mojibake(str(row["science_category"]))
        major = recover_mojibake(str(row["major"]))
        highest_score = recover_mojibake(str(row["highest_score"]))
        minimum_score = recover_mojibake(str(row["minimum_score"]))
        if province != "广西":
            continue
        if "物" not in science_category:
            continue
        if major == "科类总计":
            continue
        rows.append(
            {
                "school_name": "东华大学",
                "school_key": "donghua_211",
                "year": "2025",
                "province": province,
                "type": "本科一批",
                "science_category": science_category,
                "major": major,
                "requirement": science_category,
                "campus": "",
                "remarks": "",
                "highest_score": highest_score,
                "minimum_score": minimum_score,
                "lowest_score_ranking": "",
                "record_id": f"dhu-score-2025-{idx}",
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
        description="Extract Donghua official Guangxi score rows from the article table."
    )
    parser.add_argument("--source-html", type=Path, default=SOURCE_HTML, help="Cached Donghua Guangxi score article HTML.")
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics major-score seed CSV to update.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "article_structured" / "dhu_guangxi_score_rows.csv",
        help="Donghua Guangxi score rows output CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "dhu_guangxi_score_article_summary.csv",
        help="Donghua score article extraction summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    table = select_score_table(args.source_html)
    score_rows = normalize_score_rows(table)
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    existing_score_rows = read_rows(args.score_major_merged)
    merged_score_rows = merge_rows(
        existing_score_rows,
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("science_category", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": "donghua_211",
            "school_name": "东华大学",
            "province": "广西",
            "year": "2025",
            "score_rows": str(len(score_rows)),
            "science_categories": "|".join(sorted({row["science_category"] for row in score_rows})),
            "source_url": SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(score_rows)} Donghua Guangxi physics-major score rows.")


if __name__ == "__main__":
    main()
