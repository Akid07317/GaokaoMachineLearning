from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.html_tables import (
    extract_tables_from_file,
    summarize_tables,
    write_summary_csv,
    write_table_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract HTML tables to CSV without third-party deps.")
    parser.add_argument("--input", required=True, type=Path, help="Input HTML file.")
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to store extracted table CSV files.",
    )
    parser.add_argument(
        "--prefix",
        help="Prefix for output CSV files. Defaults to the input stem.",
    )
    parser.add_argument(
        "--table-index",
        type=int,
        help="Only write the specified 1-based table index.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    tables = extract_tables_from_file(args.input)
    summaries = summarize_tables(tables)
    prefix = args.prefix or args.input.stem

    summary_path = args.output_dir / f"{prefix}_table_summary.csv"
    write_summary_csv(summaries, summary_path)

    if args.table_index is not None:
        selected = args.table_index
        if selected < 1 or selected > len(tables):
            raise SystemExit(f"table-index {selected} out of range; found {len(tables)} tables")
        output_path = args.output_dir / f"{prefix}_table_{selected:02d}.csv"
        write_table_csv(tables[selected - 1], output_path)
        print(f"Extracted table {selected} to {output_path} and summary to {summary_path}")
        return

    for index, table in enumerate(tables, start=1):
        output_path = args.output_dir / f"{prefix}_table_{index:02d}.csv"
        write_table_csv(table, output_path)
    print(f"Extracted {len(tables)} tables to {args.output_dir} and summary to {summary_path}")


if __name__ == "__main__":
    main()
