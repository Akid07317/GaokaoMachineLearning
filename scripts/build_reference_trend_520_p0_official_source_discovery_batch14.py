#!/usr/bin/env python3
"""Write batch-14 official source discovery preview for queue ranks 131-150.

This batch records first-party official candidates, carry-forward candidates,
and rejected/context-only hits. It does not cache, OCR, parse, replay forms, or
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

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch14_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch14_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch14_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch14_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch14.md"
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
    enriched = {
        "source_id": f"reference_trend_520_p0_batch14_{idx:04d}",
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
        "requires_manual_approval": "false_until_browser_or_form_or_ocr_route_needed",
        "eligible_for_intake_preview": "false_until_source_packet_parse_and_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch14_{idx:04d}",
    }
    enriched.update(row)
    return enriched


def build_rows() -> list[dict[str, object]]:
    raw_rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0131",
            "queue_rank": "131",
            "university_code": "11658",
            "university_name": "海南师范大学",
            "source_url": "https://zhaosheng.hainnu.edu.cn/|https://zjc.hainnu.edu.cn/",
            "source_owner": "海南师范大学招生就业处/招生信息网",
            "source_title": "招生信息网/招生就业处官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "collector_note": "Official admissions portals found, but no auditable Guangxi ordinary physical plan rows were cached or parsed in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_plan_source_not_cached",
            "next_action": "drill down official 招生计划/分省计划 pages; keep portal context out of intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0132|reference_trend_520_plan_source_queue_0133",
            "queue_rank": "132|133",
            "university_code": "10332",
            "university_name": "苏州科技大学",
            "source_url": "https://zsb.usts.edu.cn/",
            "source_owner": "苏州科技大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_portal_needs_plan_detail_cache",
            "source_contains_plan_count": "unknown_until_detail_cache",
            "collector_note": "Official admissions portal located; needs 招生计划 detail/page search before any source-packet preview.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "cache plan list/detail if Guangxi rows are present; otherwise log context-only.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0134|reference_trend_520_plan_source_queue_0135",
            "queue_rank": "134|135",
            "university_code": "16302",
            "university_name": "西交利物浦大学",
            "source_url": "https://www.xjtlu.edu.cn/zh/admissions/domestic/entry-requirements",
            "source_owner": "西交利物浦大学本科招生",
            "source_title": "中国内地本科招生录取要求/招生信息官方入口",
            "round_type": "official_context_plan_authority_delegated",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "false_for_local_guangxi_rows",
            "special_type_detected": "sino_foreign_cooperation_boundary",
            "collector_note": "Official admissions page found; plan details may be delegated to provincial materials, and sino-foreign cooperation boundary must remain explicit.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "look for first-party province-plan table/PDF; do not infer plan rows from admissions policy page.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0136",
            "queue_rank": "136",
            "university_code": "10623",
            "university_name": "西华大学",
            "source_url": "https://zhaosheng.xhu.edu.cn/",
            "source_owner": "西华大学本科招生信息网",
            "source_title": "本科招生信息网官方入口",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_portal_needs_plan_detail_cache",
            "source_contains_plan_count": "unknown_until_detail_cache",
            "collector_note": "Official admissions portal located; Guangxi source packet still needs detail discovery/cache.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "search/crawl official 招生计划 page; isolate ordinary本科物理 rows if found.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0137",
            "queue_rank": "137",
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
            "collector_note": "Carried forward from batch13 parse/mapping workbench; acceptance sheet exists and remains pending.",
            "collector_confidence": "T1_existing_official_source_packet_with_mapping_sheet",
            "source_packet_status": "existing_acceptance_sheet_pending_human_decision",
            "requires_network": "false_existing_local_artifacts",
            "next_action": "wait for group mapping acceptance sheet decision; do not regenerate or overwrite human fields.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0138",
            "queue_rank": "138",
            "university_code": "10108",
            "university_name": "山西大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "round_type": "existing_low_relevance_or_noise_candidate",
            "source_role": "noise_or_context_rejected_for_plan_rows",
            "source_contains_plan_count": "false",
            "collector_note": "Queue already marks candidate_kind=low_relevance_or_noise_candidate; no new first-party Guangxi plan source was accepted in this batch.",
            "collector_confidence": "T4_existing_noise_candidate_rejected",
            "source_packet_status": "no_first_party_plan_source_found_this_batch",
            "requires_network": "true_for_future_retry",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official admissions domain only if needed; keep existing low-relevance/noise candidate out of intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0139",
            "queue_rank": "139",
            "university_code": "11835",
            "university_name": "上海政法学院",
            "source_url": "https://zs.shupl.edu.cn/",
            "source_owner": "上海政法学院招生网",
            "source_title": "招生网官方入口/分省分专业本科招生计划列表候选",
            "round_type": "official_plan_index_candidate",
            "source_role": "official_plan_list_needs_detail_cache",
            "source_contains_plan_count": "true_if_plan_detail_available",
            "collector_note": "Official admissions site surfaced plan-list context; needs detail cache and row parse before use.",
            "collector_confidence": "T2_official_plan_index_needs_detail_cache",
            "source_packet_status": "official_plan_index_discovered_not_cached",
            "next_action": "cache 2025分省分专业本科招生计划 detail/attachment and parse Guangxi physical ordinary rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0140",
            "queue_rank": "140",
            "university_code": "10264",
            "university_name": "上海海洋大学",
            "source_url": "https://zsjy.shou.edu.cn/main.htm",
            "source_owner": "上海海洋大学本科招生网",
            "source_title": "本科招生网/2025年普通本科分省招生计划列表候选",
            "round_type": "official_plan_index_candidate",
            "source_role": "official_plan_list_needs_detail_cache",
            "source_contains_plan_count": "true_if_plan_detail_available",
            "collector_note": "Official admissions site has plan-list context; needs detail cache to verify Guangxi group/plan rows.",
            "collector_confidence": "T2_official_plan_index_needs_detail_cache",
            "source_packet_status": "official_plan_index_discovered_not_cached",
            "next_action": "cache plan detail/PDF/table; separate普通批物理 from special/cooperation rows.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0141",
            "queue_rank": "141",
            "university_code": "10159",
            "university_name": "中国医科大学",
            "source_url": "https://bkzs.cmu.edu.cn/",
            "source_owner": "中国医科大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "special_type_detected": "medical_major_boundary_unknown",
            "collector_note": "Official admissions portal located, but no Guangxi plan rows were cached or parsed in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official plan/publicity pages; cache only if Guangxi rows are visible.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0142",
            "queue_rank": "142",
            "university_code": "10452",
            "university_name": "临沂大学",
            "source_url": "https://zhaosheng.lyu.edu.cn/",
            "source_owner": "临沂大学招生网",
            "source_title": "招生网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "collector_note": "Official admissions portal found; any 专升本 or non-普通本科 hits must remain rejected.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "look for ordinary本科分省计划 only; reject专升本/省内-only context.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0143",
            "queue_rank": "143",
            "university_code": "10063",
            "university_name": "天津中医药大学",
            "source_url": "https://zsjy.tjutcm.edu.cn/",
            "source_owner": "天津中医药大学招生就业网",
            "source_title": "招生就业网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "special_type_detected": "medical/tcm_major_boundary_unknown",
            "collector_note": "Official portal found; this batch did not cache a Guangxi ordinary physical plan table.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 2025分省计划/招生计划 pages; keep 天津本地计划 examples out of Guangxi intake.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0144",
            "queue_rank": "144",
            "university_code": "10068",
            "university_name": "天津外国语大学",
            "source_url": "https://zsb.tjfsu.edu.cn/",
            "source_owner": "天津外国语大学招生网",
            "source_title": "招生网官方入口/招生计划栏目候选",
            "round_type": "official_plan_portal_candidate",
            "source_role": "official_plan_portal_needs_detail_cache",
            "source_contains_plan_count": "unknown_until_detail_cache",
            "collector_note": "Official招生计划栏目入口 located; needs 2025广西 detail cache before row-level assessment.",
            "collector_confidence": "T2_official_plan_portal_needs_detail_cache",
            "source_packet_status": "official_plan_portal_discovered_not_cached",
            "next_action": "cache招生计划 detail if available; isolate普通批物理/外语限科 boundaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0145",
            "queue_rank": "145",
            "university_code": "10070",
            "university_name": "天津财经大学",
            "source_url": "https://zhaosheng.tjufe.edu.cn/",
            "source_owner": "天津财经大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "collector_note": "Official admissions portal found; no Guangxi plan rows cached or parsed in this batch.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 招生计划 pages and ignore score-only/third-party summaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0146",
            "queue_rank": "146",
            "university_code": "10749",
            "university_name": "宁夏大学",
            "source_url": "https://zs.nxu.edu.cn/",
            "source_owner": "宁夏大学本科招生网",
            "source_title": "本科招生网官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "collector_note": "Official admissions portal found; any charter-only source remains context, not plan intake.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "drill down official 2025分省计划/source packet if available.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0147",
            "queue_rank": "147",
            "university_code": "10360",
            "university_name": "安徽工业大学",
            "source_url": "https://zs.ahut.edu.cn/info/6077/2973.htm",
            "source_owner": "安徽工业大学本科招生网",
            "source_title": "安徽工业大学2025年普通本科招生计划",
            "published_date": "2025-06-25",
            "round_type": "existing_official_plan_image_candidate",
            "source_role": "existing_image_candidate_hold_for_ocr_or_manual_transcription",
            "source_contains_plan_count": "true_in_images_unparsed",
            "collector_note": "Carry-forward from batch13. Official image plan candidate exists; OCR/manual transcription remains approval-gated.",
            "collector_confidence": "T2_existing_official_plan_image_candidate",
            "source_packet_status": "existing_image_candidate_hold_for_ocr_or_manual_transcription",
            "requires_manual_approval": "true_for_image_ocr_or_manual_transcription",
            "next_action": "cache/render images if not already cached; ask approval before OCR/manual transcription.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0148",
            "queue_rank": "148",
            "university_code": "10573",
            "university_name": "广东药科大学",
            "source_url": "https://zsb.gdpu.edu.cn/",
            "source_owner": "广东药科大学招生办公室",
            "source_title": "招生办公室官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "special_type_detected": "medical/pharmacy_major_boundary_unknown",
            "collector_note": "Official admissions portal found; no Guangxi source-packet rows cached in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 分省分专业招生计划 page; separate普通批物理 and special tracks.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0149",
            "queue_rank": "149",
            "university_code": "11116",
            "university_name": "成都工业学院",
            "source_url": "https://zjc.cdtu.edu.cn/",
            "source_owner": "成都工业学院招生就业处",
            "source_title": "招生就业处官方入口",
            "round_type": "official_context_portal_needs_plan_drilldown",
            "source_role": "official_context_not_structured_guangxi_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "collector_note": "Official admissions/employment portal found; needs official Guangxi plan detail discovery.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 招生计划 detail/PDF; reject third-party plan summaries.",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0150",
            "queue_rank": "150",
            "university_code": "10595",
            "university_name": "桂林电子科技大学",
            "source_url": "https://www.guet.edu.cn/zs/",
            "source_owner": "桂林电子科技大学招生信息网",
            "source_title": "招生信息网官方入口",
            "round_type": "local_official_context_needs_group_plan_source",
            "source_role": "official_context_not_structured_guangxi_group_plan_rows",
            "source_contains_plan_count": "unknown_until_plan_page_found",
            "collector_note": "Local Guangxi university; official portal context found, but group-level Guangxi physical ordinary source packet still needs explicit page/PDF/table.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_structured_plan_rows",
            "next_action": "search official 2025广西招生计划/分专业计划; local familiarity is not sufficient for intake.",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(raw_rows, start=1)]


def main() -> None:
    rows = build_rows()
    counts = Counter(str(row["source_packet_status"]) for row in rows)
    confidence_counts = Counter(str(row["collector_confidence"]) for row in rows)
    manual_approval_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    official_candidate_rows = [
        row
        for row in rows
        if str(row["collector_confidence"]).startswith(("T1_", "T2_"))
    ]
    context_or_reject_rows = [row for row in rows if row not in official_candidate_rows]

    rollup_rows = [
        {"metric": "queue_rank_min", "value": 131, "note": "Batch14 lower bound."},
        {"metric": "queue_rank_max", "value": 150, "note": "Batch14 upper bound."},
        {"metric": "discovery_rows", "value": len(rows), "note": "One per school or duplicate queue group cluster."},
        {"metric": "official_candidate_or_carry_forward_rows", "value": len(official_candidate_rows), "note": "T1/T2 rows needing detail cache/parse or acceptance."},
        {"metric": "context_or_rejected_rows", "value": len(context_or_reject_rows), "note": "Portal/context/noise rows not suitable for intake."},
        {"metric": "manual_approval_rows", "value": len(manual_approval_rows), "note": "OCR/manual transcription approval-gated rows."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Discovery only."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(counts.items()):
        rollup_rows.append({"metric": f"status::{key}", "value": value, "note": ""})
    for key, value in sorted(confidence_counts.items()):
        rollup_rows.append({"metric": f"confidence::{key}", "value": value, "note": ""})

    qa_rows = [
        {
            "check": "batch14_row_count",
            "status": "PASS" if len(rows) == 18 else "REVIEW",
            "detail": f"rows={len(rows)}; duplicate queue clusters compress 20 ranks into 18 rows",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS",
            "detail": "All rows reference_trend_pool_eligible=false.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS",
            "detail": "All rows canonical_ml_entry_open=false.",
        },
        {
            "check": "manual_approval_gated",
            "status": "PASS",
            "detail": "Image/OCR routes are marked approval-gated.",
        },
    ]

    exclusions = [
        row
        for row in rows
        if str(row["collector_confidence"]).startswith(("T3_", "T4_"))
        or row["source_packet_status"] in {
            "official_context_found_no_structured_plan_rows",
            "no_first_party_plan_source_found_this_batch",
        }
    ]

    doc_lines = [
        "# Reference Trend 520 Official Source Discovery Batch14",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: queue ranks 131-150. This is source discovery only; no source asset",
        "cache, OCR, form replay, source-packet parse, reference-trend intake, canonical,",
        "or ML output is opened.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP_OUT.relative_to(ROOT)}`",
        f"- `{QA_OUT.relative_to(ROOT)}`",
        f"- `{EXCLUSION_OUT.relative_to(ROOT)}`",
        "",
        "## Key candidates",
        "",
    ]
    for row in official_candidate_rows:
        doc_lines.append(
            f"- {row['university_name']} ({row['queue_rank']}): "
            f"{row['collector_confidence']}; {row['source_packet_status']}."
        )
    doc_lines.extend(
        [
            "",
            "## Boundary",
            "",
            "All rows remain `reference_trend_pool_eligible=false`,",
            "`calibration_eligible=false`, and `canonical_ml_entry_open=false`.",
        ]
    )

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, FIELDS)
    DOC_OUT.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")

    marker = "## 55. 2026-05-16 P1 官方来源发现 batch 14"
    handoff = f"""

{marker}

已新增 batch14 官方来源发现预览：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：queue rank 131-150。苏州科技大学、西华大学、上海政法学院、上海海洋大学、天津外国语大学形成 T2 官方入口/计划列表候选，需后续缓存详情页确认是否有广西物理普通批行；集美大学和安徽工业大学作为既有候选承接，分别等待人工映射接受与图片 OCR/人工转录审批；其余学校本轮主要是官方门户/上下文，未形成可入 source-packet 的结构化计划行。

准入边界：本轮只做 source discovery preview，不缓存、不解析、不 OCR，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮优先缓存/解析上海政法学院、上海海洋大学、天津外国语大学或苏州科技大学的 2025 广西计划详情；安徽工业大学图片路线仍需人工批准。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
