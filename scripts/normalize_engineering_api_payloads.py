from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_api_normalize import normalize_api_payloads, read_api_fetch_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize fetched engineering API payloads into structured CSV tables."
    )
    parser.add_argument(
        "--fetch-log",
        type=Path,
        default=Path("reports") / "engineering_api_fetch_a1_a2.csv",
        help="API fetch log CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("clean_data") / "engineering_api_a1_a2",
        help="Directory for normalized CSV tables.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("reports") / "engineering_api_payload_summary.csv",
        help="Summary CSV for normalization results.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    fetch_rows = read_api_fetch_rows(args.fetch_log)
    summary_rows = normalize_api_payloads(
        fetch_rows,
        project_root=PROJECT_ROOT,
        output_dir=args.output_dir,
        summary_path=args.summary,
    )
    print(
        f"Normalized {len(summary_rows)} payload entries into "
        f"{args.output_dir} with summary {args.summary}."
    )


if __name__ == "__main__":
    main()
