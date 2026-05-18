from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_extract import (
    build_a1_a2_core_targets,
    extract_target_tables,
    read_rows,
    write_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract HTML tables for A1/A2 core engineering schools into CSV files."
    )
    parser.add_argument(
        "--segments",
        type=Path,
        default=Path("reports") / "engineering_focus_second_round_segments_520_master.csv",
        help="Segment CSV with A1/A2 core labels.",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path("reports") / "engineering_targets_520_master.csv",
        help="Master target CSV.",
    )
    parser.add_argument(
        "--fetch-log",
        type=Path,
        default=Path("reports") / "engineering_fetch_520_master.csv",
        help="Master fetch log CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs") / "extracted" / "engineering_core_a1_a2",
        help="Directory for extracted table CSVs.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("reports") / "engineering_core_a1_a2_table_manifest.csv",
        help="Manifest CSV output path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    segment_rows = read_rows(args.segments)
    target_rows = read_rows(args.targets)
    fetch_rows = read_rows(args.fetch_log)
    targets = build_a1_a2_core_targets(segment_rows, target_rows, fetch_rows)
    manifest = extract_target_tables(
        targets,
        project_root=PROJECT_ROOT,
        output_dir=args.output_dir,
    )
    write_manifest(manifest, args.manifest)
    ok_count = sum(1 for row in manifest if row["status"] == "ok")
    nonzero_count = sum(1 for row in manifest if row["status"] == "ok" and int(row["table_count"]) > 0)
    print(
        f"Extracted A1/A2 core tables for {len(manifest)} pages: "
        f"{ok_count} parsed, {nonzero_count} with at least one table. "
        f"Manifest written to {args.manifest}."
    )


if __name__ == "__main__":
    main()
