from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.api_fetch import fetch_api_target, read_target_rows, write_api_fetch_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch a CSV list of JSON/API targets into a local cache."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports") / "engineering_api_targets_a1_a2.csv",
        help="CSV of API targets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("raw_data") / "engineering_api_a1_a2",
        help="Directory for fetched payloads.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("reports") / "engineering_api_fetch_a1_a2.csv",
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
    rows = read_target_rows(args.input)
    results = [
        fetch_api_target(
            row,
            output_dir=args.output_dir,
            timeout=args.timeout,
            verify_ssl=not args.insecure,
        )
        for row in rows
    ]
    write_api_fetch_log(results, args.log_path)
    success = sum(result.status == "ok" for result in results)
    print(
        f"Fetched {len(results)} API targets: {success} ok. "
        f"Log written to {args.log_path}."
    )


if __name__ == "__main__":
    main()
