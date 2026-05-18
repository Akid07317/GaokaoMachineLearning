from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_focus import (
    build_school_matrix,
    filter_engineering_targets,
    read_csv_rows,
    read_engineering_schools,
    write_dict_rows,
    write_target_rows,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the strong-engineering focus round from 211 crawl outputs."
    )
    parser.add_argument(
        "--schools",
        type=Path,
        default=Path("configs") / "engineering_focus_211_non985.csv",
        help="Engineering school configuration CSV.",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path("reports") / "discovery_211_second_round_targets.csv",
        help="Second-round target list CSV.",
    )
    parser.add_argument(
        "--fetch-log",
        type=Path,
        default=Path("reports") / "discovery_211_second_round_fetch_full.csv",
        help="Second-round fetch log CSV.",
    )
    parser.add_argument(
        "--target-output",
        type=Path,
        default=Path("reports") / "engineering_focus_targets.csv",
        help="Focused engineering target output CSV.",
    )
    parser.add_argument(
        "--matrix-output",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix.csv",
        help="Focused engineering school matrix output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    schools = read_engineering_schools(args.schools)
    target_rows = read_csv_rows(args.targets)
    fetch_rows = read_csv_rows(args.fetch_log)
    targets = filter_engineering_targets(target_rows, schools)
    matrix = build_school_matrix(schools, targets, fetch_rows)
    write_target_rows(targets, args.target_output)
    write_dict_rows(matrix, args.matrix_output)
    print(
        f"Built engineering focus round: {len(targets)} targets across "
        f"{len(matrix)} schools."
    )


if __name__ == "__main__":
    main()
