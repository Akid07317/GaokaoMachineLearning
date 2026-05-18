from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.second_round import (
    read_priority_candidates,
    select_second_round_targets,
    write_second_round_targets,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Select focused second-round targets from first-pass candidate links."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports") / "discovery_211_full_candidates_priority.csv",
        help="Prioritized first-pass candidate CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "discovery_211_second_round_targets.csv",
        help="Output CSV for selected second-round targets.",
    )
    parser.add_argument(
        "--max-per-seed",
        type=int,
        default=8,
        help="Maximum number of second-round targets to keep per seed.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_priority_candidates(args.input)
    selected = select_second_round_targets(rows, max_per_seed=args.max_per_seed)
    write_second_round_targets(selected, args.output)
    print(f"Selected {len(selected)} second-round targets into {args.output}.")


if __name__ == "__main__":
    main()
