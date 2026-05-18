from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_subdivide import classify_row, read_rows, write_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Subdivide the engineering focus matrix into second-round segments."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520.csv",
        help="Engineering focus school matrix CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_focus_second_round_segments_520.csv",
        help="Second-round segmentation output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.input)
    classified = [classify_row(row) for row in rows]
    write_rows(classified, args.output)
    print(
        f"Built second-round segmentation for {len(classified)} engineering schools "
        f"into {args.output}."
    )


if __name__ == "__main__":
    main()
