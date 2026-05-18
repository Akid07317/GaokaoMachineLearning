#!/usr/bin/env python3
"""Write batch-12 official source discovery preview for P0 queue rows.

This batch covers queue ranks 91-110. It records official source candidates
and known carry-forward candidates from earlier batches. Every row stays in
source-packet preview only: no reference-pool intake, no canonical, no ML.
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

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch12_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch12_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch12_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch12_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch12.md"
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def common(row: dict[str, object], idx: int) -> dict[str, object]:
    enriched = {
        "source_id": f"reference_trend_520_p0_batch12_{idx:04d}",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "raw_file_path": "",
        "intended_layer": "reference_trend_source_packet_preview_only",
        "eligible_for_intake_preview": "false_until_source_packet_parse_and_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch12_{idx:04d}",
    }
    enriched.update(row)
    return enriched


def build_rows() -> list[dict[str, object]]:
    rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0091",
            "queue_rank": "91",
            "university_code": "10460",
            "university_name": "河南理工大学",
            "source_url": "https://www6.hpu.edu.cn/__local/0/F1/2A/C4518527B841AE23CBB7281803F_6AF2C0FC_24A0B.pdf|https://www6.hpu.edu.cn/web5/info/10602/93003.htm",
            "source_owner": "河南理工大学/河南理工大学招生就业处",
            "source_title": "河南理工大学2025年全国招生来源计划 + 2025年分专业录取分数情况——广西",
            "published_date": "",
            "round_type": "existing_source_packet_and_group_workbench_carried_forward",
            "source_role": "existing_noncanonical_group_line_workbench_reuse",
            "source_contains_group_code": "true_after_existing_group_line_workbench",
            "source_contains_min_score": "true",
            "source_contains_min_rank": "true",
            "source_contains_plan_count": "true",
            "special_type_detected": "handled_in_existing_workbench",
            "raw_file_path": "clean_data/engineering_guangxi_seed/reference_trend_hpu_group_line_workbench.csv",
            "collector_note": "Earlier batch already built HPU source-packet parse, group-line workbench, and intake preview candidate. Batch12 only carries the status forward to avoid duplicate discovery.",
            "collector_confidence": "T1_existing_official_group_line_workbench",
            "source_packet_status": "existing_mapping_workbench_hold_for_group_acceptance",
            "requires_network": "false",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false_existing_noncanonical_artifact_only",
            "next_action": "use existing HPU workbench/intake candidate if policy opens review; do not rediscover source",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0092",
            "queue_rank": "92",
            "university_code": "11647",
            "university_name": "浙江传媒学院",
            "source_url": "https://xxgk.cuz.edu.cn/info/1008/1789.htm|https://zsw.cuz.edu.cn/",
            "source_owner": "浙江传媒学院信息公开网/本科招生网",
            "source_title": "2025年本科生招生章程及特殊类型招生办法，分批次、分科类招生计划 / 本科招生网首页",
            "published_date": "2025-10-27",
            "round_type": "existing_official_index_and_portal_cached",
            "source_role": "existing_candidate_no_guangxi_rows_yet",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "not_in_cached_html",
            "special_type_detected": "art/special materials must stay isolated",
            "raw_file_path": "raw_sources/reference_trend/batch6_official/cuz_info_1008_1789.html|raw_sources/reference_trend/batch6_official/cuz_zsw_root.html",
            "collector_note": "Earlier batch cached official information-disclosure page and admissions portal root, but no Guangxi physical ordinary structured rows surfaced.",
            "collector_confidence": "T2_existing_official_index_needs_asset_or_endpoint_drilldown",
            "source_packet_status": "existing_official_index_cached_no_guangxi_rows",
            "requires_network": "false_for_this_batch_existing_cache;true_for_future_endpoint_drilldown",
            "requires_manual_approval": "false_until_browser_or_viewer_replay_needed",
            "eligible_for_intake_preview": "false_until_pdf_or_plan_asset_rows_return",
            "next_action": "drill official viewer assets or endpoint if approved; do not ingest index text",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0093",
            "queue_rank": "93",
            "university_code": "10340",
            "university_name": "浙江海洋大学",
            "source_url": "https://zs.zjou.edu.cn/",
            "source_owner": "浙江海洋大学招生网",
            "source_title": "2025年招生计划及2024年录取分数（广西）",
            "published_date": "",
            "round_type": "official_homepage_search_candidate",
            "source_role": "official_plan_score_candidate_needs_detail_cache",
            "source_contains_group_code": "unknown_until_detail_parse",
            "source_contains_min_score": "likely_true_until_detail_parse",
            "source_contains_min_rank": "unknown_until_detail_parse",
            "source_contains_plan_count": "likely_true_until_detail_parse",
            "special_type_detected": "marine/ship/cooperation boundaries unknown until detail parse",
            "collector_note": "Official admissions homepage/search result exposes a Guangxi plan-score candidate, but the exact detail page has not been cached in this run.",
            "collector_confidence": "T2_official_homepage_guangxi_plan_score_candidate_not_cached",
            "source_packet_status": "official_plan_score_candidate_discovered_not_cached",
            "requires_network": "true_for_detail_cache",
            "requires_manual_approval": "false_for_normal_page_cache",
            "next_action": "cache exact official detail page, then parse Guangxi ordinary physical rows and separate score-only fields",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0094",
            "queue_rank": "94",
            "university_code": "11057",
            "university_name": "浙江科技大学",
            "source_url": "https://zsb.zust.edu.cn/",
            "source_owner": "浙江科技大学招生网",
            "source_title": "招生网/招生计划入口上下文",
            "published_date": "",
            "round_type": "official_context_or_portal_no_rows",
            "source_role": "official_context_not_structured_plan_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "unknown",
            "collector_note": "This pass found official admissions context/portal only; no first-party 2025 Guangxi physical ordinary plan table/PDF was accepted.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry with official domain and招生计划关键词; keep third-party rows out",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0095",
            "queue_rank": "95",
            "university_code": "10343",
            "university_name": "温州医科大学",
            "source_url": "https://recruit.wmu.edu.cn/bkzn/zsjh.htm",
            "source_owner": "温州医科大学本科招生网",
            "source_title": "温州医科大学2025年本科分省分专业招生计划",
            "published_date": "",
            "round_type": "official_plan_index_candidate",
            "source_role": "official_plan_page_candidate_needs_cache_parse",
            "source_contains_group_code": "unknown_until_page_parse",
            "source_contains_plan_count": "likely_true_until_page_parse",
            "special_type_detected": "medical/orientation/cooperation boundaries unknown until parse",
            "collector_note": "Official plan index candidate was found, but Guangxi rows were not cached or parsed in this run.",
            "collector_confidence": "T2_official_plan_page_candidate_not_cached",
            "source_packet_status": "official_plan_page_candidate_discovered_not_cached",
            "requires_network": "true_for_page_cache",
            "requires_manual_approval": "false_for_normal_page_cache",
            "next_action": "cache official plan page and parse Guangxi ordinary physical rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0096",
            "queue_rank": "96",
            "university_code": "10351",
            "university_name": "温州大学",
            "source_url": "https://zsw.wzu.edu.cn/info/1164/4608.htm",
            "source_owner": "温州大学本科招生网",
            "source_title": "温州大学2025年普通高校招生章程",
            "published_date": "",
            "round_type": "official_charter_context_only",
            "source_role": "official_context_not_structured_plan_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "charter mentions admission rules, not plan rows",
            "collector_note": "Official charter is first-party context but not a Guangxi plan-row source packet.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "search official招生计划/省外计划 asset; do not parse charter as plan data",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0097",
            "queue_rank": "97",
            "university_code": "10500",
            "university_name": "湖北工业大学",
            "source_url": "https://zs.hbut.edu.cn/",
            "source_owner": "湖北工业大学本科招生网",
            "source_title": "本科招生网入口上下文",
            "published_date": "",
            "round_type": "official_portal_context_no_rows",
            "source_role": "official_context_not_structured_plan_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "unknown until plan source found",
            "collector_note": "Search found official-domain context but no first-party Guangxi physical ordinary plan table/PDF suitable for source-packet intake.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official plan source discovery or use exam-authority score/rank-only context if policy allows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0098",
            "queue_rank": "98",
            "university_code": "10541",
            "university_name": "湖南中医药大学",
            "source_url": "https://zhaosheng.hnucm.edu.cn/info/1143/6051.htm",
            "source_owner": "湖南中医药大学招生就业处",
            "source_title": "湖南中医药大学2025年分省分专业计划",
            "published_date": "",
            "round_type": "official_html_plan_table_discovered",
            "source_role": "official_html_plan_table_candidate_parse_ready",
            "source_contains_group_code": "unknown_until_table_parse",
            "source_contains_plan_count": "true",
            "special_type_detected": "medical/Chinese-medicine majors; ordinary/special boundary to isolate after parse",
            "collector_note": "Official HTML plan table exposes province columns including Guangxi and is the strongest parse-ready candidate in this batch.",
            "collector_confidence": "T1_official_html_table_plan_candidate_parse_ready",
            "source_packet_status": "official_html_plan_table_parse_ready",
            "requires_network": "true_for_page_cache",
            "requires_manual_approval": "false_for_normal_page_cache",
            "eligible_for_intake_preview": "false_until_html_table_parsed_and_group_boundary_QA",
            "next_action": "cache/parse official HTML table, extract Guangxi ordinary physical plan rows, then hold for group mapping",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0099",
            "queue_rank": "99",
            "university_code": "10545",
            "university_name": "湘南学院",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "teacher/medicine/art boundaries unknown",
            "collector_note": "This pass found no first-party 2025 Guangxi physical ordinary plan source; third-party references are not accepted.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official admissions site/source discovery",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0100",
            "queue_rank": "100",
            "university_code": "10632",
            "university_name": "西南医科大学",
            "source_url": "https://zsxxw.swmu.edu.cn/info/1221/8711.htm",
            "source_owner": "西南医科大学招生办",
            "source_title": "2025年普教本科分省分专业招生计划表",
            "published_date": "2025-06-06",
            "round_type": "existing_official_attachment_page_captcha_blocked",
            "source_role": "existing_official_plan_attachment_candidate_gated",
            "source_contains_group_code": "unknown_until_attachment_parse",
            "source_contains_plan_count": "true_in_attachment_metadata_not_downloaded",
            "special_type_detected": "unknown_until_attachment_parse",
            "raw_file_path": "raw_sources/reference_trend/batch7_official/swmu_2025_plan_detail.html",
            "collector_note": "Earlier batch cached the official detail page; attachment download route was captcha-gated. Batch12 carries this forward without replay.",
            "collector_confidence": "T2_existing_official_attachment_candidate_captcha_blocked",
            "source_packet_status": "existing_official_detail_cached_attachment_download_captcha_blocked",
            "requires_network": "false_for_this_batch_existing_cache;true_for_attachment_retry",
            "requires_manual_approval": "true_for_browser_or_captcha_replay",
            "eligible_for_intake_preview": "false_until_attachment_obtained_or_official_table_rows_available",
            "next_action": "use manual download/browser-approved route if needed; do not parse captcha page as data",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0101",
            "queue_rank": "101",
            "university_code": "11560",
            "university_name": "西安财经大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "finance/economics ordinary boundary unknown",
            "collector_note": "No first-party 2025 Guangxi plan source was found in this pass.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official招生网/信息公开/公众号 source discovery",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0102",
            "queue_rank": "102",
            "university_code": "10694",
            "university_name": "西藏大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "ethnic/region policy boundaries unknown",
            "collector_note": "Search did not surface a first-party 2025 Guangxi physical ordinary plan source suitable for source-packet preview.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official source discovery or rely on exam-authority score/rank-only context until plan source appears",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0103",
            "queue_rank": "103",
            "university_code": "10671",
            "university_name": "贵州财经大学",
            "source_url": "https://zhaosheng.gufe.edu.cn/__local/8/39/7A/03FC1CF1C8D778BA1F7919F6739_B68BB2C4_70AEED.pdf",
            "source_owner": "贵州财经大学招生网",
            "source_title": "2025本科招生报考指南",
            "published_date": "",
            "round_type": "existing_official_pdf_candidate_reachability_blocked",
            "source_role": "existing_official_pdf_candidate_not_cached",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "likely_true_until_pdf_parse",
            "special_type_detected": "unknown_until_pdf_parse",
            "collector_note": "Earlier batch found official-domain PDF candidate but terminal TLS/reachability failed; web text may be visible, yet no audited local PDF parse has been made.",
            "collector_confidence": "T2_existing_official_pdf_candidate_reachability_blocked",
            "source_packet_status": "existing_official_pdf_candidate_reachability_blocked",
            "requires_network": "true_for_approved_cache_or_alternate_route",
            "requires_manual_approval": "true_for_browser_or_alt_tls_retry",
            "eligible_for_intake_preview": "false_until_pdf_cached_and_parsed",
            "next_action": "retry with approved browser/alternate fetch route or locate equivalent official HTML source",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0104",
            "queue_rank": "104",
            "university_code": "10140",
            "university_name": "辽宁大学",
            "source_url": "https://zs.lnu.edu.cn/",
            "source_owner": "辽宁大学本科招生网",
            "source_title": "2025年各省录取最低分官方 PDF 候选 / 本科招生网入口",
            "published_date": "",
            "round_type": "official_score_candidate_not_plan_source",
            "source_role": "official_score_rank_reference_not_plan_packet",
            "source_contains_group_code": "unknown_until_score_pdf_parse",
            "source_contains_min_score": "likely_true_until_pdf_parse",
            "source_contains_min_rank": "unknown_until_pdf_parse",
            "source_contains_plan_count": "false",
            "special_type_detected": "score/rank source only; not a plan source",
            "collector_note": "Official score/minimum PDF candidate was found, but this does not solve the P0 plan-source task. Keep as score reference only.",
            "collector_confidence": "T3_official_score_reference_not_plan_source",
            "source_packet_status": "official_score_reference_found_not_plan_source",
            "requires_network": "true_for_score_pdf_cache_if_needed",
            "requires_manual_approval": "false_for_normal_pdf_cache",
            "eligible_for_intake_preview": "false",
            "next_action": "continue official plan-source discovery; score PDF can support separate score/rank reachability only",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0105",
            "queue_rank": "105",
            "university_code": "10462",
            "university_name": "郑州轻工业大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "ordinary/cooperation boundary unknown",
            "collector_note": "This pass did not locate a first-party 2025 Guangxi physical ordinary plan source.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official招生信息网/source discovery; keep third-party rows out",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0106",
            "queue_rank": "106",
            "university_code": "14830",
            "university_name": "重庆中医药学院",
            "source_url": "https://zs.cqctcm.edu.cn/info/1137/1514.htm",
            "source_owner": "重庆中医药学院招生网",
            "source_title": "2025年普通本科招生章程及分省分专业招生计划",
            "published_date": "",
            "round_type": "official_plan_charter_candidate",
            "source_role": "official_plan_charter_page_candidate_needs_parse",
            "source_contains_group_code": "unknown_until_page_parse",
            "source_contains_plan_count": "likely_true_until_page_parse",
            "special_type_detected": "medical/Chinese-medicine ordinary boundary unknown until parse",
            "collector_note": "Official page title indicates both charter and province/major plan; needs cache/parse to determine whether Guangxi rows are exposed.",
            "collector_confidence": "T2_official_plan_page_candidate_not_cached",
            "source_packet_status": "official_plan_page_candidate_discovered_not_cached",
            "requires_network": "true_for_page_cache",
            "requires_manual_approval": "false_for_normal_page_cache",
            "next_action": "cache official page and parse/verify Guangxi ordinary physical rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0107",
            "queue_rank": "107",
            "university_code": "11799",
            "university_name": "重庆工商大学",
            "source_url": "https://acgozs.ctbu.edu.cn/info/1010/1710.htm",
            "source_owner": "重庆工商大学招生办公室",
            "source_title": "2025年招生计划",
            "published_date": "",
            "round_type": "official_plan_context_no_province_rows",
            "source_role": "official_context_or_aggregate_not_structured_guangxi_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "aggregate_or_unknown_not_guangxi_rows",
            "special_type_detected": "unknown",
            "collector_note": "Official plan page exists, but this pass did not confirm structured Guangxi group/major rows; keep as context only.",
            "collector_confidence": "T3_official_plan_context_no_guangxi_rows_confirmed",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry_or_endpoint",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "look for province-specific table/API before accepting as source packet",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0108",
            "queue_rank": "108",
            "university_code": "11551",
            "university_name": "重庆科技大学",
            "source_url": "https://zhinengdayi.com/cqust/static/front/cqust/basic/html_web/zsjh.html",
            "source_owner": "重庆科技大学招生计划查询系统",
            "source_title": "招生计划查询入口",
            "published_date": "",
            "round_type": "official_or_school_plan_portal_needs_endpoint",
            "source_role": "plan_query_portal_endpoint_drilldown_needed",
            "source_contains_group_code": "unknown_until_endpoint_drilldown",
            "source_contains_plan_count": "unknown_until_endpoint_drilldown",
            "special_type_detected": "unknown_until_endpoint_drilldown",
            "collector_note": "Plan query portal is a plausible official/school-linked source, but province rows require endpoint/form drilldown.",
            "collector_confidence": "T2_plan_query_portal_needs_endpoint_drilldown",
            "source_packet_status": "official_plan_portal_discovered_endpoint_needed",
            "requires_network": "true_for_endpoint_drilldown",
            "requires_manual_approval": "true_if_form_browser_or_header_replay_needed",
            "eligible_for_intake_preview": "false_until_endpoint_rows_return",
            "next_action": "map endpoint parameters only through an auditable route; wait for approval if browser/form/header replay is needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0109",
            "queue_rank": "109",
            "university_code": "10186",
            "university_name": "长春理工大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "ordinary/cooperation boundary unknown",
            "collector_note": "This pass did not locate a first-party 2025 Guangxi physical ordinary plan source.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official招生网/source discovery",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0110",
            "queue_rank": "110",
            "university_code": "10489",
            "university_name": "长江大学",
            "source_url": "https://xxgk.yangtzeu.edu.cn/info/1108/5946.htm",
            "source_owner": "长江大学信息公开网",
            "source_title": "2025年分省分批次招生计划",
            "published_date": "",
            "round_type": "official_batch_plan_context_only",
            "source_role": "official_context_not_detailed_major_group_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "batch_count_context_not_major_group_rows",
            "special_type_detected": "unknown",
            "collector_note": "Official information-disclosure page gives province/batch plan context, but not detailed school-group/year major rows required by the trend source packet.",
            "collector_confidence": "T3_official_context_only_no_detailed_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "search for detailed分省分专业 plan attachment/table before accepting as source packet",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(rows, start=1)]


def boolish_starts(row: dict[str, object], field: str, prefix: str) -> bool:
    return str(row.get(field, "")).startswith(prefix)


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["source_packet_status"]) for row in rows)
    by_confidence = Counter(str(row["collector_confidence"]) for row in rows)
    official_candidate = sum(str(row["collector_confidence"]).startswith(("T1", "T2")) for row in rows)
    t1_parse_ready = sum("parse_ready" in str(row["collector_confidence"]) or "parse_ready" in str(row["source_packet_status"]) for row in rows)
    rollup = [
        {"metric": "discovery_rows", "value": len(rows), "note": "Queue ranks 91-110."},
        {"metric": "unique_universities", "value": len({row["university_name"] for row in rows}), "note": ""},
        {"metric": "existing_candidate_carried_forward_rows", "value": sum(str(row["round_type"]).startswith("existing") for row in rows), "note": "Earlier noncanonical source artifacts/status carried forward only."},
        {"metric": "official_plan_candidate_rows", "value": official_candidate, "note": "Requires cache/parse, endpoint drilldown, or existing-artifact review before intake."},
        {"metric": "t1_parse_ready_rows", "value": t1_parse_ready, "note": "湖南中医药大学 official HTML table is the only parse-ready candidate."},
        {"metric": "first_party_context_or_score_only_rows", "value": sum(str(row["collector_confidence"]).startswith("T3") for row in rows), "note": "Official context or score source, not a detailed plan packet."},
        {"metric": "third_party_or_missing_rows", "value": sum(str(row["collector_confidence"]).startswith("T4") for row in rows), "note": "No accepted first-party source packet."},
        {"metric": "requires_manual_approval_rows", "value": sum(boolish_starts(row, "requires_manual_approval", "true") for row in rows), "note": "Captcha/browser/alt-TLS/form routes."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year rows opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
    ]
    rollup.extend({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items()))
    rollup.extend({"metric": f"confidence::{key}", "value": value, "note": ""} for key, value in sorted(by_confidence.items()))
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "check": "no_reference_trend_pool_intake_open",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "false" for row in rows) else "FAIL",
            "detail": "All rows remain source-packet preview/carry-forward only.",
        },
        {
            "check": "no_calibration_open",
            "status": "PASS" if all(str(row["calibration_eligible"]) == "false" for row in rows) else "FAIL",
            "detail": "No group-year calibration row opened.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(str(row["canonical_ml_entry_open"]) == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML input opened.",
        },
        {
            "check": "decision_pool_boundary",
            "status": "PASS" if all("do_not_merge" in str(row["decision_pool_boundary"]) for row in rows) else "FAIL",
            "detail": "32-school decision_pool boundary preserved.",
        },
        {
            "check": "has_next_parse_candidate",
            "status": "PASS" if any("parse_ready" in str(row["source_packet_status"]) for row in rows) else "WARN",
            "detail": "湖南中医药大学 official HTML plan table is ready for a future cache/parse pass.",
        },
        {
            "check": "approval_gated_routes_flagged",
            "status": "PASS" if any(boolish_starts(row, "requires_manual_approval", "true") for row in rows) else "WARN",
            "detail": "西南医科、贵州财经、重庆科技等 gated routes are explicitly flagged.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "queue_rank": row["queue_rank"],
            "exclusion_scope": "reference_trend_pool_calibration_canonical_ml",
            "exclusion_reason": row["source_packet_status"],
            "required_resolution": row["next_action"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 P0 Official Source Discovery Batch 12",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: queue ranks 91-110. This is source discovery and carry-forward only, not reference trend intake.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Key source findings:",
    ]
    for row in rows:
        lines.append(f"- {row['queue_rank']} {row['university_name']}: {row['source_packet_status']} ({row['collector_confidence']}).")
    lines.extend(
        [
            "",
            "Boundary:",
            "- This batch does not cache or parse any new PDF, endpoint, image, attachment, or HTML table.",
            "- All rows remain `reference_trend_source_packet_preview_only` or existing noncanonical carry-forward status.",
            "- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.",
            "- 32-school `decision_pool` remains isolated.",
            "",
            "Next safe action:",
            "- Prioritize 湖南中医药大学 official HTML plan table cache/parse because it is the only T1 parse-ready row in this batch.",
            "- Continue source recovery for 浙江海洋大学、温州医科大学、重庆中医药学院 and endpoint drilldown for 重庆科技大学.",
            "- Keep 西南医科大学 captcha route and 贵州财经大学 alternate PDF route approval-gated.",
            "",
            "Rollup:",
        ]
    )
    lines.extend(f"- {row['metric']}: {row['value']} {row['note']}".rstrip() for row in rollup)
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    exclusion = build_exclusion(rows)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "queue_rank", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup)

    marker = "## 47. 2026-05-16 P0 官方来源发现 batch 12"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch12 官方来源发现/既有候选承接预览：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：queue rank 91-110。河南理工大学、浙江传媒学院、西南医科大学、贵州财经大学承接前序非 canonical 候选状态，避免重复发现；湖南中医药大学命中官方 HTML 计划表，是本批唯一 T1 parse-ready 候选；浙江海洋大学、温州医科大学、重庆中医药学院命中官方计划/计划分数候选但尚未缓存解析；重庆科技大学命中招生计划查询入口但需 endpoint/form drilldown。浙江科技大学、温州大学、湖北工业大学、辽宁大学、重庆工商大学、长江大学目前只保留官方上下文或 score-only 参考；湘南学院、西安财经大学、西藏大学、郑州轻工业大学、长春理工大学本轮未找到可接收的一方广西计划源。

准入边界：本轮只生成 source discovery preview，不缓存/解析 PDF、endpoint、图片、附件或 HTML 表；所有行 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先解析湖南中医药大学官方 HTML 表；西南医科 captcha、贵州财经 PDF 替代抓取、重庆科技 endpoint/form/browser 路线继续 approval-gated。
""",
    )


if __name__ == "__main__":
    main()
