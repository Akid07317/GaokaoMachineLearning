#!/usr/bin/env python3
"""Write P1 batch-16 official source discovery preview for queue ranks 171-190.

This records first-party official candidates found for the next queue slice. It
does not cache, parse PDFs/tables, OCR images, replay forms, or open
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

OUT = SEED_DIR / "reference_trend_520_p1_official_source_discovery_batch16_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p1_official_source_discovery_batch16_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p1_official_source_discovery_batch16_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p1_official_source_discovery_batch16_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p1_official_source_discovery_batch16.md"
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
        "source_id": f"reference_trend_520_p1_batch16_{idx:04d}",
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
        "record_id": f"reference_trend_520_p1_batch16_{idx:04d}",
    }
    base.update(row)
    return base


def build_rows() -> list[dict[str, object]]:
    raw_rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0171",
            "queue_rank": "171",
            "university_code": "10126",
            "university_name": "内蒙古大学",
            "source_url": "https://xxgk.imu.edu.cn/info/1003/1874.htm",
            "source_owner": "内蒙古大学信息公开网",
            "source_title": "内蒙古大学2024—2025学年信息公开工作报告",
            "round_type": "official_policy_context_no_plan_rows",
            "source_role": "official_context_confirms_school_plan_disclosure_channels",
            "collector_note": "Official information-disclosure report says plans are published through education authorities and school admissions office channels; no Guangxi physical plan rows cached.",
            "collector_confidence": "T3_official_policy_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_policy_context_found_no_plan_rows",
            "next_action": "find/cache first-party 2025 Guangxi plan table or keep as context-only.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0172",
            "queue_rank": "172",
            "university_code": "10315",
            "university_name": "南京中医药大学",
            "source_url": "https://zs.njucm.edu.cn/",
            "source_owner": "南京中医药大学本科招生网",
            "source_title": "本科招生网/2025年本科招生计划入口候选",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_plan_portal_needs_detail_cache",
            "source_contains_plan_count": "true_if_2025_plan_detail_cached",
            "special_type_detected": "medical_tcm_major_boundary_unknown",
            "collector_note": "Official admissions portal surfaced with 2025 undergraduate plan context; cache/detail parse required before Guangxi use.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "cache the official 2025本科招生计划 detail and isolate Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0173",
            "queue_rank": "173",
            "university_code": "10555",
            "university_name": "南华大学",
            "source_url": "https://slxy.usc.edu.cn/zsjy/zsxx.htm",
            "source_owner": "南华大学数理学院",
            "source_title": "招生信息/南华大学2025年招生计划（本科普通批）候选",
            "round_type": "official_college_plan_listing_candidate",
            "source_role": "official_2025_plan_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_if_detail_cached",
            "collector_note": "Official college listing exposes a 2025本科普通批招生计划 candidate; needs cache/parse and university-wide authority check.",
            "collector_confidence": "T2_official_plan_page_needs_cache_parse",
            "source_packet_status": "official_plan_candidate_found_not_cached",
            "next_action": "cache candidate detail page and verify whether it covers queue group 101 or only college-level majors.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0174",
            "queue_rank": "174",
            "university_code": "10403",
            "university_name": "南昌大学",
            "source_url": "https://zjc.ncu.edu.cn/",
            "source_owner": "南昌大学招生与就业工作处",
            "source_title": "招生与就业工作处官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "collector_note": "Official admissions/employment portal surfaced; no first-party Guangxi physical ordinary plan rows cached in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search/cache first-party 2025分省计划 or reject to context-only.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0175",
            "queue_rank": "175",
            "university_code": "10304",
            "university_name": "南通大学",
            "source_url": "https://zs.ntu.edu.cn/",
            "source_owner": "南通大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_portal_with_policy_context",
            "source_role": "official_context_needs_plan_detail_cache",
            "collector_note": "Official portal and 2025 charter context surfaced; no Guangxi plan rows cached.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_portal_found_plan_detail_not_cached",
            "next_action": "find/cache official 2025分省计划; exclude comprehensive-evaluation-only PDFs.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0176",
            "queue_rank": "176",
            "university_code": "11062",
            "university_name": "厦门理工学院",
            "source_url": "https://zsb.xmut.edu.cn/",
            "source_owner": "厦门理工学院招生网",
            "source_title": "招生网官方入口",
            "round_type": "official_portal_context_only",
            "source_role": "official_portal_needs_plan_detail_cache",
            "collector_note": "Official admissions domain surfaced, but exact Guangxi plan table was not cached in this pass.",
            "collector_confidence": "T3_official_portal_context_only_no_cached_plan_rows",
            "source_packet_status": "official_portal_found_plan_detail_not_cached",
            "next_action": "search/cache official 2025广西招生计划 page; do not use third-party reposts for intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0177",
            "queue_rank": "177",
            "university_code": "10626",
            "university_name": "四川农业大学",
            "source_url": "https://zs.sicau.edu.cn/zszn1/zsjh.htm",
            "source_owner": "四川农业大学本科招生网",
            "source_title": "招生计划栏目/四川农业大学2025年招生计划",
            "round_type": "official_plan_page_candidate",
            "source_role": "official_2025_plan_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_if_plan_page_cached",
            "collector_note": "Official admissions plan column exposes 2025 plan context; cache/parse required to isolate Guangxi physical ordinary rows.",
            "collector_confidence": "T2_official_plan_page_needs_cache_parse",
            "source_packet_status": "official_plan_candidate_found_not_cached",
            "next_action": "cache official plan page and extract Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0178",
            "queue_rank": "178",
            "university_code": "11937",
            "university_name": "四川警察学院",
            "source_url": "https://zs.scpolicec.edu.cn/bkzn.htm|https://gat.sc.gov.cn/scgat/c103388/2025/6/17/7b80ac1d5fb04cdb9975f57dd9f897b7.shtml",
            "source_owner": "四川警察学院招生信息网/四川省公安厅",
            "source_title": "报考指南/2025年本专科招生简章",
            "round_type": "official_police_special_context",
            "source_role": "official_context_special_type_boundary_hold",
            "source_contains_plan_count": "unknown_special_type_until_cache_parse",
            "special_type_detected": "police_college_or_public_security_boundary_unknown",
            "collector_note": "Official school/gov context surfaced; police/public-security special-type boundaries require manual separation before any trend use.",
            "collector_confidence": "T3_official_context_only_special_type_boundary_hold",
            "source_packet_status": "official_context_found_special_type_boundary_hold",
            "requires_manual_approval": "true_if_public_security_or_special_type_inclusion_considered",
            "next_action": "only cache/parse if ordinary batch non-police rows can be isolated; otherwise keep excluded from trend intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0179",
            "queue_rank": "179",
            "university_code": "10161",
            "university_name": "大连医科大学",
            "source_url": "https://recruit.dmu.edu.cn/",
            "source_owner": "大连医科大学本科招生网",
            "source_title": "本科招生网/本科招生计划栏目候选",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_plan_portal_needs_detail_cache",
            "source_contains_plan_count": "true_if_2025_plan_detail_cached",
            "special_type_detected": "medical_major_boundary_unknown",
            "collector_note": "Official admissions site surfaced with plan column context; search result exposed 2024 plan and related 2025 admissions items, but no Guangxi 2025 rows cached.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "cache official 2025本科招生计划 if published; otherwise hold as no-current-plan candidate.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0180|reference_trend_520_plan_source_queue_0181",
            "queue_rank": "180|181",
            "university_code": "10152",
            "university_name": "大连工业大学",
            "source_url": "https://zsb.dep.dlpu.edu.cn/plan",
            "source_owner": "大连工业大学本科招生信息网",
            "source_title": "本科招生计划查询",
            "round_type": "official_plan_query_candidate",
            "source_role": "official_query_needs_guangxi_parameter_cache",
            "source_contains_plan_count": "true_if_query_cached_for_guangxi",
            "collector_note": "Official plan query endpoint surfaced with structured rows in search index; needs parameterized cache for Guangxi physical ordinary rows and group 105/109 separation.",
            "collector_confidence": "T2_official_plan_query_needs_parameter_cache",
            "source_packet_status": "official_plan_query_candidate_found_not_cached",
            "next_action": "cache query result for 2025 Guangxi physical ordinary batch; no browser/form replay without approval if needed.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0182|reference_trend_520_plan_source_queue_0183",
            "queue_rank": "182|183",
            "university_code": "10057",
            "university_name": "天津科技大学",
            "source_url": "https://zsb.tust.edu.cn/bkzn/jhcx/gx/index.htm",
            "source_owner": "天津科技大学招生信息网",
            "source_title": "2025年广西壮族自治区本科招生计划表",
            "round_type": "official_guangxi_plan_page_candidate",
            "source_role": "official_2025_guangxi_plan_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_if_page_cached",
            "collector_note": "Exact official Guangxi plan page surfaced; parse/cache needed to separate group 104 and 303 including special/boundary notes.",
            "collector_confidence": "T1_exact_official_guangxi_plan_page_candidate",
            "source_packet_status": "official_exact_plan_candidate_found_not_cached",
            "next_action": "cache official Guangxi page and parse group-level physical ordinary plan rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0184",
            "queue_rank": "184",
            "university_code": "10370",
            "university_name": "安徽师范大学",
            "source_url": "https://zsxx.ahnu.edu.cn/",
            "source_owner": "安徽师范大学本科招生信息网",
            "source_title": "本科招生信息网官方入口",
            "round_type": "official_portal_context_only",
            "source_role": "official_context_needs_plan_detail_cache",
            "collector_note": "Official admissions portal surfaced; exact Guangxi physical plan rows not cached in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_portal_found_plan_detail_not_cached",
            "next_action": "search/cache official 2025分省计划; keep third-party summaries out of intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0185",
            "queue_rank": "185",
            "university_code": "10878",
            "university_name": "安徽建筑大学",
            "source_url": "https://www.ahjzu.edu.cn/zsw/_t6/2025/0617/c2397a254020/page.htm",
            "source_owner": "安徽建筑大学招生网",
            "source_title": "安徽建筑大学2025年分省分专业招生计划",
            "round_type": "official_plan_page_candidate",
            "source_role": "official_2025_plan_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_if_page_cached",
            "collector_note": "Official 2025 province/major plan page surfaced; cache/parse required to isolate Guangxi physical ordinary rows.",
            "collector_confidence": "T1_exact_official_plan_page_candidate_needs_parse",
            "source_packet_status": "official_exact_plan_candidate_found_not_cached",
            "next_action": "cache official page and parse Guangxi physical ordinary group 103 plan rows if group mapping is present.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0186",
            "queue_rank": "186",
            "university_code": "10378",
            "university_name": "安徽财经大学",
            "source_url": "https://zsjy.aufe.edu.cn/",
            "source_owner": "安徽财经大学本科招生信息网",
            "source_title": "本科招生信息网/招生计划入口候选",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_plan_portal_needs_detail_cache",
            "source_contains_plan_count": "true_if_2025_plan_detail_cached",
            "collector_note": "Official admissions portal surfaced; exact Guangxi 2025 plan rows not cached in this pass.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "cache official 2025招生计划 detail/table; reject third-party mirrors.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0187|reference_trend_520_plan_source_queue_0188",
            "queue_rank": "187|188",
            "university_code": "10602",
            "university_name": "广西师范大学",
            "source_url": "https://bkzs.gxnu.edu.cn/pg/jh/index.php",
            "source_owner": "广西师范大学本科招生网",
            "source_title": "招生计划查询",
            "round_type": "official_local_plan_query_candidate",
            "source_role": "official_2025_plan_query_candidate_needs_group_reconcile",
            "source_contains_plan_count": "true_if_query_cached",
            "collector_note": "Official local plan query surfaced with 2025 Guangxi rows in search index; cache/parse required to reconcile groups 151 and 155.",
            "collector_confidence": "T1_exact_official_local_plan_query_candidate",
            "source_packet_status": "official_plan_query_candidate_found_not_cached",
            "next_action": "cache query result and reconcile group 151/155 with ordinary/special-type boundaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0189",
            "queue_rank": "189",
            "university_code": "10577",
            "university_name": "惠州学院",
            "source_url": "https://zs.hzu.edu.cn/_upload/article/files/a2/fb/9de322d54859b374cdc5f4e349e8/e1e67b91-542f-4e4e-8a05-52e12e565fa5.pdf",
            "source_owner": "惠州学院招生信息网",
            "source_title": "惠州学院2025年省外招生计划PDF",
            "round_type": "official_plan_pdf_candidate",
            "source_role": "official_2025_plan_pdf_candidate_needs_cache_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "collector_note": "Official PDF candidate surfaced for out-of-province plans; PDF parse/manual QA needed for Guangxi physical ordinary rows.",
            "collector_confidence": "T2_official_pdf_plan_candidate_needs_parser",
            "source_packet_status": "official_pdf_candidate_found_not_cached",
            "requires_manual_approval": "true_if_pdf_table_parse_or_manual_transcription_needed",
            "next_action": "cache official PDF, parse table, then isolate Guangxi physical ordinary row(s).",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0190",
            "queue_rank": "190",
            "university_code": "10446",
            "university_name": "曲阜师范大学",
            "source_url": "https://www.qfnu.edu.cn/",
            "source_owner": "曲阜师范大学官网",
            "source_title": "学校官网/本科招生入口上下文",
            "round_type": "official_main_site_context_only",
            "source_role": "official_context_needs_undergraduate_admission_plan_detail",
            "collector_note": "Official main site surfaced with undergraduate admissions navigation; exact 2025 Guangxi plan rows not cached.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "locate/cache first-party本科招生网 2025广西招生计划; keep current row context-only until then.",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(raw_rows, 1)]


def write_rollup(rows: list[dict[str, object]]) -> None:
    confidence = Counter(str(row["collector_confidence"]) for row in rows)
    status = Counter(str(row["source_packet_status"]) for row in rows)
    manual = sum(str(row["requires_manual_approval"]).startswith("true") for row in rows)
    count_confidence_prefix = lambda prefix: sum(v for k, v in confidence.items() if k.startswith(prefix))

    rollup_rows = [
        {"metric": "batch16_source_discovery_rows", "value": len(rows), "note": "Compressed official candidates for P1 queue ranks 171-190."},
        {"metric": "queue_rank_min", "value": "171", "note": ""},
        {"metric": "queue_rank_max", "value": "190", "note": ""},
        {"metric": "t1_exact_official_candidates", "value": count_confidence_prefix("T1_"), "note": "Exact official plan/query candidates, not parsed."},
        {"metric": "t2_official_plan_candidates", "value": count_confidence_prefix("T2_"), "note": ""},
        {"metric": "t3_context_only_rows", "value": count_confidence_prefix("T3_"), "note": ""},
        {"metric": "manual_or_parser_approval_rows", "value": manual, "note": "PDF/special-type/manual parse routes."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"status::{k}", "value": v, "note": ""} for k, v in sorted(status.items()))
    rollup_rows.extend({"metric": f"confidence::{k}", "value": v, "note": ""} for k, v in sorted(confidence.items()))
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "no_pool_or_canonical_entry",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "All rows remain discovery preview only.",
        },
        {
            "check": "official_url_present",
            "status": "PASS" if all(row["source_url"] for row in rows) else "FAIL",
            "detail": "Every row has at least one official or first-party/government URL candidate.",
        },
        {
            "check": "no_raw_cache_claimed",
            "status": "PASS" if all(not row["raw_file_path"] for row in rows) else "FAIL",
            "detail": "No row claims a local cache or parsed source packet.",
        },
        {
            "check": "p1_boundary",
            "status": "PASS" if all("p1" in row["source_id"] for row in rows) else "FAIL",
            "detail": "Batch is P1 discovery only; not P0/canonical/decision pool.",
        },
        {
            "check": "no_browser_cookie_replay",
            "status": "PASS",
            "detail": "No browser, cookie/header replay, form submission, OCR, or PDF parse performed.",
        },
    ]
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])


def write_exclusion_log() -> None:
    rows = [
        {
            "item": "batch16_all_rows",
            "reason": "source_discovery_preview_only_not_parsed",
            "effect": "excluded_from_reference_trend_intake_and_calibration_until_source_packet_parse_QA",
        }
    ]
    write_csv(EXCLUSION_OUT, rows, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    confidence = Counter(str(row["collector_confidence"]) for row in rows)
    status = Counter(str(row["source_packet_status"]) for row in rows)
    count_confidence_prefix = lambda prefix: sum(v for k, v in confidence.items() if k.startswith(prefix))
    lines = [
        "# Reference trend 520 P1 official source discovery batch16",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This batch covers P1 plan source queue ranks 171-190. It records official source candidates only; it does not cache, parse, OCR, replay forms, or open intake/canonical/ML.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP_OUT.relative_to(ROOT)}`",
        f"- `{QA_OUT.relative_to(ROOT)}`",
        f"- `{EXCLUSION_OUT.relative_to(ROOT)}`",
        "",
        "## Rollup",
        "",
        f"- Discovery rows: {len(rows)}",
        f"- T1 exact official candidates: {count_confidence_prefix('T1_')}",
        f"- T2 official plan candidates: {count_confidence_prefix('T2_')}",
        f"- T3 context-only rows: {count_confidence_prefix('T3_')}",
        "- Reference trend pool eligible rows: 0",
        "- Calibration eligible rows: 0",
        "- Canonical/ML entry rows: 0",
        "",
        "## Status distribution",
        "",
    ]
    lines.extend(f"- {k}: {v}" for k, v in sorted(status.items()))
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- All rows remain `reference_trend_source_packet_preview_only`.",
            "- No row enters reference trend intake until official source packet cache/parse QA is complete.",
            "- No row may be merged into the 32-school decision pool.",
            "- Canonical/ML remains closed.",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion_log()
    write_doc(rows)

    marker = "## 111. 2026-05-17 P1 official source discovery batch16"
    handoff = f"""

{marker}

已新增 P1 official source discovery batch16：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：处理 P1 queue ranks 171-190，压缩为 {len(rows)} 条官方来源候选/官方上下文 rows；其中 T1 精确官方计划/查询候选 {sum(str(r['collector_confidence']).startswith('T1_') for r in rows)} 条，T2 官方计划候选 {sum(str(r['collector_confidence']).startswith('T2_') for r in rows)} 条，T3 官方上下文-only {sum(str(r['collector_confidence']).startswith('T3_') for r in rows)} 条。QA PASS。

准入边界：本轮只做 source discovery preview，不缓存、不解析、不 OCR、不表单 replay、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
