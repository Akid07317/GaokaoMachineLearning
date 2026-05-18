#!/usr/bin/env python3
"""Build a focused repair queue for D2/G2 rows that require row-level fixes."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

SOURCE = SEED_DIR / "guangxi_pre_ml_d2_g2_gpt_review_decisions_merged.csv"
QUEUE = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv"
SUMMARY = REPORT_DIR / "engineering_pre_ml_d2_g2_request_row_fix_queue_school_summary.csv"
ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_g2_request_row_fix_queue_coverage_rollup.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def has_placeholder_url(row: dict[str, str]) -> bool:
    urls = f"{row.get('plan_source_url', '')}|{row.get('score_source_url', '')}".lower()
    return "yoursite.com" in urls or "example.com" in urls


def classify(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    fixes = row.get("required_row_fixes", "")
    gaps = row.get("gap_signature", "")
    if has_placeholder_url(row):
        return (
            "P0_source_identity_fix",
            "source_url_placeholder_needs_official_domain_fix",
            "先重获官方招生计划/历年分数 URL，再验证 2025 普通批物理类口径；修复前不得进入 canonical。",
            "source_reacquisition_required",
            "hold_before_review_gate_until_official_url_fixed",
        )
    if "fresh_2025_record_needed" in fixes:
        return (
            "P1_latest_plan_score_alignment",
            "fresh_2025_record_needed|plan_side_needs_structured_fill",
            "补齐 2025 计划侧结构化记录，并确认 2025 分数/位次是否可替代 2024 可比记录。",
            "local_structured_refill_then_recompute",
            "request_row_fix_then_reassess_g2",
        )
    if "reference_year_not_latest" in fixes:
        return (
            "P1_reference_year_and_field_mapping",
            "reference_year_not_latest|score_field_needs_confirm|rank_field_needs_confirm|plan_linkage_needs_fill",
            "用已有官方结构化计划/分数源复核字段映射，把计划数、最低分、最低位次与 reference_year 说明写实。",
            "local_field_mapping_audit",
            "request_row_fix_then_reassess_g2",
        )
    if "missing_plan" in gaps:
        return (
            "P2_plan_gap_note",
            "missing_plan",
            "确认缺计划是否可局部补齐；不可补齐时保留隔离备注。",
            "manual_plan_gap_review",
            "keep_g2_caution_or_hold",
        )
    return (
        "P2_caution_note_cleanup",
        fixes or gaps or "caution_note_required",
        "清理 caution 备注并复核来源精度。",
        "local_note_cleanup",
        "request_row_fix_then_reassess_g2",
    )


def main() -> None:
    source_rows = read_csv(SOURCE)
    queue_rows: list[dict[str, object]] = []
    for row in source_rows:
        if row.get("review_decision") != "request_row_fix":
            continue
        priority, fix_class, action, route, exit_condition = classify(row)
        queue_rows.append(
            {
                "school_key": row["school_key"],
                "school_name": row["school_name"],
                "fix_queue_status": "queued_for_row_fix",
                "fix_priority": priority,
                "fix_class": fix_class,
                "recommended_action": action,
                "fix_route": route,
                "exit_condition": exit_condition,
                "current_gate_status": row["gate_status"],
                "current_readiness_band": row["readiness_band"],
                "current_review_lane": row["review_lane"],
                "current_review_risk_score": row["review_risk_score"],
                "reference_year": row["reference_year"],
                "latest_year": row["latest_year"],
                "data_completeness": row["data_completeness"],
                "total_plan_count": row["total_plan_count"],
                "minimum_score": row["minimum_score"],
                "minimum_rank": row["minimum_rank"],
                "trend_available": row["trend_available"],
                "trend_signal": row["trend_signal"],
                "gap_signature": row["gap_signature"],
                "resolution_status": row["resolution_status"],
                "plan_source_resolution": row["plan_source_resolution"],
                "score_source_resolution": row["score_source_resolution"],
                "structured_plan_rows": row["structured_plan_rows"],
                "structured_score_major_rows": row["structured_score_major_rows"],
                "structured_score_summary_rows": row["structured_score_summary_rows"],
                "plan_source_url": row["plan_source_url"],
                "score_source_url": row["score_source_url"],
                "required_row_fixes": row["required_row_fixes"],
                "residual_followups": row["residual_followups"],
                "ml_boundary_note": "row fix queue only; canonical/ML remain closed",
                "record_id": f"{row['school_key']}-d2-g2-request-row-fix-queue",
                "source_record_id": row["record_id"],
                "source_slug": "pre_ml_d2_g2_request_row_fix_queue",
            }
        )

    fields = [
        "school_key",
        "school_name",
        "fix_queue_status",
        "fix_priority",
        "fix_class",
        "recommended_action",
        "fix_route",
        "exit_condition",
        "current_gate_status",
        "current_readiness_band",
        "current_review_lane",
        "current_review_risk_score",
        "reference_year",
        "latest_year",
        "data_completeness",
        "total_plan_count",
        "minimum_score",
        "minimum_rank",
        "trend_available",
        "trend_signal",
        "gap_signature",
        "resolution_status",
        "plan_source_resolution",
        "score_source_resolution",
        "structured_plan_rows",
        "structured_score_major_rows",
        "structured_score_summary_rows",
        "plan_source_url",
        "score_source_url",
        "required_row_fixes",
        "residual_followups",
        "ml_boundary_note",
        "record_id",
        "source_record_id",
        "source_slug",
    ]
    write_csv(QUEUE, queue_rows, fields)

    summary_fields = [
        "school_key",
        "school_name",
        "fix_priority",
        "fix_class",
        "recommended_action",
        "fix_route",
        "exit_condition",
        "reference_year",
        "latest_year",
        "data_completeness",
        "gap_signature",
    ]
    write_csv(SUMMARY, queue_rows, summary_fields)

    priorities = Counter(row["fix_priority"] for row in queue_rows)
    routes = Counter(row["fix_route"] for row in queue_rows)
    metrics = [
        {"metric": "d2_g2_request_row_fix_queue_rows", "value": len(queue_rows)},
        {"metric": "P0_source_identity_fix_rows", "value": priorities["P0_source_identity_fix"]},
        {"metric": "P1_latest_plan_score_alignment_rows", "value": priorities["P1_latest_plan_score_alignment"]},
        {"metric": "P1_reference_year_and_field_mapping_rows", "value": priorities["P1_reference_year_and_field_mapping"]},
        {"metric": "source_reacquisition_required_rows", "value": routes["source_reacquisition_required"]},
        {"metric": "local_structured_refill_then_recompute_rows", "value": routes["local_structured_refill_then_recompute"]},
        {"metric": "local_field_mapping_audit_rows", "value": routes["local_field_mapping_audit"]},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    write_csv(ROLLUP, metrics, ["metric", "value"])
    print(f"request_row_fix_queue_rows={len(queue_rows)}")


if __name__ == "__main__":
    main()
