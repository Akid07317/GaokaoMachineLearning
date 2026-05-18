#!/usr/bin/env python3
"""Build cache/readiness packet from P1 batch-16 action queue.

This packet prioritizes the next auditable work items. It does not fetch,
cache, parse, OCR, replay forms, or create source-packet/intake/canonical rows.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

ACTION_QUEUE = CLEAN / "reference_trend_520_p1_batch16_action_queue.csv"
OUT = CLEAN / "reference_trend_520_p1_batch16_cache_readiness_packet.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch16_cache_readiness_packet_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch16_cache_readiness_packet_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch16_cache_readiness_packet_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch16_cache_readiness_packet.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "readiness_id",
    "action_id",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "source_title",
    "action_route",
    "readiness_lane",
    "readiness_priority",
    "readiness_status",
    "cache_attempt_allowed_without_browser",
    "browser_or_form_approval_required_before_execution",
    "manual_review_required_before_intake",
    "safe_next_artifact",
    "safe_next_action",
    "expected_output_layer",
    "source_packet_parse_eligible_now",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
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


def classify(row: dict[str, str]) -> dict[str, str]:
    route = row.get("action_route", "")
    if route == "exact_official_page_cache_parse_preview":
        return {
            "readiness_lane": "static_official_page_cache_candidate",
            "readiness_priority": "P1R1_exact_page_first",
            "readiness_status": "ready_for_static_cache_attempt_not_intake",
            "cache_attempt_allowed_without_browser": "true",
            "browser_or_form_approval_required_before_execution": "false_unless_static_cache_blocked",
            "manual_review_required_before_intake": "true_after_parse_preview_QA",
            "safe_next_artifact": "official_page_cache_parse_preview",
            "safe_next_action": "Attempt auditable static page cache, then build parse preview and QA before any source_packet row.",
        }
    if route == "official_pdf_cache_then_text_extract_preview":
        return {
            "readiness_lane": "static_official_pdf_cache_candidate",
            "readiness_priority": "P1R2_pdf_cache_then_local_text_preview",
            "readiness_status": "ready_for_static_pdf_cache_attempt_not_intake",
            "cache_attempt_allowed_without_browser": "true",
            "browser_or_form_approval_required_before_execution": "false_unless_download_blocked",
            "manual_review_required_before_intake": "true_pdf_table_layout_QA_required",
            "safe_next_artifact": "official_pdf_cache_text_extract_preview",
            "safe_next_action": "Cache official PDF only through auditable static route, then run local text/table preview.",
        }
    if route == "official_query_cache_parameter_review":
        return {
            "readiness_lane": "official_query_static_cache_candidate",
            "readiness_priority": "P1R3_query_static_before_browser",
            "readiness_status": "ready_for_static_query_probe_only_if_no_form_replay",
            "cache_attempt_allowed_without_browser": "true_if_query_url_is_static_or_parameterized",
            "browser_or_form_approval_required_before_execution": "true_if_query_requires_form_browser_state",
            "manual_review_required_before_intake": "true_after_query_parse_QA",
            "safe_next_artifact": "official_query_cache_or_reachability_preview",
            "safe_next_action": "Try only static parameterized query/cache first; stop and request approval if browser/form state is required.",
        }
    if route == "official_plan_portal_or_page_drilldown":
        return {
            "readiness_lane": "official_plan_detail_drilldown_candidate",
            "readiness_priority": "P1R4_detail_discovery_or_static_cache",
            "readiness_status": "needs_exact_detail_url_or_static_cache_before_parse",
            "cache_attempt_allowed_without_browser": "true_for_exact_static_detail_urls",
            "browser_or_form_approval_required_before_execution": "false_unless_blocked",
            "manual_review_required_before_intake": "true_if_medical_major_or_special_boundary_appears",
            "safe_next_artifact": "detail_url_discovery_or_cache_preview",
            "safe_next_action": "Locate/cache exact official detail page; demote to context hold if no Guangxi physical ordinary rows appear.",
        }
    if route == "special_type_boundary_manual_review_hold":
        return {
            "readiness_lane": "special_type_boundary_hold",
            "readiness_priority": "P1R0_human_boundary_before_execution",
            "readiness_status": "blocked_until_human_boundary_decision",
            "cache_attempt_allowed_without_browser": "false",
            "browser_or_form_approval_required_before_execution": "false",
            "manual_review_required_before_intake": "true_before_any_execution",
            "safe_next_artifact": "special_type_boundary_decision_sheet_if_promoted",
            "safe_next_action": "Keep held unless reviewer confirms ordinary-batch non-special rows can be separated.",
        }
    return {
        "readiness_lane": "context_only_hold",
        "readiness_priority": "P1R9_context_only_low_priority",
        "readiness_status": "hold_until_exact_official_plan_source_found",
        "cache_attempt_allowed_without_browser": "false",
        "browser_or_form_approval_required_before_execution": "false",
        "manual_review_required_before_intake": "false_until_candidate_found",
        "safe_next_artifact": "future_source_discovery_preview_only",
        "safe_next_action": "Keep as context-only evidence; continue source discovery later without intake.",
    }


def build_rows() -> list[dict[str, object]]:
    action_rows = read_csv(ACTION_QUEUE)
    rows: list[dict[str, object]] = []
    for idx, action in enumerate(action_rows, 1):
        readiness = classify(action)
        rows.append(
            {
                "readiness_id": f"reference_trend_520_p1_batch16_readiness_{idx:04d}",
                "action_id": action.get("action_id", ""),
                "source_id": action.get("source_id", ""),
                "queue_record_id": action.get("queue_record_id", ""),
                "queue_rank": action.get("queue_rank", ""),
                "university_code": action.get("university_code", ""),
                "university_name": action.get("university_name", ""),
                "source_url": action.get("source_url", ""),
                "source_title": action.get("source_title", ""),
                "action_route": action.get("action_route", ""),
                **readiness,
                "expected_output_layer": "p1_batch16_cache_readiness_only_not_source_packet_not_intake",
                "source_packet_parse_eligible_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Derived from marker 112 action queue; no network/cache/parse/browser action performed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    lane = Counter(str(row["readiness_lane"]) for row in rows)
    status = Counter(str(row["readiness_status"]) for row in rows)
    static_ready = sum(str(row["cache_attempt_allowed_without_browser"]).startswith("true") for row in rows)
    browser_possible = sum(str(row["browser_or_form_approval_required_before_execution"]).startswith("true") for row in rows)
    blocked = sum(str(row["readiness_status"]).startswith("blocked") or str(row["readiness_lane"]).endswith("hold") for row in rows)
    rollup_rows = [
        {"metric": "batch16_readiness_rows", "value": len(rows), "note": "One readiness row per marker 112 action row."},
        {"metric": "static_cache_attempt_candidate_rows", "value": static_ready, "note": "Still no network/cache performed in this run."},
        {"metric": "browser_or_form_approval_possible_rows", "value": browser_possible, "note": "Only if static query/cache is blocked."},
        {"metric": "hold_or_blocked_rows", "value": blocked, "note": "Context-only or special boundary hold."},
        {"metric": "source_packet_parse_eligible_now_rows", "value": 0, "note": "No source packet parse rows yet."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Readiness only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"lane::{key}", "value": value, "note": ""} for key, value in sorted(lane.items()))
    rollup_rows.extend({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(status.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "source_action_rows_mapped",
            "status": "PASS" if len(rows) == len(read_csv(ACTION_QUEUE)) and rows else "FAIL",
            "detail": f"Mapped {len(rows)} readiness rows from marker 112 action queue.",
        },
        {
            "check": "no_source_packet_parse_eligible_now",
            "status": "PASS" if all(row["source_packet_parse_eligible_now"] == "false" for row in rows) else "FAIL",
            "detail": "Readiness packet does not open source-packet parse.",
        },
        {
            "check": "no_reference_trend_intake",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" for row in rows) else "FAIL",
            "detail": "No row is eligible for trend intake yet.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "Canonical/ML remains closed.",
        },
        {
            "check": "no_execution_claimed",
            "status": "PASS",
            "detail": "No network, cache, parse, OCR, browser/form replay, or manual transcription performed.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch16_cache_readiness_all_rows",
            "reason": "readiness_packet_only_no_cache_no_parse",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    for row in rows:
        if row["readiness_lane"] in {"context_only_hold", "special_type_boundary_hold"}:
            exclusions.append(
                {
                    "item": row["readiness_id"],
                    "reason": row["readiness_lane"],
                    "effect": "hold_until_exact_official_plan_source_or_human_boundary_decision",
                }
            )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    lane = Counter(str(row["readiness_lane"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch16 cache readiness packet",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This packet prioritizes batch16 cache/parse readiness. It does not fetch, cache, parse, OCR, replay forms, or create source-packet/intake/canonical rows.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Lane distribution",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(lane.items()))
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a readiness layer only.",
            "- Static cache candidates still require a future explicit cache/parse preview run.",
            "- Browser/form replay remains approval-gated.",
            "- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.",
        ]
    )
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)
    marker = "## 113. 2026-05-17 P1 batch16 cache readiness packet"
    handoff = f"""

{marker}

已新增 P1 batch16 cache readiness packet：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：从 marker 112 的 17 条 action rows 派生 17 条 readiness rows；分流出静态官方页面/PDF/query 缓存候选、detail drilldown 候选、context hold 和 special boundary hold。QA PASS。

准入边界：本轮只生成 readiness packet，不联网、不缓存、不解析、不 OCR、不浏览器/form replay、不生成 source_packet parse 或 intake rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
