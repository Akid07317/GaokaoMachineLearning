#!/usr/bin/env python3
"""Write batch-9 official source discovery preview for remaining P0 rows.

This batch uses web-verified official/source-owner URLs only. It writes
reference-trend source-packet/preview artifacts and keeps canonical/ML closed.
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

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch9_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch9_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch9_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch9_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch9.md"
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


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def common(row: dict[str, object], idx: int) -> dict[str, object]:
    enriched = {
        "source_id": f"reference_trend_520_p0_batch9_{idx:04d}",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "raw_file_path": "",
        "intended_layer": "reference_trend_source_packet_preview_only",
        "requires_network": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch9_{idx:04d}",
    }
    enriched.update(row)
    return enriched


def build_rows() -> list[dict[str, object]]:
    discovered = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0051",
            "queue_rank": "51",
            "university_code": "10681",
            "university_name": "云南师范大学",
            "source_url": "https://jh.ynnu.edu.cn/",
            "source_owner": "云南师范大学招生办公室",
            "source_title": "云南师范大学本科招生计划",
            "published_date": "",
            "round_type": "official_parameterized_plan_portal",
            "source_role": "official_plan_portal_parameterized_candidate",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "conditional_after_parameter_or_api_drilldown",
            "special_type_detected": "portal includes ordinary and special plan types; filter to 广西/2025/普通类/物理类 before use",
            "collector_note": "Official plan portal exposes province/year/type/subject selectors and search index confirms 广西 is available. Browser/API parameter drilldown is still needed because the fetched default page renders 云南/历史类 rows.",
            "collector_confidence": "T2_official_parameterized_plan_portal_needs_drilldown",
            "source_packet_status": "official_plan_portal_found_parameterized_not_parsed",
            "eligible_for_intake_preview": "false_until_guangxi_physics_rows_are_extracted",
            "next_action": "drill down portal/API for 广西 2025 普通类 物理类; hold if browser state or JS endpoint inspection is required",
            "requires_manual_approval": "false_for_web_discovery; true_if_browser_state_or_api_probe_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0052",
            "queue_rank": "52",
            "university_code": "11349",
            "university_name": "五邑大学",
            "source_url": "https://www.wyu.edu.cn/zsb/info/1042/5560.htm",
            "source_owner": "五邑大学招生办",
            "source_title": "〖权威发布〗五邑大学2025年外省招生计划情况",
            "published_date": "2025-06-17",
            "round_type": "official_image_plan_page",
            "source_role": "official_external_province_plan_image_candidate",
            "source_contains_group_code": "unknown_image_not_ocrd",
            "source_contains_plan_count": "true_in_images_unparsed",
            "special_type_detected": "external province plans shown as images; official page says final plans follow provincial exam authority",
            "collector_note": "Official招生办 page states 2025外省22省招生计划 and embeds province plan images. Guangxi rows are likely in images, but no OCR/browser image extraction is performed in this batch.",
            "collector_confidence": "T2_official_image_plan_candidate_needs_ocr_or_image_parse",
            "source_packet_status": "official_image_plan_page_found_not_ocrd",
            "eligible_for_intake_preview": "false_until_image_rows_are_extracted_and_mapped",
            "next_action": "extract embedded images or use official zsb.wyu.edu.cn plan system; keep queue ranks 52-54 tied to the same source packet",
            "requires_manual_approval": "true_if_browser_image_capture_or_ocr_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0053",
            "queue_rank": "53",
            "university_code": "11349",
            "university_name": "五邑大学",
            "source_url": "https://www.wyu.edu.cn/zsb/info/1042/5560.htm",
            "source_owner": "五邑大学招生办",
            "source_title": "〖权威发布〗五邑大学2025年外省招生计划情况",
            "published_date": "2025-06-17",
            "round_type": "official_image_plan_page",
            "source_role": "same_source_packet_as_queue_rank_52",
            "source_contains_group_code": "unknown_image_not_ocrd",
            "source_contains_plan_count": "true_in_images_unparsed",
            "special_type_detected": "same school has multiple Guangxi group rows in queue; no group-year allocation until image/system rows expose mapping",
            "collector_note": "Same official source as queue rank 52. This row is a duplicate source-packet pointer for the second 五邑大学 Guangxi group in the rank window.",
            "collector_confidence": "T2_official_image_plan_candidate_needs_ocr_or_image_parse",
            "source_packet_status": "official_image_plan_page_found_not_ocrd",
            "eligible_for_intake_preview": "false_until_image_rows_are_extracted_and_mapped",
            "next_action": "deduplicate with queue rank 52 during parse; do not infer group plan from image page until OCR/system extraction succeeds",
            "requires_manual_approval": "true_if_browser_image_capture_or_ocr_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0054",
            "queue_rank": "54",
            "university_code": "11349",
            "university_name": "五邑大学",
            "source_url": "https://www.wyu.edu.cn/zsb/info/1042/5560.htm",
            "source_owner": "五邑大学招生办",
            "source_title": "〖权威发布〗五邑大学2025年外省招生计划情况",
            "published_date": "2025-06-17",
            "round_type": "official_image_plan_page",
            "source_role": "same_source_packet_as_queue_rank_52",
            "source_contains_group_code": "unknown_image_not_ocrd",
            "source_contains_plan_count": "true_in_images_unparsed",
            "special_type_detected": "same school has multiple Guangxi group rows in queue; no group-year allocation until image/system rows expose mapping",
            "collector_note": "Same official source as queue rank 52. This row is a duplicate source-packet pointer for the third 五邑大学 Guangxi group in the rank window.",
            "collector_confidence": "T2_official_image_plan_candidate_needs_ocr_or_image_parse",
            "source_packet_status": "official_image_plan_page_found_not_ocrd",
            "eligible_for_intake_preview": "false_until_image_rows_are_extracted_and_mapped",
            "next_action": "deduplicate with queue rank 52 during parse; do not infer group plan from image page until OCR/system extraction succeeds",
            "requires_manual_approval": "true_if_browser_image_capture_or_ocr_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0056",
            "queue_rank": "56",
            "university_code": "10016",
            "university_name": "北京建筑大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "official_source_not_found_in_web_pass",
            "source_role": "no_first_party_plan_source_found",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "",
            "collector_note": "This pass found third-party/charter mirrors and Beijing-local plan context, but no first-party Guangxi 2025 plan table/PDF suitable for source-packet intake.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "eligible_for_intake_preview": "false",
            "next_action": "retry targeted first-party search on 北京建筑大学本科招生网 or use exam-authority group lines only",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0057",
            "queue_rank": "57",
            "university_code": "16401",
            "university_name": "北师香港浸会大学",
            "source_url": "https://uic.edu.cn/virtual_attach_file.vsb?afc=VM7l2bnlWVnzv4Ud8rfLm78M8l4oRf-VMRCsU87bLz7ZLRU0gihFp2hmCIa0MSybLkyPLYhVLRNaUzrfMmUboRr7LzNbLl-8MN-iLRMVMzWFnmnkUNCDoRAFL8VkMRNJv2nto4OeosrXCDMJgDTJQty0LzUDMSyPMR7DMkbw62W8c&e=.pdf&nid=14164&oid=1678407622&tid=1465",
            "source_owner": "北师香港浸会大学",
            "source_title": "北师香港浸会大学章程",
            "published_date": "",
            "round_type": "official_charter_pdf_context_only",
            "source_role": "official_charter_context_not_plan_table",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "joint-venture/internationalized university boundary; fee/major interpretation should stay separate",
            "collector_note": "Official UIC PDF/virtual attachment found as charter context. No Guangxi 2025 group/major plan table was exposed in this batch.",
            "collector_confidence": "T3_official_charter_pdf_context_only_no_plan_rows",
            "source_packet_status": "official_charter_pdf_context_only",
            "eligible_for_intake_preview": "false",
            "next_action": "find official Guangxi plan PDF/table or keep as score/rank-only reference row",
            "requires_manual_approval": "false_for_context; true_if_pdf_download_parse_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0058",
            "queue_rank": "58",
            "university_code": "10009",
            "university_name": "北方工业大学",
            "source_url": "https://bkzs.ncut.edu.cn/info/1013/2661.htm",
            "source_owner": "北方工业大学招生网",
            "source_title": "北方工业大学2025年本科分专业招生计划",
            "published_date": "2025-06-24",
            "round_type": "official_html_plan_table",
            "source_role": "official_plan_table_extractable_candidate",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true",
            "special_type_detected": "national cross-province table includes arts/ordinary rows; filter by ordinary physical-compatible majors before use",
            "collector_note": "Official HTML table contains a 广西 column in the 2025本科分专业招生计划. It appears extractable, but no Guangxi professional-group code is printed.",
            "collector_confidence": "T1_official_html_extractable_plan_table_candidate",
            "source_packet_status": "official_html_plan_table_found_extractable",
            "eligible_for_intake_preview": "conditional_after_source_packet_parse_and_group_mapping",
            "next_action": "parse official table into Guangxi plan rows; hold group-year calibration until group mapping is verified",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0059",
            "queue_rank": "59",
            "university_code": "10385",
            "university_name": "华侨大学",
            "source_url": "https://zsc.hqu.edu.cn/info/1024/7692.htm",
            "source_owner": "华侨大学招生信息网",
            "source_title": "华侨大学2025年普高本科分省分专业招生计划（境内版）",
            "published_date": "2025-06-20",
            "round_type": "official_plan_page_search_hit_403_on_open",
            "source_role": "official_plan_table_candidate_reachability_blocked",
            "source_contains_group_code": "unknown_until_cached",
            "source_contains_plan_count": "true_in_search_snippet_unparsed",
            "special_type_detected": "ordinary/art/special rows may coexist; source says provincial booklet is authoritative",
            "collector_note": "Search result on first-party zsc.hqu.edu.cn reports 广西 plan totals, but web open returned 403. Kept in reachability/backoff; do not scrape with headers/browser without approval.",
            "collector_confidence": "T2_official_plan_candidate_reachability_blocked",
            "source_packet_status": "official_plan_page_found_403_not_cached",
            "eligible_for_intake_preview": "false_until_official_page_cached_or_alternate_first_party_source_found",
            "next_action": "retry with approved browser/header route or locate alternate official attachment/list page",
            "requires_manual_approval": "true_for_browser_or_header_retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0060",
            "queue_rank": "60",
            "university_code": "10081",
            "university_name": "华北理工大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "official_source_not_found_in_web_pass",
            "source_role": "no_first_party_plan_source_found",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "",
            "collector_note": "This pass found third-party/mirror charter pages, but no first-party 华北理工大学 Guangxi 2025 plan table/PDF suitable for source-packet intake.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "eligible_for_intake_preview": "false",
            "next_action": "retry first-party domain search or use exam-authority group lines only",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0061",
            "queue_rank": "61",
            "university_code": "10406",
            "university_name": "南昌航空大学",
            "source_url": "https://zsw.nchu.edu.cn/index.php?act=view&article_id=J3rWGDJAY47y&module=article&param=53&sys=home",
            "source_owner": "南昌航空大学招生信息网",
            "source_title": "南昌航空大学2025年全国招生计划查询说明候选",
            "published_date": "",
            "round_type": "official_query_entry_context_only",
            "source_role": "official_plan_query_entry_not_structured",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "flight-tech/special major context appears in adjacent official pages; isolate if later parsed",
            "collector_note": "Official result states 2025各省分专业招生计划可在学校招生信息网查询, but this pass did not expose a structured Guangxi table.",
            "collector_confidence": "T3_official_query_entry_context_only_no_plan_rows",
            "source_packet_status": "official_query_entry_context_not_structured",
            "eligible_for_intake_preview": "false",
            "next_action": "inspect official query parameters/endpoints for 广西; keep rank 61 and 62 deduplicated by university",
            "requires_manual_approval": "true_if_form_or_browser_replay_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0062",
            "queue_rank": "62",
            "university_code": "10406",
            "university_name": "南昌航空大学",
            "source_url": "https://zsw.nchu.edu.cn/index.php?act=view&article_id=J3rWGDJAY47y&module=article&param=53&sys=home",
            "source_owner": "南昌航空大学招生信息网",
            "source_title": "南昌航空大学2025年全国招生计划查询说明候选",
            "published_date": "",
            "round_type": "official_query_entry_context_only",
            "source_role": "same_source_packet_as_queue_rank_61",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "collector_note": "Same official query-entry context as queue rank 61. No structured Guangxi plan rows exposed in this batch.",
            "collector_confidence": "T3_official_query_entry_context_only_no_plan_rows",
            "source_packet_status": "official_query_entry_context_not_structured",
            "eligible_for_intake_preview": "false",
            "next_action": "deduplicate with queue rank 61 during endpoint/form investigation",
            "requires_manual_approval": "true_if_form_or_browser_replay_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0064",
            "queue_rank": "64",
            "university_code": "10622",
            "university_name": "四川轻化工大学",
            "source_url": "https://rwxy.suse.edu.cn/2025/0626/c3555a197065/page.htm",
            "source_owner": "四川轻化工大学人文学院/学校官方域",
            "source_title": "四川轻化工大学2025年招生计划",
            "published_date": "2025-06-26",
            "round_type": "official_attachment_bundle_context",
            "source_role": "official_plan_attachment_bundle_candidate",
            "source_contains_group_code": "unknown_until_attachment_parse",
            "source_contains_plan_count": "true_in_attachment_bundle_unparsed",
            "special_type_detected": "attachment bundle may mix guide/charter/plan and in-Sichuan group materials; isolate province/batch rows",
            "collector_note": "Official-domain page says the 2025招生计划表 is among four attachments. Attachment parsing was not performed in this batch.",
            "collector_confidence": "T2_official_attachment_bundle_plan_candidate_needs_parse",
            "source_packet_status": "official_attachment_bundle_found_not_parsed",
            "eligible_for_intake_preview": "false_until_attachment_rows_are_extracted",
            "next_action": "locate/download official attachment or alternate招生办 page; parse only 广西/本科普通批/物理类 rows",
            "requires_manual_approval": "true_if_attachment_download_or_browser_needed",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(discovered, start=1)]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    universities = sorted({str(row["university_name"]) for row in rows if row.get("university_name")})
    t1_rows = [row for row in rows if str(row.get("collector_confidence", "")).startswith("T1_")]
    manual_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    rollup = [
        {"metric": "batch9_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "queue_ranks_covered", "value": ",".join(str(row["queue_rank"]) for row in rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(universities)},
        {"metric": "t1_high_value_rows", "value": len(t1_rows), "note": "|".join(str(row["university_name"]) for row in t1_rows)},
        {"metric": "requires_manual_approval_rows", "value": len(manual_rows), "note": "|".join(str(row["university_name"]) for row in manual_rows)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery/source-packet preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for key, count in sorted(Counter(str(row["collector_confidence"]) for row in rows).items()):
        rollup.append({"metric": f"collector_confidence::{key}", "value": count, "note": ""})
    for key, count in sorted(Counter(str(row["source_packet_status"]) for row in rows).items()):
        rollup.append({"metric": f"source_packet_status::{key}", "value": count, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    accepted_source_rows = [
        row for row in rows
        if row.get("source_url") or row.get("source_packet_status") == "no_official_source_found_in_batch"
    ]
    manual_count = sum(1 for row in rows if str(row.get("requires_manual_approval", "")).startswith("true"))
    return [
        {
            "qa_check": "rows_are_official_or_explicit_no_source_backoff",
            "status": "pass" if len(accepted_source_rows) == len(rows) else "warn",
            "value": len(accepted_source_rows),
            "note": "Rows are official first-party URLs, official-domain reachability/backoff, or explicit no-first-party-source findings.",
        },
        {
            "qa_check": "extractable_plan_candidates",
            "status": "pass",
            "value": sum("T1_" in str(row.get("collector_confidence", "")) for row in rows),
            "note": "Only T1 rows should be parsed next without browser/form replay.",
        },
        {
            "qa_check": "manual_approval_boundary",
            "status": "pass",
            "value": manual_count,
            "note": "Browser/form/header/image/OCR-needed rows are held and not parsed.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
        {
            "qa_check": "decision_pool_boundary",
            "status": "pass",
            "value": "closed",
            "note": "No merge into the 32-school decision_pool.",
        },
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    exclusions = []
    blocked_tokens = ["not_found", "context", "not_ocrd", "not_parsed", "403"]
    for row in rows:
        status = str(row.get("source_packet_status", ""))
        if any(token in status for token in blocked_tokens):
            exclusions.append(
                {
                    "record_id": row["record_id"],
                    "queue_rank": row["queue_rank"],
                    "university_name": row["university_name"],
                    "source_url": row["source_url"],
                    "exclusion_reason": status,
                    "recommended_next_action": row["next_action"],
                    "canonical_ml_entry_open": "false",
                }
            )
    return exclusions


def write_doc(rows: list[dict[str, object]]) -> None:
    t1 = [row for row in rows if str(row.get("collector_confidence", "")).startswith("T1_")]
    manual = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    no_source = [row for row in rows if row.get("source_packet_status") == "no_official_source_found_in_batch"]
    text = f"""# Reference Trend 520 P0 Official Source Discovery Batch 9

Generated: {date.today().isoformat()}

## Scope

This batch covers next P0 plan-source queue rows after batch8, mainly queue ranks 51-64 except rank 55, which already has a mapping workbench. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch9_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_exclusion_log.csv`

## Key Findings

- Candidate rows: {len(rows)}
- Queue ranks covered: {', '.join(str(row['queue_rank']) for row in rows)}
- Universities covered: {len({row['university_name'] for row in rows})}
- T1 extractable official candidates: {len(t1)} ({'、'.join(row['university_name'] for row in t1) if t1 else 'none'})
- Manual approval / browser-form-image boundaries: {len(manual)} ({'、'.join(sorted({row['university_name'] for row in manual})) if manual else 'none'})
- No first-party official source found this pass: {len(no_source)} ({'、'.join(row['university_name'] for row in no_source) if no_source else 'none'})

High-value row:

1. 北方工业大学: official 2025本科分专业招生计划 HTML table includes a 广西 column and appears parseable. It does not expose Guangxi professional-group codes, so parsing must still hold group-year calibration until mapping is verified.

Held/context rows:

- 云南师范大学: official parameterized plan portal found; 广西/物理类 drilldown needs API/browser inspection.
- 五邑大学: official 2025外省招生计划 page found, but plan details are embedded images; OCR or official system extraction is needed.
- 华侨大学: official 2025分省分专业计划 page found in search, but direct open returned 403; keep in reachability/backoff.
- 南昌航空大学: official query-entry context found, but no structured Guangxi rows exposed yet.
- 四川轻化工大学: official attachment bundle candidate found; attachment parse is still pending.
- 北师香港浸会大学: official charter PDF context found; no Guangxi plan table.
- 北京建筑大学、华北理工大学: no first-party Guangxi 2025 plan source found in this pass.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next safe step is to parse 北方工业大学 T1 HTML, and separately hold 云南师范大学/五邑大学/华侨大学/四川轻化工大学 for approved browser/API/OCR/attachment handling.
"""
    DOC_OUT.write_text(text, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 39. 2026-05-16 P0 官方来源发现 batch 9"
    content = f"""

{marker}

已新增 batch9 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch9_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch9.md`

覆盖结果：queue rank {', '.join(str(row['queue_rank']) for row in rows)}。北方工业大学命中官方 2025 本科分专业招生计划 HTML 表，广西列可见，是本批唯一 T1 可解析候选；云南师范大学命中官方参数化计划门户，五邑大学命中官方外省计划图片页，华侨大学命中官方计划页但 403，南昌航空大学命中官方查询入口上下文，四川轻化工大学命中官方附件包候选。北京建筑大学、华北理工大学本轮未找到可接收的一方广西计划源。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先解析北方工业大学 T1 HTML 表；涉及云南师范大学 API/五邑大学图片 OCR/华侨大学 403/四川轻化工附件下载时继续等待人工批准或走可审计路线。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, build_rollup(rows), ["metric", "value", "note"])
    write_csv(QA_OUT, build_qa(rows), ["qa_check", "status", "value", "note"])
    write_csv(
        EXCLUSION_OUT,
        build_exclusions(rows),
        [
            "record_id",
            "queue_rank",
            "university_name",
            "source_url",
            "exclusion_reason",
            "recommended_next_action",
            "canonical_ml_entry_open",
        ],
    )
    write_doc(rows)
    write_handoff(rows)

    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    print(f"wrote {ROLLUP_OUT.relative_to(ROOT)}")
    print(f"wrote {QA_OUT.relative_to(ROOT)}")
    print(f"wrote {EXCLUSION_OUT.relative_to(ROOT)}")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
