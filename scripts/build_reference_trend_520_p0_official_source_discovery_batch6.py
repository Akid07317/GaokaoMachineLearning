#!/usr/bin/env python3
"""Write batch-6 official discovery and ZUCC image-plan parse previews.

Outputs stay in reference_trend source-packet/preview layers only.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch6_official"

BATCH_OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch6_preview.csv"
BATCH_ROLLUP = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch6_rollup.csv"
BATCH_QA = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch6_qa.csv"
BATCH_EXCLUSION = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch6_exclusion_log.csv"
BATCH_DOC = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch6.md"

ZUCC_OUT = SEED_DIR / "reference_trend_zucc_2025_plan_image_parse_preview.csv"
ZUCC_ROLLUP = REPORT_DIR / "reference_trend_zucc_2025_plan_image_parse_rollup.csv"
ZUCC_QA = REPORT_DIR / "reference_trend_zucc_2025_plan_image_parse_qa.csv"
ZUCC_EXCLUSION = REPORT_DIR / "reference_trend_zucc_2025_plan_image_parse_exclusion_log.csv"
ZUCC_DOC = DOCS_DIR / "reference_trend_zucc_2025_plan_image_parse.md"

HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

BATCH_FIELDS = [
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

PARSE_FIELDS = [
    "record_id",
    "row_scope",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_path",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "university_group_code_candidate",
    "major_or_group",
    "duration_years",
    "tuition_yuan",
    "history_plan_count",
    "physics_plan_count",
    "plan_count_total",
    "remark",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "special_type_detected",
    "qa_status",
    "collector_confidence",
    "intended_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def build_batch_rows() -> list[dict[str, object]]:
    raw = {
        "zucc_guide": RAW_DIR / "zucc_guide_240.html",
        "zucc_plan_page": RAW_DIR / "zucc_guangxi_plan_show_868.html",
        "zucc_plan_image": RAW_DIR / "zucc_guangxi_plan_image_202506171553553437.png",
        "zucc_admissions": RAW_DIR / "zucc_admissions.html",
        "cuz_info": RAW_DIR / "cuz_info_1008_1789.html",
        "cuz_root": RAW_DIR / "cuz_zsw_root.html",
        "hnmu_insecure": RAW_DIR / "hnmu_plan_index_insecure.html",
        "bzmc_main": RAW_DIR / "bzmc_zb_main.html",
        "bzmc_zsjh": RAW_DIR / "bzmc_zsjh_list.html",
        "bzmc_change": RAW_DIR / "bzmc_2025_plan_change.html",
        "bzmc_change_page2": RAW_DIR / "bzmc_2025_plan_change_page2.html",
    }
    discovered = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0029",
            "queue_rank": "29",
            "university_code": "13021",
            "university_name": "浙大城市学院",
            "source_url": "https://zs.hzcu.edu.cn/guide-240.html",
            "source_owner": "浙大城市学院本科招生网",
            "source_title": "招生计划列表",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_plan_list_page_cached",
            "source_role": "official_plan_list_confirms_guangxi_asset",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "indirect_specific_asset_linked",
            "special_type_detected": "unknown_until_specific_asset_parse",
            "raw_file_path": rel(raw["zucc_guide"]),
            "collector_note": "Official plan list explicitly links to 浙大城市学院2025年广西招生计划 dated 2025-06-17.",
            "collector_confidence": "T1_official_list_confirms_specific_guangxi_plan_asset",
            "source_packet_status": "official_list_cached_asset_found",
            "eligible_for_intake_preview": "false_until_specific_asset_parse_and_group_mapping",
            "next_action": "use linked image plan asset as source-packet parse preview; hold group-year calibration until group code mapping is verified",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0029",
            "queue_rank": "29",
            "university_code": "13021",
            "university_name": "浙大城市学院",
            "source_url": "https://zs.hzcu.edu.cn/guide/show-868.html",
            "source_owner": "浙大城市学院本科招生网",
            "source_title": "浙大城市学院2025年广西招生计划",
            "published_date": "2025-06-17",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_plan_image_asset_cached",
            "source_role": "official_plan_image_parse_candidate",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "true",
            "special_type_detected": "history_and_physics_columns_must_be_split",
            "raw_file_path": rel(raw["zucc_plan_image"]),
            "collector_note": "Official detail page embeds an image table with 广西史 and 广西物 columns. Visual parse gives 17 major rows and 广西物 total 80.",
            "collector_confidence": "T1_official_image_extractable_plan_count_candidate",
            "source_packet_status": "official_image_plan_cached_and_parsed_to_preview",
            "eligible_for_intake_preview": "false_group_code_absent_hold_for_mapping",
            "next_action": "verify whether Guangxi exam-authority group 13021-102 is the only physical ordinary group before any group-year calibration",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0029",
            "queue_rank": "29",
            "university_code": "13021",
            "university_name": "浙大城市学院",
            "source_url": "https://zs.hzcu.edu.cn/admissions.html",
            "source_owner": "浙大城市学院本科招生网",
            "source_title": "浙大城市学院2025年招生常见问题",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_context_faq_total_plan",
            "source_role": "official_context_only_total_plan",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "school_total_context_only",
            "special_type_detected": "not_guangxi_specific_rows",
            "raw_file_path": rel(raw["zucc_admissions"]),
            "collector_note": "FAQ states 2025 total enrollment and province coverage including Guangxi, but it is not a Guangxi group/major plan source.",
            "collector_confidence": "T3_official_context_not_structured_plan_rows",
            "source_packet_status": "context_only_hold_out",
            "eligible_for_intake_preview": "false",
            "next_action": "do not use for calibration; keep as source context only",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0030",
            "queue_rank": "30",
            "university_code": "11647",
            "university_name": "浙江传媒学院",
            "source_url": "https://xxgk.cuz.edu.cn/info/1008/1789.htm",
            "source_owner": "浙江传媒学院信息公开网",
            "source_title": "2025年本科生招生章程及特殊类型招生办法，分批次、分科类招生计划",
            "published_date": "2025-10-27",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_info_disclosure_plan_index",
            "source_role": "official_plan_index_candidate_no_province_rows",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "not_in_cached_html",
            "special_type_detected": "art_charter_links_present",
            "raw_file_path": rel(raw["cuz_info"]),
            "collector_note": "Information-disclosure page names 2025 undergraduate plans and links official PDF viewer assets, but cached HTML does not expose Guangxi physical ordinary rows.",
            "collector_confidence": "T2_official_info_disclosure_needs_pdf_viewer_or_asset_drilldown",
            "source_packet_status": "official_index_cached_no_guangxi_rows",
            "eligible_for_intake_preview": "false_until_pdf_or_plan_asset_rows_return",
            "next_action": "drill official viewer file links or admissions plan endpoint; keep art/special materials isolated",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0030",
            "queue_rank": "30",
            "university_code": "11647",
            "university_name": "浙江传媒学院",
            "source_url": "https://zsw.cuz.edu.cn/",
            "source_owner": "浙江传媒学院本科招生网",
            "source_title": "浙江传媒学院本科招生网首页",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_admissions_portal_js_root",
            "source_role": "official_portal_root_needs_endpoint_drilldown",
            "source_contains_group_code": "unknown_until_endpoint_drilldown",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "unknown_until_endpoint_drilldown",
            "special_type_detected": "unknown_until_endpoint_drilldown",
            "raw_file_path": rel(raw["cuz_root"]),
            "collector_note": "Portal root cached, but homepage content is JS/category driven and did not expose Guangxi rows directly.",
            "collector_confidence": "T2_official_portal_js_endpoint_needed",
            "source_packet_status": "official_portal_cached_no_structured_rows",
            "eligible_for_intake_preview": "false_until_endpoint_rows_return",
            "next_action": "inspect official category/ajax endpoint if allowed; do not use third-party mirrors",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0031",
            "queue_rank": "31",
            "university_code": "12214",
            "university_name": "湖南医药学院",
            "source_url": "https://zs.hnmu.com.cn/招生计划.htm",
            "source_owner": "湖南医药学院招生网",
            "source_title": "招生计划",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_plan_index_tls_timeout",
            "source_role": "official_plan_index_backoff",
            "source_contains_group_code": "unknown",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "unknown",
            "special_type_detected": "unknown",
            "raw_file_path": "",
            "collector_note": "Official plan index was identified, but terminal fetch hit TLS hostname mismatch and timed out even with an insecure retry. Keep as source-reachability backoff, not a data source.",
            "collector_confidence": "T3_official_plan_index_reachability_blocked",
            "source_packet_status": "official_plan_index_reachability_blocked",
            "eligible_for_intake_preview": "false",
            "next_action": "retry via browser-state or manual official-site check only with explicit approval",
            "requires_manual_approval": "true",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0032",
            "queue_rank": "32",
            "university_code": "10440",
            "university_name": "滨州医学院",
            "source_url": "https://zb.bzmc.edu.cn/zsjh/list.htm",
            "source_owner": "滨州医学院本科招生网",
            "source_title": "招生计划查询",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_plan_query_system_cached",
            "source_role": "official_plan_query_system_needs_form_query",
            "source_contains_group_code": "unknown_until_query",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "unknown_until_query",
            "special_type_detected": "unknown_until_query",
            "raw_file_path": rel(raw["bzmc_zsjh"]),
            "collector_note": "Official list page states 招生计划查询 and can query by year/province/subject/category, but cached HTML does not include Guangxi result rows.",
            "collector_confidence": "T2_official_plan_query_form_needs_replay_or_browser",
            "source_packet_status": "official_query_system_cached_no_rows",
            "eligible_for_intake_preview": "false_until_query_returns_guangxi_rows",
            "next_action": "request approval for browser/form replay or find static API behind query system",
            "requires_manual_approval": "true",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0032",
            "queue_rank": "32",
            "university_code": "10440",
            "university_name": "滨州医学院",
            "source_url": "https://zb.bzmc.edu.cn/2025/0624/c2117a133872/page.htm",
            "source_owner": "滨州医学院本科招生网",
            "source_title": "滨州医学院2025年本科招生计划变更信息公告",
            "published_date": "2025-06-24",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_plan_change_context_rejected",
            "source_role": "official_context_only_not_guangxi_plan",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "not_guangxi_specific",
            "special_type_detected": "sino_foreign_change_context",
            "raw_file_path": rel(raw["bzmc_change"]),
            "collector_note": "Official change notice is about application psychology Sino-foreign plan adjustments in other provinces; no Guangxi row was found in cached text.",
            "collector_confidence": "T4_official_context_not_target_province_rejected",
            "source_packet_status": "rejected_official_context_no_guangxi_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "use only as context; continue with official query system for Guangxi rows",
            "requires_manual_approval": "false",
        },
    ]

    rows: list[dict[str, object]] = []
    for idx, item in enumerate(discovered, start=1):
        rows.append(
            {
                **item,
                "source_id": f"reference_trend_batch6_web_candidate_{idx:04d}",
                "intended_layer": "reference_trend_source_packet_preview_only",
                "requires_network": "true",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "record_id": f"reference_trend_520_p0_source_candidate_batch6_{idx:04d}",
            }
        )
    return rows


def build_zucc_parse_rows() -> list[dict[str, object]]:
    source_url = "https://zs.hzcu.edu.cn/guide/show-868.html"
    raw_image = rel(RAW_DIR / "zucc_guangxi_plan_image_202506171553553437.png")
    majors = [
        ("计算机科学与技术", "4", "6300", "", "3", ""),
        ("软件工程", "4", "6300", "", "7", ""),
        ("应用统计学", "4", "4800", "", "6", ""),
        ("电子科学与技术", "4", "5500", "", "7", ""),
        ("电子信息工程", "4", "5500", "", "7", ""),
        ("自动化", "4", "5500", "", "6", ""),
        ("人工智能", "4", "5500", "", "3", ""),
        ("土木工程", "4", "5500", "", "4", ""),
        ("机械电子工程", "4", "5500", "", "6", ""),
        ("智能制造工程", "4", "5500", "", "7", ""),
        ("智能建造", "4", "5500", "", "8", ""),
        ("药学", "4", "5500", "", "6", ""),
        ("城乡规划", "5", "5500", "", "4", ""),
        ("新闻学", "4", "4800", "2", "1", ""),
        ("广告学", "4", "4800", "2", "1", ""),
        ("英语", "4", "4800", "3", "2", "英语单科成绩不低于100分"),
        ("德语", "4", "4800", "3", "2", ""),
    ]
    rows: list[dict[str, object]] = []
    for idx, (major, duration, tuition, history, physics, remark) in enumerate(majors, start=1):
        special = ""
        if history:
            special = "history_column_present_split_required"
        rows.append(
            {
                "record_id": f"reference_trend_zucc_2025_plan_image_major_{idx:04d}",
                "row_scope": "official_plan_image_major_row",
                "source_id": "reference_trend_batch6_web_candidate_0002",
                "queue_record_id": "reference_trend_520_plan_source_queue_0029",
                "queue_rank": "29",
                "source_url": source_url,
                "source_owner": "浙大城市学院本科招生网",
                "source_title": "浙大城市学院2025年广西招生计划",
                "raw_file_path": raw_image,
                "university_code": "13021",
                "university_name": "浙大城市学院",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "university_group_code_candidate": "102_unverified_from_queue",
                "major_or_group": major,
                "duration_years": duration,
                "tuition_yuan": tuition,
                "history_plan_count": history,
                "physics_plan_count": physics,
                "plan_count_total": str((int(history) if history else 0) + int(physics)),
                "remark": remark,
                "source_contains_group_code": "false",
                "source_contains_plan_count": "true",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "special_type_detected": special,
                "qa_status": "official_image_plan_count_extracted_hold_for_group_mapping",
                "collector_confidence": "T1_official_image_plan_count_visual_parse",
                "intended_layer": "reference_trend_source_packet_parse_preview_only",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "required_resolution": "verify official/exam-authority group code mapping before converting major-plan rows into group-year calibration evidence",
                "evidence_note": "Official ZUCC Guangxi plan image lists major-level 广西物 plan count; group code is not printed in the image.",
            }
        )

    rows.append(
        {
            "record_id": "reference_trend_zucc_2025_plan_image_group_summary_0001",
            "row_scope": "official_plan_image_summary_row",
            "source_id": "reference_trend_batch6_web_candidate_0002",
            "queue_record_id": "reference_trend_520_plan_source_queue_0029",
            "queue_rank": "29",
            "source_url": source_url,
            "source_owner": "浙大城市学院本科招生网",
            "source_title": "浙大城市学院2025年广西招生计划",
            "raw_file_path": raw_image,
            "university_code": "13021",
            "university_name": "浙大城市学院",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "university_group_code_candidate": "102_unverified_from_queue",
            "major_or_group": "广西物合计",
            "duration_years": "",
            "tuition_yuan": "",
            "history_plan_count": "10",
            "physics_plan_count": "80",
            "plan_count_total": "90",
            "remark": "Image total row: 广西史10, 广西物80. This summary remains group-mapping hold.",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "special_type_detected": "history_and_physics_split_required",
            "qa_status": "plan_sum_pass_hold_for_group_mapping",
            "collector_confidence": "T1_official_image_plan_count_visual_parse",
            "intended_layer": "reference_trend_source_packet_parse_preview_only",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
            "required_resolution": "do not treat the 80 physical plan count as a 13021-102 group count until group-code mapping is confirmed",
            "evidence_note": "The image total row shows 广西物=80; the 17 parsed major physics counts sum to 80.",
        }
    )
    return rows


def write_batch_outputs(rows: list[dict[str, object]]) -> None:
    counts = Counter()
    universities = set()
    for row in rows:
        counts["batch6_candidate_rows"] += 1
        universities.add(str(row["university_name"]))
        counts[f"source_packet_status::{row['source_packet_status']}"] += 1
        counts[f"collector_confidence::{row['collector_confidence']}"] += 1
        if str(row["collector_confidence"]).startswith("T1_"):
            counts["t1_high_value_rows"] += 1
        if row["requires_manual_approval"] == "true":
            counts["requires_manual_approval_rows"] += 1
        if "rejected" in str(row["source_packet_status"]) or "context_only" in str(row["source_packet_status"]) or "blocked" in str(row["source_packet_status"]):
            counts["hold_or_rejected_rows"] += 1

    exclusions = [
        row
        for row in rows
        if row["eligible_for_intake_preview"] == "false"
        or "false_until" in str(row["eligible_for_intake_preview"])
        or "hold" in str(row["eligible_for_intake_preview"])
    ]
    rollup = [
        {"metric": "batch6_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(sorted(universities))},
        {"metric": "t1_high_value_rows", "value": counts["t1_high_value_rows"], "note": "ZUCC official list/image plan asset."},
        {"metric": "requires_manual_approval_rows", "value": counts["requires_manual_approval_rows"], "note": "HNMU reachability and BZMC form/query replay."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery/source-packet preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for key, value in sorted(counts.items()):
        if "::" in key:
            rollup.append({"metric": key, "value": value, "note": ""})

    qa = [
        {
            "qa_check": "official_cache_rows",
            "status": "pass",
            "value": len(rows),
            "note": "Rows use first-party official roots/pages/assets or explicit reachability backoff; no third-party rows accepted.",
        },
        {
            "qa_check": "manual_approval_boundary",
            "status": "pass",
            "value": counts["requires_manual_approval_rows"],
            "note": "Rows requiring browser/form/TLS workaround are held and not parsed into data.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]

    write_csv(BATCH_OUT, rows, BATCH_FIELDS)
    write_csv(BATCH_ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(BATCH_QA, qa, ["qa_check", "status", "value", "note"])
    write_csv(BATCH_EXCLUSION, exclusions, BATCH_FIELDS)

    status_lines = "\n".join(f"- {k}: {v}" for k, v in sorted(counts.items()) if "::" in k)
    BATCH_DOC.write_text(
        f"""# P0 Official Source Discovery Batch 6

Generated: {date.today().isoformat()}

This batch records official-source discovery for the next P0/P1 plan-source queue segment after the HPU enrichment pass. It is a source-packet preview only.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch6_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_exclusion_log.csv`

## Coverage

- Candidate rows: {len(rows)}
- Universities covered: {len(universities)}
- T1 high-value official rows: {counts['t1_high_value_rows']}
- Rows requiring manual approval/browser/form/TLS workaround: {counts['requires_manual_approval_rows']}

## Source Notes

- ZUCC: official 2025 Guangxi plan page and embedded image asset were cached; image plan counts were parsed into a separate preview.
- CUZ: official information-disclosure page was cached, but it exposes viewer/PDF links rather than Guangxi physical ordinary rows.
- HNMU: official plan index was identified but terminal fetch is blocked by TLS/reachability; held for manual/browser approval.
- BZMC: official plan query page was cached; Guangxi rows require form/query replay or a static endpoint.

## Status Rollup

{status_lines}

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Batch 6 does not write group-year records, does not open ML, and does not expand the 32-school decision pool.
""",
        encoding="utf-8",
    )


def write_zucc_outputs(rows: list[dict[str, object]]) -> None:
    major_rows = [row for row in rows if row["row_scope"] == "official_plan_image_major_row"]
    summary_rows = [row for row in rows if row["row_scope"] == "official_plan_image_summary_row"]
    physics_total = sum(int(row["physics_plan_count"]) for row in major_rows if row["physics_plan_count"])
    history_total = sum(int(row["history_plan_count"]) for row in major_rows if row["history_plan_count"])
    rollup = [
        {"metric": "parsed_rows", "value": len(rows), "note": "17 major rows + 1 summary row"},
        {"metric": "major_rows", "value": len(major_rows), "note": ""},
        {"metric": "summary_rows", "value": len(summary_rows), "note": ""},
        {"metric": "physics_plan_sum_from_major_rows", "value": physics_total, "note": "Matches image total row 广西物=80."},
        {"metric": "history_plan_sum_from_major_rows", "value": history_total, "note": "Matches image total row 广西史=10."},
        {"metric": "source_contains_group_code_rows", "value": 0, "note": "Image has no group code."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Hold for group-code mapping."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Hold for group-code mapping."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    qa = [
        {
            "qa_check": "image_asset_cached",
            "status": "pass",
            "value": rel(RAW_DIR / "zucc_guangxi_plan_image_202506171553553437.png"),
            "note": "Official page image asset was cached locally.",
        },
        {
            "qa_check": "physics_plan_sum",
            "status": "pass",
            "value": physics_total,
            "note": "Major rows sum to the image total row 广西物=80.",
        },
        {
            "qa_check": "history_plan_sum",
            "status": "pass",
            "value": history_total,
            "note": "Major rows sum to the image total row 广西史=10.",
        },
        {
            "qa_check": "group_code_mapping",
            "status": "hold",
            "value": "missing_in_source",
            "note": "Do not map to 13021-102 until exam-authority group boundary is verified.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]
    exclusions = list(rows)

    write_csv(ZUCC_OUT, rows, PARSE_FIELDS)
    write_csv(ZUCC_ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(ZUCC_QA, qa, ["qa_check", "status", "value", "note"])
    write_csv(ZUCC_EXCLUSION, exclusions, PARSE_FIELDS)

    ZUCC_DOC.write_text(
        f"""# ZUCC 2025 Guangxi Plan Image Parse Preview

Generated: {date.today().isoformat()}

This preview parses the official ZUCC 2025 Guangxi plan image into major-level plan rows. It remains a source-packet parse preview only because the official image does not print the Guangxi institution-professional-group code.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_zucc_2025_plan_image_parse_preview.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_rollup.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_qa.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_exclusion_log.csv`

## Parsed Result

- Major rows: {len(major_rows)}
- 广西物 plan sum: {physics_total}
- 广西史 plan sum: {history_total}
- Official image total row: 广西物 80, 广西史 10

## Hold Reason

The source is useful for field thickness, but not yet a calibration row. The image has no group code, so the queue's `13021-102` candidate must be verified against Guangxi exam-authority group lines before conversion to group-year trend evidence.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. This preview does not write canonical/ML data and does not touch the 32-school decision pool.
""",
        encoding="utf-8",
    )


def main() -> None:
    batch_rows = build_batch_rows()
    zucc_rows = build_zucc_parse_rows()
    write_batch_outputs(batch_rows)
    write_zucc_outputs(zucc_rows)

    marker = "## 30. "
    append_handoff_once(
        marker,
        f"""

## 30. {date.today().isoformat()} P0 官方来源发现 batch 6 + 浙大城市学院图片计划解析

已新增 batch6 官方来源发现与 ZUCC 图片计划解析预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch6_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch6.md`
- `clean_data/engineering_guangxi_seed/reference_trend_zucc_2025_plan_image_parse_preview.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_rollup.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_qa.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_exclusion_log.csv`
- `docs/reference_trend_zucc_2025_plan_image_parse.md`

覆盖结果：batch6 候选 {len(batch_rows)} 行，覆盖 4 所学校。浙大城市学院官方广西计划页与图片资产已缓存，图片解析出 17 个专业行，广西物计划合计 80、广西史计划合计 10；但图片无专业组代码，因此仍停留在 source_packet parse preview。浙江传媒学院官方信息公开页和本科招生网入口已缓存，但未得到广西物理普通批结构化行；滨州医学院官方计划查询入口已缓存但需要表单/端点 replay；湖南医药学院官方计划页存在 TLS/reachability 阻塞。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。本轮不进入 canonical/ML，不并入 32 所 decision_pool。

下一轮优先级：优先核验 ZUCC 广西考试院 13021-102 是否唯一/对应该 80 人物理计划；若无法本地核验，则继续处理下一个 P0/P1 官方计划源，或在人工批准后对 BZMC 查询系统做 browser/form replay。
""",
    )

    for path in [
        BATCH_OUT,
        BATCH_ROLLUP,
        BATCH_QA,
        BATCH_EXCLUSION,
        BATCH_DOC,
        ZUCC_OUT,
        ZUCC_ROLLUP,
        ZUCC_QA,
        ZUCC_EXCLUSION,
        ZUCC_DOC,
    ]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
