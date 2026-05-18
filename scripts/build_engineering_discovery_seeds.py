from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_discovery import (
    build_engineering_seed_rows,
    read_rows,
    write_rows,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a discovery seed file for the current engineering focus pool."
    )
    parser.add_argument(
        "--engineering-schools",
        type=Path,
        default=Path("configs") / "engineering_focus_211_non985.csv",
        help="Engineering focus school configuration CSV.",
    )
    parser.add_argument(
        "--discovery-seeds",
        type=Path,
        default=Path("configs") / "discovery_seeds_211_non985_full.csv",
        help="Master discovery seeds CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("configs") / "discovery_seeds_engineering_520_fullsweep.csv",
        help="Output CSV for engineering full-sweep seeds.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Override crawl max depth for engineering full sweep.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=18,
        help="Override crawl max pages for engineering full sweep.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    engineering_rows = read_rows(args.engineering_schools)
    discovery_rows = read_rows(args.discovery_seeds)
    seed_rows, missing_seed_ids = build_engineering_seed_rows(
        engineering_rows,
        discovery_rows,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
    )
    write_rows(seed_rows, args.output)
    print(
        f"Built {len(seed_rows)} engineering discovery seeds into {args.output}."
    )
    if missing_seed_ids:
        print("Missing discovery seeds for:", ", ".join(missing_seed_ids))


if __name__ == "__main__":
    main()
