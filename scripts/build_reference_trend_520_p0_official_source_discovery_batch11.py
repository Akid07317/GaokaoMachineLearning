#!/usr/bin/env python3
"""Write batch-11 official source discovery preview for P0 queue rows.

This batch covers queue ranks 76-90. It records official source candidates
found through normal web discovery and keeps every row in source-packet preview
only: no reference-pool intake, no canonical, no ML.
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

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch11_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch11_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch11_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch11_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch11.md"
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
        "source_id": f"reference_trend_520_p0_batch11_{idx:04d}",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "raw_file_path": "",
        "intended_layer": "reference_trend_source_packet_preview_only",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch11_{idx:04d}",
    }
    enriched.update(row)
    return enriched


def build_rows() -> list[dict[str, object]]:
    rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0076",
            "queue_rank": "76",
            "university_code": "10424",
            "university_name": "山东科技大学",
            "source_url": "https://zs.sdust.edu.cn/info/1042/4420.htm|https://zs.sdust.edu.cn/__local/9/C5/43/9C6B02E1D7D86C60EE197EC373F_325C45C7_32086.pdf",
            "source_owner": "山东科技大学招生网",
            "source_title": "山东科技大学2025年分省本科招生计划",
            "published_date": "2025-06-20",
            "round_type": "official_plan_article_and_pdf_discovered",
            "source_role": "official_pdf_plan_candidate_needs_parse",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "special_type_detected": "may contain normal/cooperation/art rows; isolate after parse",
            "collector_note": "Official招生计划 index exposes the 2025 plan article; web search exposes the attached official PDF. Not cached in this run.",
            "collector_confidence": "T2_official_pdf_plan_candidate_not_cached",
            "source_packet_status": "official_pdf_plan_candidate_discovered_not_cached",
            "requires_network": "true_for_pdf_cache",
            "requires_manual_approval": "false_for_normal_pdf_cache",
            "eligible_for_intake_preview": "false_until_pdf_parse",
            "next_action": "cache official PDF if network route is available, then parse Guangxi ordinary physical rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0077",
            "queue_rank": "77",
            "university_code": "10456",
            "university_name": "山东财经大学",
            "source_url": "https://www.eol.cn/shandong/sdgd/202506/t20250624_2676632.shtml",
            "source_owner": "中国教育在线",
            "source_title": "7255人，山东财经大学2025年招生计划发布",
            "published_date": "2025-06-24",
            "round_type": "third_party_plan_reference_found_no_first_party",
            "source_role": "third_party_reference_not_accepted_as_source_packet",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true_in_third_party_unaccepted",
            "special_type_detected": "multiple Guangxi group rows in queue",
            "collector_note": "Search found third-party plan article mentioning Guangxi, but no first-party official plan source was found in this pass.",
            "collector_confidence": "T4_third_party_only_no_first_party_plan_source",
            "source_packet_status": "no_first_party_source_found_third_party_reference_only",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry first-party招生计划/本科招生网/official WeChat mirror search; do not ingest third-party plan rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0078",
            "queue_rank": "78",
            "university_code": "10456",
            "university_name": "山东财经大学",
            "source_url": "https://www.eol.cn/shandong/sdgd/202506/t20250624_2676632.shtml",
            "source_owner": "中国教育在线",
            "source_title": "7255人，山东财经大学2025年招生计划发布",
            "published_date": "2025-06-24",
            "round_type": "third_party_plan_reference_found_no_first_party",
            "source_role": "same_unaccepted_reference_as_rank_77",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true_in_third_party_unaccepted",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "collector_note": "Duplicate school context for rank 77/78. No first-party source accepted.",
            "collector_confidence": "T4_third_party_only_no_first_party_plan_source",
            "source_packet_status": "no_first_party_source_found_third_party_reference_only",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "deduplicate with rank 77 during next official-source retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0079",
            "queue_rank": "79",
            "university_code": "10566",
            "university_name": "广东海洋大学",
            "source_url": "https://zsjy.gdou.edu.cn/info/1175/1335.htm",
            "source_owner": "广东海洋大学招生网",
            "source_title": "广东海洋大学2025年普通本科招生计划",
            "published_date": "2025-06-24",
            "round_type": "official_plan_page_attachment_captcha",
            "source_role": "official_plan_attachment_candidate_needs_approval_or_manual_download",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "true_in_attachment_unparsed",
            "special_type_detected": "two Guangxi queue groups; attachment may mix physical/history/art rows",
            "collector_note": "Official page lists two PDF attachments. The attachment endpoint asks for verification code, so it is held and not terminal-cached.",
            "collector_confidence": "T2_official_attachment_captcha_blocked",
            "source_packet_status": "official_plan_page_found_attachment_captcha_blocked",
            "requires_network": "true_for_attachment_cache",
            "requires_manual_approval": "true_for_captcha_or_browser_download",
            "eligible_for_intake_preview": "false_until_attachment_cached_and_parsed",
            "next_action": "with approval/manual download, cache attachments and parse Guangxi ordinary physical rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0080",
            "queue_rank": "80",
            "university_code": "10566",
            "university_name": "广东海洋大学",
            "source_url": "https://zsjy.gdou.edu.cn/info/1175/1335.htm",
            "source_owner": "广东海洋大学招生网",
            "source_title": "广东海洋大学2025年普通本科招生计划",
            "published_date": "2025-06-24",
            "round_type": "official_plan_page_attachment_captcha",
            "source_role": "same_official_attachment_candidate_as_rank_79",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "true_in_attachment_unparsed",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "collector_note": "Duplicate school context for rank 79/80; same captcha-gated official attachment route.",
            "collector_confidence": "T2_official_attachment_captcha_blocked",
            "source_packet_status": "official_plan_page_found_attachment_captcha_blocked",
            "requires_network": "true_for_attachment_cache",
            "requires_manual_approval": "true_for_captcha_or_browser_download",
            "eligible_for_intake_preview": "false_until_attachment_cached_and_parsed",
            "next_action": "deduplicate with rank 79 after attachment is approved/cached",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0081",
            "queue_rank": "81",
            "university_code": "11656",
            "university_name": "广东石油化工学院",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "petrochemical school; ordinary/special group boundary unknown",
            "collector_note": "Search found school/news context but no first-party 2025 Guangxi ordinary本科计划 table/PDF suitable for source-packet intake.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry招生网 source discovery or use exam-authority score/rank only until official plan source appears",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0082",
            "queue_rank": "82",
            "university_code": "11656",
            "university_name": "广东石油化工学院",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "same_missing_source_as_rank_81",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "collector_note": "Duplicate school context for rank 81/82. No first-party source accepted.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "deduplicate with rank 81 during next official-source retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0083",
            "queue_rank": "83",
            "university_code": "10184",
            "university_name": "延边大学",
            "source_url": "https://zsb.ybu.edu.cn/info/1010/1663.htm",
            "source_owner": "延边大学招生网",
            "source_title": "延边大学2025年招生章程",
            "published_date": "2025-05-20",
            "round_type": "official_charter_context_only",
            "source_role": "official_context_not_structured_plan_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "minority/preparatory/cooperation boundaries mentioned in charter, but no Guangxi plan rows",
            "collector_note": "Official charter is first-party context, but not a 2025 Guangxi plan-row source packet.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "search official招生计划/录取查询/公众号 plan asset; do not parse charter as plan data",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0084",
            "queue_rank": "84",
            "university_code": "10184",
            "university_name": "延边大学",
            "source_url": "https://zsb.ybu.edu.cn/info/1010/1663.htm",
            "source_owner": "延边大学招生网",
            "source_title": "延边大学2025年招生章程",
            "published_date": "2025-05-20",
            "round_type": "official_charter_context_only",
            "source_role": "same_context_as_rank_83",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "collector_note": "Duplicate school context for rank 83/84; no structured Guangxi plan rows.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "deduplicate with rank 83 during next official-source retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0085",
            "queue_rank": "85",
            "university_code": "10577",
            "university_name": "惠州学院",
            "source_url": "https://zs.hzu.edu.cn/2025/0619/c4726a268719/page.htm|https://zs.hzu.edu.cn/_upload/article/files/a2/fb/9de322d54859b374cdc5f4e349e8/e1e67b91-542f-4e4e-8a05-52e12e565fa5.pdf",
            "source_owner": "惠州学院招生办公室",
            "source_title": "惠州学院2025年招生简章/2025年省外招生计划",
            "published_date": "2025-06-19",
            "round_type": "official_brochure_and_out_of_province_plan_pdf_discovered",
            "source_role": "official_pdf_plan_candidate_needs_parse",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "special_type_detected": "may include teacher-training/cooperation/special plan boundaries; isolate after parse",
            "collector_note": "Official招生简章 page links a brochure; search also exposes official省外招生计划 PDF. Not cached in this run.",
            "collector_confidence": "T2_official_pdf_plan_candidate_not_cached",
            "source_packet_status": "official_pdf_plan_candidate_discovered_not_cached",
            "requires_network": "true_for_pdf_cache",
            "requires_manual_approval": "false_for_normal_pdf_cache",
            "eligible_for_intake_preview": "false_until_pdf_parse",
            "next_action": "cache official PDF if network route is available, then parse Guangxi ordinary physical rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0086",
            "queue_rank": "86",
            "university_code": "10633",
            "university_name": "成都中医药大学",
            "source_url": "https://zs.cdutcm.edu.cn/Homecdutcm/List?ColumnCode=1058",
            "source_owner": "成都中医药大学招生网",
            "source_title": "招生章程/招生信息列表",
            "published_date": "",
            "round_type": "official_context_list_no_plan_rows",
            "source_role": "official_context_not_structured_plan_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "medical/cooperation specialty boundary may matter if plan source found",
            "collector_note": "Official admissions list/charter context found, but no first-party Guangxi plan table/PDF was found in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official plan source or accept exam-authority score/rank-only trend row if policy allows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0087",
            "queue_rank": "87",
            "university_code": "14389",
            "university_name": "成都师范学院",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "no_first_party_plan_source_found",
            "source_role": "official_source_not_found_in_web_pass",
            "source_contains_group_code": "unknown",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "teacher-training plan boundary unknown",
            "collector_note": "This pass found third-party plan pages only; no first-party 2025 Guangxi plan source accepted.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official admissions site/source discovery",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0088",
            "queue_rank": "88",
            "university_code": "10496",
            "university_name": "武汉轻工大学",
            "source_url": "https://xxgkw.whpu.edu.cn/zdgk1/zsksxx/zszcjtslxzsbf_fpc_fklzsjh.htm|https://xxgkw.whpu.edu.cn/info/1095/3606.htm",
            "source_owner": "武汉轻工大学信息公开网",
            "source_title": "武汉轻工大学2025年分省分专业招生计划数",
            "published_date": "2025-06-26",
            "round_type": "official_info_disclosure_plan_page_discovered",
            "source_role": "official_plan_page_candidate_cache_miss",
            "source_contains_group_code": "unknown_until_page_parse",
            "source_contains_plan_count": "true_in_plan_page_unparsed",
            "special_type_detected": "ordinary/art/cooperation boundary unknown until page parse",
            "collector_note": "Official信息公开 page lists the 2025分省分专业招生计划 entry. Direct page fetch had cache miss in web tool, so no local raw cache or parse was made.",
            "collector_confidence": "T2_official_plan_page_candidate_not_cached",
            "source_packet_status": "official_plan_page_candidate_discovered_not_cached",
            "requires_network": "true_for_page_cache",
            "requires_manual_approval": "false_for_normal_page_cache",
            "eligible_for_intake_preview": "false_until_page_cached_and_parsed",
            "next_action": "cache official plan page if network route is available, then parse Guangxi ordinary physical rows",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0089",
            "queue_rank": "89",
            "university_code": "10320",
            "university_name": "江苏师范大学",
            "source_url": "https://www.chinaschool.com.cn/i_region/i_10_jiangsu/a_24/2025/jihua-2025.html",
            "source_owner": "大学志",
            "source_title": "江苏师范大学－2025年招生计划",
            "published_date": "",
            "round_type": "third_party_plan_reference_found_no_first_party",
            "source_role": "third_party_reference_not_accepted_as_source_packet",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true_in_third_party_unaccepted",
            "special_type_detected": "normal/teacher-training boundaries unknown",
            "collector_note": "Search found third-party plan reference only. It is not accepted as a first-party source packet.",
            "collector_confidence": "T4_third_party_only_no_first_party_plan_source",
            "source_packet_status": "no_first_party_source_found_third_party_reference_only",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official本科招生网/省外招生计划 source discovery",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0090",
            "queue_rank": "90",
            "university_code": "10075",
            "university_name": "河北大学",
            "source_url": "https://www.dxsbb.com/news/101131.html",
            "source_owner": "大学生必备网",
            "source_title": "2025河北大学招生计划-各专业招生人数是多少",
            "published_date": "",
            "round_type": "third_party_plan_reference_found_no_first_party",
            "source_role": "third_party_reference_not_accepted_as_source_packet",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true_in_third_party_unaccepted",
            "special_type_detected": "multi-group ordinary boundary unknown",
            "collector_note": "Search found third-party plan reference only. It is not accepted as a first-party source packet.",
            "collector_confidence": "T4_third_party_only_no_first_party_plan_source",
            "source_packet_status": "no_first_party_source_found_third_party_reference_only",
            "requires_network": "true_for_retry",
            "requires_manual_approval": "false",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official本科招生网/招生计划 source discovery",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(rows, start=1)]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["source_packet_status"]) for row in rows)
    by_confidence = Counter(str(row["collector_confidence"]) for row in rows)
    official_candidate = sum("official" in str(row["collector_confidence"]) and "context_only" not in str(row["collector_confidence"]) for row in rows)
    rollup = [
        {"metric": "discovery_rows", "value": len(rows), "note": "Queue ranks 76-90, including duplicate-school group rows."},
        {"metric": "unique_universities", "value": len({row["university_name"] for row in rows}), "note": ""},
        {"metric": "official_plan_candidate_rows", "value": official_candidate, "note": "Needs cache/parse before intake."},
        {"metric": "first_party_context_only_rows", "value": sum("context_only" in str(row["collector_confidence"]) for row in rows), "note": "Official context but no plan rows."},
        {"metric": "third_party_or_missing_rows", "value": sum(str(row["collector_confidence"]).startswith("T4") for row in rows), "note": "Not accepted as source packets."},
        {"metric": "requires_manual_approval_rows", "value": sum(str(row["requires_manual_approval"]).startswith("true") for row in rows), "note": "Captcha/browser-gated attachment routes."},
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
            "check": "no_intake_preview_open",
            "status": "PASS" if all(str(row["eligible_for_intake_preview"]) == "false" or str(row["eligible_for_intake_preview"]).startswith("false_until") for row in rows) else "FAIL",
            "detail": "All rows require source cache/parse or first-party source recovery.",
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
            "check": "manual_approval_needed_for_captcha",
            "status": "PASS" if any(str(row["requires_manual_approval"]).startswith("true") for row in rows) else "WARN",
            "detail": "广东海洋大学 attachment route is captcha/browser gated.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "queue_rank": row["queue_rank"],
            "exclusion_scope": "reference_trend_pool_and_calibration",
            "exclusion_reason": row["source_packet_status"],
            "required_resolution": row["next_action"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 P0 Official Source Discovery Batch 11",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: queue ranks 76-90. This is source discovery only, not intake.",
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
            "- This batch does not parse any PDF, attachment, or HTML plan table.",
            "- All rows remain `reference_trend_source_packet_preview_only`.",
            "- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.",
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

    marker = "## 44. 2026-05-16 P0 官方来源发现 batch 11"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch11 官方来源发现预览：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：queue rank 76-90。山东科技大学命中官方招生计划文章和 PDF；广东海洋大学命中官方计划页但附件下载有验证码；惠州学院命中官方招生简章/省外计划 PDF 候选；武汉轻工大学命中官方信息公开计划入口但需缓存解析。延边大学、成都中医药大学仅命中官方章程/上下文，不是计划行来源；山东财经大学、广东石油化工学院、成都师范学院、江苏师范大学、河北大学本轮没有可接收的一方广西计划源或仅有第三方引用。

准入边界：本轮只生成 source discovery preview，未缓存/解析 PDF 或 HTML 表；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先缓存/解析山东科技大学、惠州学院、武汉轻工大学的官方计划候选；广东海洋附件需验证码/浏览器态批准。
""",
    )


if __name__ == "__main__":
    main()
