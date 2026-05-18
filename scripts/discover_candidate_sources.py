from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.link_discovery import (
    crawl_seed,
    read_discovery_seeds,
    write_candidate_links,
    write_pages_log,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Broad crawl official admissions seed sites and collect candidate links."
    )
    parser.add_argument(
        "--seed-file",
        type=Path,
        default=Path("configs") / "discovery_seeds.csv",
        help="CSV file containing crawl seeds.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("raw_data") / "discovery",
        help="Directory to cache fetched pages.",
    )
    parser.add_argument(
        "--pages-log",
        type=Path,
        default=Path("reports") / "discovery_pages.csv",
        help="Output CSV for page-level crawl logs.",
    )
    parser.add_argument(
        "--candidate-log",
        type=Path,
        default=Path("reports") / "discovery_candidates.csv",
        help="Output CSV for scored candidate URLs.",
    )
    parser.add_argument(
        "--seed-id",
        action="append",
        default=[],
        help="Only crawl the specified seed_id values. Repeatable.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification for requests.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    seeds = read_discovery_seeds(args.seed_file)
    if args.seed_id:
        wanted = set(args.seed_id)
        seeds = [seed for seed in seeds if seed.seed_id in wanted]

    all_pages = []
    all_candidates = []
    for seed in seeds:
        pages, candidates = crawl_seed(
            seed,
            cache_dir=args.cache_dir,
            timeout=args.timeout,
            verify_ssl=not args.insecure,
        )
        all_pages.extend(pages)
        all_candidates.extend(candidates)

    write_pages_log(all_pages, args.pages_log)
    write_candidate_links(all_candidates, args.candidate_log)
    print(
        f"Crawled {len(seeds)} seeds, cached {len(all_pages)} pages, "
        f"ranked {len(all_candidates)} candidate links."
    )


if __name__ == "__main__":
    main()
