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
    "source_track",
    "latest_year",
    "reference_year",
    "plan_source_url",
    "plan_source_origin",
    "score_source_url",
    "score_source_origin",
    "backup_score_url",
    "has_plan_source",
    "has_score_source",
    "source_pack_notes",
    "record_id",
    "source_slug",
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
        description="Build a 32-school official source pack for Guangxi engineering targets."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="Engineering target matrix CSV.",
    )
    parser.add_argument(
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Current pipeline status CSV.",
    )
    parser.add_argument(
        "--latest-snapshot",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_snapshot_merged.csv",
        help="Latest primary snapshot CSV.",
    )
    parser.add_argument(
        "--latest-profile",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_profile_merged.csv",
        help="Latest primary profile CSV.",
    )
    parser.add_argument(
        "--actionable-evidence-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_actionable_evidence_pack_merged.csv",
        help="Actionable evidence pack CSV.",
    )
    parser.add_argument(
        "--cold-entry-registry",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_cold_queue_entry_registry_merged.csv",
        help="Cold queue entry registry CSV.",
    )
    parser.add_argument(
        "--fallback-registry",
        type=Path,
        default=Path("configs") / "actionable_source_fallback_registry.csv",
        help="Fallback source registry CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_official_source_pack_merged.csv",
        help="Output merged source pack CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_official_source_pack_school_summary.csv",
        help="School summary CSV output.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_official_source_pack_coverage_rollup.csv",
        help="Coverage rollup CSV output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    matrix_rows = read_rows(args.matrix)
    pipeline_rows = read_rows(args.pipeline_status)
    snapshot_rows = read_rows(args.latest_snapshot)
    profile_rows = read_rows(args.latest_profile)
    evidence_rows = read_rows(args.actionable_evidence_pack)
    cold_rows = read_rows(args.cold_entry_registry)
    fallback_rows = read_rows(args.fallback_registry)

    pipeline_by_key = {normalize_text(row.get("school_key", "")): row for row in pipeline_rows}
    snapshot_by_key = {normalize_text(row.get("school_key", "")): row for row in snapshot_rows}
    profile_by_key = {normalize_text(row.get("school_key", "")): row for row in profile_rows}
    evidence_by_key = {normalize_text(row.get("school_key", "")): row for row in evidence_rows}
    cold_by_key = {normalize_text(row.get("school_key", "")): row for row in cold_rows}
    fallback_by_key = {normalize_text(row.get("school_key", "")): row for row in fallback_rows}

    merged_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    main_chain_count = 0
    cold_queue_count = 0
    plan_count = 0
    score_count = 0

    for row in matrix_rows:
        school_key = normalize_text(row.get("seed_id", ""))
        school_name = normalize_text(row.get("source_name", school_key))
        pipeline = pipeline_by_key.get(school_key, {})
        snapshot = snapshot_by_key.get(school_key, {})
        profile = profile_by_key.get(school_key, {})
        evidence = evidence_by_key.get(school_key, {})
        cold = cold_by_key.get(school_key, {})
        fallback = fallback_by_key.get(school_key, {})

        plan_source_url = ""
        plan_source_origin = ""
        score_source_url = ""
        score_source_origin = ""
        backup_score_url = ""
        source_track = "unresolved"

        if normalize_text(snapshot.get("plan_source_url", "")):
            plan_source_url = normalize_text(snapshot.get("plan_source_url", ""))
            plan_source_origin = "primary_latest_snapshot"
            source_track = "main_chain"
        elif normalize_text(profile.get("latest_plan_source_url", "")):
            plan_source_url = normalize_text(profile.get("latest_plan_source_url", ""))
            plan_source_origin = "primary_latest_profile"
            source_track = "main_chain"
        elif normalize_text(evidence.get("plan_source_url", "")):
            plan_source_url = normalize_text(evidence.get("plan_source_url", ""))
            plan_source_origin = "actionable_evidence_pack"
            source_track = "main_chain"
        elif normalize_text(cold.get("plan_entry_url", "")):
            plan_source_url = normalize_text(cold.get("plan_entry_url", ""))
            plan_source_origin = "cold_queue_entry_registry"
            source_track = "cold_queue"
        elif normalize_text(fallback.get("plan_source_url", "")):
            plan_source_url = normalize_text(fallback.get("plan_source_url", ""))
            plan_source_origin = "fallback_registry"
            source_track = "main_chain"

        if normalize_text(snapshot.get("score_source_url", "")):
            score_source_url = normalize_text(snapshot.get("score_source_url", ""))
            score_source_origin = "primary_latest_snapshot"
            source_track = "main_chain" if source_track == "unresolved" else source_track
        elif normalize_text(profile.get("latest_score_source_url", "")):
            score_source_url = normalize_text(profile.get("latest_score_source_url", ""))
            score_source_origin = "primary_latest_profile"
            source_track = "main_chain" if source_track == "unresolved" else source_track
        elif normalize_text(evidence.get("score_source_url", "")):
            score_source_url = normalize_text(evidence.get("score_source_url", ""))
            score_source_origin = "actionable_evidence_pack"
            source_track = "main_chain" if source_track == "unresolved" else source_track
        elif normalize_text(cold.get("score_entry_url", "")):
            score_source_url = normalize_text(cold.get("score_entry_url", ""))
            score_source_origin = "cold_queue_entry_registry"
            source_track = "cold_queue" if source_track == "unresolved" else source_track
        elif normalize_text(fallback.get("score_source_url", "")):
            score_source_url = normalize_text(fallback.get("score_source_url", ""))
            score_source_origin = "fallback_registry"
            source_track = "main_chain" if source_track == "unresolved" else source_track

        backup_score_url = normalize_text(cold.get("score_alt_url", ""))
        if not backup_score_url:
            backup_score_url = normalize_text(cold.get("score_entry_url", ""))

        has_plan_source = "true" if plan_source_url else "false"
        has_score_source = "true" if score_source_url else "false"
        if source_track == "main_chain":
            main_chain_count += 1
        elif source_track == "cold_queue":
            cold_queue_count += 1
        if has_plan_source == "true":
            plan_count += 1
        if has_score_source == "true":
            score_count += 1

        merged_rows.append(
            {
                "school_key": school_key,
                "school_name": school_name,
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(pipeline.get("pipeline_status", "")),
                "source_track": source_track,
                "latest_year": normalize_text(snapshot.get("latest_year", profile.get("latest_year", ""))),
                "reference_year": normalize_text(evidence.get("reference_year", "")),
                "plan_source_url": plan_source_url,
                "plan_source_origin": plan_source_origin,
                "score_source_url": score_source_url,
                "score_source_origin": score_source_origin,
                "backup_score_url": backup_score_url,
                "has_plan_source": has_plan_source,
                "has_score_source": has_score_source,
                "source_pack_notes": "统一收口主链来源、行动证据来源、冷队列入口与回填来源，供 32 校快速核验与后续补数使用",
                "record_id": f"{school_key}-official-source-pack",
                "source_slug": "official_source_pack",
            }
        )
        school_summary_rows.append(
            {
                "school_key": school_key,
                "school_name": school_name,
                "official_source_pack_rows": "1",
            }
        )

    merged_rows.sort(key=lambda item: (item["engineering_tier"], item["school_key"]))
    school_summary_rows.sort(key=lambda item: item["school_key"])

    write_rows(args.output, merged_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "official_source_pack_rows"],
    )
    write_rows(
        args.coverage_output,
        [
            {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
            {"metric": "official_source_pack_schools", "value": str(len(merged_rows))},
            {"metric": "official_source_pack_coverage_ratio", "value": f"{len(merged_rows) / TARGET_TOTAL:.4f}"},
            {"metric": "official_source_pack_main_chain_schools", "value": str(main_chain_count)},
            {"metric": "official_source_pack_cold_queue_schools", "value": str(cold_queue_count)},
            {"metric": "official_source_pack_plan_source_schools", "value": str(plan_count)},
            {"metric": "official_source_pack_score_source_schools", "value": str(score_count)},
        ],
        ["metric", "value"],
    )

    print(f"Wrote official source pack for {len(merged_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
