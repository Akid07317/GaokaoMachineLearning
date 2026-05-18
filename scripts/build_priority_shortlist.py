from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.discovery_filter import (
    categorize_candidate,
    read_candidates,
    sort_candidates,
    write_candidates,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a prioritized shortlist from discovery candidate links."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports") / "discovery_candidates.csv",
        help="Candidate link CSV from discovery crawl.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "discovery_candidates_priority.csv",
        help="Filtered shortlist CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_candidates(args.input)
    shortlisted = sort_candidates([categorize_candidate(row) for row in rows])
    write_candidates(shortlisted, args.output)
    print(
        f"Prioritized {len(shortlisted)} candidate links into "
        f"{args.output}."
    )


if __name__ == "__main__":
    main()
