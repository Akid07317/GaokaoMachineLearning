from __future__ import annotations

import argparse
from pathlib import Path
import sys
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_api_targets import build_engineering_api_targets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a CSV of API/JSON targets exposed by core A1/A2 engineering school pages."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_api_targets_a1_a2.csv",
        help="Output CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_engineering_api_targets()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_id",
        "source_name",
        "segment",
        "target_kind",
        "url",
        "method",
        "request_body",
        "target_slug",
        "file_suffix",
        "notes",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} engineering API targets to {args.output}.")


if __name__ == "__main__":
    main()
