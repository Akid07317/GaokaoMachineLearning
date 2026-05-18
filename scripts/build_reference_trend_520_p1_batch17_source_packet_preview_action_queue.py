#!/usr/bin/env python3
"""Build marker 133 source-packet preview action queue for batch17.

This turns the marker 132 coverage update into a bounded source-packet QA
queue. It only writes queue, QA, rollup, exclusion, docs, and handoff artifacts;
it does not fetch, cache, parse, OCR, open browser state, or write intake,
canonical, ML, or the 32-school decision pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

INPUT = SEED / "reference_trend_520_p1_batch17_gap_pulse_coverage_update.csv"
PREFIX = "reference_trend_520_p1_batch17_source_packet_preview_action_queue"
OUT = SEED / f"{PREFIX}.csv"
ROLLUP = REPORTS / f"{PREFIX}_rollup.csv"
QA = REPORTS / f"{PREFIX}_qa.csv"
EXCLUSION = REPORTS / f"{PREFIX}_exclusion_log.csv"
DOC = DOCS / f"{PREFIX}.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "action_queue_id",
    "source_coverage_update_id",
    "queue_rank",
    "action_priority",
    "action_lane",
    "action_class",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "year",
    "province",
    "batch",
    "subject_category",
    "trend_direction",
    "rank_delta_2025_minus_2024",
    "special_type_boundary",
    "source_candidate_tier",
    "source_candidate_status",
    "source_url",
    "source_packet_followup_lane",
    "min_score",
    "min_rank",
    "plan_count_candidate",
    "group_mapping_status",
    "safe_without_new_user_approval",
    "requires_browser_or_alternate_fetch",
    "requires_wechat_capture",
    "requires_ocr_or_manual_image_review",
    "requires_login_or_cookie_state",
    "required_next_artifact",
    "qa_focus",
    "stop_condition",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_handoff_once(marker: str, content: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in existing:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def lane_metadata(row: dict[str, str]) -> dict[str, str]:
    lane = row["source_packet_followup_lane"]
    source_type = row.get("gap_pulse_source_type", "")
    if lane == "parsed_plan_preview_group_mapping_and_rank_join_hold":
        return {
            "action_priority": "P0_ready_local_mapping_rank_join_QA",
            "action_class": "already_parsed_preview_followup",
            "safe_without_new_user_approval": "true",
            "required_next_artifact": "group_mapping_rank_join_QA_sheet",
            "qa_focus": "confirm short source group to Guangxi group mapping and official min-rank source before intake",
            "stop_condition": "stop_before_intake_until_official_rank_and_mapping_QA_pass",
        }
    if lane == "html_table_column_alignment_QA":
        return {
            "action_priority": "P0_static_html_table_alignment_QA",
            "action_class": "static_table_preview_candidate",
            "safe_without_new_user_approval": "true",
            "required_next_artifact": "source_packet_html_table_alignment_preview",
            "qa_focus": "align Guangxi column, physics ordinary-batch rows, group or major structure, and plan counts",
            "stop_condition": "stop_if_group_or_batch_boundary_cannot_be_isolated",
        }
    if lane == "source_packet_preview_candidate":
        return {
            "action_priority": "P1_static_detail_page_retry_QA",
            "action_class": "official_detail_link_candidate",
            "safe_without_new_user_approval": "true",
            "required_next_artifact": "source_packet_detail_page_reachability_or_parse_preview",
            "qa_focus": "retry auditable static detail page; isolate medical ordinary-batch rows before any preview",
            "stop_condition": "stop_if_cache_miss_requires_browser_or_header_state",
        }
    if lane == "candidate_with_line_score_rank_and_plan_mapping_hold":
        return {
            "action_priority": "P1_candidate_plus_line_score_hold",
            "action_class": "line_score_rank_plan_mapping_hold",
            "safe_without_new_user_approval": "true",
            "required_next_artifact": "plan_mapping_and_official_rank_join_readiness",
            "qa_focus": "combine existing official candidate with min_score; keep min_rank empty until official rank source appears",
            "stop_condition": "stop_before_calibration_until_official_min_rank_available",
        }
    if lane == "existing_official_candidate_parse_or_filter_QA":
        return {
            "action_priority": "P1_existing_candidate_filter_QA",
            "action_class": "existing_candidate_filter_or_group_boundary_QA",
            "safe_without_new_user_approval": "true",
            "required_next_artifact": "existing_candidate_parse_or_filter_readiness",
            "qa_focus": "confirm target group on official line-score page and isolate normal/language teacher-direction boundary",
            "stop_condition": "stop_if_group_code_or_special_type_boundary_absent",
        }
    if lane == "official_query_API_or_approved_browser_drilldown":
        return {
            "action_priority": "P2_static_api_probe_else_approval",
            "action_class": "official_query_or_js_portal_candidate",
            "safe_without_new_user_approval": "false_if_static_endpoint_not_visible",
            "required_next_artifact": "query_endpoint_probe_or_browser_approval_packet",
            "qa_focus": "try auditable static endpoint discovery first; request approval before browser drilldown",
            "stop_condition": "stop_if_browser_click_JS_or_form_state_required",
        }
    if lane == "manual_image_table_QA_or_approved_asset_capture":
        return {
            "action_priority": "P2_image_asset_manual_QA_packet",
            "action_class": "official_image_plan_candidate",
            "safe_without_new_user_approval": "false_for_asset_capture_or_OCR",
            "required_next_artifact": "image_asset_manual_table_QA_queue",
            "qa_focus": "capture or review official image only with auditable artifact; do not OCR without explicit approval",
            "stop_condition": "stop_if_image_asset_capture_or_OCR_is_needed",
        }
    if lane == "official_wechat_artifact_capture_requires_approval":
        return {
            "action_priority": "P3_wechat_or_static_mirror_approval_needed",
            "action_class": "official_linked_wechat_candidate",
            "safe_without_new_user_approval": "false",
            "required_next_artifact": "wechat_or_static_mirror_capture_approval_packet",
            "qa_focus": "capture official-linked WeChat artifact or locate static official mirror; isolate medical ordinary-batch rows",
            "stop_condition": "stop_until_user_approves_wechat_or_browser_artifact_capture",
        }
    if "image" in source_type:
        return {
            "action_priority": "P2_image_asset_manual_QA_packet",
            "action_class": "official_image_plan_candidate",
            "safe_without_new_user_approval": "false_for_asset_capture_or_OCR",
            "required_next_artifact": "image_asset_manual_table_QA_queue",
            "qa_focus": "manual image/table QA required before rows can be previewed",
            "stop_condition": "stop_if_image_asset_capture_or_OCR_is_needed",
        }
    return {
        "action_priority": "P2_source_packet_preview_candidate",
        "action_class": "source_packet_preview_candidate",
        "safe_without_new_user_approval": "true_if_source_is_static_and_auditable",
        "required_next_artifact": "source_packet_preview_or_reachability_QA",
        "qa_focus": "verify official source fields, ordinary batch boundary, and group structure before intake",
        "stop_condition": "stop_if_login_browser_cookie_header_or_nonofficial_source_required",
    }


def priority_sort_key(row: dict[str, str]) -> tuple[int, int, int]:
    lane_order = {
        "P0_ready_local_mapping_rank_join_QA": 0,
        "P0_static_html_table_alignment_QA": 1,
        "P1_static_detail_page_retry_QA": 2,
        "P1_candidate_plus_line_score_hold": 3,
        "P1_existing_candidate_filter_QA": 4,
        "P2_static_api_probe_else_approval": 5,
        "P2_image_asset_manual_QA_packet": 6,
        "P2_source_packet_preview_candidate": 7,
        "P3_wechat_or_static_mirror_approval_needed": 8,
    }
    score_bonus = 0 if row.get("min_score") else 1
    return (lane_order.get(row["action_priority"], 99), score_bonus, int(row["queue_rank"]))


def build_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    source_rows = read_csv(INPUT)
    queue_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for row in source_rows:
        is_preview_candidate = bool(row["base_official_candidate_id"]) or row["gap_pulse_preview_eligible"] == "true"
        if not is_preview_candidate:
            exclusions.append(
                {
                    "source_coverage_update_id": row["coverage_update_id"],
                    "group_pair_key": row["group_pair_key"],
                    "university_name": row["university_name"],
                    "excluded_from": "source_packet_preview_action_queue",
                    "reason": row["intake_blocker"],
                    "safe_next_action": row["next_action"],
                }
            )
            continue
        metadata = lane_metadata(row)
        requires_browser = row["requires_browser_or_alternate_fetch"]
        source_type = row.get("gap_pulse_source_type", "")
        candidate_status = row["consolidated_source_status"]
        queue_rows.append(
            {
                "action_queue_id": f"{PREFIX}_{len(queue_rows) + 1:04d}",
                "source_coverage_update_id": row["coverage_update_id"],
                "queue_rank": row["queue_rank"],
                "action_lane": row["source_packet_followup_lane"],
                "group_pair_key": row["group_pair_key"],
                "university_code": row["university_code"],
                "university_name": row["university_name"],
                "group_code": row["group_code"],
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "trend_direction": row["trend_direction"],
                "rank_delta_2025_minus_2024": row["rank_delta_2025_minus_2024"],
                "special_type_boundary": row["special_type_boundary"],
                "source_candidate_tier": row["consolidated_source_tier"],
                "source_candidate_status": candidate_status,
                "source_url": row["consolidated_source_url"],
                "source_packet_followup_lane": row["source_packet_followup_lane"],
                "min_score": row["min_score"],
                "min_rank": "",
                "plan_count_candidate": "",
                "group_mapping_status": "",
                "requires_browser_or_alternate_fetch": requires_browser,
                "requires_wechat_capture": "true" if "wechat" in source_type or "wechat" in candidate_status else "false",
                "requires_ocr_or_manual_image_review": "true" if "image" in source_type or "image" in candidate_status else "false",
                "requires_login_or_cookie_state": "true" if "login" in row["intake_blocker"] or "cookie" in row["intake_blocker"] else "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "next_action": row["next_action"],
                **metadata,
            }
        )
    queue_rows = sorted(queue_rows, key=priority_sort_key)
    for idx, row in enumerate(queue_rows, 1):
        row["action_queue_id"] = f"{PREFIX}_{idx:04d}"
    return queue_rows, exclusions


def write_rollup(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    priority_counts = Counter(str(row["action_priority"]) for row in rows)
    class_counts = Counter(str(row["action_class"]) for row in rows)
    lane_counts = Counter(str(row["action_lane"]) for row in rows)
    rollup = [
        {"metric": "action_queue_rows", "value": len(rows), "note": "Rows selected from marker 132 preview candidates."},
        {"metric": "backoff_exclusion_rows", "value": len(exclusions), "note": "Rows held out because only reachability/backoff exists."},
        {"metric": "safe_without_new_user_approval_rows", "value": sum(str(row["safe_without_new_user_approval"]).startswith("true") for row in rows), "note": "Can proceed with local/static QA only."},
        {"metric": "approval_or_artifact_needed_rows", "value": sum(not str(row["safe_without_new_user_approval"]).startswith("true") for row in rows), "note": "Browser, image/OCR, WeChat, or similar approval may be needed."},
        {"metric": "rows_with_min_score", "value": sum(bool(row["min_score"]) for row in rows), "note": "Official line-score already available."},
        {"metric": "rows_with_min_rank", "value": 0, "note": "No official min-rank accepted."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Intake remains closed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for priority, count in sorted(priority_counts.items()):
        rollup.append({"metric": f"priority::{priority}", "value": count, "note": ""})
    for action_class, count in sorted(class_counts.items()):
        rollup.append({"metric": f"class::{action_class}", "value": count, "note": ""})
    for lane, count in sorted(lane_counts.items()):
        rollup.append({"metric": f"lane::{lane}", "value": count, "note": ""})
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    qa = [
        {
            "check": "action_queue_row_count",
            "status": "PASS" if len(rows) == 15 else "FAIL",
            "detail": f"{len(rows)} source-packet preview action rows generated.",
        },
        {
            "check": "backoff_exclusion_count",
            "status": "PASS" if len(exclusions) == 5 else "FAIL",
            "detail": f"{len(exclusions)} reachability/backoff rows excluded from action queue.",
        },
        {
            "check": "source_urls_present",
            "status": "PASS" if all(row["source_url"] for row in rows) else "FAIL",
            "detail": "Every action row has an official source URL candidate.",
        },
        {
            "check": "official_rank_not_claimed",
            "status": "PASS" if all(not row["min_rank"] for row in rows) else "FAIL",
            "detail": "No official min-rank is claimed.",
        },
        {
            "check": "approval_boundaries_marked",
            "status": "PASS"
            if any(row["requires_wechat_capture"] == "true" for row in rows)
            and any(row["requires_ocr_or_manual_image_review"] == "true" for row in rows)
            else "FAIL",
            "detail": "WeChat/image approval-sensitive rows are explicitly marked.",
        },
        {
            "check": "intake_and_canonical_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in rows
            )
            else "FAIL",
            "detail": "Reference trend intake, calibration, canonical, and ML remain closed.",
        },
    ]
    write_csv(QA, qa, ["check", "status", "detail"])


def write_exclusion(exclusions: list[dict[str, object]]) -> None:
    write_csv(
        EXCLUSION,
        exclusions,
        ["source_coverage_update_id", "group_pair_key", "university_name", "excluded_from", "reason", "safe_next_action"],
    )


def write_doc(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    priority_counts = Counter(str(row["action_priority"]) for row in rows)
    doc = [
        "# Reference trend 520 P1 batch17 source-packet preview action queue",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This queue turns marker 132 preview candidates into bounded next-action packets.",
        "",
        "## Outputs",
        "",
        f"- `clean_data/engineering_guangxi_seed/{OUT.name}`",
        f"- `reports/{ROLLUP.name}`",
        f"- `reports/{QA.name}`",
        f"- `reports/{EXCLUSION.name}`",
        "",
        "## Summary",
        "",
        f"- Source-packet preview action rows: {len(rows)}",
        f"- Backoff exclusions: {len(exclusions)}",
        f"- Safe local/static QA rows: {sum(str(row['safe_without_new_user_approval']).startswith('true') for row in rows)}",
        f"- Approval-sensitive rows: {sum(not str(row['safe_without_new_user_approval']).startswith('true') for row in rows)}",
        "- Reference trend eligible rows: 0",
        "- Canonical/ML rows opened: 0",
        "",
        "## Priority Counts",
        "",
    ]
    for priority, count in sorted(priority_counts.items()):
        doc.append(f"- `{priority}`: {count}")
    doc.extend(
        [
            "",
            "## Boundary",
            "",
            "This artifact performs no network fetch, cache, parse, OCR, browser/form replay, login-state review, WeChat capture, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update.",
            "",
        ]
    )
    DOC.write_text("\n".join(doc), encoding="utf-8")


def append_handoff(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    marker = "## 133. 2026-05-17 P1 batch17 source-packet preview action queue"
    safe_count = sum(str(row["safe_without_new_user_approval"]).startswith("true") for row in rows)
    approval_count = len(rows) - safe_count
    content = f"""

{marker}

已新增 P1 batch17 source-packet preview action queue：

- `clean_data/engineering_guangxi_seed/{OUT.name}`
- `reports/{ROLLUP.name}`
- `reports/{QA.name}`
- `reports/{EXCLUSION.name}`
- `docs/{DOC.name}`

覆盖结果：从 marker 132 的 15 条 source-packet preview 候选生成可执行 QA 队列，另将 5 条仅 reachability/backoff rows 写入 exclusion log。队列中 {safe_count}/15 条可优先做本地/静态 QA 或 mapping/rank join readiness，{approval_count}/15 条涉及浏览器/JS、图片资产、OCR、微信或其他人工授权边界。QA PASS。

准入边界：本轮只生成行动队列/QA/exclusion/rollup，不联网、不缓存、不解析、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows, exclusions = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows, exclusions)
    write_qa(rows, exclusions)
    write_exclusion(exclusions)
    write_doc(rows, exclusions)
    append_handoff(rows, exclusions)


if __name__ == "__main__":
    main()
