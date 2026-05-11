from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean Guangxi gaokao source data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    rank_parser = subparsers.add_parser(
        "add-rank-interval",
        help="Add rank_start and rank_end columns to a score-rank CSV.",
    )
    rank_parser.add_argument("--input", required=True, type=Path)
    rank_parser.add_argument("--output", required=True, type=Path)

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "add-rank-interval":
        from gaokao_planner.io import read_csv, write_csv
        from gaokao_planner.rank import add_rank_interval

        data = read_csv(args.input)
        cleaned = add_rank_interval(data)
        write_csv(cleaned, args.output)


if __name__ == "__main__":
    main()
