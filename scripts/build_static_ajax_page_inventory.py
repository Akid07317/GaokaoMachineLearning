from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.static_ajax_page_inventory import (
    build_page_record,
    build_school_summary,
    discover_static_ajax_pages,
    write_page_records,
    write_summary_rows,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory static-front AJAX admissions pages and summarize their endpoint/filter metadata."
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path("raw_data"),
        help="Root directory containing fetched raw HTML pages.",
    )
    parser.add_argument(
        "--pages-output",
        type=Path,
        default=Path("reports") / "static_ajax_page_inventory.csv",
        help="Output CSV with one row per static AJAX page.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "static_ajax_school_summary.csv",
        help="Output CSV summarizing static AJAX page coverage per school.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    pages = discover_static_ajax_pages(args.raw_root)
    records = [build_page_record(page, args.raw_root) for page in pages]
    summaries = build_school_summary(records)
    write_page_records(records, args.pages_output)
    write_summary_rows(summaries, args.summary_output)
    print(
        f"Wrote {len(records)} page records to {args.pages_output} and "
        f"{len(summaries)} school summaries to {args.summary_output}."
    )


if __name__ == "__main__":
    main()
