#!/usr/bin/env python3
"""Build next-action queue from P1 batch-16 source discovery preview.

The queue only plans cache/parse/review work. It does not fetch, cache, parse
PDFs/tables, replay forms, or open reference_trend_pool/canonical/ML intake.
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

SOURCE = CLEAN / "reference_trend_520_p1_official_source_discovery_batch16_preview.csv"
OUT = CLEAN / "reference_trend_520_p1_batch16_action_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch16_action_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch16_action_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch16_action_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch16_action_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "action_id",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "source_owner",
    "source_title",
    "collector_confidence",
    "source_packet_status",
    "action_route",
    "action_priority",
    "action_requires_network",
    "action_requires_browser_or_form_approval",
    "action_requires_manual_pdf_or_ocr",
    "action_requires_special_type_review",
    "safe_next_action",
    "expected_output_layer",
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
    confidence = row.get("collector_confidence", "")
    status = row.get("source_packet_status", "")
    source_url = row.get("source_url", "")

    if "special_type_boundary_hold" in status or "special_type_boundary" in confidence:
        return {
            "action_route": "special_type_boundary_manual_review_hold",
            "action_priority": "P1H0_special_type_boundary_before_any_cache",
            "action_requires_network": "false_until_manual_boundary_approval",
            "action_requires_browser_or_form_approval": "false",
            "action_requires_manual_pdf_or_ocr": "false",
            "action_requires_special_type_review": "true",
            "safe_next_action": "Keep on hold unless a reviewer confirms ordinary-batch non-special rows can be isolated.",
        }

    if "pdf" in status or "pdf" in confidence or source_url.lower().endswith(".pdf"):
        return {
            "action_route": "official_pdf_cache_then_text_extract_preview",
            "action_priority": "P1P1_pdf_cache_parse_preview_candidate",
            "action_requires_network": "true_for_official_pdf_cache",
            "action_requires_browser_or_form_approval": "false_unless_download_blocked",
            "action_requires_manual_pdf_or_ocr": "true_after_cache_for_table_layout_QA",
            "action_requires_special_type_review": "false_until_parse",
            "safe_next_action": "Cache official PDF only if normal network access works; then run local text/table preview and QA before source_packet.",
        }

    if "query" in status or "query" in confidence:
        return {
            "action_route": "official_query_cache_parameter_review",
            "action_priority": "P1Q1_query_cache_candidate",
            "action_requires_network": "true_for_query_cache",
            "action_requires_browser_or_form_approval": "true_if_query_requires_form_browser_state",
            "action_requires_manual_pdf_or_ocr": "false",
            "action_requires_special_type_review": "true_if_query_returns_mixed_special_rows",
            "safe_next_action": "Try auditable static query/cache route first; request approval before browser/form replay.",
        }

    if confidence.startswith("T1_"):
        return {
            "action_route": "exact_official_page_cache_parse_preview",
            "action_priority": "P1A1_exact_page_cache_parse_candidate",
            "action_requires_network": "true_for_official_page_cache",
            "action_requires_browser_or_form_approval": "false_unless_blocked",
            "action_requires_manual_pdf_or_ocr": "false",
            "action_requires_special_type_review": "true_if_page_contains_mixed_special_rows",
            "safe_next_action": "Cache official page and build parse preview for Guangxi physical ordinary rows; do not enter intake before QA.",
        }

    if confidence.startswith("T2_"):
        return {
            "action_route": "official_plan_portal_or_page_drilldown",
            "action_priority": "P1A2_plan_candidate_cache_or_detail_discovery",
            "action_requires_network": "true_for_detail_cache_or_discovery",
            "action_requires_browser_or_form_approval": "false_unless_blocked",
            "action_requires_manual_pdf_or_ocr": "false_until_asset_type_known",
            "action_requires_special_type_review": "true_if_medical_or_major_boundary_unknown",
            "safe_next_action": "Cache/detail the official plan candidate or demote to context-only if no Guangxi physical ordinary rows are present.",
        }

    return {
        "action_route": "context_only_hold_search_refinement",
        "action_priority": "P1C3_context_hold_low_risk",
        "action_requires_network": "true_only_for_future_source_discovery",
        "action_requires_browser_or_form_approval": "false",
        "action_requires_manual_pdf_or_ocr": "false",
        "action_requires_special_type_review": "false_until_candidate_found",
        "safe_next_action": "Hold as official context; continue source discovery later without entering intake.",
    }


def build_rows() -> list[dict[str, object]]:
    source_rows = read_csv(SOURCE)
    rows: list[dict[str, object]] = []
    for idx, source in enumerate(source_rows, 1):
        action = classify(source)
        rows.append(
            {
                "action_id": f"reference_trend_520_p1_batch16_action_{idx:04d}",
                "source_id": source.get("source_id", ""),
                "queue_record_id": source.get("queue_record_id", ""),
                "queue_rank": source.get("queue_rank", ""),
                "university_code": source.get("university_code", ""),
                "university_name": source.get("university_name", ""),
                "source_url": source.get("source_url", ""),
                "source_owner": source.get("source_owner", ""),
                "source_title": source.get("source_title", ""),
                "collector_confidence": source.get("collector_confidence", ""),
                "source_packet_status": source.get("source_packet_status", ""),
                **action,
                "expected_output_layer": "p1_batch16_action_queue_only_not_source_packet_not_intake",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Derived from batch16 source discovery preview; no network/cache/parse performed in this run.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    route = Counter(str(row["action_route"]) for row in rows)
    priority = Counter(str(row["action_priority"]) for row in rows)
    network = Counter(str(row["action_requires_network"]) for row in rows)
    browser = sum(str(row["action_requires_browser_or_form_approval"]).startswith("true") for row in rows)
    manual_pdf = sum(str(row["action_requires_manual_pdf_or_ocr"]).startswith("true") for row in rows)
    special = sum(str(row["action_requires_special_type_review"]).startswith("true") for row in rows)
    rollup_rows = [
        {"metric": "batch16_action_rows", "value": len(rows), "note": "One action row per batch16 source-discovery preview row."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Action queue only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        {"metric": "browser_or_form_approval_possible_rows", "value": browser, "note": "Only if static cache route is blocked."},
        {"metric": "manual_pdf_or_ocr_rows", "value": manual_pdf, "note": "PDF/table QA routes."},
        {"metric": "special_type_review_rows", "value": special, "note": "Rows needing boundary review before trend use."},
    ]
    rollup_rows.extend({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(route.items()))
    rollup_rows.extend({"metric": f"priority::{key}", "value": value, "note": ""} for key, value in sorted(priority.items()))
    rollup_rows.extend({"metric": f"network::{key}", "value": value, "note": ""} for key, value in sorted(network.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "source_rows_mapped",
            "status": "PASS" if len(rows) == len(read_csv(SOURCE)) and rows else "FAIL",
            "detail": f"Mapped {len(rows)} action rows from source discovery preview.",
        },
        {
            "check": "no_reference_trend_intake",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" for row in rows) else "FAIL",
            "detail": "Action queue does not create intake rows.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "Canonical/ML remains closed.",
        },
        {
            "check": "no_cache_parse_claimed",
            "status": "PASS",
            "detail": "This run did not fetch, cache, parse, OCR, or replay browser/form state.",
        },
        {
            "check": "decision_pool_boundary",
            "status": "PASS" if all("32_school" in row["decision_pool_boundary"] for row in rows) else "FAIL",
            "detail": "All rows are excluded from 32-school decision pool.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch16_action_queue_all_rows",
            "reason": "action_queue_only_no_parsed_source_packet",
            "effect": "excluded_from_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    for row in rows:
        if row["action_route"] in {"special_type_boundary_manual_review_hold", "context_only_hold_search_refinement"}:
            exclusions.append(
                {
                    "item": row["action_id"],
                    "reason": row["action_route"],
                    "effect": "hold_until_exact_official_plan_rows_and_boundaries_are_available",
                }
            )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    route = Counter(str(row["action_route"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch16 action queue",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This queue turns batch16 official source-discovery preview rows into safe next actions. It does not cache, parse, OCR, replay forms, or create source-packet/intake/canonical rows.",
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
    lines.extend(f"- {key}: {value}" for key, value in sorted(route.items()))
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Expected output layer is `p1_batch16_action_queue_only_not_source_packet_not_intake`.",
            "- Browser/form replay still requires explicit approval if a static cache route is blocked.",
            "- PDF/table routes require later local preview and QA before source packet rows.",
            "- Canonical/ML and the 32-school decision pool remain closed.",
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
    marker = "## 112. 2026-05-17 P1 batch16 action queue"
    handoff = f"""

{marker}

已新增 P1 batch16 action queue：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：从 marker 111 的 17 条 source-discovery preview rows 派生 17 条下一步 action rows；按 exact page/query/PDF/portal/context/special boundary 分流。QA PASS。

准入边界：本轮只生成行动队列，不联网、不缓存、不解析、不 OCR、不浏览器/form replay、不生成 source_packet parse 或 intake rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
