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


AJAX_FAMILY_IDS = {
    "beijing_keji_211",
    "zhongguo_kuangye_211",
    "beijing_jiaotong_211",
    "zhongguo_shiyou_beijing_211",
    "zhongguo_dizhi_beijing_211",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a focused CSV of ajax-family API targets for additional engineering schools."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_api_targets_ajax_family.csv",
        help="Output CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = [row for row in build_engineering_api_targets() if row["source_id"] in AJAX_FAMILY_IDS]
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
    print(f"Wrote {len(rows)} ajax-family API targets to {args.output}.")


if __name__ == "__main__":
    main()
