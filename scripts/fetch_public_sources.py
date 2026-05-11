from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.source_fetch import fetch_source, read_source_list, write_fetch_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch public Guangxi gaokao source pages and log the results."
    )
    parser.add_argument(
        "--source-list",
        type=Path,
        default=Path("source_list.csv"),
        help="CSV source registry path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("raw_data"),
        help="Directory for downloaded raw files.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("reports") / "fetch_status.csv",
        help="CSV path for fetch results.",
    )
    parser.add_argument(
        "--source-id",
        action="append",
        default=[],
        help="Specific source_id values to fetch. Repeatable.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-request timeout in seconds.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sources = read_source_list(args.source_list)
    if args.source_id:
        wanted = set(args.source_id)
        sources = [source for source in sources if source["source_id"] in wanted]

    results = [fetch_source(source, args.output_dir, timeout=args.timeout) for source in sources]
    write_fetch_log(results, args.log_path)

    success = sum(result.status == "ok" for result in results)
    partial = sum(result.status == "blocked_antibot_html" for result in results)
    failed = len(results) - success - partial

    print(
        f"Fetched {len(results)} sources: "
        f"{success} ok, {partial} anti-bot shells, {failed} failed. "
        f"Log written to {args.log_path}."
    )


if __name__ == "__main__":
    main()
