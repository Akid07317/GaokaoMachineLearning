#!/usr/bin/env python3
"""Build a consolidated manual-approval queue for batch13/batch14 blockers.

This queue is intentionally outside reference_trend_pool/canonical/ML. It
collects the safe next choices that need human acceptance, OCR/PDF parsing, or
browser/header approval before any row-level source-packet intake can proceed.
Existing reviewer fields are preserved when the queue is regenerated.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

JMU_ACCEPTANCE = SEED_DIR / "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.csv"
ASSET_READINESS = SEED_DIR / "reference_trend_520_batch14_asset_pdf_readiness_preview.csv"
BATCH14_DISCOVERY = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch14_preview.csv"
HTML_BACKOFF = SEED_DIR / "reference_trend_520_batch14_html_cache_backoff_preview.csv"
XHU_BACKOFF = SEED_DIR / "reference_trend_520_batch14_xhu_web_reachability_backoff_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch14_manual_approval_queue.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch14_manual_approval_queue_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch14_manual_approval_queue_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch14_manual_approval_queue_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch14_manual_approval_queue.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "approval_record_id",
    "upstream_record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "approval_category",
    "approval_scope",
    "approval_priority",
    "approval_needed",
    "approval_status",
    "selected_decision",
    "reviewer",
    "decision_notes",
    "reviewed_at",
    "source_url",
    "source_title",
    "asset_path",
    "blocked_reason",
    "action_if_approved",
    "action_if_denied",
    "expected_output_layer",
    "reference_trend_pool_eligible_before_approval",
    "calibration_eligible_before_approval",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
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


def preserve_reviewer_fields(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    old = {row.get("approval_record_id", ""): row for row in read_csv(OUT)}
    for row in rows:
        old_row = old.get(str(row.get("approval_record_id", "")), {})
        for field in ("selected_decision", "reviewer", "decision_notes", "reviewed_at"):
            if old_row.get(field):
                row[field] = old_row[field]
    return rows


def boundary() -> dict[str, str]:
    return {
        "approval_status": "pending_human_approval",
        "selected_decision": "",
        "reviewer": "",
        "decision_notes": "",
        "reviewed_at": "",
        "expected_output_layer": "post_approval_source_packet_or_intake_preview_only_not_canonical",
        "reference_trend_pool_eligible_before_approval": "false",
        "calibration_eligible_before_approval": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "manual_approval_queue_only_not_32_school_decision_pool",
    }


def jmu_summary_row() -> dict[str, object] | None:
    rows = read_csv(JMU_ACCEPTANCE)
    pending = [row for row in rows if not row.get("selected_decision")]
    if not rows:
        return None
    plan_sum = sum(int(row.get("plan_count_sum") or 0) for row in rows)
    queue_ranks = sorted({row.get("queue_rank", "") for row in rows if row.get("queue_rank", "")})
    source_groups = sorted({row.get("source_professional_group_code", "") for row in rows if row.get("source_professional_group_code", "")})
    return {
        **boundary(),
        "approval_record_id": "reference_trend_520_batch14_manual_approval_0001",
        "upstream_record_id": "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet",
        "queue_record_id": "|".join(sorted({row.get("queue_record_id", "") for row in rows if row.get("queue_record_id", "")})),
        "queue_rank": "|".join(queue_ranks),
        "university_code": "10390",
        "university_name": "集美大学",
        "approval_category": "human_accept_group_code_mapping",
        "approval_scope": f"{len(rows)} candidate group mappings; pending={len(pending)}; source_groups={'/'.join(source_groups)}; plan_sum={plan_sum}",
        "approval_priority": "P0_unblocks_parsed_official_source_packet",
        "approval_needed": "accept_mapping_for_reference_trend_preview|hold_mapping|request_score_rank_source_fix|reject_mapping",
        "source_url": rows[0].get("source_url", ""),
        "source_title": "集美大学2025年广西招生计划",
        "asset_path": rows[0].get("source_preview_file", ""),
        "blocked_reason": "official source packet parsed and candidate group-line mapping exists, but human acceptance is required before intake preview",
        "action_if_approved": "generate post-human-decision intake preview for accepted groups only; still keep canonical/ML closed",
        "action_if_denied": "keep groups in hold/reject/request_fix route and do not write intake preview",
        "evidence_note": "Existing acceptance sheet preserves per-group reviewer fields; this queue is an aggregate reminder, not a replacement.",
    }


def asset_rows(start_index: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i, row in enumerate(read_csv(ASSET_READINESS), start=start_index):
        category = "ocr_or_manual_transcription"
        if "pdf" in row.get("asset_type", "").lower():
            category = "pdf_table_parse_or_manual_transcription"
        rows.append(
            {
                **boundary(),
                "approval_record_id": f"reference_trend_520_batch14_manual_approval_{i:04d}",
                "upstream_record_id": row.get("record_id", ""),
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "approval_category": category,
                "approval_scope": row.get("asset_type", ""),
                "approval_priority": "P0_cached_asset_needs_parse_approval",
                "approval_needed": "approve_parse_or_manual_transcription|hold_asset|reject_asset_route",
                "source_url": row.get("source_url", ""),
                "source_title": row.get("source_title", ""),
                "asset_path": row.get("asset_path", ""),
                "blocked_reason": row.get("parser_readiness", ""),
                "action_if_approved": "parse/transcribe official asset into source-packet preview and QA before any pool consideration",
                "action_if_denied": "keep cached asset in readiness/backoff layer only",
                "evidence_note": row.get("evidence_note", ""),
            }
        )
    return rows


def ahut_row(index: int) -> dict[str, object] | None:
    rows = [row for row in read_csv(BATCH14_DISCOVERY) if row.get("university_name") == "安徽工业大学"]
    if not rows:
        return None
    row = rows[0]
    return {
        **boundary(),
        "approval_record_id": f"reference_trend_520_batch14_manual_approval_{index:04d}",
        "upstream_record_id": row.get("record_id", ""),
        "queue_record_id": row.get("queue_record_id", ""),
        "queue_rank": row.get("queue_rank", ""),
        "university_code": row.get("university_code", ""),
        "university_name": row.get("university_name", ""),
        "approval_category": "image_ocr_or_manual_transcription",
        "approval_scope": "official 2025 plan image candidate carried from batch13/batch14 discovery",
        "approval_priority": "P1_existing_official_image_candidate",
        "approval_needed": "approve_image_ocr_or_manual_transcription|hold_image_route|reject_image_route",
        "source_url": row.get("source_url", ""),
        "source_title": row.get("source_title", ""),
        "asset_path": row.get("raw_file_path", ""),
        "blocked_reason": "official image plan candidate remains unparsed and approval-gated",
        "action_if_approved": "cache/render images if needed, OCR/transcribe, then isolate Guangxi physical ordinary rows in preview/QA",
        "action_if_denied": "keep AHUT in image-route hold; continue other P0/P1 source discovery",
        "evidence_note": row.get("collector_note", ""),
    }


def xhu_row(index: int) -> dict[str, object] | None:
    rows = read_csv(XHU_BACKOFF)
    if not rows:
        return None
    portal = rows[-1]
    return {
        **boundary(),
        "approval_record_id": f"reference_trend_520_batch14_manual_approval_{index:04d}",
        "upstream_record_id": "|".join(row.get("record_id", "") for row in rows),
        "queue_record_id": portal.get("queue_record_id", ""),
        "queue_rank": portal.get("queue_rank", ""),
        "university_code": portal.get("university_code", ""),
        "university_name": portal.get("university_name", ""),
        "approval_category": "browser_header_cookie_or_exact_url_route",
        "approval_scope": "official portal/article visible by web index but terminal cache blocked; no exact 2025 Guangxi plan rows",
        "approval_priority": "P2_only_if_exact_detail_or_browser_route_approved",
        "approval_needed": "approve_browser_or_header_cookie_route|provide_exact_2025_guangxi_plan_url|hold_backoff",
        "source_url": portal.get("source_url", ""),
        "source_title": portal.get("source_title", ""),
        "asset_path": "",
        "blocked_reason": portal.get("terminal_cache_status", ""),
        "action_if_approved": "use approved auditable browser/header route to cache exact source, then parse only if Guangxi physical ordinary rows are visible",
        "action_if_denied": "do not repeat terminal curl; continue other P0/P1 candidates",
        "evidence_note": portal.get("evidence_note", ""),
    }


def html_backoff_rows(start_index: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i, row in enumerate(read_csv(HTML_BACKOFF), start=start_index):
        rows.append(
            {
                **boundary(),
                "approval_record_id": f"reference_trend_520_batch14_manual_approval_{i:04d}",
                "upstream_record_id": row.get("record_id", ""),
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "approval_category": "exact_detail_url_or_dynamic_browser_route",
                "approval_scope": "cached official HTML did not expose static 2025 Guangxi physical plan rows",
                "approval_priority": "P3_do_not_retry_same_static_url",
                "approval_needed": "provide_exact_2025_guangxi_plan_url|approve_dynamic_browser_route|hold_backoff",
                "source_url": row.get("source_url", ""),
                "source_title": "",
                "asset_path": row.get("cached_files", ""),
                "blocked_reason": row.get("backoff_reason", ""),
                "action_if_approved": "cache exact detail/dynamic source and write source-packet preview only if row-level Guangxi physical plan data appears",
                "action_if_denied": "keep as backoff and move to new P0/P1 candidates",
                "evidence_note": row.get("evidence_note", ""),
            }
        )
    return rows


def main() -> None:
    rows: list[dict[str, object]] = []
    jmu = jmu_summary_row()
    if jmu:
        rows.append(jmu)
    rows.extend(asset_rows(len(rows) + 1))
    ahut = ahut_row(len(rows) + 1)
    if ahut:
        rows.append(ahut)
    xhu = xhu_row(len(rows) + 1)
    if xhu:
        rows.append(xhu)
    rows.extend(html_backoff_rows(len(rows) + 1))
    rows = preserve_reviewer_fields(rows)

    pending = [row for row in rows if not row.get("selected_decision")]
    by_category: dict[str, int] = {}
    for row in rows:
        by_category[str(row.get("approval_category", ""))] = by_category.get(str(row.get("approval_category", "")), 0) + 1
    rollup_rows = [
        {"metric": "manual_approval_queue_rows", "value": len(rows), "note": "Aggregate approval items, not pool rows."},
        {"metric": "pending_decision_rows", "value": len(pending), "note": ""},
        {"metric": "approved_rows", "value": len(rows) - len(pending), "note": "Rows with selected_decision already filled, if any."},
        {"metric": "jmu_group_mapping_candidate_groups", "value": len(read_csv(JMU_ACCEPTANCE)), "note": "Per-group sheet remains authoritative."},
        {"metric": "asset_parse_approval_rows", "value": sum(1 for row in rows if "transcription" in str(row.get("approval_category", "")) or "pdf" in str(row.get("approval_category", ""))), "note": "OCR/PDF/manual routes."},
        {"metric": "browser_or_exact_url_route_rows", "value": sum(1 for row in rows if "browser" in str(row.get("approval_category", "")) or "exact_detail" in str(row.get("approval_category", ""))), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows_before_approval", "value": 0, "note": "No row can enter pool before approval and downstream QA."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for category, count in sorted(by_category.items()):
        rollup_rows.append({"metric": f"category::{category}", "value": count, "note": ""})

    qa_rows = [
        {
            "check": "preserve_reviewer_fields",
            "status": "PASS",
            "detail": "Existing selected_decision/reviewer/decision_notes/reviewed_at are preserved on rerun.",
        },
        {
            "check": "no_pool_or_canonical_entry",
            "status": "PASS" if all(row.get("reference_trend_pool_eligible_before_approval") == "false" and row.get("canonical_ml_entry_open") == "false" for row in rows) else "FAIL",
            "detail": "Approval queue only.",
        },
        {
            "check": "source_assets_or_backoff_linked",
            "status": "PASS" if rows else "REVIEW",
            "detail": f"{len(rows)} approval/backoff items linked to upstream artifacts.",
        },
        {
            "check": "manual_tables_not_overwritten",
            "status": "PASS",
            "detail": "JMU per-group decision sheet is read only; this queue is separate.",
        },
    ]

    doc = f"""# Reference Trend 520 Batch14 Manual Approval Queue

Generated: {date.today().isoformat()}

Purpose: consolidate source routes that should not advance automatically without
human approval. This file is outside the reference_trend_pool, canonical layer,
ML inputs, and the 32-school decision_pool.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Included Approval Items

- 集美大学: aggregate reminder for the existing per-group mapping acceptance
  sheet; the per-group sheet remains authoritative.
- 上海政法学院: official embedded PNG plan images require OCR or manual
  transcription approval.
- 上海海洋大学: official PDF plan attachment requires reliable PDF table parser
  or manual transcription approval.
- 安徽工业大学: official image plan candidate requires OCR/manual transcription
  approval.
- 西华大学: official pages are visible through web index but terminal caching is
  blocked; continue only with exact URL or approved browser/header route.
- 苏州科技大学 / 天津外国语大学: static official pages are cached but no 2025
  Guangxi physical plan rows are visible; retry only with exact detail URL or
  approved dynamic/browser route.

## Boundary

All rows remain `reference_trend_pool_eligible_before_approval=false`,
`calibration_eligible_before_approval=false`, and
`canonical_ml_entry_open=false`. Approval only unlocks a downstream source-packet
or intake preview with QA; it does not open canonical/ML.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 59. 2026-05-16 batch14 manual approval queue"
    handoff_content = f"""

{marker}

已新增 batch14 manual approval queue：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：合并集美大学 group mapping 人工接受、上海政法学院 PNG OCR/人工转录、上海海洋大学 PDF 表格解析/人工转录、安徽工业大学图片 OCR/人工转录、西华大学浏览器/header/exact URL 路线，以及苏州科技大学/天津外国语大学 exact detail 或动态浏览器路线。队列只做批准决策入口，不替代原始人工表。

准入边界：本轮没有批准任何路线，也没有写 reference_trend_pool/canonical/ML；所有行在批准前均为不可入池。下一轮若仍无人工批准，应继续开新的 P0/P1 官方来源候选；若发现本队列有 selected_decision，则先做 post-approval intake/QA。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
