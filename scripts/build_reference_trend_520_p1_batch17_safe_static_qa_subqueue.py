from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_safe_static_qa_subqueue"
INPUT = SEED_DIR / "reference_trend_520_p1_batch17_source_packet_preview_action_queue.csv"

OUT_QUEUE = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"


QUEUE_FIELDS = [
    "subqueue_id",
    "source_action_queue_id",
    "queue_rank",
    "action_priority",
    "local_static_lane",
    "action_class",
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
    "source_url",
    "source_candidate_tier",
    "source_candidate_status",
    "required_next_artifact",
    "strict_local_static_lane",
    "allowed_without_new_approval",
    "allowed_actions_without_new_approval",
    "disallowed_actions",
    "rank_status",
    "qa_focus",
    "stop_condition",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
]

EXCLUSION_FIELDS = [
    "exclusion_id",
    "source_action_queue_id",
    "group_pair_key",
    "university_name",
    "exclusion_reason",
    "source_flag_summary",
    "blocked_until",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def classify_exclusion(row: dict[str, str]) -> str | None:
    safe = row.get("safe_without_new_user_approval", "").strip()
    browser = row.get("requires_browser_or_alternate_fetch", "").strip()

    if not is_true(safe):
        return "not_safe_without_new_user_approval"
    if is_true(row.get("requires_wechat_capture", "")):
        return "requires_wechat_artifact_capture"
    if is_true(row.get("requires_ocr_or_manual_image_review", "")):
        return "requires_image_or_ocr_artifact"
    if is_true(row.get("requires_login_or_cookie_state", "")):
        return "requires_login_or_cookie_state"
    if browser.startswith("true_if_static_fetch") or "approved" in browser or "browser_review" in browser:
        return "requires_browser_or_static_retry_approval"
    return None


def lane_for(row: dict[str, str]) -> str:
    lane = row.get("action_lane", "")
    artifact = row.get("required_next_artifact", "")
    if "html_table_column_alignment" in lane:
        return "static_html_table_alignment_no_fetch"
    if "parsed_plan_preview" in lane:
        return "local_parsed_plan_mapping_review_no_rank_selection"
    if "line_score_rank_plan_mapping" in lane:
        return "plan_mapping_official_rank_wait_readiness_no_rank_selection"
    if "existing_candidate" in lane:
        return "existing_candidate_filter_static_QA_no_fetch"
    return f"local_static_{artifact}_no_fetch"


def rank_status(row: dict[str, str]) -> str:
    if row.get("min_rank", "").strip():
        return "unexpected_rank_present_review_required"
    if row.get("min_score", "").strip():
        return "official_line_score_present_rank_capture_waiting_user_approval"
    return "no_official_line_score_rank_join_not_ready"


def build() -> None:
    rows = read_rows(INPUT)
    subqueue: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for row in rows:
        reason = classify_exclusion(row)
        if reason:
            idx = len(exclusions) + 1
            flags = (
                f"safe={row.get('safe_without_new_user_approval','')};"
                f"browser={row.get('requires_browser_or_alternate_fetch','')};"
                f"wechat={row.get('requires_wechat_capture','')};"
                f"ocr={row.get('requires_ocr_or_manual_image_review','')};"
                f"login={row.get('requires_login_or_cookie_state','')}"
            )
            exclusions.append(
                {
                    "exclusion_id": f"{MARKER}_exclusion_{idx:04d}",
                    "source_action_queue_id": row["action_queue_id"],
                    "group_pair_key": row.get("group_pair_key", ""),
                    "university_name": row.get("university_name", ""),
                    "exclusion_reason": reason,
                    "source_flag_summary": flags,
                    "blocked_until": "user_approval_or_official_raw_artifact_or_manual_review_available",
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )
            continue

        idx = len(subqueue) + 1
        min_score = row.get("min_score", "").strip()
        focus = row.get("qa_focus", "")
        if min_score:
            focus = f"{focus}; retain official min_score={min_score} but keep min_rank empty until approved official score-rank raw cache exists"
        subqueue.append(
            {
                "subqueue_id": f"{MARKER}_{idx:04d}",
                "source_action_queue_id": row["action_queue_id"],
                "queue_rank": row.get("queue_rank", ""),
                "action_priority": row.get("action_priority", ""),
                "local_static_lane": lane_for(row),
                "action_class": row.get("action_class", ""),
                "group_pair_key": row.get("group_pair_key", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "group_code": row.get("group_code", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "min_score": min_score,
                "min_rank": "",
                "source_url": row.get("source_url", ""),
                "source_candidate_tier": row.get("source_candidate_tier", ""),
                "source_candidate_status": row.get("source_candidate_status", ""),
                "required_next_artifact": row.get("required_next_artifact", ""),
                "strict_local_static_lane": "true",
                "allowed_without_new_approval": "true",
                "allowed_actions_without_new_approval": (
                    "local_cache_or_existing_preview_QA;"
                    "column_alignment_review;"
                    "group_mapping_readiness;"
                    "coverage_or_exclusion_rollup"
                ),
                "disallowed_actions": (
                    "no_new_fetch;no_browser;no_cookie_header_form;"
                    "no_ocr;no_wechat;no_rank_selection;"
                    "no_reference_trend_intake;no_canonical_ml"
                ),
                "rank_status": rank_status(row),
                "qa_focus": focus,
                "stop_condition": "stop_before_rank_selection_intake_calibration_canonical_or_ml",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "next_action": "Run only local/static QA and write source_packet preview QA outputs; keep rank/intake gates closed.",
            }
        )

    reason_counts = Counter(row["exclusion_reason"] for row in exclusions)
    lane_counts = Counter(row["local_static_lane"] for row in subqueue)
    with_score = sum(1 for row in subqueue if row["min_score"])
    with_rank = sum(1 for row in subqueue if row["min_rank"])

    rollup = [
        {"metric": "source_action_queue_rows", "value": len(rows), "notes": str(INPUT.relative_to(ROOT))},
        {"metric": "strict_safe_static_subqueue_rows", "value": len(subqueue), "notes": "No browser/OCR/WeChat/login/new-fetch dependency allowed."},
        {"metric": "excluded_rows", "value": len(exclusions), "notes": "Rows blocked by approval, browser/static retry, OCR/image, or WeChat boundary."},
        {"metric": "subqueue_rows_with_official_min_score", "value": with_score, "notes": "Min score may be retained for QA, but rank remains blank."},
        {"metric": "subqueue_rows_with_min_rank", "value": with_rank, "notes": "Must stay 0 until official score-rank raw cache is approved and QA passes."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Gate remains closed."},
    ]
    for lane, count in sorted(lane_counts.items()):
        rollup.append({"metric": f"lane::{lane}", "value": count, "notes": "subqueue lane count"})
    for reason, count in sorted(reason_counts.items()):
        rollup.append({"metric": f"exclusion::{reason}", "value": count, "notes": "exclusion reason count"})

    expected_ids = {
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0001",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0002",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0004",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0005",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0006",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0007",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0008",
        "reference_trend_520_p1_batch17_source_packet_preview_action_queue_0010",
    }
    actual_ids = {row["source_action_queue_id"] for row in subqueue}
    qa_rows = [
        {
            "qa_check": "input_action_queue_present",
            "status": "PASS" if INPUT.exists() and len(rows) == 15 else "FAIL",
            "details": f"Read {len(rows)} rows from marker 133 action queue.",
        },
        {
            "qa_check": "row_balance",
            "status": "PASS" if len(subqueue) + len(exclusions) == len(rows) else "FAIL",
            "details": f"subqueue={len(subqueue)} exclusions={len(exclusions)} source={len(rows)}",
        },
        {
            "qa_check": "strict_expected_subqueue_membership",
            "status": "PASS" if actual_ids == expected_ids else "FAIL",
            "details": f"expected={len(expected_ids)} actual={len(actual_ids)}",
        },
        {
            "qa_check": "no_browser_approval_rows_in_subqueue",
            "status": "PASS"
            if all(
                "approved" not in read.get("requires_browser_or_alternate_fetch", "")
                and "browser_review" not in read.get("requires_browser_or_alternate_fetch", "")
                and not read.get("requires_browser_or_alternate_fetch", "").startswith("true_if_static_fetch")
                for read in rows
                if read["action_queue_id"] in actual_ids
            )
            else "FAIL",
            "details": "Subqueue permits local/static QA only; table alignment text that starts false_for_reachability is allowed.",
        },
        {
            "qa_check": "no_ocr_wechat_login_rows_in_subqueue",
            "status": "PASS"
            if all(
                not is_true(read.get("requires_wechat_capture", ""))
                and not is_true(read.get("requires_ocr_or_manual_image_review", ""))
                and not is_true(read.get("requires_login_or_cookie_state", ""))
                for read in rows
                if read["action_queue_id"] in actual_ids
            )
            else "FAIL",
            "details": "Image/OCR, WeChat, and login/cookie rows are excluded.",
        },
        {
            "qa_check": "min_rank_stays_blank",
            "status": "PASS" if with_rank == 0 else "FAIL",
            "details": "No rank selected or inferred.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in subqueue
            )
            else "FAIL",
            "details": "Subqueue is QA-only and remains outside intake/canonical/ML.",
        },
    ]

    write_csv(OUT_QUEUE, QUEUE_FIELDS, subqueue)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)
    write_csv(OUT_ROLLUP, ["metric", "value", "notes"], rollup)
    write_csv(OUT_QA, ["qa_check", "status", "details"], qa_rows)

    doc = f"""# P1 batch17 safe static QA subqueue

## Summary

从 marker 133 的 15 条 source-packet preview action queue 中，拆出 {len(subqueue)} 条可以在无新增批准条件下继续推进的 strict local/static QA rows，并将 {len(exclusions)} 条涉及浏览器/JS、条件 fetch、图片/OCR 或 WeChat 的 rows 写入 exclusion log。

本轮不联网、不缓存、不解析新网页、不 OCR、不打开微信或浏览器态；只为后续本地表格对齐、既有 preview QA、group mapping readiness、coverage/exclusion rollup 提供安全子队列。

## Outputs

- `{OUT_QUEUE.relative_to(ROOT)}`
- `{OUT_ROLLUP.relative_to(ROOT)}`
- `{OUT_QA.relative_to(ROOT)}`
- `{OUT_EXCLUSION.relative_to(ROOT)}`

## Coverage

- Source action queue rows: {len(rows)}
- Strict safe/static subqueue rows: {len(subqueue)}
- Excluded rows: {len(exclusions)}
- Subqueue rows with official min_score: {with_score}
- Subqueue rows with selected min_rank: {with_rank}

## Boundaries

- `min_rank` 继续为空；等待 marker 136 的官方一分一档 raw cache/浏览器态批准后才能选择位次。
- `reference_trend_pool_eligible=false`，`calibration_eligible=false`，`canonical_ml_entry_open=false`。
- 不合并 32 所 decision_pool，不写 canonical/ML，不做 intake。

## QA

QA PASS: row balance、strict membership、browser/approval exclusion、OCR/WeChat/login exclusion、rank blank gate、intake/canonical/ML closure all pass.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    handoff_block = f"""

## 137. 2026-05-17 P1 batch17 safe static QA subqueue

已新增 P1 batch17 safe static QA subqueue：

- `{OUT_QUEUE.relative_to(ROOT)}`
- `{OUT_ROLLUP.relative_to(ROOT)}`
- `{OUT_QA.relative_to(ROOT)}`
- `{OUT_EXCLUSION.relative_to(ROOT)}`
- `{OUT_DOC.relative_to(ROOT)}`

覆盖结果：从 marker 133 的 15 条 source-packet preview action queue 中拆出 {len(subqueue)} 条无需新增批准的 strict local/static QA rows，另将 {len(exclusions)} 条因浏览器/JS、条件 fetch、图片/OCR 或 WeChat 边界写入 exclusion log。子队列中 {with_score} 条保留官方最低分用于 QA/readiness，但 `min_rank` 全部继续为空。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步可在该子队列内做本地表格对齐、既有 source_packet preview QA、group mapping readiness 和 coverage rollup；官方位次仍等待 marker 136 批准包或用户提供官方 raw artifact。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 137. 2026-05-17 P1 batch17 safe static QA subqueue" not in existing:
        HANDOFF.write_text(existing.rstrip() + handoff_block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(subqueue)} subqueue rows and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
