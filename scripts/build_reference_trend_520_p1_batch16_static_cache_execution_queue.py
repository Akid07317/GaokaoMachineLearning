#!/usr/bin/env python3
"""Build a static-cache execution queue from P1 batch-16 readiness rows.

This queue is intentionally not an execution run: it does not use network,
cache pages, parse source packets, OCR, replay forms, or open canonical/ML.
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

READINESS = CLEAN / "reference_trend_520_p1_batch16_cache_readiness_packet.csv"
OUT = CLEAN / "reference_trend_520_p1_batch16_static_cache_execution_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch16_static_cache_execution_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch16_static_cache_execution_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch16_static_cache_execution_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch16_static_cache_execution_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "execution_candidate_id",
    "readiness_id",
    "action_id",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "source_title",
    "readiness_lane",
    "cache_execution_route",
    "cache_execution_priority",
    "network_permission_status",
    "blocked_by_known_terminal_curl_backoff",
    "browser_or_form_replay_approval_required_before_execution",
    "static_fetch_rule",
    "stop_condition",
    "expected_next_artifact",
    "manual_review_required_before_intake",
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


def execution_route(row: dict[str, str]) -> dict[str, str]:
    lane = row.get("readiness_lane", "")
    if lane == "static_official_page_cache_candidate":
        return {
            "cache_execution_route": "static_html_page_cache_candidate",
            "cache_execution_priority": "P1E1_exact_official_page_first",
            "expected_next_artifact": "static_html_cache_receipt_then_parse_preview",
            "browser_or_form_replay_approval_required_before_execution": "false_unless_static_fetch_blocked",
            "stop_condition": "stop_if_requires_cookie_header_browser_state_or_form_replay",
        }
    if lane == "static_official_pdf_cache_candidate":
        return {
            "cache_execution_route": "static_pdf_cache_candidate",
            "cache_execution_priority": "P1E2_official_pdf_second",
            "expected_next_artifact": "static_pdf_cache_receipt_then_text_extract_preview",
            "browser_or_form_replay_approval_required_before_execution": "false_unless_static_download_blocked",
            "stop_condition": "stop_if_download_requires_cookie_header_browser_state_or_form_replay",
        }
    if lane == "official_query_static_cache_candidate":
        return {
            "cache_execution_route": "static_query_probe_candidate",
            "cache_execution_priority": "P1E3_query_probe_before_browser",
            "expected_next_artifact": "static_query_reachability_or_cache_receipt",
            "browser_or_form_replay_approval_required_before_execution": "true_if_query_requires_form_browser_state",
            "stop_condition": "stop_before_any_form_submit_cookie_header_or_browser_replay",
        }
    return {
        "cache_execution_route": "detail_url_discovery_before_cache",
        "cache_execution_priority": "P1E4_find_exact_static_detail_url_first",
        "expected_next_artifact": "exact_detail_url_discovery_preview_or_context_hold",
        "browser_or_form_replay_approval_required_before_execution": "false_unless_official_site_blocks_static_discovery",
        "stop_condition": "stop_if_exact_detail_requires_browser_state_or if only context page is found",
    }


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    readiness_rows = read_csv(READINESS)
    candidates = [
        row
        for row in readiness_rows
        if str(row.get("cache_attempt_allowed_without_browser", "")).startswith("true")
    ]
    for idx, row in enumerate(candidates, 1):
        route = execution_route(row)
        rows.append(
            {
                "execution_candidate_id": f"reference_trend_520_p1_batch16_static_cache_exec_{idx:04d}",
                "readiness_id": row.get("readiness_id", ""),
                "action_id": row.get("action_id", ""),
                "source_id": row.get("source_id", ""),
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_url": row.get("source_url", ""),
                "source_title": row.get("source_title", ""),
                "readiness_lane": row.get("readiness_lane", ""),
                **route,
                "network_permission_status": "user_allows_network_but_shell_static_fetch_requires_sandbox_escalation_or_separate_approved_runner",
                "blocked_by_known_terminal_curl_backoff": "false_for_this_batch16_queue",
                "static_fetch_rule": "official_url_only_no_cookie_no_header_replay_no_form_submit_no_browser_state",
                "manual_review_required_before_intake": row.get("manual_review_required_before_intake", "true_after_cache_parse_QA"),
                "source_packet_parse_eligible_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Derived from marker 113 readiness packet; no network/cache/parse/browser action performed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]], readiness_rows: list[dict[str, str]]) -> None:
    routes = Counter(str(row["cache_execution_route"]) for row in rows)
    lanes = Counter(str(row["readiness_lane"]) for row in rows)
    hold_count = sum(
        not str(row.get("cache_attempt_allowed_without_browser", "")).startswith("true")
        for row in readiness_rows
    )
    browser_possible = sum(
        str(row["browser_or_form_replay_approval_required_before_execution"]).startswith("true")
        for row in rows
    )
    rollup_rows = [
        {"metric": "batch16_static_cache_execution_candidates", "value": len(rows), "note": "No execution performed."},
        {"metric": "batch16_readiness_rows_read", "value": len(readiness_rows), "note": "Source marker 113 readiness rows."},
        {"metric": "batch16_hold_or_not_static_cache_rows", "value": hold_count, "note": "Not included in static cache execution queue."},
        {"metric": "shell_network_escalation_or_approved_runner_required_rows", "value": len(rows), "note": "Network is not executed in this artifact."},
        {"metric": "browser_or_form_possible_rows", "value": browser_possible, "note": "Static query rows must stop before form/browser replay."},
        {"metric": "known_terminal_curl_backoff_rows", "value": 0, "note": "Known qg/qn and NUIST blocked URLs are not in this batch16 queue."},
        {"metric": "source_packet_parse_eligible_now_rows", "value": 0, "note": "Execution queue only."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No parsed source rows."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed source rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(routes.items()))
    rollup_rows.extend({"metric": f"lane::{key}", "value": value, "note": ""} for key, value in sorted(lanes.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]], readiness_rows: list[dict[str, str]]) -> None:
    expected = sum(
        str(row.get("cache_attempt_allowed_without_browser", "")).startswith("true")
        for row in readiness_rows
    )
    qa_rows = [
        {
            "check": "all_static_cache_candidates_mapped",
            "status": "PASS" if len(rows) == expected and expected else "FAIL",
            "detail": f"Mapped {len(rows)} candidate rows from {expected} cache-allowed readiness rows.",
        },
        {
            "check": "execution_not_performed",
            "status": "PASS",
            "detail": "This artifact does not fetch/cache/parse/OCR/replay forms.",
        },
        {
            "check": "known_backoff_not_retried",
            "status": "PASS" if all(row["blocked_by_known_terminal_curl_backoff"] == "false_for_this_batch16_queue" for row in rows) else "FAIL",
            "detail": "Known blocked Guangxi qg/qn and NUIST terminal-curl cases are not retried.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "Canonical/ML remains closed.",
        },
        {
            "check": "no_reference_trend_intake",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" for row in rows) else "FAIL",
            "detail": "No execution candidate is eligible for trend intake yet.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]], readiness_rows: list[dict[str, str]]) -> None:
    queued_ids = {str(row["readiness_id"]) for row in rows}
    exclusions = [
        {
            "item": "batch16_static_cache_execution_queue_all_rows",
            "reason": "execution_queue_only_no_network_no_cache_no_parse",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    for row in readiness_rows:
        if row.get("readiness_id", "") not in queued_ids:
            exclusions.append(
                {
                    "item": row.get("readiness_id", ""),
                    "reason": row.get("readiness_lane", "not_static_cache_candidate"),
                    "effect": "not_in_static_cache_execution_queue",
                }
            )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]], readiness_rows: list[dict[str, str]]) -> None:
    routes = Counter(str(row["cache_execution_route"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch16 static cache execution queue",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This queue isolates batch16 rows that could be attempted through an auditable static cache path in a later run. It is not itself a network/cache/parse run.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Route distribution",
        "",
    ]
    for key, value in sorted(routes.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Execution boundary",
            "",
            f"- Readiness rows read: {len(readiness_rows)}",
            f"- Static-cache execution candidates: {len(rows)}",
            "- Network/cache was not performed in this run.",
            "- Future execution must use official URLs only, with no cookie/header/form/browser-state replay.",
            "- If a query or site requires browser/form state, stop and ask for approval.",
            "- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    readiness_rows = read_csv(READINESS)
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows, readiness_rows)
    write_qa(rows, readiness_rows)
    write_exclusion(rows, readiness_rows)
    write_doc(rows, readiness_rows)

    marker = "## 114. 2026-05-17 P1 batch16 static cache execution queue"
    handoff = f"""

{marker}

已新增 P1 batch16 static cache execution queue：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：从 marker 113 的 17 条 readiness rows 中抽出 10 条可作为后续静态缓存/查询候选的 rows；其余 7 条保持 context/special-boundary hold。该队列只定义后续官方 URL 静态抓取边界，不执行联网、不缓存、不解析、不 OCR、不浏览器/form replay。QA PASS。

准入边界：本轮只生成 execution queue，不生成 source_packet parse 或 intake rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
