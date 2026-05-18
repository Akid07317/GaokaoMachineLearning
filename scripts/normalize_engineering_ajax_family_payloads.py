from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_ajax_family_normalize import normalize_ajax_family_payloads


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize ajax-family engineering payloads into structured CSV tables."
    )
    parser.add_argument(
        "--fetch-log",
        type=Path,
        default=Path("reports") / "engineering_api_fetch_ajax_family.csv",
        help="Ajax-family fetch log CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("clean_data") / "engineering_api_ajax_family",
        help="Output directory for normalized CSV tables.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("reports") / "engineering_ajax_family_payload_summary.csv",
        help="Summary CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = normalize_ajax_family_payloads(
        args.fetch_log,
        project_root=PROJECT_ROOT,
        output_dir=args.output_dir,
        summary_path=args.summary,
    )
    print(
        f"Normalized {len(rows)} ajax-family datasets into "
        f"{args.output_dir} with summary {args.summary}."
    )


if __name__ == "__main__":
    main()
