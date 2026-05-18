#!/usr/bin/env python3
"""Build marker 129 batch17 gap-search pulse A.

This records a small official-source discovery pulse for the first four rows
from marker 128's gap queue. It writes only candidate/reachability preview,
QA, rollup, exclusion, and handoff artifacts.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

GAP_QUEUE = SEED / "reference_trend_520_p1_batch17_official_candidate_gap_queue.csv"

PREFIX = "reference_trend_520_p1_batch17_gap_search_pulse_a"
OUT = SEED / f"{PREFIX}.csv"
ROLLUP = REPORTS / f"{PREFIX}_rollup.csv"
QA = REPORTS / f"{PREFIX}_qa.csv"
EXCLUSION = REPORTS / f"{PREFIX}_exclusion_log.csv"
DOC = DOCS / f"{PREFIX}.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "pulse_id",
    "gap_id",
    "queue_rank",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "source_candidate_tier",
    "source_candidate_status",
    "source_url",
    "source_title",
    "source_type",
    "source_access_status",
    "evidence_summary",
    "desired_source_fields",
    "found_plan_granularity",
    "ordinary_batch_boundary_status",
    "parse_or_access_blocker",
    "requires_browser_or_alternate_fetch",
    "requires_manual_approval_now",
    "source_packet_preview_eligible",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "rejected_nonofficial_evidence_note",
    "next_action",
]

MANUAL_DISCOVERY = {
    "13022-102": {
        "source_candidate_tier": "T2_official_plan_query_page_candidate",
        "source_candidate_status": "official_plan_query_page_found_requires_click_or_js_for_guangxi_rows",
        "source_url": "https://zsw.nbt.edu.cn/bkzn/zsjh.htm",
        "source_title": "招生计划-浙大宁波理工学院招生网",
        "source_type": "official_university_admission_plan_query_page",
        "source_access_status": "static_page_readable_query_detail_not_extracted",
        "evidence_summary": "Official admissions plan page states red-dot provinces can be clicked for province plans and historical admission data.",
        "found_plan_granularity": "province_query_entry_only_no_group_rows_yet",
        "ordinary_batch_boundary_status": "unknown_until_guangxi_detail_drilldown",
        "parse_or_access_blocker": "province_detail_requires_click_or_js_drilldown_before_group_fields_are visible",
        "requires_browser_or_alternate_fetch": "true_for_detail_drilldown_if_static_links_not_exposed",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "Third-party summaries were not accepted.",
        "next_action": "Inspect official query assets or use approved browser drilldown to capture Guangxi physics ordinary-batch rows.",
    },
    "10344-104": {
        "source_candidate_tier": "T2_official_plan_query_portal_candidate",
        "source_candidate_status": "official_plan_query_portal_found_requires_static_api_or_browser_review",
        "source_url": "https://zscx.zcmu.edu.cn/",
        "source_title": "浙江中医药大学招生计划查询入口",
        "source_type": "official_university_admission_plan_query_portal",
        "source_access_status": "official_link_found_from_zsb_home_static_content_empty",
        "evidence_summary": "ZCMU undergraduate admissions site links 招生计划 to zscx.zcmu.edu.cn; the query portal itself did not expose static rows in this pass.",
        "found_plan_granularity": "query_portal_only_no_guangxi_group_rows_yet",
        "ordinary_batch_boundary_status": "unknown_until_query_result",
        "parse_or_access_blocker": "query_portal_static_content_empty_likely_js_or_api_required",
        "requires_browser_or_alternate_fetch": "true_for_static_api_or_browser_review_if_needed",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "No third-party plan rows accepted.",
        "next_action": "Inspect official query endpoint/API or use approved browser review to filter year=2025 province=广西 subject=物理类.",
    },
    "11658-106": {
        "source_candidate_tier": "T4_official_portal_reachability_backoff",
        "source_candidate_status": "official_site_found_no_official_plan_candidate_in_current_query",
        "source_url": "https://www.hainnu.edu.cn/",
        "source_title": "海南师范大学",
        "source_type": "official_university_main_site_reachability",
        "source_access_status": "official_main_site_readable_admission_plan_not_located",
        "evidence_summary": "Official main site exposes 招生信息, but current official-site searches did not locate a Guangxi 2025 ordinary-batch plan page.",
        "found_plan_granularity": "none",
        "ordinary_batch_boundary_status": "not_established",
        "parse_or_access_blocker": "no_official_plan_page_found_in_current_query",
        "requires_browser_or_alternate_fetch": "false_until_static_official_discovery_is_exhausted",
        "source_packet_preview_eligible": "false",
        "rejected_nonofficial_evidence_note": "Third-party plan summaries were found but rejected for source-packet preview.",
        "next_action": "Continue official-only search on 海南师范大学招生就业处 /招生信息 surfaces before considering browser or manual review.",
    },
    "10351-301": {
        "source_candidate_tier": "T2_official_image_plan_page_candidate",
        "source_candidate_status": "official_out_province_plan_page_found_image_layout_manual_or_ocr_required",
        "source_url": "https://zs.wzu.edu.cn/info/1247/9184.htm",
        "source_title": "温州大学2025年招生计划（省外）",
        "source_type": "official_university_out_province_plan_page_image_layout",
        "source_access_status": "static_page_readable_rows_are_images",
        "evidence_summary": "Official WZU out-province plan page is published by admissions site and contains image-based plan content plus note to follow provincial authority.",
        "found_plan_granularity": "out_province_plan_page_image_layout_no_extracted_group_rows_yet",
        "ordinary_batch_boundary_status": "unknown_until_image_table_extract",
        "parse_or_access_blocker": "image_layout_requires_manual_table_QA_or_OCR_before_group_fields",
        "requires_browser_or_alternate_fetch": "false_for_page_reachability_true_for_image_asset_or_manual_QA_if_extracting",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "No third-party plan rows accepted.",
        "next_action": "Queue image asset/manual-table QA for Guangxi physics rows; do not OCR without an explicit artifact pass.",
    },
}


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
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in existing:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def build_rows() -> list[dict[str, object]]:
    gap_rows = read_csv(GAP_QUEUE)
    selected = [row for row in gap_rows if row["group_pair_key"] in MANUAL_DISCOVERY]
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(selected, 1):
        discovery = MANUAL_DISCOVERY[row["group_pair_key"]]
        rows.append(
            {
                "pulse_id": f"reference_trend_520_p1_batch17_gap_pulse_a_{idx:04d}",
                "gap_id": row["gap_id"],
                "queue_rank": row["queue_rank"],
                "group_pair_key": row["group_pair_key"],
                "university_code": row["university_code"],
                "university_name": row["university_name"],
                "group_code": row["group_code"],
                "desired_source_fields": row["desired_source_fields"],
                "requires_manual_approval_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                **discovery,
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    status_counts = Counter(str(row["source_candidate_status"]) for row in rows)
    tier_counts = Counter(str(row["source_candidate_tier"]) for row in rows)
    source_type_counts = Counter(str(row["source_type"]) for row in rows)
    rollup_rows = [
        {"metric": "gap_pulse_rows", "value": len(rows), "note": "First 4 marker-128 gap rows checked through official-only web search."},
        {"metric": "source_packet_preview_candidate_rows", "value": sum(row["source_packet_preview_eligible"] == "true" for row in rows), "note": "Official surfaces worth source-packet preview follow-up."},
        {"metric": "official_plan_rows_extracted", "value": 0, "note": "No plan rows parsed/extracted in this pass."},
        {"metric": "official_min_rank_rows", "value": 0, "note": "No rank source searched or accepted."},
        {"metric": "requires_manual_approval_now_rows", "value": 0, "note": "No browser/form/cookie/header action consumed."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Intake remains closed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, count in sorted(tier_counts.items()):
        rollup_rows.append({"metric": f"tier::{key}", "value": count, "note": ""})
    for key, count in sorted(status_counts.items()):
        rollup_rows.append({"metric": f"status::{key}", "value": count, "note": ""})
    for key, count in sorted(source_type_counts.items()):
        rollup_rows.append({"metric": f"source_type::{key}", "value": count, "note": ""})
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "pulse_row_count",
            "status": "PASS" if len(rows) == 4 else "FAIL",
            "detail": f"{len(rows)} rows recorded for pulse A.",
        },
        {
            "check": "official_only_or_rejected",
            "status": "PASS" if all(row["source_type"].startswith("official_") for row in rows) else "FAIL",
            "detail": "All accepted surfaces are official; nonofficial evidence is only noted as rejected.",
        },
        {
            "check": "no_plan_rows_extracted",
            "status": "PASS",
            "detail": "This pass records source candidates/reachability only; no plan rows parsed.",
        },
        {
            "check": "no_intake_or_calibration",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["calibration_eligible"] == "false" for row in rows) else "FAIL",
            "detail": "No reference trend intake or calibration eligibility opened.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML entry opened.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusion_rows = [
        {
            "pulse_id": row["pulse_id"],
            "group_pair_key": row["group_pair_key"],
            "university_name": row["university_name"],
            "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": row["parse_or_access_blocker"],
            "safe_next_action": row["next_action"],
        }
        for row in rows
    ]
    write_csv(EXCLUSION, exclusion_rows, ["pulse_id", "group_pair_key", "university_name", "excluded_from", "reason", "safe_next_action"])


def write_doc(rows: list[dict[str, object]]) -> None:
    candidate_count = sum(row["source_packet_preview_eligible"] == "true" for row in rows)
    doc = [
        "# Reference trend 520 P1 batch17 gap search pulse A",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This pulse records official-only web discovery outcomes for the first four marker-128 gap rows.",
        "",
        "## Outputs",
        "",
        f"- `clean_data/engineering_guangxi_seed/{OUT.name}`",
        f"- `reports/{ROLLUP.name}`",
        f"- `reports/{QA.name}`",
        f"- `reports/{EXCLUSION.name}`",
        "",
        "## Summary",
        "",
        f"- Gap rows checked: {len(rows)}",
        f"- Official candidate/reachability rows worth follow-up: {candidate_count}",
        "- Plan rows extracted: 0",
        "- Reference trend eligible rows: 0",
        "- Canonical/ML rows opened: 0",
        "",
        "## Source Outcomes",
        "",
    ]
    for row in rows:
        doc.append(
            f"- `{row['group_pair_key']}` {row['university_name']}: "
            f"{row['source_candidate_status']} -> {row['source_url']}"
        )
    doc.extend([
        "",
        "## Boundary",
        "",
        "No cache, parse, OCR, browser/form replay, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update is performed.",
        "",
    ])
    DOC.write_text("\n".join(doc), encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 129. 2026-05-17 P1 batch17 gap search pulse A"
    content = f"""

{marker}

已新增 P1 batch17 gap search pulse A：

- `clean_data/engineering_guangxi_seed/{OUT.name}`
- `reports/{ROLLUP.name}`
- `reports/{QA.name}`
- `reports/{EXCLUSION.name}`
- `docs/{DOC.name}`

覆盖结果：对 marker 128 前 4 条 gap rows 做官方-only web discovery 记录；3 条进入后续 source-packet preview/reachability 候选（浙大宁波理工学院官方招生计划查询页、浙江中医药大学官方招生计划查询入口、温州大学官方省外招生计划图片页），1 条海南师范大学仅确认官方站点/招生入口，未找到可用计划页。QA PASS。

准入边界：本轮只记录官方来源候选/回退状态，不缓存、不解析、不 OCR、不浏览器/form replay、不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)
    append_handoff(rows)


if __name__ == "__main__":
    main()
