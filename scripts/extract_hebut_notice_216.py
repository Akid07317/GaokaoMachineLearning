from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


SOURCE_HTML = Path("raw_data") / "official_followup" / "hebei_gongye_211" / "notice_216.html"
SOURCE_URL = "https://zs.hebut.edu.cn/2025-07-12/216.html"


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
        description="Extract Hebut Guangxi batch-completion notice rows from the public notice page."
    )
    parser.add_argument("--source-html", type=Path, default=SOURCE_HTML, help="Hebut public notice HTML.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "hebei_gongye_guangxi_batch_notice_rows.csv",
        help="Structured Hebut Guangxi batch-completion rows output CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "hebei_gongye_notice_216_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    text = args.source_html.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"广西壮族自治区(?P<batch>[^招]{1,20})招生(?P<count>\d+)人（(?P<date>[^）]+)）")
    rows: list[dict[str, str]] = []
    for index, match in enumerate(pattern.finditer(text), start=1):
        rows.append(
            {
                "school_key": "hebei_gongye_211",
                "school_name": "河北工业大学",
                "province": "广西",
                "batch_name": match.group("batch").strip(),
                "admit_count": match.group("count").strip(),
                "notice_date_text": match.group("date").strip(),
                "source_url": SOURCE_URL,
                "record_id": f"hebut-notice-216-{index}",
            }
        )
    write_rows(rows, args.output)
    summary_rows = [
        {
            "school_key": "hebei_gongye_211",
            "school_name": "河北工业大学",
            "rows": str(len(rows)),
            "province": "广西",
            "source_url": SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output)
    print(f"Extracted {len(rows)} Hebut Guangxi batch-notice rows.")


if __name__ == "__main__":
    main()
