from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a status table for the engineering-school Guangxi data pipeline."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="School matrix CSV.",
    )
    parser.add_argument(
        "--seed-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_seed_school_summary.csv",
        help="Merged Guangxi seed summary CSV.",
    )
    parser.add_argument(
        "--ajax-log",
        type=Path,
        default=Path("reports") / "engineering_api_fetch_ajax_family.csv",
        help="Ajax-family fetch log CSV.",
    )
    parser.add_argument(
        "--static-ajax-summary",
        type=Path,
        default=Path("reports") / "static_ajax_school_summary.csv",
        help="Static AJAX page summary CSV.",
    )
    parser.add_argument(
        "--same-family-probe-log",
        type=Path,
        default=Path("reports") / "engineering_same_family_probe.csv",
        help="Same-family browser-header probe log CSV.",
    )
    parser.add_argument(
        "--cached-pdf-inventory",
        type=Path,
        default=Path("reports") / "cached_pdf_inventory.csv",
        help="Cached PDF inventory CSV.",
    )
    parser.add_argument(
        "--pdf-structured-summary",
        type=Path,
        default=Path("reports") / "beijing_gongye_cached_pdf_summary.csv",
        help="Structured PDF extraction summary CSV.",
    )
    parser.add_argument(
        "--bjut-pdf-rows",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "beijing_gongye_guangxi_plan_rows.csv",
        help="Structured BJUT Guangxi plan rows extracted from cached PDFs.",
    )
    parser.add_argument(
        "--hebut-pdf-rows",
        type=Path,
        default=Path("clean_data") / "cached_pdf_structured" / "hebei_gongye_guangxi_plan_rows.csv",
        help="Structured Hebut Guangxi plan rows extracted from cached PDF.",
    )
    parser.add_argument(
        "--form-replay-log",
        type=Path,
        default=Path("reports") / "shanghai_daxue_fineui_variant_probe.csv",
        help="Form replay probe summary CSV.",
    )
    parser.add_argument(
        "--score-summary-school-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_score_summary_school_summary.csv",
        help="School-level Guangxi score summary CSV.",
    )
    parser.add_argument(
        "--score-summary-rank-enrichment-school-summary",
        type=Path,
        default=Path("reports") / "engineering_score_summary_rank_enrichment_school_summary.csv",
        help="School-level Guangxi score-summary rank enrichment CSV.",
    )
    parser.add_argument(
        "--plan-summary-school-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_plan_summary_school_summary.csv",
        help="School-level Guangxi plan summary CSV.",
    )
    parser.add_argument(
        "--overview-school-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_overview_school_summary.csv",
        help="School-level Guangxi overview summary CSV.",
    )
    parser.add_argument(
        "--integrated-school-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_integrated_school_summary.csv",
        help="School-year integrated Guangxi summary CSV.",
    )
    parser.add_argument(
        "--integrated-type-school-summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_integrated_type_school_summary.csv",
        help="School-year-type integrated Guangxi summary CSV.",
    )
    parser.add_argument(
        "--primary-snapshot-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_snapshot_school_summary.csv",
        help="Primary Guangxi physics snapshot school summary CSV.",
    )
    parser.add_argument(
        "--primary-trend-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_trend_school_summary.csv",
        help="Primary Guangxi physics trend school summary CSV.",
    )
    parser.add_argument(
        "--primary-canonical-snapshot-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_canonical_snapshot_school_summary.csv",
        help="Canonical primary Guangxi physics snapshot school summary CSV.",
    )
    parser.add_argument(
        "--primary-canonical-trend-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_canonical_trend_school_summary.csv",
        help="Canonical primary Guangxi physics trend school summary CSV.",
    )
    parser.add_argument(
        "--primary-latest-snapshot-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_latest_snapshot_school_summary.csv",
        help="Latest primary Guangxi physics snapshot school summary CSV.",
    )
    parser.add_argument(
        "--primary-latest-profile-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_latest_profile_school_summary.csv",
        help="Latest primary Guangxi physics profile school summary CSV.",
    )
    parser.add_argument(
        "--primary-best-comparable-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_best_comparable_school_summary.csv",
        help="Best comparable primary Guangxi physics profile school summary CSV.",
    )
    parser.add_argument(
        "--primary-best-comparable-signal-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_best_comparable_signal_school_summary.csv",
        help="Best comparable primary Guangxi physics signal school summary CSV.",
    )
    parser.add_argument(
        "--best-comparable-review-queue-school-summary",
        type=Path,
        default=Path("reports") / "engineering_best_comparable_review_queue_school_summary.csv",
        help="Best comparable review queue school summary CSV.",
    )
    parser.add_argument(
        "--unified-review-operating-queue-school-summary",
        type=Path,
        default=Path("reports") / "engineering_unified_review_operating_queue_school_summary.csv",
        help="Unified review operating queue school summary CSV.",
    )
    parser.add_argument(
        "--actionable-school-card-school-summary",
        type=Path,
        default=Path("reports") / "engineering_actionable_school_cards_school_summary.csv",
        help="Actionable school cards school summary CSV.",
    )
    parser.add_argument(
        "--actionable-evidence-pack-school-summary",
        type=Path,
        default=Path("reports") / "engineering_actionable_evidence_pack_school_summary.csv",
        help="Actionable evidence pack school summary CSV.",
    )
    parser.add_argument(
        "--primary-signal-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_signal_school_summary.csv",
        help="Primary Guangxi physics signal sheet school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-review-queue-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_queue_school_summary.csv",
        help="Pre-ML review queue school summary CSV.",
    )
    parser.add_argument(
        "--primary-field-gap-school-summary",
        type=Path,
        default=Path("reports") / "engineering_primary_field_gap_school_summary.csv",
        help="Primary field-gap matrix school summary CSV.",
    )
    parser.add_argument(
        "--cold-queue-entry-school-summary",
        type=Path,
        default=Path("reports") / "engineering_cold_queue_entry_registry_school_summary.csv",
        help="Cold-queue official entry registry school summary CSV.",
    )
    parser.add_argument(
        "--cold-queue-unlock-school-summary",
        type=Path,
        default=Path("reports") / "engineering_cold_queue_unlock_queue_school_summary.csv",
        help="Cold-queue unlock queue school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-model-readiness-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_model_readiness_school_summary.csv",
        help="Pre-ML model readiness school summary CSV.",
    )
    parser.add_argument(
        "--m3-rescue-round-school-summary",
        type=Path,
        default=Path("reports") / "engineering_m3_rescue_round_school_summary.csv",
        help="M3 rescue round school summary CSV.",
    )
    parser.add_argument(
        "--score-source-remediation-round-school-summary",
        type=Path,
        default=Path("reports") / "engineering_score_source_remediation_round_school_summary.csv",
        help="Score-source remediation round school summary CSV.",
    )
    parser.add_argument(
        "--source-resolution-matrix-school-summary",
        type=Path,
        default=Path("reports") / "engineering_source_resolution_matrix_school_summary.csv",
        help="Source resolution matrix school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-handoff-pack-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_handoff_pack_school_summary.csv",
        help="Pre-ML handoff pack school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-review-workbench-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_workbench_school_summary.csv",
        help="Pre-ML review workbench school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-gate-status-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_gate_status_school_summary.csv",
        help="Pre-ML gate status school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-remaining-action-backlog-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_remaining_action_backlog_school_summary.csv",
        help="Pre-ML remaining action backlog school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-local-gap-fill-candidates-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_local_gap_fill_candidates_school_summary.csv",
        help="Pre-ML local gap-fill candidates school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-gap-fill-impact-preview-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_gap_fill_impact_preview_school_summary.csv",
        help="Pre-ML gap-fill impact preview school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-review-gate-candidate-pack-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_candidate_pack_school_summary.csv",
        help="Pre-ML review gate candidate pack school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-review-gate-checklist-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_checklist_school_summary.csv",
        help="Pre-ML review gate checklist school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-review-gate-consistency-audit-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_consistency_audit_school_summary.csv",
        help="Pre-ML review gate consistency audit school summary CSV.",
    )
    parser.add_argument(
        "--pre-ml-review-gate-decision-register-school-summary",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_decision_register_school_summary.csv",
        help="Pre-ML review gate decision register school summary CSV.",
    )
    parser.add_argument(
        "--gpt55-takeover-launchpad-school-summary",
        type=Path,
        default=Path("reports") / "engineering_gpt55_takeover_launchpad_school_summary.csv",
        help="GPT-5.5 takeover launchpad school summary CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Output status CSV.",
    )
    parser.add_argument(
        "--raw-data-root",
        type=Path,
        default=Path("raw_data"),
        help="Raw data root used to detect supplemental plan/score page evidence.",
    )
    return parser


def derive_status(
    plan_rows: int,
    score_rows: int,
    pdf_plan_rows: int,
    ajax_ok: int,
    ajax_403: int,
    static_ajax_page_count: int,
    form_replay_variants: int,
    form_replay_success: int,
    has_plan_page: str,
    has_score_page: str,
    supplemental_plan_page: bool,
    supplemental_score_page: bool,
) -> str:
    if (plan_rows > 0 or pdf_plan_rows > 0) and score_rows > 0:
        return "seeded_plan_and_score"
    if plan_rows > 0 or pdf_plan_rows > 0:
        return "seeded_plan_only"
    if score_rows > 0:
        return "seeded_score_only"
    if ajax_ok > 0:
        return "ajax_payloads_present_unseeded"
    if ajax_403 > 0:
        return "ajax_blocked_403"
    if static_ajax_page_count > 0:
        return "ajax_family_page_only"
    if form_replay_variants > 0 and form_replay_success == 0:
        return "form_replay_blocked"
    if has_plan_page == "true" or has_score_page == "true" or supplemental_plan_page or supplemental_score_page:
        return "page_only"
    return "needs_discovery"


def main() -> None:
    args = build_parser().parse_args()
    matrix_rows = read_rows(args.matrix)
    seed_rows = read_rows(args.seed_summary)
    ajax_rows = read_rows(args.ajax_log) if args.ajax_log.exists() else []
    static_ajax_rows = read_rows(args.static_ajax_summary) if args.static_ajax_summary.exists() else []
    same_family_probe_rows = read_rows(args.same_family_probe_log) if args.same_family_probe_log.exists() else []
    cached_pdf_rows = read_rows(args.cached_pdf_inventory) if args.cached_pdf_inventory.exists() else []
    pdf_structured_rows = read_rows(args.pdf_structured_summary) if args.pdf_structured_summary.exists() else []
    bjut_pdf_rows = read_rows(args.bjut_pdf_rows) if args.bjut_pdf_rows.exists() else []
    hebut_pdf_rows = read_rows(args.hebut_pdf_rows) if args.hebut_pdf_rows.exists() else []
    form_replay_rows = read_rows(args.form_replay_log) if args.form_replay_log.exists() else []
    score_summary_rows = (
        read_rows(args.score_summary_school_summary) if args.score_summary_school_summary.exists() else []
    )
    score_summary_rank_enrichment_rows = (
        read_rows(args.score_summary_rank_enrichment_school_summary)
        if args.score_summary_rank_enrichment_school_summary.exists()
        else []
    )
    plan_summary_rows = (
        read_rows(args.plan_summary_school_summary) if args.plan_summary_school_summary.exists() else []
    )
    overview_summary_rows = (
        read_rows(args.overview_school_summary) if args.overview_school_summary.exists() else []
    )
    integrated_summary_rows = (
        read_rows(args.integrated_school_summary) if args.integrated_school_summary.exists() else []
    )
    integrated_type_summary_rows = (
        read_rows(args.integrated_type_school_summary) if args.integrated_type_school_summary.exists() else []
    )
    primary_snapshot_rows = (
        read_rows(args.primary_snapshot_school_summary) if args.primary_snapshot_school_summary.exists() else []
    )
    primary_trend_rows = (
        read_rows(args.primary_trend_school_summary) if args.primary_trend_school_summary.exists() else []
    )
    primary_canonical_snapshot_rows = (
        read_rows(args.primary_canonical_snapshot_school_summary)
        if args.primary_canonical_snapshot_school_summary.exists()
        else []
    )
    primary_canonical_trend_rows = (
        read_rows(args.primary_canonical_trend_school_summary)
        if args.primary_canonical_trend_school_summary.exists()
        else []
    )
    primary_latest_snapshot_rows = (
        read_rows(args.primary_latest_snapshot_school_summary)
        if args.primary_latest_snapshot_school_summary.exists()
        else []
    )
    primary_latest_profile_rows = (
        read_rows(args.primary_latest_profile_school_summary)
        if args.primary_latest_profile_school_summary.exists()
        else []
    )
    primary_best_comparable_rows = (
        read_rows(args.primary_best_comparable_school_summary)
        if args.primary_best_comparable_school_summary.exists()
        else []
    )
    primary_best_comparable_signal_rows = (
        read_rows(args.primary_best_comparable_signal_school_summary)
        if args.primary_best_comparable_signal_school_summary.exists()
        else []
    )
    best_comparable_review_queue_rows = (
        read_rows(args.best_comparable_review_queue_school_summary)
        if args.best_comparable_review_queue_school_summary.exists()
        else []
    )
    unified_review_operating_queue_rows = (
        read_rows(args.unified_review_operating_queue_school_summary)
        if args.unified_review_operating_queue_school_summary.exists()
        else []
    )
    actionable_school_card_rows = (
        read_rows(args.actionable_school_card_school_summary)
        if args.actionable_school_card_school_summary.exists()
        else []
    )
    actionable_evidence_pack_rows = (
        read_rows(args.actionable_evidence_pack_school_summary)
        if args.actionable_evidence_pack_school_summary.exists()
        else []
    )
    primary_signal_rows = (
        read_rows(args.primary_signal_school_summary)
        if args.primary_signal_school_summary.exists()
        else []
    )
    pre_ml_review_queue_rows = (
        read_rows(args.pre_ml_review_queue_school_summary)
        if args.pre_ml_review_queue_school_summary.exists()
        else []
    )
    primary_field_gap_rows = (
        read_rows(args.primary_field_gap_school_summary)
        if args.primary_field_gap_school_summary.exists()
        else []
    )
    cold_queue_entry_rows = (
        read_rows(args.cold_queue_entry_school_summary)
        if args.cold_queue_entry_school_summary.exists()
        else []
    )
    cold_queue_unlock_rows = (
        read_rows(args.cold_queue_unlock_school_summary)
        if args.cold_queue_unlock_school_summary.exists()
        else []
    )
    pre_ml_model_readiness_rows = (
        read_rows(args.pre_ml_model_readiness_school_summary)
        if args.pre_ml_model_readiness_school_summary.exists()
        else []
    )
    m3_rescue_round_rows = (
        read_rows(args.m3_rescue_round_school_summary) if args.m3_rescue_round_school_summary.exists() else []
    )
    score_source_remediation_round_rows = (
        read_rows(args.score_source_remediation_round_school_summary)
        if args.score_source_remediation_round_school_summary.exists()
        else []
    )
    source_resolution_matrix_rows = (
        read_rows(args.source_resolution_matrix_school_summary)
        if args.source_resolution_matrix_school_summary.exists()
        else []
    )
    pre_ml_handoff_pack_rows = (
        read_rows(args.pre_ml_handoff_pack_school_summary)
        if args.pre_ml_handoff_pack_school_summary.exists()
        else []
    )
    gpt55_takeover_launchpad_rows = (
        read_rows(args.gpt55_takeover_launchpad_school_summary)
        if args.gpt55_takeover_launchpad_school_summary.exists()
        else []
    )
    pre_ml_review_workbench_rows = (
        read_rows(args.pre_ml_review_workbench_school_summary)
        if args.pre_ml_review_workbench_school_summary.exists()
        else []
    )
    pre_ml_gate_status_rows = (
        read_rows(args.pre_ml_gate_status_school_summary)
        if args.pre_ml_gate_status_school_summary.exists()
        else []
    )
    pre_ml_remaining_action_backlog_rows = (
        read_rows(args.pre_ml_remaining_action_backlog_school_summary)
        if args.pre_ml_remaining_action_backlog_school_summary.exists()
        else []
    )
    pre_ml_local_gap_fill_candidate_rows = (
        read_rows(args.pre_ml_local_gap_fill_candidates_school_summary)
        if args.pre_ml_local_gap_fill_candidates_school_summary.exists()
        else []
    )
    pre_ml_gap_fill_impact_preview_rows = (
        read_rows(args.pre_ml_gap_fill_impact_preview_school_summary)
        if args.pre_ml_gap_fill_impact_preview_school_summary.exists()
        else []
    )
    pre_ml_review_gate_candidate_pack_rows = (
        read_rows(args.pre_ml_review_gate_candidate_pack_school_summary)
        if args.pre_ml_review_gate_candidate_pack_school_summary.exists()
        else []
    )
    pre_ml_review_gate_checklist_rows = (
        read_rows(args.pre_ml_review_gate_checklist_school_summary)
        if args.pre_ml_review_gate_checklist_school_summary.exists()
        else []
    )
    pre_ml_review_gate_consistency_audit_rows = (
        read_rows(args.pre_ml_review_gate_consistency_audit_school_summary)
        if args.pre_ml_review_gate_consistency_audit_school_summary.exists()
        else []
    )
    pre_ml_review_gate_decision_register_rows = (
        read_rows(args.pre_ml_review_gate_decision_register_school_summary)
        if args.pre_ml_review_gate_decision_register_school_summary.exists()
        else []
    )

    seed_by_key = {
        row["school_key"]: row for row in seed_rows
    }
    static_ajax_by_key = {
        row["school_key"]: row for row in static_ajax_rows
    }
    score_summary_by_key = {
        row["school_key"]: row for row in score_summary_rows
    }
    score_summary_rank_enrichment_by_key = {
        row["school_key"]: row for row in score_summary_rank_enrichment_rows
    }
    plan_summary_by_key = {
        row["school_key"]: row for row in plan_summary_rows
    }
    overview_summary_by_key = {
        row["school_key"]: row for row in overview_summary_rows
    }
    integrated_summary_by_key = {
        row["school_key"]: row for row in integrated_summary_rows
    }
    integrated_type_summary_by_key = {
        row["school_key"]: row for row in integrated_type_summary_rows
    }
    primary_snapshot_by_key = {
        row["school_key"]: row for row in primary_snapshot_rows
    }
    primary_trend_by_key = {
        row["school_key"]: row for row in primary_trend_rows
    }
    primary_canonical_snapshot_by_key = {
        row["school_key"]: row for row in primary_canonical_snapshot_rows
    }
    primary_canonical_trend_by_key = {
        row["school_key"]: row for row in primary_canonical_trend_rows
    }
    primary_latest_snapshot_by_key = {
        row["school_key"]: row for row in primary_latest_snapshot_rows
    }
    primary_latest_profile_by_key = {
        row["school_key"]: row for row in primary_latest_profile_rows
    }
    primary_best_comparable_by_key = {
        row["school_key"]: row for row in primary_best_comparable_rows
    }
    primary_best_comparable_signal_by_key = {
        row["school_key"]: row for row in primary_best_comparable_signal_rows
    }
    best_comparable_review_queue_by_key = {
        row["school_key"]: row for row in best_comparable_review_queue_rows
    }
    unified_review_operating_queue_by_key = {
        row["school_key"]: row for row in unified_review_operating_queue_rows
    }
    actionable_school_card_by_key = {
        row["school_key"]: row for row in actionable_school_card_rows
    }
    actionable_evidence_pack_by_key = {
        row["school_key"]: row for row in actionable_evidence_pack_rows
    }
    primary_signal_by_key = {
        row["school_key"]: row for row in primary_signal_rows
    }
    pre_ml_review_queue_by_key = {
        row["school_key"]: row for row in pre_ml_review_queue_rows
    }
    primary_field_gap_by_key = {
        row["school_key"]: row for row in primary_field_gap_rows
    }
    cold_queue_entry_by_key = {
        row["school_key"]: row for row in cold_queue_entry_rows
    }
    cold_queue_unlock_by_key = {
        row["school_key"]: row for row in cold_queue_unlock_rows
    }
    pre_ml_model_readiness_by_key = {
        row["school_key"]: row for row in pre_ml_model_readiness_rows
    }
    m3_rescue_round_by_key = {
        row["school_key"]: row for row in m3_rescue_round_rows
    }
    score_source_remediation_round_by_key = {
        row["school_key"]: row for row in score_source_remediation_round_rows
    }
    source_resolution_matrix_by_key = {
        row["school_key"]: row for row in source_resolution_matrix_rows
    }
    pre_ml_handoff_pack_by_key = {
        row["school_key"]: row for row in pre_ml_handoff_pack_rows
    }
    gpt55_takeover_launchpad_by_key = {
        row["school_key"]: row for row in gpt55_takeover_launchpad_rows
    }
    pre_ml_review_workbench_by_key = {
        row["school_key"]: row for row in pre_ml_review_workbench_rows
    }
    pre_ml_gate_status_by_key = {
        row["school_key"]: row for row in pre_ml_gate_status_rows
    }
    pre_ml_remaining_action_backlog_by_key = {
        row["school_key"]: row for row in pre_ml_remaining_action_backlog_rows
    }
    pre_ml_local_gap_fill_candidate_by_key = {
        row["school_key"]: row for row in pre_ml_local_gap_fill_candidate_rows
    }
    pre_ml_gap_fill_impact_preview_by_key = {
        row["school_key"]: row for row in pre_ml_gap_fill_impact_preview_rows
    }
    pre_ml_review_gate_candidate_pack_by_key = {
        row["school_key"]: row for row in pre_ml_review_gate_candidate_pack_rows
    }
    pre_ml_review_gate_checklist_by_key = {
        row["school_key"]: row for row in pre_ml_review_gate_checklist_rows
    }
    pre_ml_review_gate_consistency_audit_by_key = {
        row["school_key"]: row for row in pre_ml_review_gate_consistency_audit_rows
    }
    pre_ml_review_gate_decision_register_by_key = {
        row["school_key"]: row for row in pre_ml_review_gate_decision_register_rows
    }

    ajax_ok = Counter()
    ajax_http_error = Counter()
    ajax_403 = Counter()
    ajax_timeout_like = Counter()
    ajax_by_kind = defaultdict(Counter)
    for row in ajax_rows:
        key = row.get("source_id", "")
        status = row.get("status", "")
        if status == "ok":
            ajax_ok[key] += 1
        elif status == "http_error":
            ajax_http_error[key] += 1
            if row.get("error_message", "").startswith("403"):
                ajax_403[key] += 1
        if status in {"timeout", "ssl_error", "url_error"}:
            ajax_timeout_like[key] += 1
        ajax_by_kind[key][row.get("target_kind", "")] += 1

    same_family_ok = Counter()
    same_family_403 = Counter()
    same_family_url_error = Counter()
    same_family_page_ok = Counter()
    same_family_probe_ok = Counter()
    for row in same_family_probe_rows:
        key = row.get("school_key", "")
        status = row.get("status", "")
        probe_kind = row.get("probe_kind", "")
        if status == "ok":
            same_family_ok[key] += 1
            if probe_kind.endswith("_page_get"):
                same_family_page_ok[key] += 1
            else:
                same_family_probe_ok[key] += 1
        elif status == "http_error" and row.get("http_code", "") == "403":
            same_family_403[key] += 1
        elif status == "url_error":
            same_family_url_error[key] += 1

    cached_pdf_count = Counter()
    cached_pdf_guangxi = Counter()
    cached_pdf_physics = Counter()
    cached_pdf_ordinary_batch = Counter()
    seen_pdf = set()
    for row in cached_pdf_rows:
        school_key = row.get("school_key", "")
        pdf_path = row.get("pdf_path", "")
        dedupe_key = (school_key, Path(pdf_path).name)
        if dedupe_key in seen_pdf:
            continue
        seen_pdf.add(dedupe_key)
        cached_pdf_count[school_key] += 1
        if row.get("has_guangxi", "") == "true":
            cached_pdf_guangxi[school_key] += 1
        if row.get("has_physics", "") == "true":
            cached_pdf_physics[school_key] += 1
        if row.get("has_ordinary_batch", "") == "true":
            cached_pdf_ordinary_batch[school_key] += 1

    pdf_structured_guangxi_rows = Counter()
    pdf_structured_source_count = Counter()
    for row in pdf_structured_rows:
        pdf_name = row.get("source_pdf_name", "")
        if pdf_name:
            pdf_structured_source_count["beijing_gongye_211"] += 1
        try:
            pdf_structured_guangxi_rows["beijing_gongye_211"] = max(
                pdf_structured_guangxi_rows["beijing_gongye_211"],
                int(row.get("row_count_guangxi", "0") or 0),
            )
        except ValueError:
            pass
    if bjut_pdf_rows:
        pdf_structured_guangxi_rows["beijing_gongye_211"] = max(
            pdf_structured_guangxi_rows["beijing_gongye_211"],
            len(bjut_pdf_rows),
        )
        pdf_structured_source_count["beijing_gongye_211"] = max(
            pdf_structured_source_count["beijing_gongye_211"],
            len({row.get("source_pdf_name", "") for row in bjut_pdf_rows if row.get("source_pdf_name", "")}),
        )
    if hebut_pdf_rows:
        pdf_structured_guangxi_rows["hebei_gongye_211"] += len(hebut_pdf_rows)
        pdf_structured_source_count["hebei_gongye_211"] += len(
            {row.get("source_pdf_name", "") for row in hebut_pdf_rows if row.get("source_pdf_name", "")}
        )

    form_replay_variants = Counter()
    form_replay_success = Counter()
    form_replay_rows_max = Counter()
    for row in form_replay_rows:
        key = "shanghai_daxue_211"
        form_replay_variants[key] += 1
        if row.get("year_ok") == "true" and row.get("province_ok") == "true":
            form_replay_success[key] += 1
        try:
            form_replay_rows_max[key] = max(
                form_replay_rows_max.get(key, 0),
                int(row.get("record_count", "-1") or -1),
            )
        except ValueError:
            pass

    supplemental_plan_page = Counter()
    supplemental_score_page = Counter()
    if args.raw_data_root.exists():
        for page in args.raw_data_root.rglob("*.html"):
            school_key = page.parent.name
            name = page.name.lower()
            if "zsjh" in name:
                supplemental_plan_page[school_key] += 1
            if "lnfs" in name:
                supplemental_score_page[school_key] += 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "school_key",
        "school_name",
        "engineering_tier",
        "fetched_ok_count",
        "has_plan_page",
        "has_score_page",
        "has_rule_page",
        "supplemental_plan_page",
        "supplemental_score_page",
        "plan_rows",
        "score_major_rows",
        "ajax_ok",
        "ajax_http_error",
        "ajax_403",
        "ajax_timeout_like",
        "ajax_targets_seen",
        "static_ajax_page_count",
        "static_ajax_source_buckets",
        "static_ajax_param_endpoints",
        "static_ajax_data_endpoints",
        "static_ajax_config_signature",
        "same_family_probe_ok",
        "same_family_page_ok",
        "same_family_403",
        "same_family_url_error",
        "cached_pdf_count",
        "cached_pdf_guangxi_count",
        "cached_pdf_physics_count",
        "cached_pdf_ordinary_batch_count",
        "pdf_structured_source_count",
        "pdf_structured_guangxi_rows",
        "form_replay_variants_tested",
        "form_replay_success_count",
        "form_replay_record_count_max",
        "plan_summary_rows",
        "score_summary_rows",
        "score_summary_rank_enriched_rows",
        "overview_summary_rows",
        "integrated_summary_rows",
        "integrated_type_summary_rows",
        "primary_snapshot_rows",
        "primary_trend_rows",
        "primary_canonical_snapshot_rows",
        "primary_canonical_trend_rows",
        "primary_latest_snapshot_rows",
        "primary_latest_profile_rows",
        "primary_best_comparable_rows",
        "primary_best_comparable_signal_rows",
        "best_comparable_review_queue_rows",
        "unified_review_operating_queue_rows",
        "actionable_school_card_rows",
        "actionable_evidence_pack_rows",
        "primary_signal_rows",
        "pre_ml_review_queue_rows",
        "primary_field_gap_rows",
        "cold_queue_entry_rows",
        "cold_queue_unlock_rows",
        "pre_ml_model_readiness_rows",
        "m3_rescue_round_rows",
        "score_source_remediation_round_rows",
        "source_resolution_matrix_rows",
        "pre_ml_handoff_pack_rows",
        "gpt55_takeover_launchpad_rows",
        "pre_ml_review_workbench_rows",
        "pre_ml_gate_status_rows",
        "pre_ml_remaining_action_backlog_rows",
        "pre_ml_local_gap_fill_candidate_rows",
        "pre_ml_gap_fill_impact_preview_rows",
        "pre_ml_review_gate_candidate_pack_rows",
        "pre_ml_review_gate_checklist_rows",
        "pre_ml_review_gate_consistency_audit_rows",
        "pre_ml_review_gate_decision_register_rows",
        "pipeline_status",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in matrix_rows:
            key = row["seed_id"]
            seed = seed_by_key.get(key, {})
            static_ajax = static_ajax_by_key.get(key, {})
            plan_rows = int(seed.get("plan_rows", "0") or 0)
            score_rows = int(seed.get("score_major_rows", "0") or 0)
            pdf_plan_rows = pdf_structured_guangxi_rows.get(key, 0)
            ok_count = ajax_ok.get(key, 0)
            http_error_count = ajax_http_error.get(key, 0)
            blocked_403_count = ajax_403.get(key, 0)
            timeout_like_count = ajax_timeout_like.get(key, 0)
            has_supp_plan = supplemental_plan_page.get(key, 0) > 0
            has_supp_score = supplemental_score_page.get(key, 0) > 0
            static_ajax_page_count = int(static_ajax.get("page_count", "0") or 0)
            writer.writerow(
                {
                    "school_key": key,
                    "school_name": row["source_name"],
                    "engineering_tier": row["engineering_tier"],
                    "fetched_ok_count": row["fetched_ok_count"],
                    "has_plan_page": row["has_plan_page"],
                    "has_score_page": row["has_score_page"],
                    "has_rule_page": row["has_rule_page"],
                    "supplemental_plan_page": str(has_supp_plan).lower(),
                    "supplemental_score_page": str(has_supp_score).lower(),
                    "plan_rows": plan_rows,
                    "score_major_rows": score_rows,
                    "ajax_ok": ok_count,
                    "ajax_http_error": http_error_count,
                    "ajax_403": blocked_403_count,
                    "ajax_timeout_like": timeout_like_count,
                    "ajax_targets_seen": sum(ajax_by_kind.get(key, Counter()).values()),
                    "static_ajax_page_count": static_ajax_page_count,
                    "static_ajax_source_buckets": static_ajax.get("source_buckets", ""),
                    "static_ajax_param_endpoints": static_ajax.get("param_endpoints", ""),
                    "static_ajax_data_endpoints": static_ajax.get("data_endpoints", ""),
                    "static_ajax_config_signature": static_ajax.get("config_name_signature", ""),
                    "same_family_probe_ok": same_family_probe_ok.get(key, 0),
                    "same_family_page_ok": same_family_page_ok.get(key, 0),
                    "same_family_403": same_family_403.get(key, 0),
                    "same_family_url_error": same_family_url_error.get(key, 0),
                    "cached_pdf_count": cached_pdf_count.get(key, 0),
                    "cached_pdf_guangxi_count": cached_pdf_guangxi.get(key, 0),
                    "cached_pdf_physics_count": cached_pdf_physics.get(key, 0),
                    "cached_pdf_ordinary_batch_count": cached_pdf_ordinary_batch.get(key, 0),
                    "pdf_structured_source_count": pdf_structured_source_count.get(key, 0),
                    "pdf_structured_guangxi_rows": pdf_structured_guangxi_rows.get(key, 0),
                    "form_replay_variants_tested": form_replay_variants.get(key, 0),
                    "form_replay_success_count": form_replay_success.get(key, 0),
                    "form_replay_record_count_max": form_replay_rows_max.get(key, 0),
                    "plan_summary_rows": plan_summary_by_key.get(key, {}).get("plan_summary_rows", "0"),
                    "score_summary_rows": score_summary_by_key.get(key, {}).get("score_summary_rows", "0"),
                    "score_summary_rank_enriched_rows": score_summary_rank_enrichment_by_key.get(key, {}).get(
                        "score_summary_rank_enriched_rows", "0"
                    ),
                    "overview_summary_rows": overview_summary_by_key.get(key, {}).get("overview_summary_rows", "0"),
                    "integrated_summary_rows": integrated_summary_by_key.get(key, {}).get("integrated_summary_rows", "0"),
                    "integrated_type_summary_rows": integrated_type_summary_by_key.get(key, {}).get("integrated_type_summary_rows", "0"),
                    "primary_snapshot_rows": primary_snapshot_by_key.get(key, {}).get("primary_snapshot_rows", "0"),
                    "primary_trend_rows": primary_trend_by_key.get(key, {}).get("primary_trend_rows", "0"),
                    "primary_canonical_snapshot_rows": primary_canonical_snapshot_by_key.get(key, {}).get("primary_canonical_snapshot_rows", "0"),
                    "primary_canonical_trend_rows": primary_canonical_trend_by_key.get(key, {}).get("primary_canonical_trend_rows", "0"),
                    "primary_latest_snapshot_rows": primary_latest_snapshot_by_key.get(key, {}).get("primary_latest_snapshot_rows", "0"),
                    "primary_latest_profile_rows": primary_latest_profile_by_key.get(key, {}).get("primary_latest_profile_rows", "0"),
                    "primary_best_comparable_rows": primary_best_comparable_by_key.get(key, {}).get("primary_best_comparable_rows", "0"),
                    "primary_best_comparable_signal_rows": primary_best_comparable_signal_by_key.get(key, {}).get(
                        "primary_best_comparable_signal_rows", "0"
                    ),
                    "best_comparable_review_queue_rows": best_comparable_review_queue_by_key.get(key, {}).get(
                        "best_comparable_review_queue_rows", "0"
                    ),
                    "unified_review_operating_queue_rows": unified_review_operating_queue_by_key.get(key, {}).get(
                        "unified_review_operating_queue_rows", "0"
                    ),
                    "actionable_school_card_rows": actionable_school_card_by_key.get(key, {}).get(
                        "actionable_school_card_rows", "0"
                    ),
                    "actionable_evidence_pack_rows": actionable_evidence_pack_by_key.get(key, {}).get(
                        "actionable_evidence_pack_rows", "0"
                    ),
                    "primary_signal_rows": primary_signal_by_key.get(key, {}).get("primary_signal_rows", "0"),
                    "pre_ml_review_queue_rows": pre_ml_review_queue_by_key.get(key, {}).get("pre_ml_review_queue_rows", "0"),
                    "primary_field_gap_rows": primary_field_gap_by_key.get(key, {}).get("primary_field_gap_rows", "0"),
                    "cold_queue_entry_rows": cold_queue_entry_by_key.get(key, {}).get("cold_queue_entry_rows", "0"),
                    "cold_queue_unlock_rows": cold_queue_unlock_by_key.get(key, {}).get("cold_queue_unlock_rows", "0"),
                    "pre_ml_model_readiness_rows": pre_ml_model_readiness_by_key.get(key, {}).get("pre_ml_model_readiness_rows", "0"),
                    "m3_rescue_round_rows": m3_rescue_round_by_key.get(key, {}).get("m3_rescue_round_rows", "0"),
                    "score_source_remediation_round_rows": score_source_remediation_round_by_key.get(key, {}).get(
                        "score_source_remediation_round_rows", "0"
                    ),
                    "source_resolution_matrix_rows": source_resolution_matrix_by_key.get(key, {}).get(
                        "source_resolution_matrix_rows", "0"
                    ),
                    "pre_ml_handoff_pack_rows": pre_ml_handoff_pack_by_key.get(key, {}).get(
                        "pre_ml_handoff_pack_rows", "0"
                    ),
                    "gpt55_takeover_launchpad_rows": (
                        "1" if key in gpt55_takeover_launchpad_by_key else "0"
                    ),
                    "pre_ml_review_workbench_rows": (
                        "1" if key in pre_ml_review_workbench_by_key else "0"
                    ),
                    "pre_ml_gate_status_rows": (
                        "1" if key in pre_ml_gate_status_by_key else "0"
                    ),
                    "pre_ml_remaining_action_backlog_rows": (
                        "1" if key in pre_ml_remaining_action_backlog_by_key else "0"
                    ),
                    "pre_ml_local_gap_fill_candidate_rows": (
                        "1" if key in pre_ml_local_gap_fill_candidate_by_key else "0"
                    ),
                    "pre_ml_gap_fill_impact_preview_rows": (
                        "1" if key in pre_ml_gap_fill_impact_preview_by_key else "0"
                    ),
                    "pre_ml_review_gate_candidate_pack_rows": (
                        "1" if key in pre_ml_review_gate_candidate_pack_by_key else "0"
                    ),
                    "pre_ml_review_gate_checklist_rows": (
                        "1" if key in pre_ml_review_gate_checklist_by_key else "0"
                    ),
                    "pre_ml_review_gate_consistency_audit_rows": (
                        "1" if key in pre_ml_review_gate_consistency_audit_by_key else "0"
                    ),
                    "pre_ml_review_gate_decision_register_rows": (
                        "1" if key in pre_ml_review_gate_decision_register_by_key else "0"
                    ),
                    "pipeline_status": derive_status(
                        plan_rows,
                        score_rows,
                        pdf_plan_rows,
                        ok_count,
                        blocked_403_count,
                        static_ajax_page_count,
                        form_replay_variants.get(key, 0),
                        form_replay_success.get(key, 0),
                        row["has_plan_page"],
                        row["has_score_page"],
                        has_supp_plan,
                        has_supp_score,
                    ),
                }
            )

    print(f"Wrote engineering pipeline status to {args.output}.")


if __name__ == "__main__":
    main()
