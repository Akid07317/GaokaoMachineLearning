#!/usr/bin/env python3
"""Write batch-4 official discovery candidates for 520-window plan sources."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

QUERY_PACK = SEED_DIR / "reference_trend_520_plan_discovery_query_pack.csv"
OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch4_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch4_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch4_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch4_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch4.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "source_id",
    "query_record_id",
    "query_rank",
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


DISCOVERED = [
    {
        "university_code": "10594",
        "university_name": "广西科技大学",
        "source_url": "https://www.gxust.edu.cn/__local/B/9F/E2/7347DA77DE419CAE79136D61E66_D492B847_148FB.pdf",
        "source_owner": "广西科技大学",
        "source_title": "广西科技大学2025年区内普通本科招生专业组设置",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_group_structure_pdf",
        "source_role": "official_group_structure_pdf_candidate",
        "source_contains_group_code": "true",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_pdf_parse",
        "special_type_detected": "contains_sports_or_special_rows_possible",
        "collector_note": "Official university-domain PDF is a high-value group-structure source for Guangxi internal ordinary undergraduate admission groups. It should be parsed first, then ordinary physical rows separated from sports/special rows.",
        "collector_confidence": "T1_official_pdf_group_structure_candidate",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_after_pdf_parse_and_special_type_exclusion",
        "next_action": "download_or_parse_group_structure_pdf_then_write_mapping_workbench",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10594",
        "university_name": "广西科技大学",
        "source_url": "https://www.gxust.edu.cn/zsw/index.htm",
        "source_owner": "广西科技大学招生信息网",
        "source_title": "广西科技大学招生信息网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_admissions_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "links_or_announces_official_plan_assets",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "links_or_announces_official_plan_assets",
        "special_type_detected": "unknown_until_asset_parse",
        "collector_note": "Official admissions portal surfaced the 2025 outside-province plan and ordinary undergraduate brochure entries. Use as source root; structured packet depends on linked assets.",
        "collector_confidence": "T2_official_portal_with_plan_assets",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_asset_parsed",
        "next_action": "parse_official_pdf_assets_or_locate_2025_guangxi_plan_page",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10674",
        "university_name": "昆明理工大学",
        "source_url": "https://www.kmust.edu.cn/__local/5/FB/A4/03EBAFE28E3B30274A5B272952D_4700FC4A_15593.pdf",
        "source_owner": "昆明理工大学",
        "source_title": "2025年昆明理工大学普通本科计划来源表",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_plan_source_pdf",
        "source_role": "official_plan_pdf_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "true",
        "special_type_detected": "unknown_until_pdf_parse",
        "collector_note": "Official PDF exposes national plan-source table with province columns including Guangxi. It can support plan-count/major-structure source packets, but likely lacks Guangxi institution-major-group codes.",
        "collector_confidence": "T1_official_pdf_extractable_plan_candidate",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_after_pdf_parse_and_group_mapping_QA",
        "next_action": "parse_pdf_guangxi_column_then_hold_for_group_code_mapping",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10674",
        "university_name": "昆明理工大学",
        "source_url": "https://www.kmust.edu.cn/__local/6/6C/3C/DC6CDD2532B9BD2C15EF269E10E_BA46E7DC_4454F.pdf",
        "source_owner": "昆明理工大学",
        "source_title": "2025年昆明理工大学普通本科分省分专业录取分数情况",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科批",
        "subject_category": "物理类",
        "round_type": "official_major_score_rank_pdf",
        "source_role": "official_score_rank_pdf_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "true",
        "source_contains_min_rank": "true",
        "source_contains_plan_count": "false",
        "special_type_detected": "unknown_until_pdf_parse",
        "collector_note": "Official PDF exposes Guangxi 2025 major-level minimum scores and ranks. It is useful as score/rank evidence but cannot identify Guangxi group codes by itself.",
        "collector_confidence": "T1_official_pdf_extractable_score_rank_candidate",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_score_rank_reference_after_parse",
        "next_action": "parse_pdf_guangxi_major_score_rank_rows_then_join_exam_authority_group_lines_for_QA",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10299",
        "university_name": "江苏大学",
        "source_url": "https://zb.ujs.edu.cn/info/1113/15508.htm",
        "source_owner": "江苏大学本科招生网",
        "source_title": "江苏大学2025年在广西录取情况",
        "published_date": "2025-08-02",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_major_score_reference",
        "source_role": "official_score_reference_html_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "true",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "admission_count_not_plan_count",
        "special_type_detected": "contains_national_special_rows_needs_exclusion",
        "collector_note": "Official HTML page exposes 2025 Guangxi major-level admission counts and min scores, including ordinary physical-chemistry rows and national-special rows. It has no min rank or group code.",
        "collector_confidence": "T1_official_html_extractable_score_candidate",
        "source_packet_status": "web_verified_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_score_reference_only_no_rank",
        "next_action": "parse_ordinary_physics_rows_then_hold_for_rank_and_group_mapping",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10299",
        "university_name": "江苏大学",
        "source_url": "https://zb.ujs.edu.cn/zsjh.htm",
        "source_owner": "江苏大学本科招生网",
        "source_title": "招生计划",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_plan_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown_until_portal_query",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_portal_query",
        "special_type_detected": "unknown_until_portal_query",
        "collector_note": "Official plan portal lists province tabs including Guangxi, but lightweight fetch did not expose structured rows. Needs endpoint discovery or browser-query inspection.",
        "collector_confidence": "T2_official_portal_needs_endpoint",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_rows_return",
        "next_action": "locate_plan_portal_endpoint_for_2025_guangxi_rows",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10407",
        "university_name": "江西理工大学",
        "source_url": "https://zs.jxust.edu.cn/zsxx/zsjh.htm",
        "source_owner": "江西理工大学本科招生信息网",
        "source_title": "招生计划",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_plan_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown_until_portal_query",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_portal_query",
        "special_type_detected": "unknown_until_portal_query",
        "collector_note": "Official plan portal lists Guangxi as a selectable province but server-side text preview defaults to Jiangxi rows. Needs endpoint/form drilldown before packet rows.",
        "collector_confidence": "T2_official_portal_needs_endpoint",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_rows_return",
        "next_action": "locate_or_replay_official_plan_query_endpoint_for_guangxi_rows",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10143",
        "university_name": "沈阳航空航天大学",
        "source_url": "https://zs.sau.edu.cn/info/1047/1760.htm",
        "source_owner": "沈阳航空航天大学本科招生网",
        "source_title": "沈阳航空航天大学2025本科招生计划",
        "published_date": "2025-06-17",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_plan_pdf_attachment_page",
        "source_role": "official_plan_attachment_page_candidate",
        "source_contains_group_code": "attachment_unknown_until_download",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "attachment_unknown_until_download",
        "special_type_detected": "unknown_until_attachment_parse",
        "collector_note": "Official 2025 plan page exists, but the PDF attachment download requires a CAPTCHA in lightweight access. Keep in backoff unless browser/manual approved.",
        "collector_confidence": "T2_official_attachment_captcha_required",
        "source_packet_status": "official_attachment_requires_captcha_backoff",
        "eligible_for_intake_preview": "false_until_attachment_downloaded_and_parsed",
        "next_action": "request_browser_or_manual_download_approval_before_attachment_parse",
        "requires_manual_approval": "true",
    },
    {
        "university_code": "10143",
        "university_name": "沈阳航空航天大学",
        "source_url": "https://zs.sau.edu.cn/info/1048/1819.htm",
        "source_owner": "沈阳航空航天大学本科招生网",
        "source_title": "沈阳航空航天大学2025年本科分省录取最低分数一览表",
        "published_date": "2025-12-07",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_score_xlsx_attachment_page",
        "source_role": "official_score_attachment_page_candidate",
        "source_contains_group_code": "attachment_unknown_until_download",
        "source_contains_min_score": "attachment_unknown_until_download",
        "source_contains_min_rank": "attachment_unknown_until_download",
        "source_contains_plan_count": "false",
        "special_type_detected": "unknown_until_attachment_parse",
        "collector_note": "Official 2025 score page exists, but the XLSX attachment download requires a CAPTCHA in lightweight access. Keep as backoff evidence.",
        "collector_confidence": "T2_official_attachment_captcha_required",
        "source_packet_status": "official_attachment_requires_captcha_backoff",
        "eligible_for_intake_preview": "false_until_attachment_downloaded_and_parsed",
        "next_action": "request_browser_or_manual_download_approval_before_score_attachment_parse",
        "requires_manual_approval": "true",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def attach_query_metadata(candidates: list[dict[str, str]], query_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_code = {row["university_code"]: row for row in query_rows}
    out: list[dict[str, object]] = []
    for idx, candidate in enumerate(candidates, start=1):
        query = by_code.get(candidate["university_code"], {})
        row: dict[str, object] = {
            **candidate,
            "source_id": f"reference_trend_batch4_web_candidate_{idx:04d}",
            "query_record_id": query.get("record_id", ""),
            "query_rank": query.get("query_rank", ""),
            "raw_file_path": "",
            "intended_layer": "reference_trend_source_packet_preview_only",
            "requires_network": "true",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
            "record_id": f"reference_trend_520_p0_source_candidate_batch4_{idx:04d}",
        }
        out.append(row)
    return out


def write_handoff(section: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    marker = "## 20. 2026-05-16 P0/P1 官方来源发现 batch 4"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip()
    HANDOFF.write_text(existing.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")


def main() -> None:
    query_rows = read_csv(QUERY_PACK)
    rows = attach_query_metadata(DISCOVERED, query_rows)

    status_counts = Counter(str(row["source_packet_status"]) for row in rows)
    confidence_counts = Counter(str(row["collector_confidence"]) for row in rows)
    universities = sorted({str(row["university_name"]) for row in rows})
    t1_rows = sum(str(row["collector_confidence"]).startswith("T1_") for row in rows)
    t2_rows = sum(str(row["collector_confidence"]).startswith("T2_") for row in rows)
    manual_rows = sum(str(row["requires_manual_approval"]) == "true" for row in rows)

    rollup = [
        {"metric": "batch4_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(universities)},
        {"metric": "t1_official_extractable_or_high_value_rows", "value": t1_rows, "note": ""},
        {"metric": "t2_portal_or_attachment_rows", "value": t2_rows, "note": ""},
        {"metric": "requires_manual_or_browser_approval_rows", "value": manual_rows, "note": "SAU attachment pages require CAPTCHA in lightweight access."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery preview only; no parsed group-year rows."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Discovery preview only."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for status, count in sorted(status_counts.items()):
        rollup.append({"metric": f"source_packet_status::{status}", "value": count, "note": ""})
    for confidence, count in sorted(confidence_counts.items()):
        rollup.append({"metric": f"collector_confidence::{confidence}", "value": count, "note": ""})

    qa = [
        {
            "qa_check": "official_domain_rows",
            "status": "pass",
            "value": len(rows),
            "note": "All retained candidates are first-party university-domain pages/assets.",
        },
        {
            "qa_check": "high_value_next_parse_targets",
            "status": "info",
            "value": "广西科技大学_group_pdf|昆明理工大学_plan_pdf|昆明理工大学_score_rank_pdf|江苏大学_score_html",
            "note": "These are the safest next local parse targets.",
        },
        {
            "qa_check": "manual_backoff_targets",
            "status": "info",
            "value": "沈阳航空航天大学_plan_pdf_attachment|沈阳航空航天大学_score_xlsx_attachment",
            "note": "Attachment downloads require CAPTCHA; do not brute-force with terminal curl.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No candidate opens canonical or ML.",
        },
    ]

    exclusions = [
        row
        for row in rows
        if row["source_packet_status"] in {
            "official_portal_candidate_not_structured",
            "official_attachment_requires_captcha_backoff",
        }
    ]

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION_OUT, exclusions, FIELDS)

    doc = f"""# Reference Trend 520 P0/P1 Official Source Discovery Batch 4

日期：{date.today().isoformat()}

## 结论

本轮登记下一批 P0/P1 官方来源候选，共 {len(rows)} 行，覆盖 {len(universities)} 所学校：{"、".join(universities)}。

## 覆盖

- T1 官方可解析/高价值候选：{t1_rows}
- T2 官方门户或附件边界候选：{t2_rows}
- 需要人工/浏览器批准的附件候选：{manual_rows}
- reference trend eligible: 0
- calibration eligible: 0
- canonical/ML: closed

## 下一步

1. 优先解析广西科技大学官方专业组 PDF，判断能否直接形成 group-structure mapping workbench。
2. 解析昆明理工大学官方计划 PDF 与分专业分数/位次 PDF，形成 plan/score source packet preview。
3. 解析江苏大学官方广西录取情况 HTML；该页只有专业录取分和录取人数，仍需 group/rank QA。
4. 江西理工、江苏大学计划门户需端点发现；沈阳航空航天附件下载含验证码，等待浏览器或人工下载批准。
"""
    DOC_OUT.write_text(doc, encoding="utf-8")

    handoff = f"""## 20. 2026-05-16 P0/P1 官方来源发现 batch 4

已新增 batch4 官方来源发现预览：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：候选 {len(rows)} 行，覆盖 {len(universities)} 所学校。高价值优先解析目标是广西科技大学官方专业组 PDF、昆明理工大学官方计划 PDF、昆明理工大学官方分专业分数/位次 PDF、江苏大学 2025 广西录取情况 HTML。江西理工/江苏大学计划门户仍需端点发现；沈阳航空航天计划 PDF 与分数 XLSX 附件存在验证码下载边界，先进入 backoff，不用终端硬抓。

准入边界：本轮仍是 source discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。

下一轮优先级：先解析广西科技大学和昆明理工大学官方 PDF；若 PDF 解析受阻，再做江苏大学 HTML 分数参考解析。
"""
    write_handoff(handoff)

    print(f"wrote {OUT}")
    print(f"wrote {ROLLUP_OUT}")
    print(f"wrote {QA_OUT}")
    print(f"wrote {EXCLUSION_OUT}")
    print(f"wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
