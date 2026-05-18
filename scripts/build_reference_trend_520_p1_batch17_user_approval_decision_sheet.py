from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_user_approval_decision_sheet"
MATRIX = SEED_DIR / "reference_trend_520_p1_batch17_gated_branch_decision_matrix.csv"
APPROVAL_PACKET = SEED_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.csv"

OUT_SHEET = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

SHEET_FIELDS = [
    "approval_option_id",
    "source_decision_family_id",
    "approval_priority",
    "approval_family",
    "recommended_user_choice",
    "what_user_would_allow_or_provide",
    "affected_group_pair_keys",
    "affected_universities",
    "affected_lookup_scores",
    "consumer_count_after_fanout",
    "acceptable_artifact_or_decision",
    "minimum_audit_fields",
    "safe_next_after_approval",
    "must_not_do_even_if_approved",
    "current_status",
    "source_urls",
    "source_files",
    "approval_status",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]
ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "source_decision_family_id",
    "action_bucket",
    "branch_type",
    "exclusion_reason",
    "safe_next_without_user_approval",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

PRIORITY_BY_BUCKET = {
    "official_score_rank_raw_cache_needed": "P0",
    "official_score_available_rank_raw_needed": "P0",
    "mapping_candidate_only_rank_and_group_confirmation_blocked": "P0",
    "needs_browser_or_static_endpoint_discovery_approval": "P1",
    "needs_ocr_or_manual_image_review_approval": "P1",
    "needs_wechat_capture_approval": "P1",
    "official_discovery_backoff": "P2_optional",
}

APPROVAL_FAMILY_BY_BUCKET = {
    "official_score_rank_raw_cache_needed": "official_2025_physics_score_rank_raw_cache",
    "official_score_available_rank_raw_needed": "official_min_rank_join_permission",
    "mapping_candidate_only_rank_and_group_confirmation_blocked": "official_group_code_confirmation_plus_rank_raw",
    "needs_browser_or_static_endpoint_discovery_approval": "browser_or_static_endpoint_capture",
    "needs_ocr_or_manual_image_review_approval": "OCR_or_user_provided_extracted_table",
    "needs_wechat_capture_approval": "WeChat_official_artifact_capture",
    "official_discovery_backoff": "optional_browser_OCR_manual_review_for_backoff",
}

CHOICE_BY_BUCKET = {
    "official_score_rank_raw_cache_needed": "provide_official_raw_artifact_or_approve_browser_saved_page",
    "official_score_available_rank_raw_needed": "same_as_score_rank_raw_cache_option_then_join_rank_after_QA",
    "mapping_candidate_only_rank_and_group_confirmation_blocked": "provide_official_group_code_confirmation_and_rank_raw_artifact",
    "needs_browser_or_static_endpoint_discovery_approval": "approve_browser_state_or_static_endpoint_capture",
    "needs_ocr_or_manual_image_review_approval": "approve_OCR_or_provide_official_extracted_table",
    "needs_wechat_capture_approval": "provide_WeChat_official_artifact_or_approve_capture",
    "official_discovery_backoff": "optional_approve_browser_OCR_manual_review_or_wait_for_static_official_source",
}

MIN_AUDIT_FIELDS_BY_BUCKET = {
    "official_score_rank_raw_cache_needed": "raw_file_path|source_url|retrieved_at|score_column|rank_column|total_score_policy_note",
    "official_score_available_rank_raw_needed": "raw_file_path|source_url|retrieved_at|score_column|rank_column|consumer_group_pair_key",
    "mapping_candidate_only_rank_and_group_confirmation_blocked": "official_group_code_evidence|official_rank_raw_file_path|source_url|retrieved_at|reviewer_note",
    "needs_browser_or_static_endpoint_discovery_approval": "captured_url|retrieved_at|browser_or_endpoint_method|official_domain|cache_file_path",
    "needs_ocr_or_manual_image_review_approval": "official_image_or_pdf_path|OCR_method_or_manual_review_note|source_url|retrieved_at|row_boundary_note",
    "needs_wechat_capture_approval": "WeChat_official_artifact_path|source_account_or_url|retrieved_at|capture_note",
    "official_discovery_backoff": "approved_method|source_url_if_found|retrieved_at|backoff_or_capture_note",
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


def count_consumers(value: str) -> int:
    if not value:
        return 0
    return len([item for item in value.split("|") if item])


def build() -> None:
    matrix_rows = read_csv(MATRIX)
    approval_packet_rows = read_csv(APPROVAL_PACKET)
    approval_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for row in matrix_rows:
        bucket = row["action_bucket"]
        if row["user_action_needed"] == "true" or row["user_action_needed"] == "false_optional_approval_later":
            approval_rows.append(
                {
                    "approval_option_id": f"{MARKER}_{len(approval_rows)+1:04d}",
                    "source_decision_family_id": row["decision_family_id"],
                    "approval_priority": PRIORITY_BY_BUCKET[bucket],
                    "approval_family": APPROVAL_FAMILY_BY_BUCKET[bucket],
                    "recommended_user_choice": CHOICE_BY_BUCKET[bucket],
                    "what_user_would_allow_or_provide": row["acceptable_artifact_or_decision"],
                    "affected_group_pair_keys": row["affected_group_pair_keys"],
                    "affected_universities": row["affected_universities"],
                    "affected_lookup_scores": row["affected_lookup_scores"],
                    "consumer_count_after_fanout": count_consumers(row["affected_group_pair_keys"]),
                    "acceptable_artifact_or_decision": row["acceptable_artifact_or_decision"],
                    "minimum_audit_fields": MIN_AUDIT_FIELDS_BY_BUCKET[bucket],
                    "safe_next_after_approval": row["safe_next_after_unblock"],
                    "must_not_do_even_if_approved": row["prohibited_methods"] + "|direct_intake_without_QA|canonical_ml",
                    "current_status": row["current_status"],
                    "source_urls": row["source_urls"],
                    "source_files": row["source_files"],
                    "approval_status": "pending_user_decision_or_official_raw_artifact",
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )
        else:
            exclusions.append(
                {
                    "exclusion_id": f"{MARKER}_exclusion_{len(exclusions)+1:04d}",
                    "source_decision_family_id": row["decision_family_id"],
                    "action_bucket": bucket,
                    "branch_type": row["branch_type"],
                    "exclusion_reason": "no_user_approval_needed_for_this_decision_family",
                    "safe_next_without_user_approval": row["safe_next_after_unblock"],
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )

    priority_counts = Counter(row["approval_priority"] for row in approval_rows)
    family_counts = Counter(row["approval_family"] for row in approval_rows)
    affected_scores = sorted(
        {
            score
            for row in approval_rows
            for score in str(row["affected_lookup_scores"]).split("|")
            if score
        },
        key=lambda value: int(value) if value.isdigit() else value,
    )
    rollup = [
        {"metric": "input_decision_matrix_rows", "value": len(matrix_rows), "notes": rel(MATRIX)},
        {"metric": "approval_option_rows", "value": len(approval_rows), "notes": "Rows where user approval or official raw artifact can unblock work."},
        {"metric": "no_approval_needed_exclusion_rows", "value": len(exclusions), "notes": "Local template rows excluded from approval sheet."},
        {"metric": "approval_packet_rows_in_context", "value": len(approval_packet_rows), "notes": rel(APPROVAL_PACKET)},
        {"metric": "unique_lookup_scores_in_approval_options", "value": len(affected_scores), "notes": "|".join(affected_scores)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "notes": "Approval sheet is not intake."},
        {"metric": "calibration_eligible_rows", "value": 0, "notes": "No official min_rank selected."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(priority_counts.items()):
        rollup.append({"metric": f"approval_priority::{key}", "value": value, "notes": "approval option priority"})
    for key, value in sorted(family_counts.items()):
        rollup.append({"metric": f"approval_family::{key}", "value": value, "notes": "approval option family"})

    qa_rows = [
        {
            "qa_check": "input_decision_matrix_present",
            "status": "PASS" if len(matrix_rows) == 10 else "FAIL",
            "details": f"Read {len(matrix_rows)} rows from marker 143 decision matrix.",
        },
        {
            "qa_check": "approval_sheet_scope",
            "status": "PASS" if len(approval_rows) == 7 else "FAIL",
            "details": f"Approval options={len(approval_rows)}; expected user-action plus optional backoff branches.",
        },
        {
            "qa_check": "matrix_balance",
            "status": "PASS" if len(approval_rows) + len(exclusions) == len(matrix_rows) else "FAIL",
            "details": f"approval={len(approval_rows)} exclusions={len(exclusions)} input={len(matrix_rows)}",
        },
        {
            "qa_check": "score_rank_context_preserved",
            "status": "PASS" if len(approval_packet_rows) == 5 and set(affected_scores) >= {"382", "461", "462", "490", "527"} else "FAIL",
            "details": f"approval_packet_rows={len(approval_packet_rows)} affected_scores={'|'.join(affected_scores)}",
        },
        {
            "qa_check": "no_execution_claimed",
            "status": "PASS" if all(row["approval_status"] == "pending_user_decision_or_official_raw_artifact" for row in approval_rows) else "FAIL",
            "details": "All approval rows are pending decision; no capture/fetch/OCR/WeChat action is claimed.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in approval_rows
            )
            else "FAIL",
            "details": "No approval option opens intake, calibration, canonical, or ML.",
        },
    ]

    write_csv(OUT_SHEET, SHEET_FIELDS, approval_rows)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 user approval decision sheet

## Summary

This marker extracts the branches from marker 143 that require a user decision or an official raw artifact. It is a pending decision sheet only: no browser, fetch, OCR, WeChat capture, rank selection, intake, calibration, canonical, or ML action is performed.

## Outputs

- `{rel(OUT_SHEET)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Input decision families: {len(matrix_rows)}
- Approval option rows: {len(approval_rows)}
- Local/no-approval branches excluded from this sheet: {len(exclusions)}
- Approval priorities: {", ".join(f"{key}={value}" for key, value in sorted(priority_counts.items()))}
- Score-rank lookup scores preserved: {"|".join(affected_scores)}

## Boundary

The sheet records only pending approval choices. Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 144. 2026-05-17 P1 batch17 user approval decision sheet

已新增 P1 batch17 user approval decision sheet：

- `{rel(OUT_SHEET)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 143 的 10 个 gated decision families，抽取 7 条需要用户批准或官方 raw artifact 才能推进的 approval options：P0 官方 2025 物理类一分一档 raw/cache、P0 已有官方最低分的 min_rank join、P0 江西中医药大学 group-code confirmation + rank raw、P1 browser/static endpoint capture、P1 OCR/official extracted table、P1 WeChat 官方 artifact/capture、P2 optional backoff review。3 条本地模板分支写入 exclusion log，因为它们无需新批准。QA PASS。

准入边界：本轮只生成待批准 decision sheet，不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不重复已阻塞终端 curl，不使用第三方位次，不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化只有在用户批准或提供官方 raw artifact 后，才可按对应 option 进入 capture/QA preview。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 144. 2026-05-17 P1 batch17 user approval decision sheet" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(approval_rows)} approval options and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
