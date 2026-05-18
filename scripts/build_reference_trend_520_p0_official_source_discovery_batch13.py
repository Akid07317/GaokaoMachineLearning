#!/usr/bin/env python3
"""Write batch-13 official source discovery preview for queue ranks 111-130.

This batch records first-party official plan candidates and rejected
third-party/context-only hits. It does not cache, parse, OCR, replay forms, or
open any canonical/ML intake.
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

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch13_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch13_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch13_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch13_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch13.md"
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
        "source_id": f"reference_trend_520_p0_batch13_{idx:04d}",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown_until_parse",
        "raw_file_path": "",
        "intended_layer": "reference_trend_source_packet_preview_only",
        "requires_network": "true_for_next_cache_or_retry",
        "requires_manual_approval": "false_until_browser_or_form_route_needed",
        "eligible_for_intake_preview": "false_until_source_packet_parse_and_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch13_{idx:04d}",
    }
    enriched.update(row)
    return enriched


def build_rows() -> list[dict[str, object]]:
    raw_rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0111",
            "queue_rank": "111",
            "university_code": "10708",
            "university_name": "陕西科技大学",
            "source_url": "https://shaanxi.eol.cn/shxgd/202506/t20250610_2673804.shtml",
            "source_owner": "中国教育在线陕西站",
            "source_title": "权威发布 | 陕西科技大学2025年本科招生章程",
            "published_date": "2025-06-10",
            "round_type": "third_party_charter_context_no_first_party_plan",
            "source_role": "third_party_context_rejected_for_plan_rows",
            "source_contains_plan_count": "false_for_guangxi_plan_rows",
            "collector_note": "Search did not surface an auditable first-party Guangxi plan page in this pass; third-party charter repost is retained only as rejected context.",
            "collector_confidence": "T4_third_party_context_rejected",
            "source_packet_status": "no_first_party_plan_source_found_this_batch",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry first-party admissions domain/source plan search; do not use third-party repost as plan source.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0112|reference_trend_520_plan_source_queue_0113|reference_trend_520_plan_source_queue_0114|reference_trend_520_plan_source_queue_0115",
            "queue_rank": "112|113|114|115",
            "university_code": "10390",
            "university_name": "集美大学",
            "source_url": "https://zsb.jmu.edu.cn/zsjh.htm",
            "source_owner": "集美大学招生办公室",
            "source_title": "招生计划 / 2025年分省招生计划列表",
            "published_date": "2025-06-17",
            "round_type": "official_plan_index_candidate",
            "source_role": "official_plan_list_needs_pagination_detail_cache",
            "source_contains_group_code": "unknown_until_detail_parse",
            "source_contains_plan_count": "true_in_detail_pages_unparsed",
            "collector_note": "Official plan index lists 2025 provincial plan pages; Guangxi likely behind pagination/detail page, not cached in this run.",
            "collector_confidence": "T2_official_plan_index_needs_detail_cache",
            "source_packet_status": "official_plan_index_discovered_not_cached",
            "next_action": "cache the Guangxi detail page from the official plan index, then parse ordinary physical rows and special navigation/预科 boundaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0116",
            "queue_rank": "116",
            "university_code": "10429",
            "university_name": "青岛理工大学",
            "source_url": "https://zhaosheng.qut.edu.cn/|https://zhaosheng.qut.edu.cn/info/1010/2563.htm",
            "source_owner": "青岛理工大学本专科招生信息网",
            "source_title": "招生网首页 / 2025年普通高等教育招生章程",
            "published_date": "2025-05-12",
            "round_type": "official_context_no_plan_rows",
            "source_role": "official_context_not_structured_guangxi_plan",
            "source_contains_plan_count": "false",
            "collector_note": "Official homepage and charter were found, but no first-party Guangxi plan table/PDF surfaced in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official 招生计划/分省计划 search; keep charter and local专项 pages out of plan intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0117",
            "queue_rank": "117",
            "university_code": "10743",
            "university_name": "青海大学",
            "source_url": "https://zsw.qhu.edu.cn/zsxx/zszc/92a9bb561a4e4253a01988aec41e7333.htm",
            "source_owner": "青海大学本科招生网",
            "source_title": "青海大学2025年招生计划",
            "published_date": "2025-07-04",
            "round_type": "official_plan_image_candidate",
            "source_role": "official_plan_image_needs_cache_or_ocr",
            "source_contains_group_code": "unknown_until_image_parse",
            "source_contains_plan_count": "true_in_image_unparsed",
            "collector_note": "Official page exposes a 2025 plan image; needs asset cache and OCR/manual transcription before any row-level preview.",
            "collector_confidence": "T2_official_plan_image_candidate_not_cached",
            "source_packet_status": "official_plan_image_candidate_discovered_not_cached",
            "requires_manual_approval": "true_for_image_ocr_or_manual_transcription",
            "next_action": "cache/render official plan image, isolate Guangxi physical ordinary rows, and keep OCR/transcription approval-gated.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0118",
            "queue_rank": "118",
            "university_code": "10259",
            "university_name": "上海应用技术大学",
            "source_url": "https://adm.sit.edu.cn/info/1041/1611.htm|https://adm.sit.edu.cn/info/1081/1131.htm",
            "source_owner": "上海应用技术大学全日制本科招生网",
            "source_title": "2025年本科招生章程 / 2025年招生简章",
            "published_date": "2025-05-07|2025-06-13",
            "round_type": "official_charter_and_guide_context",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "false_for_guangxi_rows",
            "collector_note": "Official charter confirms Guangxi is within ordinary admission scope, but the page points to provincial plan books rather than publishing Guangxi rows.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "look for official guide PDF/table with province rows; do not parse charter as plan source.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0119",
            "queue_rank": "119",
            "university_code": "10385",
            "university_name": "华侨大学",
            "source_url": "https://zsc.hqu.edu.cn/info/1024/7692.htm",
            "source_owner": "华侨大学招生信息网",
            "source_title": "华侨大学2025年普高本科分省分专业招生计划（境内版）",
            "published_date": "2025-06-20",
            "round_type": "official_plan_table_candidate",
            "source_role": "official_plan_source_candidate_needs_cache_parse",
            "source_contains_group_code": "maybe_in_attachment_or_table_until_parse",
            "source_contains_plan_count": "true",
            "collector_note": "Official plan page is a strong candidate; search preview shows Guangxi aggregate/subject counts, but row-level table must be cached and parsed before use.",
            "collector_confidence": "T1_official_plan_candidate_parse_ready_after_cache",
            "source_packet_status": "official_plan_candidate_discovered_not_cached",
            "next_action": "cache official page/attachment and parse Guangxi本科批物理 rows, separating arts/special/overseas categories.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0120|reference_trend_520_plan_source_queue_0121",
            "queue_rank": "120|121",
            "university_code": "11276",
            "university_name": "南京工程学院",
            "source_url": "https://www.gk100.com/read_1333910342851.htm|https://doss.xhby.net/zpaper/xhrb/pc/att/202506/25/1c5fed72-690e-403e-b432-bcaa8dac310b.pdf",
            "source_owner": "高考100/新华日报 PDF",
            "source_title": "南京工程学院2026年招生简章参考2025数据 / 高校定制报道",
            "round_type": "third_party_and_media_context_no_first_party_plan",
            "source_role": "third_party_context_rejected_for_plan_rows",
            "source_contains_plan_count": "not_accepted",
            "collector_note": "Search surfaced third-party and media plan summaries but no auditable first-party Guangxi plan source in this pass.",
            "collector_confidence": "T4_third_party_context_rejected",
            "source_packet_status": "no_first_party_plan_source_found_this_batch",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official 南京工程学院招生计划 domain search; ignore third-party summaries for intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0122",
            "queue_rank": "122",
            "university_code": "10226",
            "university_name": "哈尔滨医科大学",
            "source_url": "https://www.hrbmu.edu.cn/zhaosheng/index.htm",
            "source_owner": "哈尔滨医科大学普通教育招生网",
            "source_title": "招生计划列表：校本部2025年广西壮族自治区本科招生计划",
            "published_date": "2025-06-18",
            "round_type": "official_plan_list_candidate",
            "source_role": "official_plan_detail_candidate_needs_cache",
            "source_contains_group_code": "unknown_until_detail_parse",
            "source_contains_plan_count": "true_in_detail_page_unparsed",
            "special_type_detected": "medical/campus/batch boundaries unknown until parse",
            "collector_note": "Official homepage lists a Guangxi undergraduate plan item; detail URL needs cache before row-level assessment.",
            "collector_confidence": "T1_official_plan_candidate_parse_ready_after_detail_cache",
            "source_packet_status": "official_plan_detail_candidate_discovered_not_cached",
            "next_action": "open/cache the Guangxi plan detail page from official list and parse physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0123",
            "queue_rank": "123",
            "university_code": "10622",
            "university_name": "四川轻化工大学",
            "source_url": "https://zjc.suse.edu.cn/2025/0613/c3262a196527/page.htm",
            "source_owner": "四川轻化工大学招生就业处",
            "source_title": "四川轻化工大学2025年本科专业招生计划表",
            "published_date": "2025-06-13",
            "round_type": "official_plan_table_candidate",
            "source_role": "official_plan_source_candidate_needs_cache_parse",
            "source_contains_group_code": "unknown_until_table_parse",
            "source_contains_plan_count": "true",
            "collector_note": "Official plan table candidate found; needs caching and Guangxi physical row extraction.",
            "collector_confidence": "T1_official_plan_candidate_parse_ready_after_cache",
            "source_packet_status": "official_plan_candidate_discovered_not_cached",
            "next_action": "cache official plan table and parse Guangxi本科普通批物理 rows; isolate province/book-only disclaimers.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0124",
            "queue_rank": "124",
            "university_code": "10360",
            "university_name": "安徽工业大学",
            "source_url": "https://zs.ahut.edu.cn/info/6077/2973.htm",
            "source_owner": "安徽工业大学本科招生网",
            "source_title": "安徽工业大学2025年普通本科招生计划",
            "published_date": "2025-06-25",
            "round_type": "official_plan_image_candidate",
            "source_role": "official_plan_image_needs_cache_or_ocr",
            "source_contains_group_code": "unknown_until_image_parse",
            "source_contains_plan_count": "true_in_images_unparsed",
            "collector_note": "Official page shows a multi-image plan asset; row-level OCR/manual transcription must be approval-gated.",
            "collector_confidence": "T2_official_plan_image_candidate_not_cached",
            "source_packet_status": "official_plan_image_candidate_discovered_not_cached",
            "requires_manual_approval": "true_for_image_ocr_or_manual_transcription",
            "next_action": "cache/render official images, then OCR/transcribe Guangxi physical rows with QA.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0125",
            "queue_rank": "125",
            "university_code": "10566",
            "university_name": "广东海洋大学",
            "source_url": "existing_batch11_official_candidate_captcha_gated",
            "source_owner": "广东海洋大学本科招生网",
            "source_title": "2025招生计划官方附件候选（验证码下载页）",
            "round_type": "existing_approval_gated_candidate_carried_forward",
            "source_role": "existing_candidate_attachment_captcha_gated",
            "source_contains_plan_count": "true_in_attachment_unavailable",
            "collector_note": "Batch11 already marked official attachments as captcha-gated; carried forward for rank 125 without repeating blocked fetch.",
            "collector_confidence": "T2_existing_official_attachment_captcha_gated",
            "source_packet_status": "existing_candidate_waiting_browser_or_manual_attachment",
            "requires_manual_approval": "true_for_captcha_or_browser_attachment_download",
            "eligible_for_intake_preview": "false",
            "next_action": "wait for manual attachment/browser approval or supplied file; do not retry terminal download.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0126",
            "queue_rank": "126",
            "university_code": "11079",
            "university_name": "成都大学",
            "source_url": "https://zhaosheng.cdu.edu.cn/index.htm|https://zhaosheng.cdu.edu.cn/info/1206/5025.htm",
            "source_owner": "成都大学招生信息网",
            "source_title": "招生信息网 / 2025年全日制普通本专科招生章程",
            "published_date": "2025-05-12",
            "round_type": "official_context_no_plan_rows",
            "source_role": "official_context_not_structured_guangxi_plan",
            "source_contains_plan_count": "false_for_guangxi_rows",
            "collector_note": "Official site has招生计划入口 and charter, but this pass did not find a first-party Guangxi plan table.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "drill 招生计划入口 or official guide PDF; do not parse charter as plan rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0127",
            "queue_rank": "127",
            "university_code": "13982",
            "university_name": "无锡学院",
            "source_url": "https://www.chinaschool.com.cn/i_region/i_10_jiangsu/a_62/2025/jihua-2025.html|https://www.dakao100.com/article_45549802141.html",
            "source_owner": "大学志/大考100",
            "source_title": "无锡学院－2025年招生计划 / 广西各专业计划摘要",
            "round_type": "third_party_plan_summary_rejected",
            "source_role": "third_party_rows_rejected_until_official_source_found",
            "source_contains_plan_count": "true_but_third_party_not_accepted",
            "collector_note": "Third-party summaries include 广西 plan rows but no first-party official source was surfaced in this pass.",
            "collector_confidence": "T4_third_party_plan_rows_rejected",
            "source_packet_status": "no_first_party_plan_source_found_this_batch",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "find official 无锡学院招生计划 page or supplied official PDF before any intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0128",
            "queue_rank": "128",
            "university_code": "10596",
            "university_name": "桂林理工大学",
            "source_url": "https://zj.glut.edu.cn/info/1066/2561.htm|https://zj.glut.edu.cn/index.htm",
            "source_owner": "桂林理工大学招生网",
            "source_title": "2025年全日制本专科招生章程 / 招生网",
            "published_date": "2025-06-08",
            "round_type": "official_context_no_plan_rows",
            "source_role": "official_context_not_structured_group_year_plan",
            "source_contains_plan_count": "false_for_group_rows",
            "collector_note": "Official charter states plan publication channels but no first-party group-level Guangxi ordinary physical table was found in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_group_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "search official 招生计划/区内计划 table or Guangxi考试院 group plan source; keep local context out of intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0129",
            "queue_rank": "129",
            "university_code": "10464",
            "university_name": "河南科技大学",
            "source_url": "https://zjc.haust.edu.cn/info/1142/25594.htm",
            "source_owner": "河南科技大学招生就业办公室",
            "source_title": "广西壮族自治区 / 河南科技大学2025年广西壮族自治区招生计划",
            "published_date": "2025-06-05",
            "round_type": "official_plan_table_candidate",
            "source_role": "official_plan_source_candidate_needs_cache_parse",
            "source_contains_group_code": "not_visible_in_search_preview_until_parse",
            "source_contains_plan_count": "true",
            "collector_note": "Official province plan page contains 广西 rows and plan counts in search preview; cache/parse is the next clean step.",
            "collector_confidence": "T1_official_plan_candidate_parse_ready_after_cache",
            "source_packet_status": "official_plan_candidate_discovered_not_cached",
            "next_action": "cache official Guangxi page and parse ordinary physical rows; verify whether group code is printed or absent.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0130",
            "queue_rank": "130",
            "university_code": "11647",
            "university_name": "浙江传媒学院",
            "source_url": "https://xxgk.cuz.edu.cn/info/1008/1789.htm|https://zsw.cuz.edu.cn/",
            "source_owner": "浙江传媒学院信息公开网/本科招生网",
            "source_title": "2025年本科生招生章程及特殊类型招生办法 / 本科招生网",
            "published_date": "2025-10-27",
            "round_type": "existing_official_index_and_portal_carried_forward",
            "source_role": "existing_candidate_no_guangxi_rows_yet",
            "source_contains_plan_count": "not_in_cached_html",
            "special_type_detected": "art/special materials must stay isolated",
            "raw_file_path": "raw_sources/reference_trend/batch6_official/cuz_info_1008_1789.html|raw_sources/reference_trend/batch6_official/cuz_zsw_root.html",
            "collector_note": "Earlier batch cached official information-disclosure page and admissions portal root; no Guangxi ordinary physical structured rows surfaced.",
            "collector_confidence": "T2_existing_official_index_needs_asset_or_endpoint_drilldown",
            "source_packet_status": "existing_official_index_cached_no_guangxi_rows",
            "requires_network": "false_for_this_batch_existing_cache;true_for_future_endpoint_drilldown",
            "eligible_for_intake_preview": "false_until_pdf_or_plan_asset_rows_return",
            "next_action": "drill official viewer assets or endpoint if approved; do not ingest index text.",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(raw_rows, start=1)]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["source_packet_status"]) for row in rows)
    by_conf = Counter(str(row["collector_confidence"]) for row in rows)
    return [
        {"metric": "batch13_preview_rows", "value": len(rows), "note": "Queue ranks 111-130 compressed by duplicate school groups where appropriate."},
        {"metric": "queue_rank_coverage", "value": "111-130", "note": "All listed queue ranks are represented."},
        {"metric": "official_plan_candidate_rows", "value": sum("official_plan_candidate" in str(row["source_packet_status"]) or "official_plan_detail_candidate" in str(row["source_packet_status"]) or "official_plan_image_candidate" in str(row["source_packet_status"]) or "official_plan_index" in str(row["source_packet_status"]) for row in rows), "note": "Rows with first-party plan route candidates."},
        {"metric": "existing_carry_forward_rows", "value": sum("existing_" in str(row["source_packet_status"]) for row in rows), "note": "Prior noncanonical source state carried forward without refetch."},
        {"metric": "third_party_rejected_rows", "value": sum("third_party" in str(row["source_role"]) for row in rows), "note": "Search hits retained only as rejected context."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery only; no source-packet parse accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year rows opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "ML/canonical remains closed."},
        {"metric": "requires_manual_approval_rows", "value": sum(str(row["requires_manual_approval"]).startswith("true") for row in rows), "note": "Image OCR/captcha routes are approval-gated."},
        *({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items())),
        *({"metric": f"confidence::{key}", "value": value, "note": ""} for key, value in sorted(by_conf.items())),
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    covered = set()
    for row in rows:
        for rank in str(row["queue_rank"]).split("|"):
            covered.add(rank)
    expected = {str(i) for i in range(111, 131)}
    return [
        {
            "check": "queue_rank_111_130_covered",
            "status": "PASS" if expected <= covered else "FAIL",
            "detail": "All batch13 queue ranks represented, including duplicate university groups.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "false" for row in rows) else "FAIL",
            "detail": "Discovery rows only; no intake opened.",
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
            "check": "third_party_rows_rejected",
            "status": "PASS" if all(row["eligible_for_intake_preview"] == "false" for row in rows if "third_party" in str(row["source_role"])) else "FAIL",
            "detail": "Third-party rows are not eligible for intake.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "queue_rank": row["queue_rank"],
            "university_name": row["university_name"],
            "exclusion_scope": "reference_trend_pool_and_calibration",
            "exclusion_reason": row["source_packet_status"],
            "required_resolution": row["next_action"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 P0 Official Source Discovery Batch 13",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: queue ranks 111-130 from the plan source packet queue.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Key findings:",
    ]
    for row in rows:
        lines.append(
            f"- {row['university_name']} ({row['queue_rank']}): {row['collector_confidence']}; {row['source_packet_status']}."
        )
    lines.extend(
        [
            "",
            "Boundary:",
            "- This is source discovery only.",
            "- No remote asset cache, OCR, browser/form replay, source-packet parse, reference trend intake, canonical, or ML output is opened.",
            "- Third-party summaries are retained only as rejected context until first-party sources are found.",
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
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "queue_rank", "university_name", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup)

    marker = "## 50. 2026-05-16 P0/P1 官方来源发现 batch 13"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch13 官方来源发现预览：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：queue rank 111-130。集美大学、青海大学、华侨大学、哈尔滨医科大学、四川轻化工大学、安徽工业大学、河南科技大学形成一方官方计划候选，下一步可缓存明细页/图片/附件后做 source-packet parse preview；广东海洋大学、浙江传媒学院承接既有非 canonical/approval-gated 状态；陕西科技大学、南京工程学院、无锡学院本轮只找到第三方或媒体上下文，已明确拒绝进入 intake；青岛理工大学、上海应用技术大学、成都大学、桂林理工大学目前只有官方章程/门户上下文，不能作为计划行来源。

准入边界：本轮只生成 source discovery preview、QA 和 exclusion；所有行 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先缓存/解析河南科技大学、华侨大学、四川轻化工大学、哈尔滨医科大学；青海大学和安徽工业大学图片/OCR 路线需审批。
""",
    )


if __name__ == "__main__":
    main()
