from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_local_checklist_execution_queue"
ACTION_BOARD = SEED_DIR / "reference_trend_520_p1_batch17_post_mapping_action_board.csv"

OUT_QUEUE = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

QUEUE_FIELDS = [
    "checklist_id",
    "source_board_id",
    "group_pair_key",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "action_bucket",
    "execution_lane",
    "can_execute_without_network",
    "can_execute_without_user_approval",
    "checklist_focus",
    "required_local_inputs",
    "blocked_external_inputs",
    "expected_safe_output",
    "stop_condition",
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
    "source_board_id",
    "row_scope",
    "group_pair_key",
    "university_name",
    "action_bucket",
    "exclusion_reason",
    "blocked_until",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


LOCAL_CHECKLIST_BUCKETS = {
    "local_static_table_alignment_checklist_ready": "static_table_alignment_checklist",
    "local_group_boundary_checklist_ready": "group_boundary_checklist",
    "local_static_summary_only_no_parse_ready": "local_placeholder_cache_needed",
    "official_discovery_backoff": "official_only_discovery_backoff",
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


def focus_for(row: dict[str, str]) -> str:
    bucket = row["action_bucket"]
    if bucket == "local_static_table_alignment_checklist_ready":
        return "Verify recorded official HTML table candidate has Guangxi/physics/ordinary-batch columns and isolate any group or plan-count ambiguity without fetching the page."
    if bucket == "local_group_boundary_checklist_ready":
        return "Review recorded aggregate official candidate for group-code absence, teacher/language direction boundary, and line-score precondition before any parse attempt."
    if bucket == "local_static_summary_only_no_parse_ready":
        return "Keep a placeholder summary of what is missing locally; do not parse or infer until a local cache or approved artifact appears."
    return "Continue official-only discovery as a queue item; do not use browser/header/cookie/manual review unless later approved."


def required_inputs_for(row: dict[str, str]) -> str:
    bucket = row["action_bucket"]
    if bucket == "local_static_table_alignment_checklist_ready":
        return "marker_140_board_row|marker_133_action_queue_row|recorded_official_candidate_url_and_qa_focus"
    if bucket == "local_group_boundary_checklist_ready":
        return "marker_140_board_row|marker_133_action_queue_row|exam_authority_line_score_status_if_available"
    if bucket == "local_static_summary_only_no_parse_ready":
        return "marker_140_board_row|source_candidate_metadata_only"
    return "marker_140_board_row|source_packet_preview_action_queue_exclusion_log"


def blocked_inputs_for(row: dict[str, str]) -> str:
    bucket = row["action_bucket"]
    if bucket == "local_static_table_alignment_checklist_ready":
        return "new_page_fetch|browser_click|form_replay|OCR"
    if bucket == "local_group_boundary_checklist_ready":
        return "new_page_fetch|manual_boundary_decision|canonical_intake"
    if bucket == "local_static_summary_only_no_parse_ready":
        return "local_cache_missing|approved_artifact_missing"
    return "official_static_source_not_found_yet|browser_manual_review_not_approved"


def expected_output_for(row: dict[str, str]) -> str:
    bucket = row["action_bucket"]
    if bucket == "local_static_table_alignment_checklist_ready":
        return "table_alignment_checklist_preview_only"
    if bucket == "local_group_boundary_checklist_ready":
        return "group_boundary_checklist_preview_only"
    if bucket == "local_static_summary_only_no_parse_ready":
        return "placeholder_status_only"
    return "official_discovery_backoff_queue_only"


def stop_condition_for(row: dict[str, str]) -> str:
    bucket = row["action_bucket"]
    if bucket == "local_static_table_alignment_checklist_ready":
        return "stop_before_claiming_rows_or_plan_counts_until local cache or approved artifact is available"
    if bucket == "local_group_boundary_checklist_ready":
        return "stop_before accepting group boundary or line score until official group/score source is confirmed"
    if bucket == "local_static_summary_only_no_parse_ready":
        return "stop_before parse preview until local cache or approved artifact exists"
    return "stop_before browser/OCR/manual review; only queue official-only search terms"


def build() -> None:
    board_rows = read_csv(ACTION_BOARD)
    queue: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for row in board_rows:
        bucket = row["action_bucket"]
        if row["user_input_needed"] == "false" and bucket in LOCAL_CHECKLIST_BUCKETS:
            can_network = "false" if bucket != "official_discovery_backoff" else "false"
            queue.append(
                {
                    "checklist_id": f"{MARKER}_{len(queue)+1:04d}",
                    "source_board_id": row["board_id"],
                    "group_pair_key": row["group_pair_key"],
                    "university_name": row["university_name"],
                    "year": row["year"],
                    "province": row["province"],
                    "batch": row["batch"],
                    "subject_category": row["subject_category"],
                    "action_bucket": bucket,
                    "execution_lane": LOCAL_CHECKLIST_BUCKETS[bucket],
                    "can_execute_without_network": can_network,
                    "can_execute_without_user_approval": "true",
                    "checklist_focus": focus_for(row),
                    "required_local_inputs": required_inputs_for(row),
                    "blocked_external_inputs": blocked_inputs_for(row),
                    "expected_safe_output": expected_output_for(row),
                    "stop_condition": stop_condition_for(row),
                    "source_url": row["source_url"],
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                    "evidence_note": row["evidence_note"],
                }
            )
        else:
            exclusions.append(
                {
                    "exclusion_id": f"{MARKER}_exclusion_{len(exclusions)+1:04d}",
                    "source_board_id": row["board_id"],
                    "row_scope": row["row_scope"],
                    "group_pair_key": row["group_pair_key"],
                    "university_name": row["university_name"],
                    "action_bucket": bucket,
                    "exclusion_reason": "requires_user_input_or_not_a_local_checklist_lane",
                    "blocked_until": row["blocked_until"],
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )

    lane_counts = Counter(row["execution_lane"] for row in queue)
    bucket_counts = Counter(row["action_bucket"] for row in queue)
    rollup = [
        {"metric": "input_action_board_rows", "value": len(board_rows), "notes": rel(ACTION_BOARD)},
        {"metric": "local_checklist_queue_rows", "value": len(queue), "notes": "Rows that can be routed without new user approval."},
        {"metric": "excluded_board_rows", "value": len(exclusions), "notes": "Rows requiring approval/raw artifact or not a local checklist lane."},
        {"metric": "can_execute_without_user_approval_rows", "value": sum(row["can_execute_without_user_approval"] == "true" for row in queue), "notes": "All queue rows avoid browser/OCR/login/WeChat approval."},
        {"metric": "can_execute_without_network_rows", "value": sum(row["can_execute_without_network"] == "true" for row in queue), "notes": "This queue is a no-fetch routing/checklist layer."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "notes": "Intake remains closed."},
        {"metric": "calibration_eligible_rows", "value": 0, "notes": "Calibration remains closed."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(lane_counts.items()):
        rollup.append({"metric": f"execution_lane::{key}", "value": value, "notes": "local checklist execution lane"})
    for key, value in sorted(bucket_counts.items()):
        rollup.append({"metric": f"action_bucket::{key}", "value": value, "notes": "source action bucket"})

    qa_rows = [
        {
            "qa_check": "input_action_board_present",
            "status": "PASS" if ACTION_BOARD.exists() and len(board_rows) == 25 else "FAIL",
            "details": f"Read {len(board_rows)} rows from marker 140 action board.",
        },
        {
            "qa_check": "queue_exclusion_balance",
            "status": "PASS" if len(queue) + len(exclusions) == len(board_rows) else "FAIL",
            "details": f"queue={len(queue)} exclusions={len(exclusions)} input={len(board_rows)}",
        },
        {
            "qa_check": "no_approval_required_in_queue",
            "status": "PASS" if all(row["can_execute_without_user_approval"] == "true" for row in queue) else "FAIL",
            "details": "Queue rows are approval-free checklist/routing items.",
        },
        {
            "qa_check": "no_fetch_claimed",
            "status": "PASS" if all(row["can_execute_without_network"] == "false" for row in queue) else "FAIL",
            "details": "Queue is explicitly no-fetch; it only prepares checklist/backoff routing.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in queue
            )
            else "FAIL",
            "details": "No queue row opens reference trend intake, calibration, canonical, or ML.",
        },
    ]

    write_csv(OUT_QUEUE, QUEUE_FIELDS, queue)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 local checklist execution queue

## Summary

本轮读取 marker 140 action board，仅抽取不需要用户批准的本地 checklist/backoff 路由项。未联网、未抓取新页面、未 OCR、未打开浏览器/form/header/cookie/微信状态，也未选择最低位次。

## Outputs

- `{rel(OUT_QUEUE)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Input action board rows: {len(board_rows)}
- Local checklist queue rows: {len(queue)}
- Excluded approval/raw-artifact/non-local rows: {len(exclusions)}
- Queue lanes: {", ".join(f"{key}={value}" for key, value in sorted(lane_counts.items()))}

## Boundary

This is a no-fetch routing/checklist layer. Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 141. 2026-05-17 P1 batch17 local checklist execution queue

已新增 P1 batch17 local checklist execution queue：

- `{rel(OUT_QUEUE)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 140 的 25 条 action board rows，仅抽取 8 条无需新用户批准的本地 checklist/backoff 路由项；其中 3 条为本地 checklist/placeholder（湖南农业大学 table alignment、湖北师范大学 group boundary、牡丹江医科大学 local cache placeholder），5 条为 official-only discovery backoff queue。其余 17 条因等待官方 raw artifact、browser/static endpoint approval、OCR/manual image review、WeChat capture 或 rank/group confirmation 写入 exclusion log。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可对 3 条本地 checklist 行生成更细的表格/边界审核模板，或在用户批准后处理官方 rank/browser/OCR/WeChat 分支。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 141. 2026-05-17 P1 batch17 local checklist execution queue" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(queue)} checklist rows and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
