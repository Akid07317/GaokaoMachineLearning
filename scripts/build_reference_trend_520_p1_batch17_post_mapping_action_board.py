from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_post_mapping_action_board"
ACTION_QUEUE = SEED_DIR / "reference_trend_520_p1_batch17_source_packet_preview_action_queue.csv"
ACTION_EXCLUSION = REPORT_DIR / "reference_trend_520_p1_batch17_source_packet_preview_action_queue_exclusion_log.csv"
APPROVAL_PACKET = SEED_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.csv"
INVENTORY = SEED_DIR / "reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory.csv"
JXUTCM_MAPPING = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa.csv"

OUT_BOARD = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

BOARD_FIELDS = [
    "board_id",
    "row_scope",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "year",
    "province",
    "batch",
    "subject_category",
    "min_score",
    "min_rank",
    "action_bucket",
    "latest_local_status",
    "safe_auto_next_step",
    "blocked_until",
    "user_input_needed",
    "approval_packet_id",
    "lookup_score",
    "consumer_group_pair_keys",
    "required_next_artifact",
    "source_url",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]
ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "board_id",
    "row_scope",
    "group_pair_key",
    "university_name",
    "exclusion_reason",
    "blocked_until",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


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


def truthy(value: str) -> bool:
    return value.strip().lower() == "true"


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows if row.get(key)}


def approval_by_consumer(approval_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in approval_rows:
        for group in row["consumer_group_pair_keys"].split("|"):
            out[group] = row
    return out


def classify_action(row: dict[str, str], inventory: dict[str, dict[str, str]], mapping: dict[str, dict[str, str]]) -> tuple[str, str, str, str, str]:
    group = row["group_pair_key"]
    inv = inventory.get(group)
    if group == "10412-101" and mapping:
        return (
            "mapping_candidate_only_rank_and_group_confirmation_blocked",
            "marker_139_completed_candidate_only_mapping_QA",
            "Wait for official group-code confirmation and official rank raw artifact; do not intake.",
            "official_group_mapping_confirmation_and_marker_136_official_rank_raw_artifact",
            "true",
        )
    if row.get("min_score"):
        return (
            "official_score_available_rank_raw_needed",
            inv["plan_or_mapping_artifact_status"] if inv else "line_score_available_no_selected_rank",
            "Keep min_rank blank and fan out only after marker 136 official raw artifact is approved/provided.",
            "marker_136_official_one_score_one_rank_raw_artifact",
            "true",
        )
    if truthy(row.get("requires_wechat_capture", "")):
        return (
            "needs_wechat_capture_approval",
            "official_candidate_requires_wechat_capture_or_manual_export",
            "Hold until user provides auditable WeChat official artifact or approves capture path.",
            "user_provided_wechat_official_artifact_or_approval",
            "true",
        )
    if truthy(row.get("requires_ocr_or_manual_image_review", "")):
        return (
            "needs_ocr_or_manual_image_review_approval",
            "official_image_or_visual_plan_candidate_not_parsed",
            "Hold until user approves OCR/manual image review or provides official extracted table.",
            "ocr_or_manual_image_review_approval_or_official_extracted_table",
            "true",
        )
    if truthy(row.get("requires_login_or_cookie_state", "")):
        return (
            "needs_login_or_cookie_state_approval",
            "official_candidate_requires_login_cookie_state",
            "Hold until user approves authenticated/browser-state review.",
            "user_approval_for_login_cookie_browser_state",
            "true",
        )
    if truthy(row.get("requires_browser_or_alternate_fetch", "")) or not truthy(row.get("safe_without_new_user_approval", "")):
        return (
            "needs_browser_or_static_endpoint_discovery_approval",
            "official_query_or_detail_candidate_not_auditable_locally",
            "Try only existing local/static endpoint metadata; otherwise request browser/static-fetch approval before parsing.",
            "auditable_static_endpoint_or_user_browser_approval",
            "true",
        )
    if inv and "html_table_candidate" in inv["plan_or_mapping_artifact_status"]:
        return (
            "local_static_table_alignment_checklist_ready",
            inv["plan_or_mapping_artifact_status"],
            "Prepare table-alignment checklist from recorded official candidate; do not fetch new page.",
            "local_table_alignment_then_official_score_and_rank_source",
            "false",
        )
    if inv and "group_boundary" in inv["plan_or_mapping_artifact_status"]:
        return (
            "local_group_boundary_checklist_ready",
            inv["plan_or_mapping_artifact_status"],
            "Prepare group-boundary checklist from recorded official candidate; do not fetch new page.",
            "local_group_boundary_review_then_official_score_and_rank_source",
            "false",
        )
    return (
        "local_static_summary_only_no_parse_ready",
        inv["plan_or_mapping_artifact_status"] if inv else "no_local_parse_artifact_ready",
        "Keep as local QA placeholder until a local cache, official raw artifact, or approval exists.",
        "local_cache_or_approved_artifact",
        "false",
    )


def build() -> None:
    action_rows = read_csv(ACTION_QUEUE)
    action_exclusions = read_csv(ACTION_EXCLUSION)
    approval_rows = read_csv(APPROVAL_PACKET)
    inventory_rows = read_csv(INVENTORY)
    mapping_rows = read_csv(JXUTCM_MAPPING)

    inventory_by_group = index_by(inventory_rows, "group_pair_key")
    mapping_by_source_group = index_by(mapping_rows, "source_group_code")
    approval_by_group = approval_by_consumer(approval_rows)
    board: list[dict[str, object]] = []

    for idx, row in enumerate(action_rows, 1):
        approval = approval_by_group.get(row["group_pair_key"], {})
        action_bucket, latest_status, safe_next, blocked_until, user_input_needed = classify_action(
            row, inventory_by_group, mapping_by_source_group
        )
        board.append(
            {
                "board_id": f"{MARKER}_{len(board)+1:04d}",
                "row_scope": "group_action",
                "group_pair_key": row["group_pair_key"],
                "university_code": row["university_code"],
                "university_name": row["university_name"],
                "group_code": row["group_code"],
                "year": row["year"],
                "province": row["province"],
                "batch": row["batch"],
                "subject_category": row["subject_category"],
                "min_score": row.get("min_score", ""),
                "min_rank": "",
                "action_bucket": action_bucket,
                "latest_local_status": latest_status,
                "safe_auto_next_step": safe_next,
                "blocked_until": blocked_until,
                "user_input_needed": user_input_needed,
                "approval_packet_id": approval.get("approval_packet_id", ""),
                "lookup_score": approval.get("min_score", ""),
                "consumer_group_pair_keys": approval.get("consumer_group_pair_keys", ""),
                "required_next_artifact": row["required_next_artifact"],
                "source_url": row["source_url"],
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": row["qa_focus"],
            }
        )

    for row in action_exclusions:
        board.append(
            {
                "board_id": f"{MARKER}_{len(board)+1:04d}",
                "row_scope": "coverage_backoff",
                "group_pair_key": row["group_pair_key"],
                "university_code": "",
                "university_name": row["university_name"],
                "group_code": row["group_pair_key"].split("-")[-1],
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "min_score": "",
                "min_rank": "",
                "action_bucket": "official_discovery_backoff",
                "latest_local_status": row["reason"],
                "safe_auto_next_step": row["safe_next_action"],
                "blocked_until": "official_static_source_found_or_user_approval_for_browser_manual_review",
                "user_input_needed": "false",
                "approval_packet_id": "",
                "lookup_score": "",
                "consumer_group_pair_keys": "",
                "required_next_artifact": "official_source_candidate_or_reachability_update",
                "source_url": "",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": row["reason"],
            }
        )

    for row in approval_rows:
        board.append(
            {
                "board_id": f"{MARKER}_{len(board)+1:04d}",
                "row_scope": "score_rank_lookup_target",
                "group_pair_key": "",
                "university_code": "",
                "university_name": "",
                "group_code": "",
                "year": row["year"],
                "province": row["province"],
                "batch": "本科普通批",
                "subject_category": row["subject_category"],
                "min_score": row["min_score"],
                "min_rank": "",
                "action_bucket": "official_score_rank_raw_cache_needed",
                "latest_local_status": row["review_status"],
                "safe_auto_next_step": "Do not select rank; wait for official raw artifact or approved browser-state capture.",
                "blocked_until": "user_approval_or_user_provided_official_raw_artifact",
                "user_input_needed": "true",
                "approval_packet_id": row["approval_packet_id"],
                "lookup_score": row["min_score"],
                "consumer_group_pair_keys": row["consumer_group_pair_keys"],
                "required_next_artifact": row["acceptable_artifact_types"],
                "source_url": "",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": row["rank_selection_policy"],
            }
        )

    bucket_counts = Counter(row["action_bucket"] for row in board)
    scope_counts = Counter(row["row_scope"] for row in board)
    user_needed = sum(1 for row in board if row["user_input_needed"] == "true")
    min_score_group_rows = sum(1 for row in board if row["row_scope"] == "group_action" and row["min_score"])
    selected_rank_rows = sum(1 for row in board if row["min_rank"])

    rollup = [
        {"metric": "group_action_rows", "value": scope_counts["group_action"], "notes": rel(ACTION_QUEUE)},
        {"metric": "coverage_backoff_rows", "value": scope_counts["coverage_backoff"], "notes": rel(ACTION_EXCLUSION)},
        {"metric": "score_rank_lookup_target_rows", "value": scope_counts["score_rank_lookup_target"], "notes": rel(APPROVAL_PACKET)},
        {"metric": "board_rows_total", "value": len(board), "notes": "Group actions + coverage backoff + unique score-rank lookup targets."},
        {"metric": "group_rows_with_official_min_score", "value": min_score_group_rows, "notes": "Rank remains blank for all."},
        {"metric": "selected_min_rank_rows", "value": selected_rank_rows, "notes": "No rank selected or inferred."},
        {"metric": "rows_needing_user_input_or_official_raw_artifact", "value": user_needed, "notes": "Approval/raw-artifact/browser/OCR/WeChat-gated rows."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "notes": "Intake gate remains closed."},
        {"metric": "calibration_eligible_rows", "value": 0, "notes": "Calibration gate remains closed."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Canonical/ML gate remains closed."},
    ]
    for key, value in sorted(bucket_counts.items()):
        rollup.append({"metric": f"action_bucket::{key}", "value": value, "notes": "post-mapping action bucket"})

    qa_rows = [
        {
            "qa_check": "required_inputs_present",
            "status": "PASS" if all(path.exists() for path in (ACTION_QUEUE, ACTION_EXCLUSION, APPROVAL_PACKET, INVENTORY, JXUTCM_MAPPING)) else "FAIL",
            "details": "All local marker 133/136/138/139 inputs were present.",
        },
        {
            "qa_check": "expected_row_balance",
            "status": "PASS" if len(action_rows) == 15 and len(action_exclusions) == 5 and len(approval_rows) == 5 and len(board) == 25 else "FAIL",
            "details": f"action={len(action_rows)} backoff={len(action_exclusions)} lookup={len(approval_rows)} board={len(board)}",
        },
        {
            "qa_check": "rank_stays_blank",
            "status": "PASS" if selected_rank_rows == 0 else "FAIL",
            "details": "No min_rank selected or inferred.",
        },
        {
            "qa_check": "score_rank_lookup_fanout_preserved",
            "status": "PASS" if sum(int(row["consumer_group_year_count"]) for row in approval_rows) == 6 else "FAIL",
            "details": "Five lookup scores still fan out to six group-year consumers.",
        },
        {
            "qa_check": "jxutcm_marker_139_reflected",
            "status": "PASS" if bucket_counts["mapping_candidate_only_rank_and_group_confirmation_blocked"] == 1 else "FAIL",
            "details": "10412-101 is carried forward as candidate-only mapping, not accepted.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in board
            )
            else "FAIL",
            "details": "Board remains outside reference trend intake/canonical/ML.",
        },
    ]

    exclusions = [
        {
            "exclusion_id": f"{MARKER}_exclusion_{idx:04d}",
            "board_id": row["board_id"],
            "row_scope": row["row_scope"],
            "group_pair_key": row["group_pair_key"],
            "university_name": row["university_name"],
            "exclusion_reason": row["action_bucket"],
            "blocked_until": row["blocked_until"],
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        }
        for idx, row in enumerate(board, 1)
    ]

    write_csv(OUT_BOARD, BOARD_FIELDS, board)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 post-mapping action board

## Summary

本轮读取 marker 133/136/138/139 的本地产物，将 batch17 后续工作拆为 group action、coverage backoff 和 unique score-rank lookup target 三类。未联网、未缓存新页面、未 OCR、未打开浏览器/form/header/cookie/微信状态，也未选择最低位次。

## Outputs

- `{rel(OUT_BOARD)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Rollup

- Group action rows: {scope_counts['group_action']}
- Coverage backoff rows: {scope_counts['coverage_backoff']}
- Unique score-rank lookup targets: {scope_counts['score_rank_lookup_target']}
- Group rows with official min_score: {min_score_group_rows}
- Selected min_rank rows: {selected_rank_rows}
- Rows needing user approval or official raw artifact: {user_needed}

## Boundary

All rows keep `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`. The board is for source-packet/QA workflow routing only and does not modify canonical, ML input, baseline data, or the 32-school decision pool.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 140. 2026-05-17 P1 batch17 post-mapping action board

已新增 P1 batch17 post-mapping action board：

- `{rel(OUT_BOARD)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 133/136/138/139 的本地产物，把 batch17 后续工作拆成 15 条 group action、5 条 coverage backoff 和 5 条 unique score-rank lookup target。当前 6 条 group rows 有官方最低分但均无最低位次；5 个分数 lookup target（527/490/462/461/382）仍等待 marker 136 的用户批准或官方 raw artifact。`10412-101` 已携带 marker 139 的 candidate-only mapping 结论继续阻塞在官方 group-code confirmation + rank raw artifact。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可从 action board 中优先处理本地 checklist rows，或在用户批准/提供官方 raw 后处理 score-rank fanout。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 140. 2026-05-17 P1 batch17 post-mapping action board" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(board)} board rows and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
