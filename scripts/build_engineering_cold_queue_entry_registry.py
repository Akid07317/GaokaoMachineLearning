from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "engineering_tier",
    "pipeline_status",
    "block_type",
    "evidence_kind",
    "plan_entry_url",
    "score_entry_url",
    "score_alt_url",
    "cached_plan_evidence_path",
    "cached_score_evidence_path",
    "cached_support_evidence_path",
    "extracted_api_hint",
    "plan_entry_present",
    "score_entry_present",
    "record_id",
    "source_slug",
    "notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return str(value or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build cold-queue official entry registry for blocked engineering target schools."
    )
    parser.add_argument(
        "--seed-registry",
        type=Path,
        default=Path("configs") / "cold_queue_entry_registry_seed.csv",
        help="Manual seed registry for blocked schools with official entry URLs.",
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="Engineering target school matrix CSV.",
    )
    parser.add_argument(
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Current pipeline status CSV used to carry pipeline_status into the registry.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_cold_queue_entry_registry_merged.csv",
        help="Output merged registry CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_cold_queue_entry_registry_school_summary.csv",
        help="School summary CSV output.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_cold_queue_entry_registry_coverage_rollup.csv",
        help="Coverage rollup CSV output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    seed_rows = read_rows(args.seed_registry)
    matrix_rows = read_rows(args.matrix)
    pipeline_rows = read_rows(args.pipeline_status)

    matrix_by_key = {normalize_text(row.get("seed_id", "")): row for row in matrix_rows}
    pipeline_by_key = {normalize_text(row.get("school_key", "")): row for row in pipeline_rows}

    merged_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    both_entry_count = 0
    plan_only_count = 0
    score_only_count = 0

    for row in seed_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        matrix_row = matrix_by_key.get(school_key, {})
        pipeline_row = pipeline_by_key.get(school_key, {})
        plan_entry_url = normalize_text(row.get("plan_entry_url", ""))
        score_entry_url = normalize_text(row.get("score_entry_url", ""))
        plan_present = "true" if plan_entry_url else "false"
        score_present = "true" if score_entry_url else "false"
        if plan_present == "true" and score_present == "true":
            both_entry_count += 1
        elif plan_present == "true":
            plan_only_count += 1
        elif score_present == "true":
            score_only_count += 1

        merged_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(matrix_row.get("source_name", school_key)),
                "engineering_tier": normalize_text(matrix_row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(pipeline_row.get("pipeline_status", "")),
                "block_type": normalize_text(row.get("block_type", "")),
                "evidence_kind": normalize_text(row.get("evidence_kind", "")),
                "plan_entry_url": plan_entry_url,
                "score_entry_url": score_entry_url,
                "score_alt_url": normalize_text(row.get("score_alt_url", "")),
                "cached_plan_evidence_path": normalize_text(row.get("cached_plan_evidence_path", "")),
                "cached_score_evidence_path": normalize_text(row.get("cached_score_evidence_path", "")),
                "cached_support_evidence_path": normalize_text(row.get("cached_support_evidence_path", "")),
                "extracted_api_hint": normalize_text(row.get("extracted_api_hint", "")),
                "plan_entry_present": plan_present,
                "score_entry_present": score_present,
                "record_id": f"{school_key}-cold-queue-entry-registry",
                "source_slug": "official_cold_queue_entry_registry",
                "notes": normalize_text(row.get("notes", "")),
            }
        )

        school_summary_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(matrix_row.get("source_name", school_key)),
                "cold_queue_entry_rows": "1",
            }
        )

    merged_rows.sort(key=lambda item: (item["engineering_tier"], item["school_key"]))
    school_summary_rows.sort(key=lambda item: item["school_key"])

    write_rows(args.output, merged_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "cold_queue_entry_rows"],
    )
    write_rows(
        args.coverage_output,
        [
            {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
            {"metric": "cold_queue_entry_schools", "value": str(len(merged_rows))},
            {"metric": "cold_queue_entry_coverage_ratio", "value": f"{len(merged_rows) / TARGET_TOTAL:.4f}"},
            {"metric": "cold_queue_entry_plan_and_score_schools", "value": str(both_entry_count)},
            {"metric": "cold_queue_entry_plan_only_schools", "value": str(plan_only_count)},
            {"metric": "cold_queue_entry_score_only_schools", "value": str(score_only_count)},
        ],
        ["metric", "value"],
    )

    print(f"Wrote cold-queue entry registry for {len(merged_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
