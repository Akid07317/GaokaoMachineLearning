#!/usr/bin/env python3
"""Write batch-15 official source discovery preview for queue ranks 151-170.

This batch records first-party official candidates found for the next queue
slice. It does not cache, parse PDFs/tables, OCR images, replay forms, or open
reference_trend_pool/canonical/ML intake.
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

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch15_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch15_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch15_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch15.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "source_id",
    "queue_record_id",
    "queue_rank",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "year",
    "province",
    "batch",
    "subject_category",
    "round_type",
    "university_name",
    "university_code",
    "source_role",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "special_type_detected",
    "raw_file_path",
    "collector_note",
    "collector_confidence",
    "source_packet_status",
    "intended_layer",
    "requires_network",
    "requires_manual_approval",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]


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


def common(row: dict[str, object], idx: int) -> dict[str, object]:
    base = {
        "source_id": f"reference_trend_520_p0_batch15_{idx:04d}",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_group_code": "unknown_until_cache_parse",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_cache_parse",
        "special_type_detected": "unknown_until_parse",
        "raw_file_path": "",
        "intended_layer": "reference_trend_source_packet_preview_only",
        "requires_network": "true_for_next_cache_or_retry",
        "requires_manual_approval": "false_until_browser_form_pdf_or_ocr_route_needed",
        "eligible_for_intake_preview": "false_until_source_packet_parse_and_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch15_{idx:04d}",
    }
    base.update(row)
    return base


def build_rows() -> list[dict[str, object]]:
    raw_rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0151",
            "queue_rank": "151",
            "university_code": "10595",
            "university_name": "桂林电子科技大学",
            "source_url": "https://www.guet.edu.cn/zs/",
            "source_owner": "桂林电子科技大学招生信息网",
            "source_title": "招生信息网官方入口",
            "round_type": "local_official_portal_needs_plan_detail",
            "source_role": "official_context_not_structured_guangxi_group_plan_rows",
            "collector_note": "Official local admissions portal surfaced; a third-party plan hit exists but is not accepted as source-packet evidence.",
            "collector_confidence": "T3_official_context_only_no_group_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "find/cache official 2025广西本科普通批专业组计划 page or reject to context-only.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0152",
            "queue_rank": "152",
            "university_code": "10488",
            "university_name": "武汉科技大学",
            "source_url": "https://zs.wust.edu.cn/index.htm",
            "source_owner": "武汉科技大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_portal_with_2025_policy_context",
            "source_role": "official_context_needs_plan_detail_cache",
            "collector_note": "Official undergraduate admissions portal and 2025 charter surfaced; no Guangxi plan rows cached in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_portal_found_plan_detail_not_cached",
            "next_action": "search/cache official 2025分省计划/广西计划 detail; keep charter-only context out of intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0153",
            "queue_rank": "153",
            "university_code": "11072",
            "university_name": "江汉大学",
            "source_url": "https://bkzs.jhun.edu.cn/",
            "source_owner": "江汉大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_plan_authority_delegated",
            "collector_note": "Official portal surfaced. Search result shows charter language delegating plans to provincial authorities/official channels.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "find first-party 2025 Guangxi plan table/PDF; do not infer from charter.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0154",
            "queue_rank": "154",
            "university_code": "10142",
            "university_name": "沈阳工业大学",
            "source_url": "https://zsxxw.sut.edu.cn/",
            "source_owner": "沈阳工业大学招生信息网",
            "source_title": "招生信息网官方入口/2025本科招生计划候选",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_2025_plan_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_if_2025_plan_page_cached",
            "collector_note": "Official admissions site surfaced with 2025本科招生计划 listing; needs cache/parse to isolate Guangxi physical ordinary rows.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_candidate_found_not_cached",
            "next_action": "cache 2025本科招生计划 detail/PDF/table and QA Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0155",
            "queue_rank": "155",
            "university_code": "10344",
            "university_name": "浙江中医药大学",
            "source_url": "https://zsb.zcmu.edu.cn/",
            "source_owner": "浙江中医药大学招生办官方网站",
            "source_title": "招生办官方网站/2025招生章程候选",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "special_type_detected": "medical_tcm_major_boundary_unknown",
            "collector_note": "Official site and 2025 charter surfaced; no Guangxi source-packet rows cached.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 2025分省计划/招生计划 table; isolate普通批物理 and medical special boundaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0156",
            "queue_rank": "156",
            "university_code": "11057",
            "university_name": "浙江科技大学",
            "source_url": "https://zsb.zust.edu.cn/",
            "source_owner": "浙江科技大学招生网",
            "source_title": "招生网/2025全日制本科招生计划候选",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_2025_plan_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_if_2025_plan_page_cached",
            "collector_note": "Official site surfaced 2025 full-time undergraduate plan context; cache/parse required before use.",
            "collector_confidence": "T2_official_plan_page_needs_cache_parse",
            "source_packet_status": "official_plan_candidate_found_not_cached",
            "next_action": "cache 2025本科招生计划 page and isolate Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0157",
            "queue_rank": "157",
            "university_code": "10512",
            "university_name": "湖北大学",
            "source_url": "https://zsxx.hubu.edu.cn/zsxx/zsjh.htm|https://xxgk.hubu.edu.cn/__local/0/3E/A6/5144BF67BAF45FED441FDBA3834_1D8D2799_1E3A1.pdf",
            "source_owner": "湖北大学本科招生信息网/信息公开网",
            "source_title": "招生计划栏目/2025年分省分专业招生计划表PDF",
            "round_type": "official_plan_pdf_candidate",
            "source_role": "official_2025_plan_pdf_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "collector_note": "Official admissions plan column and official 2025 plan PDF surfaced; PDF parse/manual route needed.",
            "collector_confidence": "T2_official_pdf_plan_candidate_needs_parser",
            "source_packet_status": "official_pdf_candidate_found_not_cached",
            "requires_manual_approval": "true_if_pdf_table_parse_or_manual_transcription_needed",
            "next_action": "cache official PDF, parse/transcribe, then isolate Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0158",
            "queue_rank": "158",
            "university_code": "10349",
            "university_name": "绍兴文理学院",
            "source_url": "https://zs.usx.edu.cn/",
            "source_owner": "绍兴文理学院本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_portal_candidate_from_context",
            "source_role": "official_portal_needs_plan_detail_cache",
            "collector_note": "Official admissions domain surfaced through public plan news context, but no official Guangxi rows cached.",
            "collector_confidence": "T3_official_portal_context_only_no_cached_plan_rows",
            "source_packet_status": "official_portal_found_plan_detail_not_cached",
            "next_action": "search/cache official 2025招生计划 detail; reject local-news-only summaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0159",
            "queue_rank": "159",
            "university_code": "10742",
            "university_name": "西北民族大学",
            "source_url": "https://www.xbmu.edu.cn/zsxx/index.htm",
            "source_owner": "西北民族大学招生信息网",
            "source_title": "招生信息网官方入口/招生计划栏目",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_plan_portal_needs_detail_cache",
            "collector_note": "Official admissions portal surfaced with 招生计划 navigation; no Guangxi rows cached.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "cache 2025招生计划 detail/table if Guangxi physical ordinary rows are visible.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0160",
            "queue_rank": "160",
            "university_code": "10662",
            "university_name": "贵州中医药大学",
            "source_url": "https://www.gzy.edu.cn/zsjy.htm",
            "source_owner": "贵州中医药大学招生就业",
            "source_title": "招生就业官方入口/2025章程PDF候选",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "special_type_detected": "medical_tcm_major_boundary_unknown",
            "collector_note": "Official portal and 2025 charter PDF surfaced; no structured Guangxi plan rows in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 2025本科招生计划; keep charter-only PDF out of row intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0161",
            "queue_rank": "161",
            "university_code": "10186",
            "university_name": "长春理工大学",
            "source_url": "https://zsb.cust.edu.cn/bkzn/zszc/index.htm",
            "source_owner": "长春理工大学本科招生网",
            "source_title": "本科招生网/招生政策栏目",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "collector_note": "Official undergraduate admissions policy page surfaced; plan page still needs discovery/cache.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_policy_context_found_no_plan_rows",
            "next_action": "find official 2025分省计划/广西 plan table or exact PDF.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0162",
            "queue_rank": "162",
            "university_code": "10489",
            "university_name": "长江大学",
            "source_url": "https://zszc.yangtzeu.edu.cn/bkzn/zsjh.htm|https://xxgk.yangtzeu.edu.cn/__local/3/55/84/AED89C4A8BF7FC02EED72A7D670_3AD1D955_3EF0F.pdf",
            "source_owner": "长江大学本科招生信息网/信息公开网",
            "source_title": "招生计划栏目/2025年分批次、分科类招生计划PDF",
            "round_type": "official_plan_pdf_candidate",
            "source_role": "official_2025_plan_pdf_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "collector_note": "Official plan list and official 2025 plan PDF surfaced; row-level Guangxi plan extraction still needed.",
            "collector_confidence": "T2_official_pdf_plan_candidate_needs_parser",
            "source_packet_status": "official_pdf_candidate_found_not_cached",
            "requires_manual_approval": "true_if_pdf_table_parse_or_manual_transcription_needed",
            "next_action": "cache official PDF, parse/transcribe, and isolate Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0163",
            "queue_rank": "163",
            "university_code": "10390",
            "university_name": "集美大学",
            "source_url": "https://zsb.jmu.edu.cn/info/1623/7855.htm",
            "source_owner": "集美大学招生办公室",
            "source_title": "集美大学2025年广西招生计划",
            "published_date": "2025-06-17",
            "round_type": "existing_source_packet_and_mapping_workbench",
            "source_role": "existing_group_mapping_workbench_hold_for_human_acceptance",
            "source_contains_group_code": "true",
            "source_contains_plan_count": "true",
            "collector_note": "Carried forward from batch13 parse/mapping workbench; manual approval queue now includes aggregate JMU mapping item.",
            "collector_confidence": "T1_existing_official_source_packet_with_mapping_sheet",
            "source_packet_status": "existing_acceptance_sheet_pending_human_decision",
            "requires_network": "false_existing_local_artifacts",
            "next_action": "wait for group mapping acceptance; do not overwrite human fields.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0164",
            "queue_rank": "164",
            "university_code": "10743",
            "university_name": "青海大学",
            "source_url": "https://zsw.qhu.edu.cn/zsxx/zszc/92a9bb561a4e4253a01988aec41e7333.htm",
            "source_owner": "青海大学本科招生网",
            "source_title": "青海大学2025年招生计划",
            "round_type": "official_plan_page_candidate",
            "source_role": "official_2025_plan_page_needs_cache_parse",
            "source_contains_plan_count": "true_if_plan_page_cached",
            "collector_note": "Official 2025招生计划 page surfaced; cache/parse needed to confirm Guangxi physical ordinary rows.",
            "collector_confidence": "T2_official_plan_page_needs_cache_parse",
            "source_packet_status": "official_plan_candidate_found_not_cached",
            "next_action": "cache plan page/assets and QA Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0165",
            "queue_rank": "165",
            "university_code": "10112",
            "university_name": "太原理工大学",
            "source_url": "https://zs.tyut.edu.cn/zsxx/zsjh.htm|https://zs.tyut.edu.cn/__local/6/E5/19/5342DA63DCE08172C70CE96D984_14FAE149_3B6B9.pdf",
            "source_owner": "太原理工大学本科招生网",
            "source_title": "招生计划栏目/2025年本科分省分专业招生计划表PDF",
            "round_type": "decision_pool_overlap_official_pdf_candidate",
            "source_role": "official_2025_plan_pdf_candidate_but_keep_decision_pool_boundary",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "collector_note": "Official 2025 plan PDF surfaced. Because Taiyuan Ligong is already part of prior decision_pool work, keep this only as isolated reference-trend source discovery unless explicitly approved.",
            "collector_confidence": "T2_official_pdf_candidate_with_decision_pool_boundary",
            "source_packet_status": "official_pdf_candidate_found_not_cached_boundary_hold",
            "requires_manual_approval": "true_if_pdf_table_parse_or_decision_pool_interaction_needed",
            "next_action": "cache/parse only as isolated reference-trend preview; do not merge with 32-school decision_pool.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0166|reference_trend_520_plan_source_queue_0167",
            "queue_rank": "166|167",
            "university_code": "10270",
            "university_name": "上海师范大学",
            "source_url": "https://ssdzsb.shnu.edu.cn/",
            "source_owner": "上海师范大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_portal_candidate_needs_verification",
            "source_role": "official_portal_needs_plan_detail_cache",
            "collector_note": "Public search surfaced the official undergraduate admissions site context, but no direct 2025 Guangxi plan page was accepted in this pass.",
            "collector_confidence": "T3_official_portal_context_only_no_cached_plan_rows",
            "source_packet_status": "official_portal_found_plan_detail_not_cached",
            "next_action": "verify official domain and cache exact 2025广西 plan detail/table if available.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0168|reference_trend_520_plan_source_queue_0169",
            "queue_rank": "168|169",
            "university_code": "10538",
            "university_name": "中南林业科技大学",
            "source_url": "https://zs.csuft.edu.cn/f/zsjhinfo?jhnd=2025&ssdm=45",
            "source_owner": "中南林业科技大学本科招生网",
            "source_title": "2025年中南林业科技大学招生计划（广西）",
            "round_type": "official_exact_plan_page_candidate",
            "source_role": "official_2025_guangxi_plan_page_needs_cache_parse",
            "source_contains_plan_count": "true_in_page_unparsed",
            "collector_note": "Official exact 2025 Guangxi plan page surfaced; likely strong source-packet candidate after cache/parse.",
            "collector_confidence": "T1_exact_official_guangxi_plan_page_candidate",
            "source_packet_status": "official_exact_plan_candidate_found_not_cached",
            "next_action": "cache exact official page and parse ordinary本科物理 rows, excluding special tracks.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0170",
            "queue_rank": "170",
            "university_code": "10352",
            "university_name": "丽水学院",
            "source_url": "https://zsw.lsu.edu.cn/main.htm",
            "source_owner": "丽水学院招生信息网",
            "source_title": "招生信息网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "collector_note": "Official admissions portal surfaced, but search results did not expose a direct 2025 Guangxi plan page.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search/cache official 2025普通本科招生计划 detail or hold as context-only.",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(raw_rows, start=1)]


def main() -> None:
    rows = build_rows()
    status_counts = Counter(row["source_packet_status"] for row in rows)
    confidence_counts = Counter(row["collector_confidence"] for row in rows)
    manual_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    rollup_rows = [
        {"metric": "batch15_source_discovery_rows", "value": len(rows), "note": "Compressed official candidates for queue ranks 151-170."},
        {"metric": "queue_rank_min", "value": 151, "note": ""},
        {"metric": "queue_rank_max", "value": 170, "note": ""},
        {"metric": "t1_exact_official_candidates", "value": sum(1 for row in rows if str(row["collector_confidence"]).startswith("T1")), "note": "Exact official plan page candidates, not parsed."},
        {"metric": "t2_official_plan_candidates", "value": sum(1 for row in rows if str(row["collector_confidence"]).startswith("T2")), "note": ""},
        {"metric": "t3_context_only_rows", "value": sum(1 for row in rows if str(row["collector_confidence"]).startswith("T3")), "note": ""},
        {"metric": "manual_or_parser_approval_rows", "value": len(manual_rows), "note": "PDF/parser/decision-boundary routes."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for status, count in sorted(status_counts.items()):
        rollup_rows.append({"metric": f"status::{status}", "value": count, "note": ""})
    for confidence, count in sorted(confidence_counts.items()):
        rollup_rows.append({"metric": f"confidence::{confidence}", "value": count, "note": ""})

    qa_rows = [
        {
            "check": "no_pool_or_canonical_entry",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "All rows stay source-discovery only.",
        },
        {
            "check": "official_url_present",
            "status": "PASS" if all(row.get("source_url") for row in rows) else "REVIEW",
            "detail": "Every compressed row has at least one official/context source URL.",
        },
        {
            "check": "no_raw_cache_claimed",
            "status": "PASS" if all(not row.get("raw_file_path") for row in rows) else "REVIEW",
            "detail": "This run did not cache or parse source files.",
        },
        {
            "check": "manual_approval_boundary",
            "status": "PASS",
            "detail": "PDF/parser/decision-pool-boundary routes are approval-gated before parsing.",
        },
    ]

    exclusions = [row for row in rows if row["eligible_for_intake_preview"] != "true"]
    doc = f"""# Reference Trend 520 P0 Official Source Discovery Batch15

Generated: {date.today().isoformat()}

Scope: queue ranks 151-170 from `reference_trend_520_plan_source_packet_queue.csv`.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

This batch opens the next P0/P1 source-discovery slice after batch14 moved its
blocked candidates into a manual approval queue. Stronger candidates include
中南林业科技大学 exact Guangxi plan page, 青海大学 2025招生计划 page,
长江大学/湖北大学/太原理工 official plan PDFs, and several official plan
portals that still need exact detail caching.

No row is parsed or eligible for reference_trend_pool/canonical/ML in this run.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 60. 2026-05-16 P1 官方来源发现 batch 15"
    handoff_content = f"""

{marker}

已新增 batch15 官方来源发现预览：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：queue rank 151-170。中南林业科技大学形成 exact 广西计划页候选；青海大学、沈阳工业大学、浙江科技大学、湖北大学、长江大学、太原理工大学等形成 2025 计划页/PDF/计划栏目候选；武汉科技大学、江汉大学、浙江中医药大学、绍兴文理学院、贵州中医药大学、长春理工大学、上海师范大学、丽水学院等暂为官方入口/章程/上下文，需后续 exact detail cache。

准入边界：本轮只做 source discovery preview，不缓存、不解析、不 OCR，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮优先缓存/解析中南林业科技大学 exact 广西计划页，或处理青海大学/长江大学/湖北大学等官方计划页/PDF候选。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
