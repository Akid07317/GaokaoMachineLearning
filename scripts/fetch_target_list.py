from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.second_round import read_priority_candidates
from gaokao_planner.source_fetch import FetchResult, fetch_single_url, write_fetch_log


def slugify_seed(seed_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", seed_id).strip("_") or "seed"


def slugify_url(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", url)[:120].strip("_") or "page"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch a CSV list of focused URLs into a local cache."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports") / "discovery_211_second_round_targets.csv",
        help="CSV of second-round targets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("raw_data") / "second_round_211",
        help="Directory for fetched target pages.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("reports") / "discovery_211_second_round_fetch.csv",
        help="CSV fetch log path.",
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
    rows = read_priority_candidates(args.input)
    results: list[FetchResult] = []
    for row in rows:
        seed_id = slugify_seed(row.get("seed_id", "seed"))
        target_url = row.get("target_url", "")
        slug = slugify_url(target_url)
        output_path = args.output_dir / seed_id / f"{slug}.html"
        result = fetch_single_url(
            target_url,
            output_path=output_path,
            timeout=args.timeout,
            verify_ssl=not args.insecure,
            source_id=seed_id,
        )
        results.append(result)
    write_fetch_log(results, args.log_path)
    success = sum(result.status == "ok" for result in results)
    print(
        f"Fetched {len(results)} second-round targets: {success} ok. "
        f"Log written to {args.log_path}."
    )


if __name__ == "__main__":
    main()
