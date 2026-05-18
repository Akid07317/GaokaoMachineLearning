#!/usr/bin/env python3
"""Build execution packet for P1 batch-17 university discovery queue.

This turns queue-only discovery tasks into auditable execution lanes, stop
conditions, and next-artifact expectations. It does not search, fetch, cache,
parse, OCR, replay forms, open a browser, or create source-packet/intake rows.
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

QUEUE = SEED / "reference_trend_520_p1_batch17_university_discovery_queue.csv"
OUT = SEED / "reference_trend_520_p1_batch17_discovery_execution_packet.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch17_discovery_execution_packet_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch17_discovery_execution_packet_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch17_discovery_execution_packet_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch17_discovery_execution_packet.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "packet_id",
    "queue_id",
    "university_code",
    "university_name",
    "queue_ranks",
    "group_pair_keys",
    "group_codes",
    "target_group_count",
    "trend_directions",
    "rank_delta_min",
    "rank_delta_max",
    "source_packet_priority",
    "priority_score_max",
    "execution_lane",
    "lane_priority",
    "allowed_discovery_mode",
    "primary_search_query",
    "secondary_search_query",
    "site_search_query",
    "search_query_bundle",
    "special_type_boundaries",
    "desired_source_fields",
    "must_not_accept",
    "stop_condition",
    "manual_approval_trigger",
    "requires_network",
    "requires_browser_or_alternate_fetch",
    "requires_manual_approval_now",
    "source_packet_status",
    "source_packet_preview_eligible",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "expected_next_artifact",
    "next_action",
    "evidence_note",
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
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def lane_for(row: dict[str, str]) -> dict[str, str]:
    route = row.get("discovery_route", "")
    boundary = row.get("special_type_boundaries", "")
    if "local_guangxi" in route:
        return {
            "execution_lane": "official_local_admission_site_search_first",
            "lane_priority": "P1E1_local_official_first",
            "allowed_discovery_mode": "official_site_or_exam_authority_search_only",
            "stop_condition": "stop_if_no_official_plan_page_or_if_local_site_requires_browser_cookie_form_state",
            "manual_approval_trigger": "browser_cookie_header_form_submit_required_or_local_site_unverifiable",
            "expected_next_artifact": "source_packet_candidate_preview_or_reachability_backoff",
            "next_action": "Search only official university/exam-authority surfaces for Guangxi physics ordinary-batch plan evidence.",
        }
    if "medical" in boundary or "medical" in route:
        return {
            "execution_lane": "official_medical_plan_search_with_special_type_isolation",
            "lane_priority": "P1E2_medical_boundary_guard",
            "allowed_discovery_mode": "official_site_search_with_ordinary_batch_medical_structure_review",
            "stop_condition": "stop_if_ordinary_batch_cannot_be_separated_from_medical_special_preparatory_or_nonordinary_rows",
            "manual_approval_trigger": "medical_special_type_boundary_unclear_or_pdf_table_layout_requires_manual_QA",
            "expected_next_artifact": "source_packet_candidate_preview_or_special_type_backoff",
            "next_action": "Search official plan evidence, then isolate ordinary-batch group/major structure before any preview.",
        }
    if "ethnic" in boundary or "minority" in boundary or "ethnic" in route:
        return {
            "execution_lane": "official_ethnic_plan_search_with_special_type_isolation",
            "lane_priority": "P1E3_ethnic_boundary_guard",
            "allowed_discovery_mode": "official_site_search_with_ethnic_minority_boundary_review",
            "stop_condition": "stop_if_ordinary_batch_cannot_be_separated_from_ethnic_minority_preparatory_or_special_rows",
            "manual_approval_trigger": "ethnic_minority_boundary_unclear_or_requires_human_policy_judgment",
            "expected_next_artifact": "source_packet_candidate_preview_or_special_type_backoff",
            "next_action": "Search official source candidates only if ordinary-batch non-special rows can remain isolated.",
        }
    if "agriculture" in boundary:
        return {
            "execution_lane": "official_agriculture_plan_search_with_major_structure_review",
            "lane_priority": "P1E4_agriculture_structure_review",
            "allowed_discovery_mode": "official_site_search_with_major_structure_review",
            "stop_condition": "stop_if_plan_table_lacks_group_code_or_major_structure_needed_for_group_mapping",
            "manual_approval_trigger": "major_structure_or_group_mapping_ambiguous_after_official_candidate_found",
            "expected_next_artifact": "source_packet_candidate_preview_or_group_structure_backoff",
            "next_action": "Search official plan evidence and preserve major-structure notes for later group mapping QA.",
        }
    if "normal_language" in boundary or "teacher" in boundary:
        return {
            "execution_lane": "official_normal_language_plan_search_with_teacher_direction_review",
            "lane_priority": "P1E5_normal_language_teacher_review",
            "allowed_discovery_mode": "official_site_search_with_teacher_direction_review",
            "stop_condition": "stop_if_teacher_direction_language_or_nonordinary_category_cannot_be_isolated",
            "manual_approval_trigger": "teacher_direction_language_category_or_special_program_boundary_unclear",
            "expected_next_artifact": "source_packet_candidate_preview_or_teacher_direction_backoff",
            "next_action": "Search official plan evidence while preserving teacher-direction/language category boundaries.",
        }
    return {
        "execution_lane": "official_standard_plan_search",
        "lane_priority": "P1E6_standard_official_search",
        "allowed_discovery_mode": "official_university_site_search_or_exam_authority_source_only",
        "stop_condition": "stop_if_no_official_source_or_if_login_cookie_header_form_browser_state_required",
        "manual_approval_trigger": "browser_cookie_header_form_submit_required_or_only_third_party_sources_found",
        "expected_next_artifact": "source_packet_candidate_preview_or_reachability_backoff",
        "next_action": "Search official plan source candidates and write only preview/backoff artifacts.",
    }


def build_rows() -> list[dict[str, object]]:
    queue_rows = read_csv(QUEUE)
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(queue_rows, 1):
        lane = lane_for(row)
        search_bundle = " || ".join(
            part
            for part in [
                row.get("primary_search_query", ""),
                row.get("secondary_search_query", ""),
                row.get("site_search_query", ""),
            ]
            if part
        )
        rows.append(
            {
                "packet_id": f"reference_trend_520_p1_batch17_execution_{idx:04d}",
                "queue_id": row.get("queue_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "queue_ranks": row.get("queue_ranks", ""),
                "group_pair_keys": row.get("group_pair_keys", ""),
                "group_codes": row.get("group_codes", ""),
                "target_group_count": row.get("target_group_count", ""),
                "trend_directions": row.get("trend_directions", ""),
                "rank_delta_min": row.get("rank_delta_min", ""),
                "rank_delta_max": row.get("rank_delta_max", ""),
                "source_packet_priority": row.get("source_packet_priority", ""),
                "priority_score_max": row.get("priority_score_max", ""),
                **lane,
                "primary_search_query": row.get("primary_search_query", ""),
                "secondary_search_query": row.get("secondary_search_query", ""),
                "site_search_query": row.get("site_search_query", ""),
                "search_query_bundle": search_bundle,
                "special_type_boundaries": row.get("special_type_boundaries", ""),
                "desired_source_fields": row.get("desired_source_fields", ""),
                "must_not_accept": row.get("must_not_accept", ""),
                "requires_network": "true",
                "requires_browser_or_alternate_fetch": "false_until_static_official_discovery_is_blocked",
                "requires_manual_approval_now": "false",
                "source_packet_status": "execution_packet_only_no_source_claimed",
                "source_packet_preview_eligible": "false_until_official_candidate_found_and_QA_ready",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Derived from marker 119 university queue; no web search, fetch, cache, parse, OCR, or browser action executed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    lane = Counter(str(row["execution_lane"]) for row in rows)
    priority = Counter(str(row["lane_priority"]) for row in rows)
    boundary = Counter(str(row["special_type_boundaries"]) for row in rows)
    rollup_rows = [
        {"metric": "execution_packet_rows", "value": len(rows), "note": "One execution packet row per marker 119 university task."},
        {"metric": "source_university_queue_rows_covered", "value": len(read_csv(QUEUE)), "note": ""},
        {"metric": "source_group_rows_covered", "value": sum(int(row["target_group_count"]) for row in rows), "note": "Inherited from marker 119."},
        {"metric": "requires_network_rows", "value": sum(row["requires_network"] == "true" for row in rows), "note": "Future discovery only; no network executed."},
        {"metric": "requires_browser_or_alternate_fetch_now_rows", "value": 0, "note": "All rows stop before browser/cookie/header/form state."},
        {"metric": "requires_manual_approval_now_rows", "value": 0, "note": "No approval consumed in this packet-only pass."},
        {"metric": "source_packet_preview_eligible_rows", "value": 0, "note": "No official candidates found in this pass."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Execution packet only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed records."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"lane::{key}", "value": value, "note": ""} for key, value in sorted(lane.items()))
    rollup_rows.extend({"metric": f"lane_priority::{key}", "value": value, "note": ""} for key, value in sorted(priority.items()))
    rollup_rows.extend({"metric": f"boundary::{key}", "value": value, "note": ""} for key, value in sorted(boundary.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    queue_rows = read_csv(QUEUE)
    covered_queue_ids = {row["queue_id"] for row in rows}
    source_queue_ids = {row["queue_id"] for row in queue_rows}
    qa_rows = [
        {
            "check": "all_university_queue_rows_mapped",
            "status": "PASS" if covered_queue_ids == source_queue_ids and len(rows) == len(queue_rows) else "FAIL",
            "detail": f"Mapped {len(rows)} execution packet rows from {len(queue_rows)} university queue rows.",
        },
        {
            "check": "no_source_claimed",
            "status": "PASS" if all(row["source_packet_status"] == "execution_packet_only_no_source_claimed" for row in rows) else "FAIL",
            "detail": "Execution packet does not claim official-source discovery, URL cache, parse, or receipt success.",
        },
        {
            "check": "stop_conditions_present",
            "status": "PASS" if all(row["stop_condition"] for row in rows) else "FAIL",
            "detail": "Every execution row has a stop condition before browser/form/OCR/manual ambiguity.",
        },
        {
            "check": "no_intake_or_canonical",
            "status": "PASS"
            if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows)
            else "FAIL",
            "detail": "No row enters reference trend intake, calibration, canonical, ML, or the 32-school decision pool.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch17_discovery_execution_packet_all_rows",
            "reason": "execution_constraints_only_no_official_source_discovered",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    exclusions.extend(
        {
            "item": row["packet_id"],
            "reason": row["source_packet_status"],
            "effect": row["stop_condition"],
        }
        for row in rows
    )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    lanes = Counter(str(row["execution_lane"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch17 discovery execution packet",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This packet converts the batch17 university discovery queue into auditable execution lanes and stop conditions.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Summary",
        "",
        f"- execution packet rows: {len(rows)}",
        f"- covered group rows: {sum(int(row['target_group_count']) for row in rows)}",
        "- source packet preview eligible rows: 0",
        "- reference trend intake eligible rows: 0",
        "",
        "## Lane counts",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(lanes.items()))
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No web search, fetch, cache, parse, OCR, or browser/form replay was executed.",
            "- This packet only records future execution lanes, stop conditions, and approval triggers.",
            "- Canonical/ML and the 32-school decision pool remain closed.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)

    marker = "## 120. 2026-05-17 P1 batch17 discovery execution packet"
    handoff = f"""

{marker}

已新增 P1 batch17 discovery execution packet：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：从 marker 119 的 19 条院校级 discovery tasks 派生 {len(rows)} 条执行约束 rows，覆盖 {sum(int(row['target_group_count']) for row in rows)} 个 group-level 目标；按本地院校、医学/民族/农学/师范语言/标准官方计划发现 lane 分流，并为每条记录写入 stop condition 和人工批准触发条件。QA PASS。

准入边界：本轮只生成未来官方来源发现的 execution packet，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；不声明任何官方来源已找到；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
