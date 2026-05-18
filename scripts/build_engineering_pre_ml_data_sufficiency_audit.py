#!/usr/bin/env python3
"""Audit pre-ML data sufficiency and build a targeted thickening queue.

This is a local-only audit. It quantifies years, field depth, group/mapping
signals, and repair needs for the 32-school main pool. It does not expand the
pool, fetch live sources, write canonical rows, or run ML.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

ACTION_BOARD = SEED_DIR / "guangxi_pre_ml_human_gpt_review_action_board_merged.csv"
POST_HUMAN = SEED_DIR / "guangxi_pre_ml_post_human_decision_intake_preview_merged.csv"
PLAN_SEED = SEED_DIR / "guangxi_physics_plan_seed_merged.csv"
SCORE_MAJOR_SEED = SEED_DIR / "guangxi_physics_score_major_seed_merged.csv"
SCORE_SUMMARY_SEED = SEED_DIR / "guangxi_physics_score_summary_seed_merged.csv"
PRIMARY_CANONICAL_SNAPSHOT = SEED_DIR / "guangxi_primary_physics_canonical_snapshot_merged.csv"
PRIMARY_CANONICAL_TREND = SEED_DIR / "guangxi_primary_canonical_trend_merged.csv"
LATEST_SNAPSHOT = SEED_DIR / "guangxi_primary_latest_snapshot_merged.csv"
GAP_FILL_APPLICATION = SEED_DIR / "guangxi_pre_ml_gap_fill_application_layer_merged.csv"
G4_CLOSEOUT = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_closeout_merged.csv"

AUDIT_OUT = SEED_DIR / "guangxi_pre_ml_data_sufficiency_audit_merged.csv"
QUEUE_OUT = SEED_DIR / "guangxi_pre_ml_data_thickening_priority_queue_merged.csv"
AUDIT_ROLLUP = REPORT_DIR / "engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv"
QUEUE_ROLLUP = REPORT_DIR / "engineering_pre_ml_data_thickening_priority_queue_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_data_sufficiency_audit.md"

TARGET_YEARS = {"2023", "2024", "2025"}

AUDIT_FIELDS = [
    "audit_rank",
    "school_key",
    "school_name",
    "current_bucket",
    "post_human_status",
    "selected_decision",
    "data_sufficiency_band",
    "thickening_priority",
    "broad_data_collection_needed",
    "targeted_collection_needed",
    "canonical_ml_entry_open",
    "canonical_rebuild_assessment_ready",
    "plan_seed_years",
    "score_major_years",
    "score_summary_years",
    "canonical_snapshot_years",
    "canonical_trend_pairs",
    "target_years_present",
    "target_years_missing",
    "year_depth_score",
    "latest_year",
    "latest_data_completeness",
    "latest_total_plan_count",
    "latest_minimum_score",
    "latest_minimum_rank",
    "latest_plan_group_count",
    "latest_plan_specialty_count",
    "latest_has_plan",
    "latest_has_score",
    "latest_has_rank",
    "trend_available",
    "professional_group_granularity_status",
    "candidate_group_codes",
    "missing_field_flags",
    "repair_or_thickening_focus",
    "recommended_next_action",
    "plan_source_url",
    "score_source_url",
    "source_record_ids",
    "record_id",
    "source_slug",
]

QUEUE_FIELDS = [
    "queue_rank",
    "school_key",
    "school_name",
    "priority",
    "queue_lane",
    "current_bucket",
    "post_human_status",
    "recommended_next_action",
    "repair_or_thickening_focus",
    "target_years_missing",
    "missing_field_flags",
    "professional_group_granularity_status",
    "broad_data_collection_needed",
    "targeted_collection_needed",
    "canonical_ml_entry_open",
    "plan_source_url",
    "score_source_url",
    "source_audit_record_id",
    "record_id",
    "source_slug",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("school_key", ""): row for row in rows if row.get("school_key", "")}


def grouped_years(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        key = row.get("school_key", "")
        year = str(row.get("year", "") or row.get("latest_year", "")).strip()
        if key and year:
            output[key].add(year)
    return output


def grouped_count(rows: list[dict[str, str]]) -> dict[str, int]:
    output: dict[str, int] = defaultdict(int)
    for row in rows:
        key = row.get("school_key", "")
        if key:
            output[key] += 1
    return output


def trend_pairs(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        key = row.get("school_key", "")
        pair = f"{row.get('from_year', '')}->{row.get('to_year', '')}"
        if key and pair != "->":
            output[key].add(pair)
    return output


def joined(values: set[str]) -> str:
    return "|".join(sorted(str(v) for v in values if str(v).strip()))


def parse_int(value: object) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def latest_for_school(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get("school_key", "")
        if not key:
            continue
        existing = latest.get(key)
        if existing is None or parse_int(row.get("latest_year") or row.get("year")) >= parse_int(
            existing.get("latest_year") or existing.get("year")
        ):
            latest[key] = row
    return latest


def group_codes_from_gap(gap_row: dict[str, str] | None) -> str:
    if not gap_row:
        return ""
    return gap_row.get("candidate_group_codes", "")


def group_status(latest: dict[str, str], group_codes: str) -> str:
    if group_codes:
        return "official_admission_group_codes_present"
    group_count = parse_int(latest.get("plan_selection_group_count_total", ""))
    specialty_count = parse_int(latest.get("plan_specialty_count_total", ""))
    if group_count > 0:
        return "selection_requirement_groups_present_no_admission_group_code"
    if specialty_count > 0:
        return "major_level_present_group_mapping_missing"
    return "group_and_major_mapping_missing"


def effective_latest(action: dict[str, str], latest: dict[str, str]) -> dict[str, str]:
    """Prefer action-board post-gap/post-human values over older latest snapshots."""
    merged = dict(latest)
    mapping = {
        "latest_year": "latest_year",
        "data_completeness": "data_completeness",
        "total_plan_count": "total_plan_count",
        "minimum_score": "minimum_score",
        "minimum_rank": "minimum_rank",
        "trend_signal": "trend_signal",
        "plan_source_url": "plan_source_url",
        "score_source_url": "score_source_url",
    }
    for source_field, target_field in mapping.items():
        value = str(action.get(source_field, "")).strip()
        if value:
            merged[target_field] = value
    if str(action.get("trend_available", "")).strip():
        merged["trend_available"] = action.get("trend_available", "")
    return merged


def post_human_map(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = row.get("school_key", "")
        if key:
            output[key].append(row)
    return output


def post_status(rows: list[dict[str, str]]) -> tuple[str, str]:
    if not rows:
        return "", ""
    statuses = joined({row.get("post_human_status", "") for row in rows})
    decisions = joined({row.get("selected_decision", "") for row in rows})
    return statuses, decisions


def missing_flags(
    target_missing: set[str],
    latest: dict[str, str],
    trend_count: int,
    group_granularity: str,
    post_rows: list[dict[str, str]],
    current_bucket: str,
) -> list[str]:
    flags: list[str] = []
    if target_missing:
        flags.append("missing_target_years")
    if parse_int(latest.get("total_plan_count", "")) <= 0:
        flags.append("missing_plan_count")
    if not str(latest.get("minimum_score", "")).strip():
        flags.append("missing_minimum_score")
    if not str(latest.get("minimum_rank", "")).strip():
        flags.append("missing_minimum_rank")
    if trend_count <= 0:
        flags.append("missing_canonical_trend")
    if group_granularity != "official_admission_group_codes_present":
        flags.append("professional_group_mapping_not_canonical_ready")
    if "caution" in current_bucket.lower() or any(row.get("requires_targeted_repair") == "true" for row in post_rows):
        flags.append("post_human_caution_or_repair_boundary")
    return flags


def sufficiency_band(
    canonical_year_count: int,
    latest_has_plan: bool,
    latest_has_score: bool,
    latest_has_rank: bool,
    trend_count: int,
    group_granularity: str,
    current_bucket: str,
) -> str:
    if "G4" in current_bucket or "live_source" in current_bucket:
        return "S5_source_blocked_not_sufficient"
    if "hold" in current_bucket.lower():
        return "S4_hold_not_sufficient"
    if latest_has_plan and latest_has_score and latest_has_rank and canonical_year_count >= 2 and trend_count >= 1:
        if group_granularity == "official_admission_group_codes_present":
            return "S1_rebuild_assessment_ready"
        return "S2_rebuild_possible_group_mapping_thin"
    if latest_has_score and latest_has_rank and canonical_year_count >= 2:
        return "S3_score_rank_years_present_plan_or_group_thin"
    return "S4_too_thin_for_rebuild"


def priority_for(band: str, flags: list[str], current_bucket: str, post_rows: list[dict[str, str]]) -> str:
    if band.startswith("S5"):
        return "P4_g4_source_reachability_only"
    if "post_human_caution_or_repair_boundary" in flags:
        return "P0_caution_repair_or_g2_reassessment"
    if band.startswith("S1"):
        return "P2_canonical_rebuild_assessment"
    if band.startswith("S2") or band.startswith("S3"):
        return "P1_targeted_thickening_before_rebuild"
    return "P3_hold_or_missing_core_fields"


def recommended_action(priority: str, flags: list[str]) -> str:
    if priority == "P0_caution_repair_or_g2_reassessment":
        return "先重评 caution/row-fix 边界，补齐备注、字段来源和专业组映射；不做广泛扩池。"
    if priority == "P1_targeted_thickening_before_rebuild":
        return "做定点补厚：优先补缺失年份、最低位次、计划数和专业组映射，再进 canonical rebuild assessment。"
    if priority == "P2_canonical_rebuild_assessment":
        return "进入 canonical rebuild assessment 候选；先做口径审计，不直接写训练层。"
    if priority == "P4_g4_source_reachability_only":
        return "保留在 G4 官方来源可达性支线；需要人工批准 live source/Deep Research 后才能继续。"
    return "保持 hold 或补齐核心字段后再重评。"


def queue_lane(priority: str) -> str:
    return {
        "P0_caution_repair_or_g2_reassessment": "caution_repair_reassessment",
        "P1_targeted_thickening_before_rebuild": "targeted_data_thickening",
        "P2_canonical_rebuild_assessment": "canonical_rebuild_assessment_candidate",
        "P3_hold_or_missing_core_fields": "hold_or_core_field_gap",
        "P4_g4_source_reachability_only": "g4_source_reachability_branch",
    }.get(priority, "manual_review")


def main() -> None:
    action_rows = read_csv(ACTION_BOARD)
    post_rows_by_key = post_human_map(read_csv(POST_HUMAN))
    latest_rows = latest_for_school(read_csv(LATEST_SNAPSHOT))
    gap_rows = by_key(read_csv(GAP_FILL_APPLICATION))
    g4_rows = by_key(read_csv(G4_CLOSEOUT))

    plan_years = grouped_years(read_csv(PLAN_SEED))
    score_major_years = grouped_years(read_csv(SCORE_MAJOR_SEED))
    score_summary_years = grouped_years(read_csv(SCORE_SUMMARY_SEED))
    canonical_years = grouped_years(read_csv(PRIMARY_CANONICAL_SNAPSHOT))
    trend_by_key = trend_pairs(read_csv(PRIMARY_CANONICAL_TREND))

    audit_rows: list[dict[str, object]] = []
    queue_rows: list[dict[str, object]] = []

    for action in action_rows:
        key = action.get("school_key", "")
        latest = effective_latest(action, latest_rows.get(key, {}))
        post_rows = post_rows_by_key.get(key, [])
        post_statuses, post_decisions = post_status(post_rows)
        group_codes = group_codes_from_gap(gap_rows.get(key))
        group_granularity = group_status(latest, group_codes)
        canon_years = canonical_years.get(key, set())
        target_present = canon_years & TARGET_YEARS
        target_missing = TARGET_YEARS - target_present
        trend_count = len(trend_by_key.get(key, set()))
        latest_has_plan = parse_int(latest.get("total_plan_count", "")) > 0
        latest_has_score = bool(str(latest.get("minimum_score", "")).strip())
        latest_has_rank = bool(str(latest.get("minimum_rank", "")).strip())
        current_bucket = action.get("final_gate_bucket", "")
        if key in g4_rows:
            current_bucket = "B5_g4_live_source_approval_required"
        flags = missing_flags(target_missing, latest, trend_count, group_granularity, post_rows, current_bucket)
        band = sufficiency_band(
            len(canon_years),
            latest_has_plan,
            latest_has_score,
            latest_has_rank,
            trend_count,
            group_granularity,
            current_bucket,
        )
        priority = priority_for(band, flags, current_bucket, post_rows)
        focus = "|".join(flags) if flags else "field_depth_acceptable_for_assessment"
        rec = recommended_action(priority, flags)
        record_id = f"{key}-pre-ml-data-sufficiency-audit"
        plan_url = latest.get("plan_source_url") or action.get("plan_source_url", "")
        score_url = latest.get("score_source_url") or action.get("score_source_url", "")
        source_ids = "|".join(
            item
            for item in [
                action.get("record_id", ""),
                latest.get("record_id", ""),
                *(row.get("record_id", "") for row in post_rows),
                g4_rows.get(key, {}).get("record_id", ""),
            ]
            if item
        )
        audit_rows.append(
            {
                "school_key": key,
                "school_name": action.get("school_name", ""),
                "current_bucket": current_bucket,
                "post_human_status": post_statuses,
                "selected_decision": post_decisions,
                "data_sufficiency_band": band,
                "thickening_priority": priority,
                "broad_data_collection_needed": "false",
                "targeted_collection_needed": bool_text(priority in {"P0_caution_repair_or_g2_reassessment", "P1_targeted_thickening_before_rebuild"}),
                "canonical_ml_entry_open": "false",
                "canonical_rebuild_assessment_ready": bool_text(
                    band.startswith(("S1_", "S2_", "S3_"))
                    and priority
                    not in {
                        "P0_caution_repair_or_g2_reassessment",
                        "P4_g4_source_reachability_only",
                    }
                ),
                "plan_seed_years": joined(plan_years.get(key, set())),
                "score_major_years": joined(score_major_years.get(key, set())),
                "score_summary_years": joined(score_summary_years.get(key, set())),
                "canonical_snapshot_years": joined(canon_years),
                "canonical_trend_pairs": joined(trend_by_key.get(key, set())),
                "target_years_present": joined(target_present),
                "target_years_missing": joined(target_missing),
                "year_depth_score": len(target_present),
                "latest_year": latest.get("latest_year", ""),
                "latest_data_completeness": latest.get("data_completeness", ""),
                "latest_total_plan_count": latest.get("total_plan_count", ""),
                "latest_minimum_score": latest.get("minimum_score", ""),
                "latest_minimum_rank": latest.get("minimum_rank", ""),
                "latest_plan_group_count": latest.get("plan_selection_group_count_total", ""),
                "latest_plan_specialty_count": latest.get("plan_specialty_count_total", ""),
                "latest_has_plan": bool_text(latest_has_plan),
                "latest_has_score": bool_text(latest_has_score),
                "latest_has_rank": bool_text(latest_has_rank),
                "trend_available": bool_text(trend_count > 0),
                "professional_group_granularity_status": group_granularity,
                "candidate_group_codes": group_codes,
                "missing_field_flags": focus,
                "repair_or_thickening_focus": focus,
                "recommended_next_action": rec,
                "plan_source_url": plan_url,
                "score_source_url": score_url,
                "source_record_ids": source_ids,
                "record_id": record_id,
                "source_slug": "pre_ml_data_sufficiency_audit",
            }
        )
        if priority != "P2_canonical_rebuild_assessment":
            queue_rows.append(
                {
                    "school_key": key,
                    "school_name": action.get("school_name", ""),
                    "priority": priority,
                    "queue_lane": queue_lane(priority),
                    "current_bucket": current_bucket,
                    "post_human_status": post_statuses,
                    "recommended_next_action": rec,
                    "repair_or_thickening_focus": focus,
                    "target_years_missing": joined(target_missing),
                    "missing_field_flags": focus,
                    "professional_group_granularity_status": group_granularity,
                    "broad_data_collection_needed": "false",
                    "targeted_collection_needed": bool_text(priority != "P4_g4_source_reachability_only"),
                    "canonical_ml_entry_open": "false",
                    "plan_source_url": plan_url,
                    "score_source_url": score_url,
                    "source_audit_record_id": record_id,
                    "record_id": f"{key}-pre-ml-data-thickening-priority-queue",
                    "source_slug": "pre_ml_data_thickening_priority_queue",
                }
            )

    priority_order = {
        "P0_caution_repair_or_g2_reassessment": 0,
        "P1_targeted_thickening_before_rebuild": 1,
        "P3_hold_or_missing_core_fields": 3,
        "P4_g4_source_reachability_only": 4,
    }
    audit_rows.sort(key=lambda row: (str(row["thickening_priority"]), str(row["school_key"])))
    queue_rows.sort(key=lambda row: (priority_order.get(str(row["priority"]), 9), str(row["school_key"])))
    for i, row in enumerate(audit_rows, start=1):
        row["audit_rank"] = i
    for i, row in enumerate(queue_rows, start=1):
        row["queue_rank"] = i

    write_csv(AUDIT_OUT, audit_rows, AUDIT_FIELDS)
    write_csv(QUEUE_OUT, queue_rows, QUEUE_FIELDS)
    write_csv(AUDIT_ROLLUP, rollup(audit_rows), ["metric", "value"])
    write_csv(QUEUE_ROLLUP, queue_rollup(queue_rows), ["metric", "value"])
    write_doc(audit_rows, queue_rows)
    print(
        "data_sufficiency_audit_rows="
        f"{len(audit_rows)} queue_rows={len(queue_rows)} broad_collection=0 "
        f"targeted={sum(row['targeted_collection_needed'] == 'true' for row in audit_rows)}"
    )


def rollup(audit_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    priorities = Counter(str(row["thickening_priority"]) for row in audit_rows)
    bands = Counter(str(row["data_sufficiency_band"]) for row in audit_rows)
    group_statuses = Counter(str(row["professional_group_granularity_status"]) for row in audit_rows)
    metrics: list[dict[str, object]] = [
        {"metric": "audited_school_count", "value": len(audit_rows)},
        {"metric": "broad_data_collection_needed_count", "value": sum(row["broad_data_collection_needed"] == "true" for row in audit_rows)},
        {"metric": "targeted_collection_needed_count", "value": sum(row["targeted_collection_needed"] == "true" for row in audit_rows)},
        {"metric": "canonical_rebuild_assessment_ready_count", "value": sum(row["canonical_rebuild_assessment_ready"] == "true" for row in audit_rows)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for name, count in sorted(priorities.items()):
        metrics.append({"metric": f"thickening_priority::{name}", "value": count})
    for name, count in sorted(bands.items()):
        metrics.append({"metric": f"data_sufficiency_band::{name}", "value": count})
    for name, count in sorted(group_statuses.items()):
        metrics.append({"metric": f"professional_group_granularity_status::{name}", "value": count})
    return metrics


def queue_rollup(queue_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    priorities = Counter(str(row["priority"]) for row in queue_rows)
    lanes = Counter(str(row["queue_lane"]) for row in queue_rows)
    metrics: list[dict[str, object]] = [
        {"metric": "data_thickening_queue_rows", "value": len(queue_rows)},
        {"metric": "broad_data_collection_needed_count", "value": sum(row["broad_data_collection_needed"] == "true" for row in queue_rows)},
        {"metric": "targeted_collection_needed_count", "value": sum(row["targeted_collection_needed"] == "true" for row in queue_rows)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for name, count in sorted(priorities.items()):
        metrics.append({"metric": f"priority::{name}", "value": count})
    for name, count in sorted(lanes.items()):
        metrics.append({"metric": f"queue_lane::{name}", "value": count})
    return metrics


def write_doc(audit_rows: list[dict[str, object]], queue_rows: list[dict[str, object]]) -> None:
    priorities = Counter(str(row["thickening_priority"]) for row in audit_rows)
    bands = Counter(str(row["data_sufficiency_band"]) for row in audit_rows)
    lines = [
        "# Pre-ML data sufficiency audit",
        "",
        "本报告审计 32 所主池学校的数据厚度：年份覆盖、计划/分数/位次字段、趋势、专业组或选科映射、post-human caution/row-fix 边界。未联网，未扩池，未写 canonical，未启动 ML。",
        "",
        "## Summary",
        "",
        f"- audited schools: {len(audit_rows)}",
        f"- broad data collection needed: {sum(row['broad_data_collection_needed'] == 'true' for row in audit_rows)}",
        f"- targeted collection/thickening needed: {sum(row['targeted_collection_needed'] == 'true' for row in audit_rows)}",
        f"- canonical rebuild assessment ready: {sum(row['canonical_rebuild_assessment_ready'] == 'true' for row in audit_rows)}",
        "- canonical/ML entry: closed",
        "- pool expansion: closed",
        "- non-211 search: closed",
        "- Deep Research mainline: closed",
        "",
        "## Priority counts",
        "",
    ]
    for priority, count in sorted(priorities.items()):
        lines.append(f"- {priority}: {count}")
    lines.extend(["", "## Sufficiency bands", ""])
    for band, count in sorted(bands.items()):
        lines.append(f"- {band}: {count}")
    lines.extend(["", "## Targeted Queue", ""])
    for row in queue_rows[:20]:
        lines.append(
            f"- {row['priority']} / {row['school_name']}: {row['repair_or_thickening_focus']}"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "数据确实偏少，但不是继续广泛搜集学校。下一步应补厚主池：先处理 caution/row-fix 的 8 条定点重评，再处理年份/位次/专业组映射不足的学校；G4 只在人工批准后做官方来源可达性支线。",
            "",
            "## Output files",
            "",
            f"- `{AUDIT_OUT.relative_to(ROOT)}`",
            f"- `{QUEUE_OUT.relative_to(ROOT)}`",
            f"- `{AUDIT_ROLLUP.relative_to(ROOT)}`",
            f"- `{QUEUE_ROLLUP.relative_to(ROOT)}`",
            f"- `{DOC_OUT.relative_to(ROOT)}`",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
