#!/usr/bin/env python3
"""Close out P0/P2/P3 PDF field-gap rows for YNUTCM and NJUCM.

This is a non-canonical, non-ML backoff artifact. It converts already-known PDF
parse outcomes into queue-row resolution records so the automation does not
keep treating the same "parse exists but fields are missing" state as fresh
work.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

QUEUE_STATUS = SEED_DIR / "reference_trend_520_plan_source_queue_status_reconciliation.csv"
PDF_QA = SEED_DIR / "reference_trend_520_next_batch_pdf_parse_qa_preview.csv"

OUT = SEED_DIR / "reference_trend_520_p0_pdf_gap_resolution_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_pdf_gap_resolution_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_pdf_gap_resolution_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_pdf_gap_resolution_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_pdf_gap_resolution_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

TARGET_UNIVERSITY_CODES = {"10680", "10315"}

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "source_packet_priority",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "source_url",
    "source_title",
    "raw_file_path",
    "raw_text_path",
    "pdf_parse_record_id",
    "pdf_qa_status",
    "contains_guangxi",
    "contains_physics",
    "extracted_guangxi_rows",
    "prior_reconciled_status",
    "resolution_status",
    "source_packet_status",
    "collector_confidence",
    "requires_manual_approval",
    "approval_required_for",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
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


def qa_by_university(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["university_code"]: row for row in rows if row.get("university_code") in TARGET_UNIVERSITY_CODES}


def resolution_for(pdf_row: dict[str, str]) -> dict[str, str]:
    code = pdf_row.get("university_code", "")
    qa_status = pdf_row.get("qa_status", "")
    if code == "10680":
        return {
            "resolution_status": "official_pdf_url_404_hold",
            "source_packet_status": "official_pdf_candidate_unusable_hold_for_official_source_relocation",
            "collector_confidence": "T2_official_pdf_candidate_but_404_no_parse",
            "requires_manual_approval": "false",
            "approval_required_for": "none_for_standard_official_research; approval_required_if_header_cookie_browser_or_form_state_needed",
            "next_action": "re_search_official_school_plan_page_pdf_or_xlsx; do_not_intake_existing_404_url",
            "evidence_note": "Official university-domain PDF candidate returned HTTP 404 during the prior PDF QA run; no Guangxi rows or plan fields were parsed.",
        }
    if code == "10315":
        return {
            "resolution_status": "parsed_no_guangxi_rows_rejected",
            "source_packet_status": "official_pdf_rejected_for_guangxi_scope_continue_official_source_search",
            "collector_confidence": "T1_official_pdf_parsed_but_wrong_province_scope",
            "requires_manual_approval": "false",
            "approval_required_for": "none_for_standard_official_research; approval_required_if_header_cookie_browser_or_form_state_needed",
            "next_action": "search_official_2025_out_of_province_plan_or_score_page_containing_guangxi_physics_rows; keep_current_pdf_as_rejected_clue_only",
            "evidence_note": "Official PDF parsed successfully, but province hits were outside Guangxi and extracted Guangxi rows were zero.",
        }
    return {
        "resolution_status": qa_status or "unclassified_pdf_gap_hold",
        "source_packet_status": "hold_for_manual_review",
        "collector_confidence": "T3_unclassified",
        "requires_manual_approval": "false",
        "approval_required_for": "",
        "next_action": "review_pdf_gap",
        "evidence_note": "",
    }


def build_rows() -> list[dict[str, object]]:
    queue_rows = read_csv(QUEUE_STATUS)
    pdf_rows = qa_by_university(read_csv(PDF_QA))

    rows: list[dict[str, object]] = []
    for row in queue_rows:
        code = row.get("university_code", "")
        if code not in TARGET_UNIVERSITY_CODES:
            continue
        if row.get("reconciled_status") != "source_packet_parse_exists_but_field_gaps_remain":
            continue

        pdf_row = pdf_rows.get(code, {})
        resolution = resolution_for(pdf_row)
        rows.append(
            {
                "record_id": f"reference_trend_520_p0_pdf_gap_resolution_{len(rows) + 1:04d}",
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "source_packet_priority": row.get("source_packet_priority", ""),
                "university_code": code,
                "university_name": row.get("university_name", ""),
                "group_pair_key": row.get("group_pair_key", ""),
                "group_code": row.get("group_code", ""),
                "rank_2024": row.get("rank_2024", ""),
                "rank_2025": row.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "source_url": pdf_row.get("source_url", ""),
                "source_title": pdf_row.get("source_title", ""),
                "raw_file_path": pdf_row.get("raw_file_path", ""),
                "raw_text_path": pdf_row.get("raw_text_path", ""),
                "pdf_parse_record_id": pdf_row.get("record_id", ""),
                "pdf_qa_status": pdf_row.get("qa_status", ""),
                "contains_guangxi": pdf_row.get("contains_guangxi", ""),
                "contains_physics": pdf_row.get("contains_physics", ""),
                "extracted_guangxi_rows": pdf_row.get("extracted_guangxi_rows", ""),
                "prior_reconciled_status": row.get("reconciled_status", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": "0",
                "calibration_eligible": "0",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                **resolution,
            }
        )
    return sorted(rows, key=lambda item: int(str(item["queue_rank"]) or "999999"))


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_school = Counter(str(row["university_name"]) for row in rows)
    by_priority = Counter(str(row["source_packet_priority"]) for row in rows)
    by_status = Counter(str(row["resolution_status"]) for row in rows)
    return [
        {"metric": "queue_records_resolved", "value": len(rows), "note": "All remain outside intake/trend/canonical/ML."},
        {"metric": "universities_covered", "value": len(by_school), "note": "|".join(sorted(by_school))},
        {"metric": "yunnan_tcm_rows", "value": by_school.get("云南中医药大学", 0), "note": "official PDF 404 hold"},
        {"metric": "nanjing_tcm_rows", "value": by_school.get("南京中医药大学", 0), "note": "official PDF parsed but no Guangxi rows"},
        {"metric": "p0_rows", "value": by_priority.get("P0_plan_source_packet_urgent", 0), "note": "urgent queue rows closed out as field-gap holds"},
        {"metric": "p1_rows", "value": by_priority.get("P1_plan_source_packet_high", 0), "note": "duplicate NJUCM queue group row preserved"},
        {"metric": "p2_rows", "value": by_priority.get("P2_plan_source_packet_medium", 0), "note": "duplicate YNUTCM/NJUCM queue group rows preserved"},
        {"metric": "p3_rows", "value": by_priority.get("P3_plan_source_packet_backlog", 0), "note": "duplicate NJUCM queue group row preserved"},
        {"metric": "official_pdf_url_404_hold_rows", "value": by_status.get("official_pdf_url_404_hold", 0), "note": "YNUTCM existing URL unusable"},
        {"metric": "parsed_no_guangxi_rows_rejected_rows", "value": by_status.get("parsed_no_guangxi_rows_rejected", 0), "note": "NJUCM PDF excluded for Guangxi scope"},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No eligible source packet rows produced."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No score/rank evidence from these PDFs."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    by_code = Counter(str(row["university_code"]) for row in rows)
    statuses = Counter(str(row["resolution_status"]) for row in rows)
    return [
        {"check": "input_queue_status_exists", "status": "PASS" if QUEUE_STATUS.exists() else "FAIL", "detail": str(QUEUE_STATUS.relative_to(ROOT))},
        {"check": "input_pdf_qa_exists", "status": "PASS" if PDF_QA.exists() else "FAIL", "detail": str(PDF_QA.relative_to(ROOT))},
        {"check": "target_queue_rows_preserved", "status": "PASS" if len(rows) == 6 else "FAIL", "detail": f"{len(rows)} rows"},
        {"check": "yunnan_404_hold_captured", "status": "PASS" if by_code.get("10680", 0) == 2 and statuses.get("official_pdf_url_404_hold", 0) == 2 else "FAIL", "detail": "YNUTCM queue rows should be 0005 and 0251"},
        {"check": "nanjing_no_guangxi_rejection_captured", "status": "PASS" if by_code.get("10315", 0) == 4 and statuses.get("parsed_no_guangxi_rows_rejected", 0) == 4 else "FAIL", "detail": "NJUCM queue rows should be 0008, 0172, 0256, 0416"},
        {"check": "all_rows_excluded_from_intake", "status": "PASS" if all(str(row["eligible_for_intake_preview"]) == "false" for row in rows) else "FAIL", "detail": "No source packet intake from current PDFs."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "0" and str(row["canonical_ml_entry_open"]) == "false" for row in rows) else "FAIL", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "queue_record_id": row["queue_record_id"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "source_url": row["source_url"],
            "exclusion_or_hold_reason": row["resolution_status"],
            "required_resolution": row["next_action"],
            "reference_trend_pool_eligible": row["reference_trend_pool_eligible"],
            "calibration_eligible": row["calibration_eligible"],
            "canonical_ml_entry_open": row["canonical_ml_entry_open"],
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], qa_rows: list[dict[str, str]]) -> None:
    pass_count = sum(1 for row in qa_rows if row["status"] == "PASS")
    fail_count = sum(1 for row in qa_rows if row["status"] != "PASS")
    yunnan = [row for row in rows if row["university_code"] == "10680"]
    nanjing = [row for row in rows if row["university_code"] == "10315"]
    content = f"""# Reference Trend 520 P0 PDF Gap Resolution Preview

Run date: {date.today().isoformat()}

This package closes out previously discovered PDF field gaps for 云南中医药大学 and 南京中医药大学. It does not search the web, does not open browser/header/form replay, and does not write canonical or ML inputs.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_gap_resolution_preview.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_rollup.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_qa.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_exclusion_log.csv`

## Coverage

- Queue rows resolved: {len(rows)}
- 云南中医药大学 rows: {len(yunnan)}. Current official PDF candidate is held because the prior QA run saw HTTP 404.
- 南京中医药大学 rows: {len(nanjing)}. Current official PDF is rejected for Guangxi trend use because it parsed successfully but contains no Guangxi rows.
- QA: {pass_count} pass / {fail_count} fail.

## Boundary

All rows remain `eligible_for_intake_preview=false`, `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`. The 32-school decision pool is untouched.

## Next Action

Continue official-source relocation for these schools only if useful: 云南中医药大学 needs a valid official plan page/PDF/XLSX, and 南京中医药大学 needs an official page or file containing Guangxi physical ordinary-batch rows. If the next route needs header/cookie/form/browser state, pause for approval.
"""
    DOC_OUT.write_text(content, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 81. 2026-05-16 P0 云南/南京中医药 PDF gap resolution preview"
    content = f"""

{marker}

已新增 P0 PDF gap resolution preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_gap_resolution_preview.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_rollup.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_qa.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_exclusion_log.csv`
- `docs/reference_trend_520_p0_pdf_gap_resolution_preview.md`

覆盖结果：将云南中医药大学 2 条队列行、南京中医药大学 4 条队列行从 `source_packet_parse_exists_but_field_gaps_remain` 收束为可审计 backoff。云南中医药大学当前官方 PDF 候选为 404 hold；南京中医药大学当前官方 PDF 已解析但无广西行，拒绝进入广西 reference trend。

准入边界：本轮不联网、不做浏览器/header/form replay、不写 canonical/ML、不并入 32 所 decision_pool。所有 {len(rows)} 行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一步只需继续重定位这两所的官方广西物理普通批计划/分数来源。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    qa_rows = build_qa(rows)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, build_rollup(rows), ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(
        EXCLUSION_OUT,
        build_exclusions(rows),
        [
            "record_id",
            "queue_record_id",
            "university_name",
            "group_code",
            "source_url",
            "exclusion_or_hold_reason",
            "required_resolution",
            "reference_trend_pool_eligible",
            "calibration_eligible",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    write_doc(rows, qa_rows)
    write_handoff(rows)
    print(f"wrote {len(rows)} PDF gap resolution rows")
    print(f"preview: {OUT}")
    print(f"qa: {QA_OUT}")


if __name__ == "__main__":
    main()
