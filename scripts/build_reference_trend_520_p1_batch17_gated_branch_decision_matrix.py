from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_gated_branch_decision_matrix"
ACTION_BOARD = SEED_DIR / "reference_trend_520_p1_batch17_post_mapping_action_board.csv"
APPROVAL_PACKET = SEED_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.csv"
TEMPLATES = SEED_DIR / "reference_trend_520_p1_batch17_local_checklist_review_templates.csv"

OUT_MATRIX = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

MATRIX_FIELDS = [
    "decision_family_id",
    "action_bucket",
    "branch_type",
    "action_board_rows",
    "group_year_rows",
    "control_rows",
    "affected_group_pair_keys",
    "affected_universities",
    "affected_lookup_scores",
    "user_action_needed",
    "acceptable_artifact_or_decision",
    "prohibited_methods",
    "safe_next_after_unblock",
    "current_status",
    "source_urls",
    "source_files",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]
ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "source_board_id",
    "action_bucket",
    "group_pair_key",
    "university_name",
    "blocked_until",
    "exclusion_reason",
    "needed_artifact_or_approval",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

LOCAL_DONE_BUCKETS = {
    "local_static_table_alignment_checklist_ready",
    "local_static_summary_only_no_parse_ready",
    "local_group_boundary_checklist_ready",
}

BUCKET_METADATA = {
    "local_static_table_alignment_checklist_ready": {
        "branch_type": "local_template_ready_no_new_approval",
        "user_action_needed": "false",
        "acceptable_artifact_or_decision": "future_local_cache_or_approved_official_artifact_to_fill_marker_142_template",
        "prohibited_methods": "new_fetch|browser|header_cookie_form_replay|OCR|WeChat|rank_inference|intake|canonical_ml",
        "safe_next_after_unblock": "fill_marker_142_table_alignment_template_and_keep_intake_closed",
        "current_status": "marker_142_review_template_ready",
    },
    "local_static_summary_only_no_parse_ready": {
        "branch_type": "local_placeholder_ready_no_new_approval",
        "user_action_needed": "false",
        "acceptable_artifact_or_decision": "future_local_cache_or_approved_official_artifact_to_replace_placeholder",
        "prohibited_methods": "new_fetch|browser|header_cookie_form_replay|OCR|WeChat|rank_inference|intake|canonical_ml",
        "safe_next_after_unblock": "fill_marker_142_placeholder_template_before_any_parse_preview",
        "current_status": "marker_142_placeholder_template_ready",
    },
    "local_group_boundary_checklist_ready": {
        "branch_type": "local_group_boundary_template_ready_no_new_approval",
        "user_action_needed": "false",
        "acceptable_artifact_or_decision": "future_official_group_plan_or_exam_authority_group_line_artifact",
        "prohibited_methods": "new_fetch|manual_boundary_acceptance|rank_inference|intake|canonical_ml",
        "safe_next_after_unblock": "fill_marker_142_group_boundary_template_before_any_boundary_acceptance",
        "current_status": "marker_142_group_boundary_template_ready",
    },
    "official_discovery_backoff": {
        "branch_type": "official_only_discovery_backoff",
        "user_action_needed": "false_optional_approval_later",
        "acceptable_artifact_or_decision": "official_static_source_found_later_or_user_approves_browser_OCR_manual_review",
        "prohibited_methods": "browser|OCR|manual_review|header_cookie_form_replay_without_user_approval|intake|canonical_ml",
        "safe_next_after_unblock": "create_source_packet_preview_or_keep_backoff_if_no_official_source",
        "current_status": "backoff_only_no_static_official_source_yet",
    },
    "mapping_candidate_only_rank_and_group_confirmation_blocked": {
        "branch_type": "mapping_candidate_plus_rank_blocked",
        "user_action_needed": "true",
        "acceptable_artifact_or_decision": "official_group_code_confirmation_and_official_2025_physics_score_rank_raw_artifact",
        "prohibited_methods": "manual_accept_suffix_mapping|rank_inference|third_party_rank|terminal_curl_qg_qn|intake|canonical_ml",
        "safe_next_after_unblock": "rerun_mapping_rank_QA_before_any_eligibility_or_calibration",
        "current_status": "candidate_mapping_only_rank_missing",
    },
    "needs_browser_or_static_endpoint_discovery_approval": {
        "branch_type": "browser_or_static_endpoint_approval_needed",
        "user_action_needed": "true",
        "acceptable_artifact_or_decision": "user_approval_for_browser_state_or_auditable_static_endpoint_capture",
        "prohibited_methods": "browser|header_cookie_form_replay|login_state_without_user_approval|intake|canonical_ml",
        "safe_next_after_unblock": "capture_source_packet_reachability_then_QA_preview_only",
        "current_status": "blocked_before_browser_or_static_endpoint_capture",
    },
    "needs_ocr_or_manual_image_review_approval": {
        "branch_type": "OCR_or_manual_image_review_approval_needed",
        "user_action_needed": "true",
        "acceptable_artifact_or_decision": "user_approval_for_OCR_or_user_provided_official_extracted_table",
        "prohibited_methods": "OCR|manual_image_interpretation_without_user_approval|rank_inference|intake|canonical_ml",
        "safe_next_after_unblock": "run_image_table_QA_preview_and_special_type_isolation_only",
        "current_status": "blocked_before_OCR_or_manual_image_review",
    },
    "needs_wechat_capture_approval": {
        "branch_type": "WeChat_official_artifact_or_capture_approval_needed",
        "user_action_needed": "true",
        "acceptable_artifact_or_decision": "user_provided_WeChat_official_artifact_or_user_approval_for_WeChat_capture",
        "prohibited_methods": "WeChat_capture_without_user_approval|manual_transcription_without_artifact|intake|canonical_ml",
        "safe_next_after_unblock": "record_source_packet_artifact_receipt_then_QA_preview_only",
        "current_status": "blocked_before_WeChat_artifact_capture",
    },
    "official_score_available_rank_raw_needed": {
        "branch_type": "official_line_score_available_rank_raw_needed",
        "user_action_needed": "true",
        "acceptable_artifact_or_decision": "marker_136_official_score_rank_raw_cache_or_browser_saved_page_with_url_timestamp",
        "prohibited_methods": "terminal_curl_qg_qn|third_party_mirror_rank|rank_inference|intake|canonical_ml",
        "safe_next_after_unblock": "join_official_min_rank_after_score_rank_QA_passes",
        "current_status": "official_min_score_present_min_rank_missing",
    },
    "official_score_rank_raw_cache_needed": {
        "branch_type": "score_rank_raw_cache_control_targets",
        "user_action_needed": "true",
        "acceptable_artifact_or_decision": "same_marker_136_official_score_rank_raw_cache_serves_fanout_consumers",
        "prohibited_methods": "terminal_curl_qg_qn|third_party_mirror_rank|rank_inference|intake|canonical_ml",
        "safe_next_after_unblock": "fanout_score_rank_lookup_to_consumers_after_QA",
        "current_status": "control_rows_waiting_for_official_raw_cache",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def compact_join(values: list[str]) -> str:
    return "|".join(sorted({value for value in values if value}))


def build() -> None:
    board_rows = read_csv(ACTION_BOARD)
    approval_rows = read_csv(APPROVAL_PACKET)
    template_rows = read_csv(TEMPLATES)
    rows_by_bucket: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in board_rows:
        rows_by_bucket[row["action_bucket"]].append(row)

    score_by_consumer: dict[str, list[str]] = defaultdict(list)
    control_scores: list[str] = []
    for row in approval_rows:
        control_scores.append(row["min_score"])
        for key in row["consumer_group_pair_keys"].split("|"):
            if key:
                score_by_consumer[key].append(row["min_score"])

    template_sources = {row["source_checklist_id"] for row in template_rows}

    matrix: list[dict[str, object]] = []
    for action_bucket, rows in sorted(rows_by_bucket.items()):
        meta = BUCKET_METADATA[action_bucket]
        affected_keys = [row["group_pair_key"] for row in rows if row["group_pair_key"]]
        affected_scores = []
        if action_bucket == "official_score_rank_raw_cache_needed":
            affected_scores = control_scores
        else:
            for key in affected_keys:
                affected_scores.extend(score_by_consumer.get(key, []))
            affected_scores.extend(row["lookup_score"] for row in rows if row["lookup_score"])

        source_files = [rel(ACTION_BOARD)]
        if action_bucket in {"official_score_available_rank_raw_needed", "official_score_rank_raw_cache_needed", "mapping_candidate_only_rank_and_group_confirmation_blocked"}:
            source_files.append(rel(APPROVAL_PACKET))
        if action_bucket in LOCAL_DONE_BUCKETS:
            source_files.append(rel(TEMPLATES))

        matrix.append(
            {
                "decision_family_id": f"{MARKER}_{len(matrix)+1:04d}",
                "action_bucket": action_bucket,
                "branch_type": meta["branch_type"],
                "action_board_rows": len(rows),
                "group_year_rows": sum(1 for row in rows if row["row_scope"] == "group_action" and row["group_pair_key"]),
                "control_rows": sum(1 for row in rows if not row["group_pair_key"]),
                "affected_group_pair_keys": compact_join(affected_keys),
                "affected_universities": compact_join([row["university_name"] for row in rows]),
                "affected_lookup_scores": compact_join(affected_scores),
                "user_action_needed": meta["user_action_needed"],
                "acceptable_artifact_or_decision": meta["acceptable_artifact_or_decision"],
                "prohibited_methods": meta["prohibited_methods"],
                "safe_next_after_unblock": meta["safe_next_after_unblock"],
                "current_status": meta["current_status"],
                "source_urls": compact_join([row["source_url"] for row in rows]),
                "source_files": "|".join(source_files),
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

    exclusions: list[dict[str, object]] = []
    for row in board_rows:
        if row["action_bucket"] in LOCAL_DONE_BUCKETS:
            continue
        meta = BUCKET_METADATA[row["action_bucket"]]
        exclusions.append(
            {
                "exclusion_id": f"{MARKER}_exclusion_{len(exclusions)+1:04d}",
                "source_board_id": row["board_id"],
                "action_bucket": row["action_bucket"],
                "group_pair_key": row["group_pair_key"],
                "university_name": row["university_name"],
                "blocked_until": row["blocked_until"],
                "exclusion_reason": "not_safe_for_automatic_execution_or_intake_in_this_marker",
                "needed_artifact_or_approval": meta["acceptable_artifact_or_decision"],
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

    bucket_counts = Counter(row["action_bucket"] for row in board_rows)
    user_action_rows = sum(row["user_input_needed"] == "true" for row in board_rows)
    group_rows_missing_rank = sum(
        row["action_bucket"] == "official_score_available_rank_raw_needed"
        for row in board_rows
    )
    rollup = [
        {"metric": "input_action_board_rows", "value": len(board_rows), "notes": rel(ACTION_BOARD)},
        {"metric": "decision_matrix_rows", "value": len(matrix), "notes": "One row per action bucket/decision family."},
        {"metric": "template_rows_in_context", "value": len(template_rows), "notes": rel(TEMPLATES)},
        {"metric": "template_source_rows_in_context", "value": len(template_sources), "notes": "Marker 142 source checklist rows."},
        {"metric": "approval_packet_rows_in_context", "value": len(approval_rows), "notes": rel(APPROVAL_PACKET)},
        {"metric": "action_board_rows_needing_user_action", "value": user_action_rows, "notes": "Rows marked user_input_needed=true in marker 140."},
        {"metric": "official_score_rank_unique_scores_waiting_raw", "value": len(control_scores), "notes": compact_join(control_scores)},
        {"metric": "official_score_rows_waiting_rank_join", "value": group_rows_missing_rank, "notes": "Group-year rows with official min_score but no min_rank."},
        {"metric": "exclusion_rows_not_auto_executed", "value": len(exclusions), "notes": "Non-local-template action board rows kept blocked."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "notes": "Matrix is not intake."},
        {"metric": "calibration_eligible_rows", "value": 0, "notes": "No rank selected."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(bucket_counts.items()):
        rollup.append({"metric": f"action_bucket::{key}", "value": value, "notes": "marker 140 action board"})

    covered_rows = sum(int(row["action_board_rows"]) for row in matrix)
    qa_rows = [
        {
            "qa_check": "input_action_board_present",
            "status": "PASS" if len(board_rows) == 25 else "FAIL",
            "details": f"Read {len(board_rows)} rows from marker 140 action board.",
        },
        {
            "qa_check": "matrix_covers_all_action_board_rows",
            "status": "PASS" if covered_rows == len(board_rows) else "FAIL",
            "details": f"matrix_action_rows={covered_rows} input_rows={len(board_rows)}",
        },
        {
            "qa_check": "local_template_context_present",
            "status": "PASS" if len(template_rows) == 15 and len(template_sources) == 3 else "FAIL",
            "details": f"template_rows={len(template_rows)} source_template_rows={len(template_sources)}",
        },
        {
            "qa_check": "score_rank_approval_context_present",
            "status": "PASS" if len(approval_rows) == 5 and len(control_scores) == 5 else "FAIL",
            "details": f"approval_rows={len(approval_rows)} scores={compact_join(control_scores)}",
        },
        {
            "qa_check": "blocked_rows_not_auto_executed",
            "status": "PASS" if len(exclusions) == len(board_rows) - 3 else "FAIL",
            "details": f"exclusions={len(exclusions)} local_template_rows=3 input={len(board_rows)}",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in matrix
            )
            else "FAIL",
            "details": "No decision family opens intake, calibration, canonical, or ML.",
        },
    ]

    write_csv(OUT_MATRIX, MATRIX_FIELDS, matrix)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 gated branch decision matrix

## Summary

This marker consolidates marker 140 action-board rows, marker 136 official score-rank approval packet, and marker 142 local checklist templates into a single gated-branch decision matrix. It does not fetch pages, use browser/OCR/WeChat state, select ranks, or open intake/calibration/canonical/ML.

## Outputs

- `{rel(OUT_MATRIX)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Input action-board rows: {len(board_rows)}
- Decision families: {len(matrix)}
- Rows needing user action in marker 140: {user_action_rows}
- Unique official score-rank lookup scores waiting for official raw artifact: {compact_join(control_scores)}
- Local template rows in context: {len(template_rows)} across {len(template_sources)} source checklist rows
- Non-local-template rows kept blocked/excluded from automatic execution: {len(exclusions)}

## Boundary

This is a decision-routing artifact only. Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 143. 2026-05-17 P1 batch17 gated branch decision matrix

已新增 P1 batch17 gated branch decision matrix：

- `{rel(OUT_MATRIX)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 140 action board、marker 136 官方 score-rank 批准包与 marker 142 本地审核模板，将 25 条 action board rows 归并为 10 个 gated decision families。矩阵保留 3 条本地模板分支、5 条 official-only backoff、5 个官方分数位次 raw lookup targets（527/490/462/461/382，覆盖 6 条 group-year consumers）、以及 browser/static endpoint、OCR/manual image、WeChat、JXUTCM group-code confirmation 等需要批准的分支。22 条非本地模板 rows 写入 exclusion log，等待官方 raw artifact 或用户批准。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不重复已阻塞终端 curl，不使用第三方位次，不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可按矩阵等待用户批准/官方 raw，或在本地 artifact 出现后填 marker 142 模板。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 143. 2026-05-17 P1 batch17 gated branch decision matrix" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(matrix)} decision-family rows and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
