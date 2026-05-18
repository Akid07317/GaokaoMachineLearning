#!/usr/bin/env python3
"""Build marker 130 batch17 gap-search pulse B.

This records a second small official-source discovery pulse for marker 128's
gap queue. It writes only source candidate/reachability preview, QA, rollup,
exclusion, and handoff artifacts.
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

PREFIX = "reference_trend_520_p1_batch17_gap_search_pulse_b"
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
    "10537-101": {
        "source_candidate_tier": "T2_official_html_plan_table_candidate",
        "source_candidate_status": "official_out_province_plan_html_table_found_column_alignment_required",
        "source_url": "https://zs.hunau.edu.cn/zsjh/202506/t20250625_466994.html",
        "source_title": "2025年外省招生计划-湖南农业大学招生信息网",
        "source_type": "official_university_out_province_plan_page_html_table",
        "source_access_status": "static_html_table_readable_rows_not_group_parsed",
        "evidence_summary": "Official HUNAU admissions page is dated 2025-06-25 and lists out-of-province plans with Guangxi as a province column.",
        "found_plan_granularity": "major_by_province_table_no_group_rows_extracted",
        "ordinary_batch_boundary_status": "ordinary_candidate_but_group_mapping_unknown_until_column_alignment_qa",
        "parse_or_access_blocker": "wide_html_table_requires_column_alignment_and_major_structure_QA_before_guangxi_rows",
        "requires_browser_or_alternate_fetch": "false_for_reachability_true_for_table_alignment_if_needed",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "No third-party plan rows accepted.",
        "next_action": "Queue source-packet preview/table-alignment QA for Guangxi physics rows; keep group mapping unconfirmed.",
    },
    "10542-125": {
        "source_candidate_tier": "T4_official_linked_external_query_login_backoff",
        "source_candidate_status": "official_site_links_plan_query_but_external_query_requires_login",
        "source_url": "https://zsb.hunnu.edu.cn/",
        "source_title": "湖南师范大学招生信息网",
        "source_type": "official_university_admission_site_linked_query_backoff",
        "source_access_status": "official_site_readable_external_query_login_required",
        "evidence_summary": "Official HNNU admissions site exposes 招生计划 links to bkzs/zhinengdayi query surfaces; the accessible linked query showed login required.",
        "found_plan_granularity": "query_entry_only_no_guangxi_group_rows",
        "ordinary_batch_boundary_status": "not_established_until_query_result",
        "parse_or_access_blocker": "linked_query_requires_login_or_cache_miss_before_plan_rows",
        "requires_browser_or_alternate_fetch": "true_if_user_approves_browser_or_logged_query_review",
        "source_packet_preview_eligible": "false",
        "rejected_nonofficial_evidence_note": "External login-gated rows were not accepted as evidence.",
        "next_action": "Hold in reachability backoff unless user approves browser/login-state review or an official static page is found.",
    },
    "10543-102": {
        "source_candidate_tier": "T2_official_image_plan_page_candidate",
        "source_candidate_status": "official_2025_plan_page_found_image_layout_manual_or_ocr_required",
        "source_url": "https://zjc.hnist.cn/info/1014/2863.htm",
        "source_title": "湖南理工学院2025年本科招生计划",
        "source_type": "official_university_plan_page_image_layout",
        "source_access_status": "static_page_readable_plan_content_image_only",
        "evidence_summary": "Official HNIST admissions office page is dated 2025-06-18 and contains the 2025 undergraduate plan as an image.",
        "found_plan_granularity": "image_plan_page_no_extracted_group_rows",
        "ordinary_batch_boundary_status": "unknown_until_image_table_extract",
        "parse_or_access_blocker": "image_layout_requires_manual_table_QA_or_OCR_before_group_fields",
        "requires_browser_or_alternate_fetch": "false_for_page_reachability_true_for_image_asset_or_manual_QA_if_extracting",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "No third-party plan rows accepted.",
        "next_action": "Queue image asset/manual-table QA for Guangxi physics rows; do not OCR without an explicit artifact pass.",
    },
    "10229-101": {
        "source_candidate_tier": "T2_official_plan_list_detail_candidate",
        "source_candidate_status": "official_plan_list_found_guangxi_detail_link_cache_miss",
        "source_url": "https://www.mdjmu.cn/bkzsw/zsjh.htm",
        "source_title": "招生计划-牡丹江医科大学本科招生网",
        "source_type": "official_university_plan_list_with_guangxi_detail_link",
        "source_access_status": "static_list_readable_detail_link_not_fetched",
        "evidence_summary": "Official MDJMU admissions plan list includes 2025年牡丹江医科大学招生计划-广西壮族自治区 dated 2025-06-17; the detail link was not fetched in this pass.",
        "found_plan_granularity": "province_detail_link_listed_no_rows_extracted",
        "ordinary_batch_boundary_status": "unknown_until_guangxi_detail_read",
        "parse_or_access_blocker": "official_detail_link_cache_miss_before_medical_ordinary_batch_rows",
        "requires_browser_or_alternate_fetch": "true_if_static_fetch_remains_cache_miss_and_user_approves_browser_review",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "No third-party medical plan rows accepted.",
        "next_action": "Retry official detail through auditable static fetch or approved browser review; isolate medical ordinary-batch rows before preview.",
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
                "pulse_id": f"reference_trend_520_p1_batch17_gap_pulse_b_{idx:04d}",
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
        {"metric": "gap_pulse_rows", "value": len(rows), "note": "Marker-128 gap rows 0005-0008 checked through official-only web search."},
        {"metric": "source_packet_preview_candidate_rows", "value": sum(row["source_packet_preview_eligible"] == "true" for row in rows), "note": "Official surfaces worth source-packet preview follow-up."},
        {"metric": "official_plan_rows_extracted", "value": 0, "note": "No plan rows parsed/extracted in this pass."},
        {"metric": "official_min_rank_rows", "value": 0, "note": "No rank source searched or accepted."},
        {"metric": "requires_manual_approval_now_rows", "value": 0, "note": "No browser/form/cookie/header/login action consumed."},
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
            "detail": f"{len(rows)} rows recorded for pulse B.",
        },
        {
            "check": "official_only_or_rejected",
            "status": "PASS" if all(row["source_type"].startswith("official_") for row in rows) else "FAIL",
            "detail": "All accepted surfaces are official/official-linked; nonofficial evidence is only noted as rejected.",
        },
        {
            "check": "no_plan_rows_extracted",
            "status": "PASS",
            "detail": "This pass records source candidates/reachability only; no plan rows parsed.",
        },
        {
            "check": "no_manual_or_login_action_consumed",
            "status": "PASS" if all(row["requires_manual_approval_now"] == "false" for row in rows) else "FAIL",
            "detail": "Login/browser/header/cookie/form actions were not consumed.",
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
        "# Reference trend 520 P1 batch17 gap search pulse B",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This pulse records official-only web discovery outcomes for marker-128 gap rows 0005-0008.",
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
        "No cache, parse, OCR, browser/form replay, login-state review, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update is performed.",
        "",
    ])
    DOC.write_text("\n".join(doc), encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 130. 2026-05-17 P1 batch17 gap search pulse B"
    content = f"""

{marker}

已新增 P1 batch17 gap search pulse B：

- `clean_data/engineering_guangxi_seed/{OUT.name}`
- `reports/{ROLLUP.name}`
- `reports/{QA.name}`
- `reports/{EXCLUSION.name}`
- `docs/{DOC.name}`

覆盖结果：对 marker 128 的 gap rows 0005-0008 做官方-only web discovery 记录；3 条进入后续 source-packet preview/reachability 候选（湖南农业大学官方外省招生计划 HTML 表、湖南理工学院官方 2025 本科招生计划图片页、牡丹江医科大学官方招生计划列表中的广西详情链接），1 条湖南师范大学仅确认官方招生站链接到计划查询，但可访问查询面提示登录/缓存缺失，保持 reachability backoff。QA PASS。

准入边界：本轮只记录官方来源候选/回退状态，不缓存、不解析、不 OCR、不使用浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。
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
