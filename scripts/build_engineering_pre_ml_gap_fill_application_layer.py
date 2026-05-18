#!/usr/bin/env python3
"""
Apply accepted D3/D4 local gap-fill decisions into a separate pre-ML preview layer.

This script intentionally does not overwrite the baseline readiness, handoff,
workbench, or gate-status tables. It creates post-gap-fill artifacts that can be
reviewed before any canonical/ML layer is rebuilt.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

D3_D4_DECISIONS = SEED_DIR / "guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv"
BASE_READINESS = SEED_DIR / "guangxi_pre_ml_model_readiness_merged.csv"
BASE_HANDOFF = SEED_DIR / "guangxi_pre_ml_handoff_pack_merged.csv"
BASE_WORKBENCH = SEED_DIR / "guangxi_pre_ml_review_workbench_merged.csv"
BASE_GATE = SEED_DIR / "guangxi_pre_ml_gate_status_merged.csv"

APPLICATION_LAYER = SEED_DIR / "guangxi_pre_ml_gap_fill_application_layer_merged.csv"
POST_READINESS = SEED_DIR / "guangxi_pre_ml_model_readiness_post_gap_fill_merged.csv"
POST_HANDOFF = SEED_DIR / "guangxi_pre_ml_handoff_pack_post_gap_fill_merged.csv"
POST_WORKBENCH = SEED_DIR / "guangxi_pre_ml_review_workbench_post_gap_fill_merged.csv"
POST_GATE = SEED_DIR / "guangxi_pre_ml_gate_status_post_gap_fill_merged.csv"

APPLICATION_SUMMARY = REPORT_DIR / "engineering_pre_ml_gap_fill_application_layer_school_summary.csv"
APPLICATION_ROLLUP = REPORT_DIR / "engineering_pre_ml_gap_fill_application_layer_coverage_rollup.csv"
READINESS_ROLLUP = REPORT_DIR / "engineering_pre_ml_model_readiness_post_gap_fill_coverage_rollup.csv"
HANDOFF_ROLLUP = REPORT_DIR / "engineering_pre_ml_handoff_pack_post_gap_fill_coverage_rollup.csv"
WORKBENCH_ROLLUP = REPORT_DIR / "engineering_pre_ml_review_workbench_post_gap_fill_coverage_rollup.csv"
GATE_SUMMARY = REPORT_DIR / "engineering_pre_ml_gate_status_post_gap_fill_school_summary.csv"
GATE_ROLLUP = REPORT_DIR / "engineering_pre_ml_gate_status_post_gap_fill_coverage_rollup.csv"

ACCEPTED_DECISIONS = {"accept_gap_fill_then_review", "accept_gap_fill_with_note"}
READY_BANDS = {"M1_ready_for_pre_ml_review", "M2_comparable_ready_with_note"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_metric_csv(path: Path, metrics: list[tuple[str, object]]) -> None:
    write_csv(path, [{"metric": key, "value": value} for key, value in metrics], ["metric", "value"])


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def int_or_blank(value: object) -> int | str:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return ""
    try:
        return int(float(text))
    except ValueError:
        return ""


def gap_count(signature: str) -> int:
    signature = (signature or "").strip()
    if not signature or signature in {"none", "complete_enough"}:
        return 0
    return len([part for part in signature.split("|") if part])


def ready_label(row: dict[str, str]) -> tuple[str, str, str, str, int, str, str, str]:
    if row["review_decision"] == "accept_gap_fill_then_review":
        return (
            "M1_ready_for_pre_ml_review",
            "G1_ready_for_human_gpt_review_gate",
            "H1_ready_now",
            "R1_clean_ready",
            0,
            "clean_pre_ml_review|gap_fill_applied",
            "ready_for_pre_ml_review",
            "已接受本地补洞结果，可进入人工/GPT复核闸门；复核通过前仍不启动机器学习",
        )
    return (
        "M2_comparable_ready_with_note",
        "G2_ready_with_caution_for_review_gate",
        "H2_ready_with_note",
        "R3_caution_review",
        3,
        "gap_fill_applied_with_note|missing_plan|fallback_source_resolution",
        "ready_comparable_with_note",
        "已接受本地补洞结果但仍保留 missing_plan/fallback caution；仅可带备注进入复核闸门",
    )


def build_application_rows(decisions: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in decisions:
        if row.get("decision_status") != "completed_gpt_review_decision":
            continue
        if row.get("review_decision") not in ACCEPTED_DECISIONS:
            continue

        readiness, gate, handoff, lane, risk, flags, review_priority, notes = ready_label(row)
        post_gap = row.get("preview_gap_signature") or "complete_enough"
        rows.append(
            {
                "school_key": row["school_key"],
                "school_name": row["school_name"],
                "application_status": "applied_to_post_gap_fill_preview",
                "source_decision": row["review_decision"],
                "acceptance_class": row["acceptance_class"],
                "evidence_grade": row["evidence_grade"],
                "current_gate_status": row["current_gate_status"],
                "current_readiness_band": row["current_readiness_band"],
                "post_gap_fill_gate_status": gate,
                "post_gap_fill_readiness_band": readiness,
                "post_gap_fill_handoff_bucket": handoff,
                "post_gap_fill_review_lane": lane,
                "post_gap_fill_review_risk_score": risk,
                "post_gap_fill_review_focus_flags": flags,
                "post_gap_fill_review_priority": review_priority,
                "candidate_year": row["candidate_year"],
                "candidate_subject_type": row["candidate_subject_type"],
                "candidate_batch": row["candidate_batch"],
                "candidate_group_count": int_or_blank(row["candidate_group_count"]),
                "candidate_group_codes": row["candidate_group_codes"],
                "candidate_minimum_score": int_or_blank(row["candidate_minimum_score"]),
                "candidate_minimum_rank": int_or_blank(row["candidate_minimum_rank"]),
                "candidate_min_rank_low": int_or_blank(row["candidate_min_rank_low"]),
                "candidate_min_rank_high": int_or_blank(row["candidate_min_rank_high"]),
                "candidate_source_ids": row["candidate_source_ids"],
                "candidate_data_quality": row["candidate_data_quality"],
                "candidate_fill_fields": row["candidate_fill_fields"],
                "candidate_use_scope": "formal_gap_fill_application_not_auto_ml_input",
                "current_gap_signature": row["current_gap_signature"],
                "post_gap_fill_gap_signature": post_gap,
                "post_gap_fill_gap_count": gap_count(post_gap),
                "post_gap_fill_data_completeness": row["preview_data_completeness"],
                "resolution_status": row["resolution_status"],
                "plan_source_resolution": row["plan_source_resolution"],
                "score_source_resolution": row["score_source_resolution"],
                "structured_plan_rows": int_or_blank(row["structured_plan_rows"]),
                "structured_score_major_rows": int_or_blank(row["structured_score_major_rows"]),
                "structured_score_summary_rows": int_or_blank(row["structured_score_summary_rows"]),
                "plan_source_url": row["plan_source_url"],
                "score_source_url": row["score_source_url"],
                "application_notes": notes,
                "ml_boundary_note": "post-gap-fill preview only; canonical training layer and ML remain closed",
                "record_id": f"{row['school_key']}-pre-ml-gap-fill-application",
                "source_record_id": row["record_id"],
                "source_slug": "pre_ml_gap_fill_application_layer",
            }
        )
    return rows


def application_by_key(application_rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(row["school_key"]): row for row in application_rows}


def patch_readiness(
    base_rows: list[dict[str, str]], applications: dict[str, dict[str, object]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for base in base_rows:
        row: dict[str, object] = dict(base)
        app = applications.get(base["school_key"])
        if app:
            row["pipeline_status"] = (
                "seeded_plan_and_score_after_gap_fill"
                if app["post_gap_fill_readiness_band"] == "M1_ready_for_pre_ml_review"
                else "seeded_score_only_after_gap_fill"
            )
            row["operating_lane"] = "A1_action_now" if app["post_gap_fill_readiness_band"] == "M1_ready_for_pre_ml_review" else "A2_action_with_note"
            row["latest_year"] = app["candidate_year"]
            row["reference_year"] = app["candidate_year"]
            row["data_completeness"] = app["post_gap_fill_data_completeness"]
            row["minimum_score"] = app["candidate_minimum_score"]
            row["minimum_rank"] = app["candidate_minimum_rank"]
            row["trend_available"] = "true"
            row["trend_signal"] = (
                base.get("trend_signal") if truthy(base.get("trend_available")) else "trend_seed_possible_from_gap_fill_candidate"
            )
            row["has_plan_source"] = "true" if app["post_gap_fill_data_completeness"] == "plan_and_score" else base.get("has_plan_source", "")
            row["has_score_source"] = "true"
            row["readiness_band"] = app["post_gap_fill_readiness_band"]
            row["critical_gap_signature"] = app["post_gap_fill_gap_signature"]
            row["pre_ml_next_gate"] = "gpt_review_before_ml" if app["post_gap_fill_readiness_band"] == "M1_ready_for_pre_ml_review" else "review_note_then_gpt_review"
            row["readiness_notes"] = app["application_notes"]
            row["record_id"] = f"{base['school_key']}-pre-ml-model-readiness-post-gap-fill"
            row["source_slug"] = "pre_ml_model_readiness_post_gap_fill"
        else:
            row["record_id"] = f"{base['school_key']}-pre-ml-model-readiness-post-gap-fill"
            row["source_slug"] = "pre_ml_model_readiness_post_gap_fill"
        output.append(row)
    return output


def build_handoff(
    refreshed_readiness: list[dict[str, object]],
    base_handoff_rows: list[dict[str, str]],
    gate_by_key: dict[str, dict[str, object]],
    applications: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    base_by_key = {row["school_key"]: row for row in base_handoff_rows}
    output: list[dict[str, object]] = []
    for ready in refreshed_readiness:
        school_key = str(ready["school_key"])
        if ready.get("readiness_band") not in READY_BANDS:
            continue

        base = dict(base_by_key.get(school_key, {}))
        app = applications.get(school_key)
        gate = gate_by_key.get(school_key, {})
        if base:
            row: dict[str, object] = dict(base)
        else:
            row = {
                "school_key": school_key,
                "school_name": ready.get("school_name", ""),
                "engineering_tier": ready.get("engineering_tier", ""),
                "pipeline_status": ready.get("pipeline_status", ""),
                "operating_lane": ready.get("operating_lane", ""),
                "reference_year": ready.get("reference_year", ""),
                "latest_year_available": ready.get("latest_year", ""),
                "latest_year": ready.get("latest_year", ""),
                "year_gap_from_latest": 0,
                "data_completeness": ready.get("data_completeness", ""),
                "total_plan_count": ready.get("total_plan_count", ""),
                "minimum_score": ready.get("minimum_score", ""),
                "minimum_rank": ready.get("minimum_rank", ""),
                "trend_available": ready.get("trend_available", ""),
                "trend_signal": ready.get("trend_signal", ""),
                "plan_source_resolution": gate.get("plan_source_resolution", ""),
                "score_source_resolution": gate.get("score_source_resolution", ""),
                "resolution_status": gate.get("resolution_status", ""),
                "plan_source_url": gate.get("plan_source_url", ""),
                "score_source_url": gate.get("score_source_url", ""),
                "source_record_id": ready.get("record_id", ""),
            }
        row["readiness_band"] = ready["readiness_band"]
        if app:
            row["handoff_bucket"] = app["post_gap_fill_handoff_bucket"]
            row["operating_priority"] = 1 if row["handoff_bucket"] == "H1_ready_now" else 2
            row["review_priority"] = app["post_gap_fill_review_priority"]
            row["actionability_band"] = ready.get("operating_lane", "")
            row["evidence_quality"] = "high" if row["handoff_bucket"] == "H1_ready_now" else "medium"
            row["next_action"] = "hold_for_pre_ml_review" if row["handoff_bucket"] == "H1_ready_now" else "allow_comparable_reference_with_explicit_note"
            row["handoff_notes"] = app["application_notes"]
            for field in [
                "school_name",
                "engineering_tier",
                "pipeline_status",
                "operating_lane",
                "reference_year",
                "latest_year_available",
                "latest_year",
                "data_completeness",
                "total_plan_count",
                "minimum_score",
                "minimum_rank",
                "trend_available",
                "trend_signal",
            ]:
                source_field = "latest_year" if field == "latest_year_available" else field
                row[field] = ready.get(source_field, row.get(field, ""))
            for field in [
                "plan_source_resolution",
                "score_source_resolution",
                "resolution_status",
                "plan_source_url",
                "score_source_url",
            ]:
                row[field] = gate.get(field, row.get(field, ""))
        row["record_id"] = f"{school_key}-pre-ml-handoff-post-gap-fill"
        row["source_record_id"] = ready.get("record_id", "")
        row["source_slug"] = "pre_ml_handoff_pack_post_gap_fill"
        output.append(row)
    return output


def build_workbench(
    handoff_rows: list[dict[str, object]],
    base_workbench_rows: list[dict[str, str]],
    gate_by_key: dict[str, dict[str, object]],
    applications: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    base_by_key = {row["school_key"]: row for row in base_workbench_rows}
    output: list[dict[str, object]] = []
    for handoff in handoff_rows:
        school_key = str(handoff["school_key"])
        base = dict(base_by_key.get(school_key, {}))
        app = applications.get(school_key)
        gate = gate_by_key.get(school_key, {})
        row: dict[str, object] = dict(base) if base else {}
        for field in [
            "school_key",
            "school_name",
            "readiness_band",
            "handoff_bucket",
            "engineering_tier",
            "pipeline_status",
            "operating_lane",
            "reference_year",
            "latest_year_available",
            "latest_year",
            "year_gap_from_latest",
            "data_completeness",
            "total_plan_count",
            "minimum_score",
            "minimum_rank",
            "trend_available",
            "trend_signal",
            "evidence_quality",
            "plan_source_resolution",
            "score_source_resolution",
            "resolution_status",
            "plan_source_url",
            "score_source_url",
        ]:
            row[field] = handoff.get(field, row.get(field, ""))
        row["gap_count"] = gate.get("gap_count", row.get("gap_count", ""))
        row["gap_signature"] = gate.get("gap_signature", row.get("gap_signature", ""))
        row["blocker_class"] = gate.get("blocker_class", row.get("blocker_class", ""))
        if app:
            row["review_lane"] = app["post_gap_fill_review_lane"]
            row["review_risk_score"] = app["post_gap_fill_review_risk_score"]
            row["review_focus_flags"] = app["post_gap_fill_review_focus_flags"]
            row["pre_ml_gate"] = "human_or_gpt_review_before_ml"
            row["review_prompt"] = (
                "核对正式本地补洞应用层、候选最低分/位次、专业组代码和官方来源后，再决定是否进入复核闸门。"
            )
            row["review_notes"] = app["application_notes"]
        row["record_id"] = f"{school_key}-pre-ml-review-workbench-post-gap-fill"
        row["source_record_id"] = handoff.get("record_id", "")
        row["source_slug"] = "pre_ml_review_workbench_post_gap_fill"
        output.append(row)
    return output


def patch_gate(base_rows: list[dict[str, str]], applications: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for base in base_rows:
        row: dict[str, object] = dict(base)
        app = applications.get(base["school_key"])
        if app:
            row["readiness_band"] = app["post_gap_fill_readiness_band"]
            row["gate_status"] = app["post_gap_fill_gate_status"]
            row["gate_priority"] = 1 if app["post_gap_fill_gate_status"].startswith("G1_") else 2
            row["review_lane"] = app["post_gap_fill_review_lane"]
            row["review_risk_score"] = app["post_gap_fill_review_risk_score"]
            row["review_focus_flags"] = app["post_gap_fill_review_focus_flags"]
            row["pipeline_status"] = (
                "seeded_plan_and_score_after_gap_fill"
                if app["post_gap_fill_readiness_band"] == "M1_ready_for_pre_ml_review"
                else "seeded_score_only_after_gap_fill"
            )
            row["operating_lane"] = "A1_action_now" if app["post_gap_fill_readiness_band"] == "M1_ready_for_pre_ml_review" else "A2_action_with_note"
            row["latest_year"] = app["candidate_year"]
            row["reference_year"] = app["candidate_year"]
            row["data_completeness"] = app["post_gap_fill_data_completeness"]
            row["minimum_score"] = app["candidate_minimum_score"]
            row["minimum_rank"] = app["candidate_minimum_rank"]
            row["trend_available"] = "true"
            row["trend_signal"] = (
                base.get("trend_signal") if truthy(base.get("trend_available")) else "trend_seed_possible_from_gap_fill_candidate"
            )
            row["gap_count"] = app["post_gap_fill_gap_count"]
            row["gap_signature"] = app["post_gap_fill_gap_signature"]
            row["blocker_class"] = "none" if int(app["post_gap_fill_gap_count"]) == 0 else "caution_before_ml"
            row["backfill_route"] = "formal_gap_fill_applied"
            row["structured_plan_rows"] = app["structured_plan_rows"]
            row["structured_score_major_rows"] = app["structured_score_major_rows"]
            row["structured_score_summary_rows"] = app["structured_score_summary_rows"]
            row["remaining_local_action"] = app["application_notes"]
            row["ml_gate_instruction"] = "只到人工/GPT复核闸门；canonical/ML入口继续关闭"
            row["record_id"] = f"{base['school_key']}-pre-ml-gate-status-post-gap-fill"
            row["source_record_id"] = app["record_id"]
            row["source_slug"] = "pre_ml_gate_status_post_gap_fill"
        else:
            row["record_id"] = f"{base['school_key']}-pre-ml-gate-status-post-gap-fill"
            row["source_slug"] = "pre_ml_gate_status_post_gap_fill"
        output.append(row)
    return output


def count_by(rows: list[dict[str, object]], field: str) -> Counter:
    return Counter(str(row.get(field, "")) for row in rows)


def main() -> None:
    decision_fields, decisions = read_csv(D3_D4_DECISIONS)
    readiness_fields, readiness_rows = read_csv(BASE_READINESS)
    handoff_fields, handoff_rows = read_csv(BASE_HANDOFF)
    workbench_fields, workbench_rows = read_csv(BASE_WORKBENCH)
    gate_fields, gate_rows = read_csv(BASE_GATE)

    application_rows = build_application_rows(decisions)
    applications = application_by_key(application_rows)
    refreshed_readiness = patch_readiness(readiness_rows, applications)
    refreshed_gate = patch_gate(gate_rows, applications)
    gate_by_key = {str(row["school_key"]): row for row in refreshed_gate}
    refreshed_handoff = build_handoff(refreshed_readiness, handoff_rows, gate_by_key, applications)
    refreshed_workbench = build_workbench(refreshed_handoff, workbench_rows, gate_by_key, applications)

    application_fields = [
        "school_key",
        "school_name",
        "application_status",
        "source_decision",
        "acceptance_class",
        "evidence_grade",
        "current_gate_status",
        "current_readiness_band",
        "post_gap_fill_gate_status",
        "post_gap_fill_readiness_band",
        "post_gap_fill_handoff_bucket",
        "post_gap_fill_review_lane",
        "post_gap_fill_review_risk_score",
        "post_gap_fill_review_focus_flags",
        "post_gap_fill_review_priority",
        "candidate_year",
        "candidate_subject_type",
        "candidate_batch",
        "candidate_group_count",
        "candidate_group_codes",
        "candidate_minimum_score",
        "candidate_minimum_rank",
        "candidate_min_rank_low",
        "candidate_min_rank_high",
        "candidate_source_ids",
        "candidate_data_quality",
        "candidate_fill_fields",
        "candidate_use_scope",
        "current_gap_signature",
        "post_gap_fill_gap_signature",
        "post_gap_fill_gap_count",
        "post_gap_fill_data_completeness",
        "resolution_status",
        "plan_source_resolution",
        "score_source_resolution",
        "structured_plan_rows",
        "structured_score_major_rows",
        "structured_score_summary_rows",
        "plan_source_url",
        "score_source_url",
        "application_notes",
        "ml_boundary_note",
        "record_id",
        "source_record_id",
        "source_slug",
    ]
    write_csv(APPLICATION_LAYER, application_rows, application_fields)
    write_csv(POST_READINESS, refreshed_readiness, readiness_fields)
    write_csv(POST_HANDOFF, refreshed_handoff, handoff_fields)
    write_csv(POST_WORKBENCH, refreshed_workbench, workbench_fields)
    write_csv(POST_GATE, refreshed_gate, gate_fields)

    summary_fields = [
        "school_key",
        "school_name",
        "application_status",
        "source_decision",
        "post_gap_fill_gate_status",
        "post_gap_fill_readiness_band",
        "post_gap_fill_review_lane",
        "candidate_year",
        "candidate_group_count",
        "candidate_minimum_score",
        "candidate_minimum_rank",
        "post_gap_fill_gap_signature",
        "application_notes",
    ]
    write_csv(APPLICATION_SUMMARY, application_rows, summary_fields)

    gate_summary_fields = [
        "school_key",
        "school_name",
        "readiness_band",
        "gate_status",
        "review_lane",
        "review_risk_score",
        "review_focus_flags",
        "data_completeness",
        "minimum_score",
        "minimum_rank",
        "gap_count",
        "gap_signature",
        "remaining_local_action",
    ]
    write_csv(GATE_SUMMARY, [row for row in refreshed_gate if row["school_key"] in applications], gate_summary_fields)

    readiness_counts = count_by(refreshed_readiness, "readiness_band")
    gate_counts = count_by(refreshed_gate, "gate_status")
    handoff_counts = count_by(refreshed_handoff, "readiness_band")
    workbench_counts = count_by(refreshed_workbench, "review_lane")
    application_counts = count_by(application_rows, "source_decision")

    write_metric_csv(
        APPLICATION_ROLLUP,
        [
            ("gap_fill_application_rows", len(application_rows)),
            ("applied_to_post_gap_fill_preview_rows", len(application_rows)),
            ("accept_gap_fill_then_review_rows", application_counts["accept_gap_fill_then_review"]),
            ("accept_gap_fill_with_note_rows", application_counts["accept_gap_fill_with_note"]),
            ("ml_boundary_still_closed", "true"),
        ],
    )
    write_metric_csv(
        READINESS_ROLLUP,
        [
            ("target_pool_schools", len(refreshed_readiness)),
            ("pre_ml_model_readiness_post_gap_fill_schools", len(refreshed_readiness)),
            ("M1_ready_for_pre_ml_review_schools", readiness_counts["M1_ready_for_pre_ml_review"]),
            ("M2_comparable_ready_with_note_schools", readiness_counts["M2_comparable_ready_with_note"]),
            ("M3_fill_gaps_then_review_schools", readiness_counts["M3_fill_gaps_then_review"]),
            ("M4_blocked_or_manual_route_schools", readiness_counts["M4_blocked_or_manual_route"]),
            ("post_gap_fill_applied_schools", len(application_rows)),
            ("ml_boundary_still_closed", "true"),
        ],
    )
    write_metric_csv(
        HANDOFF_ROLLUP,
        [
            ("target_pool_schools", len(refreshed_readiness)),
            ("pre_ml_handoff_pack_post_gap_fill_schools", len(refreshed_handoff)),
            ("pre_ml_handoff_pack_post_gap_fill_M1_schools", handoff_counts["M1_ready_for_pre_ml_review"]),
            ("pre_ml_handoff_pack_post_gap_fill_M2_schools", handoff_counts["M2_comparable_ready_with_note"]),
            ("post_gap_fill_applied_schools", len(application_rows)),
            ("ml_boundary_still_closed", "true"),
        ],
    )
    write_metric_csv(
        WORKBENCH_ROLLUP,
        [
            ("target_pool_schools", len(refreshed_readiness)),
            ("pre_ml_review_workbench_post_gap_fill_schools", len(refreshed_workbench)),
            ("R1_clean_ready_schools", workbench_counts["R1_clean_ready"]),
            ("R3_caution_review_schools", workbench_counts["R3_caution_review"]),
            ("R4_high_caution_review_schools", workbench_counts["R4_high_caution_review"]),
            ("post_gap_fill_applied_schools", len(application_rows)),
            ("ml_boundary_still_closed", "true"),
        ],
    )
    write_metric_csv(
        GATE_ROLLUP,
        [
            ("target_pool_schools", len(refreshed_gate)),
            ("pre_ml_gate_status_post_gap_fill_schools", len(refreshed_gate)),
            ("human_gpt_review_gate_candidate_schools", gate_counts["G1_ready_for_human_gpt_review_gate"] + gate_counts["G2_ready_with_caution_for_review_gate"]),
            ("G1_ready_for_human_gpt_review_gate_schools", gate_counts["G1_ready_for_human_gpt_review_gate"]),
            ("G2_ready_with_caution_for_review_gate_schools", gate_counts["G2_ready_with_caution_for_review_gate"]),
            ("G3_local_gap_fill_needed_schools", gate_counts["G3_local_gap_fill_needed"]),
            ("G4_blocked_or_manual_route_schools", gate_counts["G4_blocked_or_manual_route"]),
            ("post_gap_fill_applied_schools", len(application_rows)),
            ("ml_boundary_still_closed", "true"),
        ],
    )

    print(f"application_rows={len(application_rows)}")
    print(f"post_readiness_rows={len(refreshed_readiness)}")
    print(f"post_handoff_rows={len(refreshed_handoff)}")
    print(f"post_workbench_rows={len(refreshed_workbench)}")
    print(f"post_gate_rows={len(refreshed_gate)}")


if __name__ == "__main__":
    main()
