#!/usr/bin/env python3
"""Build the full pre-ML human/GPT action board and gate closeout.

This script only merges existing local review layers. It does not fetch live
sources, run Deep Research, write canonical rows, or open the ML entry.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

BASE_STATUS = SEED_DIR / "guangxi_pre_ml_gate_status_post_gap_fill_merged.csv"
D1_DECISIONS = SEED_DIR / "guangxi_pre_ml_d1_g1_gpt_review_decisions_merged.csv"
D2_DECISIONS = SEED_DIR / "guangxi_pre_ml_d2_g2_gpt_review_decisions_merged.csv"
D3_D4_DECISIONS = SEED_DIR / "guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv"
GAP_FILL_APPLICATION = SEED_DIR / "guangxi_pre_ml_gap_fill_application_layer_merged.csv"
D2_ROW_FIX_STATUS = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv"
G4_CLOSEOUT = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_closeout_merged.csv"
G4_APPROVAL = SEED_DIR / "guangxi_pre_ml_g4_human_approval_queue_merged.csv"

ACTION_BOARD_OUT = SEED_DIR / "guangxi_pre_ml_human_gpt_review_action_board_merged.csv"
FINAL_CLOSEOUT_OUT = SEED_DIR / "guangxi_pre_ml_final_gate_closeout_merged.csv"
ACTION_BOARD_ROLLUP = REPORT_DIR / "engineering_pre_ml_human_gpt_review_action_board_coverage_rollup.csv"
FINAL_CLOSEOUT_ROLLUP = REPORT_DIR / "engineering_pre_ml_final_gate_closeout_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_human_gpt_review_action_board_and_gate_closeout.md"


ACTION_BOARD_FIELDS = [
    "board_rank",
    "school_key",
    "school_name",
    "source_layer",
    "final_gate_bucket",
    "action_priority",
    "action_status",
    "source_gate_status",
    "source_readiness_band",
    "review_lane",
    "review_risk_score",
    "review_decision",
    "review_decision_status",
    "human_gpt_review_gate_action",
    "ready_for_human_gpt_review_gate",
    "requires_human_acceptance",
    "requires_row_fix",
    "row_fix_status",
    "row_fix_priority",
    "row_fix_exit_condition",
    "gap_fill_status",
    "live_source_approval_status",
    "approval_request_type",
    "approval_priority",
    "approval_scope",
    "requires_live_source_approval",
    "requires_deep_research_approval",
    "requires_header_cookie_approval",
    "requires_form_replay_approval",
    "requires_browser_state_approval",
    "can_continue_local_only",
    "hold_status",
    "canonical_ml_entry_open",
    "canonical_ml_closed_reason",
    "pool_expansion_allowed",
    "non211_search_allowed",
    "deep_research_mainline_allowed",
    "next_owner",
    "next_action",
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
    "plan_source_url",
    "score_source_url",
    "evidence_summary",
    "source_record_ids",
    "record_id",
    "source_slug",
]

FINAL_CLOSEOUT_FIELDS = [
    "closeout_rank",
    "school_key",
    "school_name",
    "final_gate_bucket",
    "final_gate_status",
    "ready_for_human_gpt_review_gate",
    "next_required_decision",
    "final_pre_ml_action",
    "canonical_ml_action",
    "closeout_reason",
    "remaining_dependency",
    "source_layer",
    "review_decision",
    "hold_status",
    "record_id",
    "source_record_id",
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


def by_school(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("school_key", ""): row for row in rows if row.get("school_key", "")}


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def compact(value: object, max_len: int = 300) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 16] + "...[truncated]"


def first_value(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def records(*rows: dict[str, str]) -> str:
    ids = [row.get("record_id", "") for row in rows if row and row.get("record_id", "")]
    return "|".join(ids)


def base_facts(base: dict[str, str], overlay: dict[str, str] | None = None) -> dict[str, str]:
    row = overlay or {}
    return {
        "reference_year": first_value(row.get("reference_year"), row.get("candidate_year"), base.get("reference_year")),
        "latest_year": first_value(row.get("latest_year"), row.get("candidate_year"), base.get("latest_year")),
        "data_completeness": first_value(row.get("data_completeness"), row.get("preview_data_completeness"), row.get("post_gap_fill_data_completeness"), base.get("data_completeness")),
        "total_plan_count": first_value(row.get("total_plan_count"), base.get("total_plan_count")),
        "minimum_score": first_value(row.get("minimum_score"), row.get("candidate_minimum_score"), base.get("minimum_score")),
        "minimum_rank": first_value(row.get("minimum_rank"), row.get("candidate_minimum_rank"), base.get("minimum_rank")),
        "trend_available": first_value(row.get("trend_available"), base.get("trend_available")),
        "trend_signal": first_value(row.get("trend_signal"), base.get("trend_signal")),
        "gap_signature": first_value(row.get("gap_signature"), row.get("preview_gap_signature"), row.get("post_gap_fill_gap_signature"), base.get("gap_signature")),
        "resolution_status": first_value(row.get("resolution_status"), base.get("resolution_status")),
        "plan_source_resolution": first_value(row.get("plan_source_resolution"), base.get("plan_source_resolution")),
        "score_source_resolution": first_value(row.get("score_source_resolution"), base.get("score_source_resolution")),
        "plan_source_url": first_value(row.get("plan_source_url"), base.get("plan_source_url")),
        "score_source_url": first_value(row.get("score_source_url"), base.get("score_source_url")),
    }


def closed_reason() -> str:
    return "pre-ML human/GPT review closeout only; canonical training layer and ML remain closed until human-approved canonical rebuild"


def action_common(base: dict[str, str], overlay: dict[str, str] | None = None) -> dict[str, str]:
    facts = base_facts(base, overlay)
    return {
        "school_key": base.get("school_key", ""),
        "school_name": first_value((overlay or {}).get("school_name"), base.get("school_name")),
        "source_gate_status": first_value((overlay or {}).get("gate_status"), (overlay or {}).get("post_gap_fill_gate_status"), base.get("gate_status")),
        "source_readiness_band": first_value((overlay or {}).get("readiness_band"), (overlay or {}).get("post_gap_fill_readiness_band"), base.get("readiness_band")),
        "review_lane": first_value((overlay or {}).get("review_lane"), (overlay or {}).get("post_gap_fill_review_lane"), base.get("review_lane")),
        "review_risk_score": first_value((overlay or {}).get("review_risk_score"), (overlay or {}).get("post_gap_fill_review_risk_score"), base.get("review_risk_score")),
        "canonical_ml_entry_open": "false",
        "canonical_ml_closed_reason": closed_reason(),
        "pool_expansion_allowed": "false",
        "non211_search_allowed": "false",
        "deep_research_mainline_allowed": "false",
        **facts,
    }


def d1_row(base: dict[str, str], decision: dict[str, str]) -> dict[str, str]:
    row = action_common(base, decision)
    row.update(
        {
            "source_layer": "D1_G1_clean_gpt_decision",
            "final_gate_bucket": "B1_ready_clean_review_gate",
            "action_priority": "01_D1_clean_review_gate",
            "action_status": "review_gate_ready_clean_accepted",
            "review_decision": decision.get("review_decision", ""),
            "review_decision_status": decision.get("decision_status", ""),
            "human_gpt_review_gate_action": "human_confirm_accept_for_review_gate",
            "ready_for_human_gpt_review_gate": bool_text(decision.get("review_decision") == "accept_for_review_gate"),
            "requires_human_acceptance": "false",
            "requires_row_fix": "false",
            "row_fix_status": "not_required",
            "row_fix_priority": "",
            "row_fix_exit_condition": "",
            "gap_fill_status": "not_required",
            "live_source_approval_status": "not_required",
            "approval_request_type": "",
            "approval_priority": "",
            "approval_scope": "",
            "requires_live_source_approval": "false",
            "requires_deep_research_approval": "false",
            "requires_header_cookie_approval": "false",
            "requires_form_replay_approval": "false",
            "requires_browser_state_approval": "false",
            "can_continue_local_only": "true",
            "hold_status": "not_hold",
            "next_owner": "human_gpt_review",
            "next_action": "复核 D1/G1 clean accepted 学校；若人工确认，可进入后续 canonical rebuild 评估，但本层仍不打开 ML。",
            "evidence_summary": compact(decision.get("acceptance_basis", "")),
            "source_record_ids": records(decision, base),
            "record_id": f"{base.get('school_key', '')}-pre-ml-action-board",
            "source_slug": "pre_ml_human_gpt_review_action_board",
        }
    )
    return row


def d2_row(base: dict[str, str], decision: dict[str, str], fix: dict[str, str] | None) -> dict[str, str]:
    overlay = fix or decision
    row = action_common(base, overlay)
    review_decision = decision.get("review_decision", "")
    if review_decision == "accept_for_review_gate":
        bucket = "B2_ready_caution_review_gate"
        priority = "02_D2_caution_review_gate"
        status = "review_gate_ready_caution_accepted"
        human_action = "human_confirm_caution_accept_for_review_gate"
        ready = True
        requires_accept = False
        requires_fix = False
        hold = "not_hold"
        next_owner = "human_gpt_review"
        next_action = "复核 D2/G2 accepted 学校；必须保留 caution note，canonical/ML 仍等待统一重建确认。"
    elif review_decision == "request_row_fix":
        bucket = "B3_row_fix_preview_requires_human_acceptance"
        priority = "03_D2_row_fix_acceptance"
        status = "row_fix_preview_ready_for_human_acceptance" if fix else "row_fix_requested_preview_missing"
        human_action = "human_accept_or_reject_row_fix_preview_then_reassess_g2"
        ready = False
        requires_accept = True
        requires_fix = True
        hold = "row_fix_hold_before_review_gate"
        next_owner = "human_row_fix_acceptance"
        next_action = first_value(
            (fix or {}).get("recommended_action"),
            "先完成人工接受或驳回 row fix preview，再重评是否可带备注进入复核闸门。",
        )
    else:
        bucket = "B4_hold_before_ml"
        priority = "04_D2_hold_before_ml"
        status = "hold_before_ml_from_d2_g2_review"
        human_action = "human_decide_hold_or_reopen_fix_path"
        ready = False
        requires_accept = False
        requires_fix = False
        hold = "hold_before_ml"
        next_owner = "human_gate_owner"
        next_action = "保持 hold_before_ml；如要重开，先新增明确的 row fix 或来源补证任务。"

    row.update(
        {
            "source_layer": "D2_G2_caution_gpt_decision",
            "final_gate_bucket": bucket,
            "action_priority": priority,
            "action_status": status,
            "review_decision": review_decision,
            "review_decision_status": decision.get("decision_status", ""),
            "human_gpt_review_gate_action": human_action,
            "ready_for_human_gpt_review_gate": bool_text(ready),
            "requires_human_acceptance": bool_text(requires_accept),
            "requires_row_fix": bool_text(requires_fix),
            "row_fix_status": first_value((fix or {}).get("fix_queue_status"), "not_required" if not requires_fix else "requested"),
            "row_fix_priority": (fix or {}).get("fix_priority", ""),
            "row_fix_exit_condition": (fix or {}).get("exit_condition", ""),
            "gap_fill_status": "not_required",
            "live_source_approval_status": "not_required",
            "approval_request_type": "",
            "approval_priority": "",
            "approval_scope": "",
            "requires_live_source_approval": "false",
            "requires_deep_research_approval": "false",
            "requires_header_cookie_approval": "false",
            "requires_form_replay_approval": "false",
            "requires_browser_state_approval": "false",
            "can_continue_local_only": "true",
            "hold_status": hold,
            "next_owner": next_owner,
            "next_action": compact(next_action),
            "evidence_summary": compact(first_value((fix or {}).get("fix_class"), decision.get("acceptance_basis"), decision.get("blocking_issues"))),
            "source_record_ids": records(decision, fix or {}, base),
            "record_id": f"{base.get('school_key', '')}-pre-ml-action-board",
            "source_slug": "pre_ml_human_gpt_review_action_board",
        }
    )
    return row


def d3_d4_row(base: dict[str, str], decision: dict[str, str], app: dict[str, str] | None) -> dict[str, str]:
    overlay = app or decision
    row = action_common(base, overlay)
    gate = first_value((app or {}).get("post_gap_fill_gate_status"), decision.get("preview_gate_status"), base.get("gate_status"))
    is_caution = "G2" in gate or "caution" in first_value((app or {}).get("acceptance_class"), decision.get("acceptance_class")).lower()
    row.update(
        {
            "source_layer": "D3_D4_gap_fill_application",
            "final_gate_bucket": "B2_ready_caution_review_gate" if is_caution else "B1_ready_clean_review_gate",
            "action_priority": "02_gap_fill_caution_review_gate" if is_caution else "01_gap_fill_clean_review_gate",
            "action_status": "gap_fill_application_ready_for_review_gate" if app else "gap_fill_acceptance_decision_ready_application_missing",
            "review_decision": decision.get("review_decision", ""),
            "review_decision_status": decision.get("decision_status", ""),
            "human_gpt_review_gate_action": "human_confirm_gap_fill_application_for_review_gate",
            "ready_for_human_gpt_review_gate": bool_text(bool(app) and gate.startswith(("G1_", "G2_"))),
            "requires_human_acceptance": "false" if app else "true",
            "requires_row_fix": "false",
            "row_fix_status": "not_required",
            "row_fix_priority": "",
            "row_fix_exit_condition": "",
            "gap_fill_status": first_value((app or {}).get("application_status"), "accepted_waiting_application_layer"),
            "live_source_approval_status": "not_required",
            "approval_request_type": "",
            "approval_priority": "",
            "approval_scope": "",
            "requires_live_source_approval": "false",
            "requires_deep_research_approval": "false",
            "requires_header_cookie_approval": "false",
            "requires_form_replay_approval": "false",
            "requires_browser_state_approval": "false",
            "can_continue_local_only": "true",
            "hold_status": "not_hold" if app else "gap_fill_application_pending",
            "next_owner": "human_gpt_review",
            "next_action": compact(first_value((app or {}).get("application_notes"), decision.get("pass_route"))),
            "evidence_summary": compact(first_value((app or {}).get("candidate_source_ids"), decision.get("acceptance_basis"))),
            "source_record_ids": records(decision, app or {}, base),
            "record_id": f"{base.get('school_key', '')}-pre-ml-action-board",
            "source_slug": "pre_ml_human_gpt_review_action_board",
        }
    )
    return row


def g4_row(base: dict[str, str], closeout: dict[str, str], approval: dict[str, str] | None) -> dict[str, str]:
    overlay = closeout
    row = action_common(base, overlay)
    row.update(
        {
            "source_layer": "G4_source_reachability_closeout",
            "final_gate_bucket": "B5_g4_live_source_approval_required",
            "action_priority": first_value((approval or {}).get("approval_priority"), closeout.get("approval_priority"), "05_G4_live_source_approval"),
            "action_status": "g4_hold_live_source_approval_required",
            "review_decision": "hold_in_g4_source_reachability",
            "review_decision_status": "closeout_complete_waiting_human_approval",
            "human_gpt_review_gate_action": "do_not_enter_review_gate_until_official_source_approved",
            "ready_for_human_gpt_review_gate": "false",
            "requires_human_acceptance": "true",
            "requires_row_fix": "false",
            "row_fix_status": "not_required",
            "row_fix_priority": "",
            "row_fix_exit_condition": "",
            "gap_fill_status": "not_required",
            "live_source_approval_status": "approval_required",
            "approval_request_type": first_value((approval or {}).get("approval_request_type"), closeout.get("approval_request_type")),
            "approval_priority": first_value((approval or {}).get("approval_priority"), closeout.get("approval_priority")),
            "approval_scope": first_value((approval or {}).get("approval_scope"), closeout.get("deep_research_boundary")),
            "requires_live_source_approval": first_value(closeout.get("requires_live_network_approval"), "true"),
            "requires_deep_research_approval": first_value(closeout.get("requires_deep_research_approval"), "false"),
            "requires_header_cookie_approval": first_value(closeout.get("requires_header_cookie_approval"), "false"),
            "requires_form_replay_approval": first_value(closeout.get("requires_form_replay_approval"), "false"),
            "requires_browser_state_approval": first_value(closeout.get("requires_browser_state_approval"), "false"),
            "can_continue_local_only": first_value(closeout.get("can_continue_local_only"), "false"),
            "hold_status": "g4_source_reachability_hold",
            "next_owner": "human_live_source_approval",
            "next_action": compact(first_value((approval or {}).get("next_action"), closeout.get("next_action"))),
            "evidence_summary": compact(closeout.get("source_evidence_summary", "")),
            "source_record_ids": records(closeout, approval or {}, base),
            "record_id": f"{base.get('school_key', '')}-pre-ml-action-board",
            "source_slug": "pre_ml_human_gpt_review_action_board",
        }
    )
    return row


def fallback_row(base: dict[str, str]) -> dict[str, str]:
    row = action_common(base)
    row.update(
        {
            "source_layer": "unclassified_post_gap_fill_status",
            "final_gate_bucket": "B9_needs_manual_classification",
            "action_priority": "09_manual_classification",
            "action_status": "manual_classification_required",
            "review_decision": "",
            "review_decision_status": "",
            "human_gpt_review_gate_action": "manual_classify_before_next_step",
            "ready_for_human_gpt_review_gate": "false",
            "requires_human_acceptance": "true",
            "requires_row_fix": "false",
            "row_fix_status": "unknown",
            "row_fix_priority": "",
            "row_fix_exit_condition": "",
            "gap_fill_status": "unknown",
            "live_source_approval_status": "unknown",
            "approval_request_type": "",
            "approval_priority": "",
            "approval_scope": "",
            "requires_live_source_approval": "false",
            "requires_deep_research_approval": "false",
            "requires_header_cookie_approval": "false",
            "requires_form_replay_approval": "false",
            "requires_browser_state_approval": "false",
            "can_continue_local_only": "false",
            "hold_status": "manual_classification_hold",
            "next_owner": "human_gate_owner",
            "next_action": "该校未命中 D1/D2/D3/G4 已知层；先检查输入表完整性。",
            "evidence_summary": "",
            "source_record_ids": records(base),
            "record_id": f"{base.get('school_key', '')}-pre-ml-action-board",
            "source_slug": "pre_ml_human_gpt_review_action_board",
        }
    )
    return row


def closeout_from_board(row: dict[str, object], rank: int) -> dict[str, object]:
    ready = row.get("ready_for_human_gpt_review_gate") == "true"
    requires_live = row.get("requires_live_source_approval") == "true"
    requires_fix = row.get("requires_row_fix") == "true"
    if ready:
        next_decision = "human_gpt_review_gate_confirm_accept_or_hold"
        final_action = "route_to_human_gpt_review_gate"
        dependency = "human/GPT review decision; no ML until canonical rebuild is separately approved"
    elif requires_fix:
        next_decision = "human_accept_or_reject_row_fix_preview"
        final_action = "hold_before_review_gate_until_row_fix_accepted"
        dependency = first_value(row.get("row_fix_exit_condition"), "row fix human acceptance")
    elif requires_live:
        next_decision = "human_approve_or_reject_live_source_scope"
        final_action = "hold_in_g4_source_reachability_branch"
        dependency = first_value(row.get("approval_request_type"), "live source approval")
    else:
        next_decision = "human_decide_hold_or_reopen"
        final_action = "hold_before_ml"
        dependency = first_value(row.get("hold_status"), "manual hold")

    return {
        "closeout_rank": rank,
        "school_key": row.get("school_key", ""),
        "school_name": row.get("school_name", ""),
        "final_gate_bucket": row.get("final_gate_bucket", ""),
        "final_gate_status": row.get("action_status", ""),
        "ready_for_human_gpt_review_gate": row.get("ready_for_human_gpt_review_gate", ""),
        "next_required_decision": next_decision,
        "final_pre_ml_action": final_action,
        "canonical_ml_action": "keep_closed",
        "closeout_reason": row.get("canonical_ml_closed_reason", ""),
        "remaining_dependency": dependency,
        "source_layer": row.get("source_layer", ""),
        "review_decision": row.get("review_decision", ""),
        "hold_status": row.get("hold_status", ""),
        "record_id": f"{row.get('school_key', '')}-pre-ml-final-gate-closeout",
        "source_record_id": row.get("record_id", ""),
        "source_slug": "pre_ml_final_gate_closeout",
    }


def rollup_rows(board_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    buckets = Counter(str(row["final_gate_bucket"]) for row in board_rows)
    statuses = Counter(str(row["action_status"]) for row in board_rows)
    decisions = Counter(str(row["review_decision"]) for row in board_rows)
    sources = Counter(str(row["source_layer"]) for row in board_rows)
    approval_types = Counter(
        str(row["approval_request_type"]) for row in board_rows if row.get("approval_request_type")
    )
    base_metrics = [
        {"metric": "main_pool_school_count", "value": len(board_rows)},
        {"metric": "ready_for_human_gpt_review_gate_count", "value": sum(row["ready_for_human_gpt_review_gate"] == "true" for row in board_rows)},
        {"metric": "requires_human_acceptance_count", "value": sum(row["requires_human_acceptance"] == "true" for row in board_rows)},
        {"metric": "requires_row_fix_count", "value": sum(row["requires_row_fix"] == "true" for row in board_rows)},
        {"metric": "row_fix_preview_ready_count", "value": sum(row["action_status"] == "row_fix_preview_ready_for_human_acceptance" for row in board_rows)},
        {"metric": "requires_live_source_approval_count", "value": sum(row["requires_live_source_approval"] == "true" for row in board_rows)},
        {"metric": "requires_deep_research_approval_count", "value": sum(row["requires_deep_research_approval"] == "true" for row in board_rows)},
        {"metric": "requires_header_cookie_approval_count", "value": sum(row["requires_header_cookie_approval"] == "true" for row in board_rows)},
        {"metric": "requires_form_replay_approval_count", "value": sum(row["requires_form_replay_approval"] == "true" for row in board_rows)},
        {"metric": "requires_browser_state_approval_count", "value": sum(row["requires_browser_state_approval"] == "true" for row in board_rows)},
        {"metric": "canonical_ml_entry_open_count", "value": sum(row["canonical_ml_entry_open"] == "true" for row in board_rows)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for name, count in sorted(buckets.items()):
        base_metrics.append({"metric": f"final_gate_bucket::{name}", "value": count})
    for name, count in sorted(statuses.items()):
        base_metrics.append({"metric": f"action_status::{name}", "value": count})
    for name, count in sorted(decisions.items()):
        base_metrics.append({"metric": f"review_decision::{name}", "value": count})
    for name, count in sorted(sources.items()):
        base_metrics.append({"metric": f"source_layer::{name}", "value": count})
    for name, count in sorted(approval_types.items()):
        base_metrics.append({"metric": f"approval_request_type::{name}", "value": count})
    return base_metrics


def write_doc(board_rows: list[dict[str, object]], closeout_rows: list[dict[str, object]]) -> None:
    buckets = Counter(str(row["final_gate_bucket"]) for row in board_rows)
    statuses = Counter(str(row["action_status"]) for row in board_rows)
    ready_rows = [row for row in board_rows if row["ready_for_human_gpt_review_gate"] == "true"]
    row_fix_rows = [row for row in board_rows if row["requires_row_fix"] == "true"]
    g4_rows = [row for row in board_rows if row["requires_live_source_approval"] == "true"]
    hold_rows = [row for row in board_rows if row["hold_status"] == "hold_before_ml"]

    lines = [
        "# Pre-ML human/GPT review action board and gate closeout",
        "",
        "本报告只合并本地已生成的 D1/G1、D2/G2、D3/D4、D2 row fix 和 G4 closeout 层；未联网，未运行 Deep Research，未 replay header/cookie/form/browser 态，也未打开 canonical/ML 入口。",
        "",
        "## Coverage",
        "",
        f"- 主池学校数：{len(board_rows)}",
        f"- 可进入 human/GPT 复核闸门：{len(ready_rows)}",
        f"- D2 row fix preview 待人工接受：{len(row_fix_rows)}",
        f"- G4 live source approval 待批准：{len(g4_rows)}",
        f"- D2 hold_before_ml：{len(hold_rows)}",
        "- canonical/ML 入口：0 所打开",
        "- 扩池 / 非 211 搜索 / Deep Research 主线：全部关闭",
        "",
        "## Gate buckets",
        "",
    ]
    for bucket, count in sorted(buckets.items()):
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "## Action statuses", ""])
    for status, count in sorted(statuses.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Ready for human/GPT review gate", ""])
    for row in ready_rows:
        lines.append(f"- {row['school_name']}：{row['final_gate_bucket']} / {row['review_decision']}")

    lines.extend(["", "## Row fix acceptance queue", ""])
    if row_fix_rows:
        for row in row_fix_rows:
            lines.append(
                f"- {row['school_name']}：{row['row_fix_priority']} / {row['row_fix_exit_condition']}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## G4 approval queue", ""])
    for row in g4_rows:
        lines.append(
            f"- {row['school_name']}：{row['approval_priority']} / {row['approval_request_type']} / local_only={row['can_continue_local_only']}"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- 允许：逐校 human/GPT 复核、人工接受或驳回 D2 row fix preview、人工批准或驳回 G4 官方来源可达性支线。",
            "- 禁止：扩充主数据池、非 211 搜索、把 G4 或 row fix preview 直接写入 canonical、启动模型训练。",
            "",
            "## Output files",
            "",
            f"- `{ACTION_BOARD_OUT.relative_to(ROOT)}`",
            f"- `{FINAL_CLOSEOUT_OUT.relative_to(ROOT)}`",
            f"- `{ACTION_BOARD_ROLLUP.relative_to(ROOT)}`",
            f"- `{FINAL_CLOSEOUT_ROLLUP.relative_to(ROOT)}`",
            f"- `{DOC_OUT.relative_to(ROOT)}`",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base_rows = read_csv(BASE_STATUS)
    d1 = by_school(read_csv(D1_DECISIONS))
    d2 = by_school(read_csv(D2_DECISIONS))
    d3_d4 = by_school(read_csv(D3_D4_DECISIONS))
    gap_app = by_school(read_csv(GAP_FILL_APPLICATION))
    d2_fixes = by_school(read_csv(D2_ROW_FIX_STATUS))
    g4_closeout = by_school(read_csv(G4_CLOSEOUT))
    g4_approval = by_school(read_csv(G4_APPROVAL))

    board_rows: list[dict[str, object]] = []
    for base in base_rows:
        key = base.get("school_key", "")
        if key in d1:
            row = d1_row(base, d1[key])
        elif key in d2:
            row = d2_row(base, d2[key], d2_fixes.get(key))
        elif key in d3_d4:
            row = d3_d4_row(base, d3_d4[key], gap_app.get(key))
        elif key in g4_closeout:
            row = g4_row(base, g4_closeout[key], g4_approval.get(key))
        else:
            row = fallback_row(base)
        board_rows.append(row)

    def sort_key(row: dict[str, object]) -> tuple[str, str, str]:
        return (
            str(row.get("action_priority", "")),
            str(row.get("final_gate_bucket", "")),
            str(row.get("school_key", "")),
        )

    board_rows.sort(key=sort_key)
    for i, row in enumerate(board_rows, start=1):
        row["board_rank"] = i

    closeout_rows = [closeout_from_board(row, i) for i, row in enumerate(board_rows, start=1)]
    write_csv(ACTION_BOARD_OUT, board_rows, ACTION_BOARD_FIELDS)
    write_csv(FINAL_CLOSEOUT_OUT, closeout_rows, FINAL_CLOSEOUT_FIELDS)
    write_csv(ACTION_BOARD_ROLLUP, rollup_rows(board_rows), ["metric", "value"])
    write_csv(FINAL_CLOSEOUT_ROLLUP, rollup_rows(board_rows), ["metric", "value"])
    write_doc(board_rows, closeout_rows)
    print(
        "action_board_rows="
        f"{len(board_rows)} ready_for_review="
        f"{sum(row['ready_for_human_gpt_review_gate'] == 'true' for row in board_rows)} "
        "row_fix_required="
        f"{sum(row['requires_row_fix'] == 'true' for row in board_rows)} "
        "g4_live_approval="
        f"{sum(row['requires_live_source_approval'] == 'true' for row in board_rows)}"
    )


if __name__ == "__main__":
    main()
