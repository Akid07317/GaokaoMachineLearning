#!/usr/bin/env python3
"""Write batch-5 official discovery candidates for still-uncovered P0 rows."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch5_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch5_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch5_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch5_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch5.md"
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

DISCOVERED = [
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0015",
        "queue_rank": "15",
        "university_code": "10378",
        "university_name": "安徽财经大学",
        "source_url": "https://zsjy.aufe.edu.cn/",
        "source_owner": "安徽财经大学本科招生信息网",
        "source_title": "安徽财经大学本科招生信息网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_admissions_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown_until_portal_drilldown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_portal_drilldown",
        "special_type_detected": "unknown_until_specific_asset_parse",
        "collector_note": "Official admissions portal exposes 招生计划 entry, but this pass did not locate a specific 2025 Guangxi physical ordinary plan asset or endpoint.",
        "collector_confidence": "T2_official_portal_needs_endpoint_or_asset",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_guangxi_plan_rows_return",
        "next_action": "drill_down_official_plan_entry_for_2025_guangxi_physics_rows",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0019",
        "queue_rank": "19",
        "university_code": "11116",
        "university_name": "成都工业学院",
        "source_url": "https://zs.cdtu.edu.cn/",
        "source_owner": "成都工业学院招生信息网",
        "source_title": "成都工业学院招生信息网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_admissions_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown_until_portal_drilldown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_portal_drilldown",
        "special_type_detected": "unknown_until_specific_asset_parse",
        "collector_note": "Official admissions-domain portal is reachable as a source root; web search also surfaced official-domain PDFs, but not a structured Guangxi plan asset in this pass.",
        "collector_confidence": "T2_official_portal_needs_endpoint_or_asset",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_guangxi_plan_rows_return",
        "next_action": "search_or_drill_down_official_plan_assets_for_2025_guangxi_rows",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0019",
        "queue_rank": "19",
        "university_code": "11116",
        "university_name": "成都工业学院",
        "source_url": "https://zs.cdtu.edu.cn/__local/7/0E/5F/7FB8963802EDCA90A3B2D51509A_3B947699_DAF8CD.pdf",
        "source_owner": "成都工业学院",
        "source_title": "2025新生入学须知",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_context_pdf_rejected",
        "source_role": "official_non_plan_pdf_context_only",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false",
        "special_type_detected": "not_plan_source",
        "collector_note": "Official-domain PDF was found but is a new-student guide, not a plan source. Keep as rejected reachability clue only.",
        "collector_confidence": "T4_official_domain_non_plan_context_rejected",
        "source_packet_status": "rejected_official_non_plan_context",
        "eligible_for_intake_preview": "false",
        "next_action": "continue_official_plan_asset_search",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0021",
        "queue_rank": "21",
        "university_code": "14389",
        "university_name": "成都师范学院",
        "source_url": "https://www.cdnu.edu.cn/",
        "source_owner": "成都师范学院",
        "source_title": "成都师范学院官网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_site_root_no_plan_asset_found",
        "source_role": "official_site_root_backoff",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false",
        "special_type_detected": "unknown",
        "collector_note": "Web search found official-domain references but no structured 2025 Guangxi plan source or admissions endpoint in this pass.",
        "collector_confidence": "T3_official_root_backoff_no_structured_plan_found",
        "source_packet_status": "no_structured_official_plan_candidate_found_this_pass",
        "eligible_for_intake_preview": "false",
        "next_action": "retry_targeted_official_admissions_search_or_exam_authority_plan_source",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0026",
        "queue_rank": "26",
        "university_code": "10144",
        "university_name": "沈阳理工大学",
        "source_url": "",
        "source_owner": "",
        "source_title": "",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "no_official_source_candidate_found",
        "source_role": "search_backoff_without_official_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false",
        "special_type_detected": "unknown",
        "collector_note": "Search pass surfaced third-party plan references and official charter mirrors, but no first-party official 2025 Guangxi plan asset was identified.",
        "collector_confidence": "T4_no_official_candidate_found_this_pass",
        "source_packet_status": "search_backoff_no_first_party_source",
        "eligible_for_intake_preview": "false",
        "next_action": "retry_with_official_domain_or_use_exam_authority_plan_if_available",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0028",
        "queue_rank": "28",
        "university_code": "10460",
        "university_name": "河南理工大学",
        "source_url": "https://www6.hpu.edu.cn/__local/0/F1/2A/C4518527B841AE23CBB7281803F_6AF2C0FC_24A0B.pdf",
        "source_owner": "河南理工大学",
        "source_title": "河南理工大学2025年全国招生来源计划",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_plan_source_pdf",
        "source_role": "official_plan_pdf_candidate",
        "source_contains_group_code": "false_or_unknown_until_pdf_parse",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "true",
        "special_type_detected": "unknown_until_pdf_parse",
        "collector_note": "Official-domain national plan-source PDF exposes a Guangxi column and should be parsed for physical ordinary plan rows; likely needs group-code mapping after parse.",
        "collector_confidence": "T1_official_pdf_extractable_plan_candidate",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_after_pdf_parse_and_group_mapping_QA",
        "next_action": "download_or_parse_pdf_guangxi_column_then_hold_for_group_mapping",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0028",
        "queue_rank": "28",
        "university_code": "10460",
        "university_name": "河南理工大学",
        "source_url": "https://www6.hpu.edu.cn/web5/info/10602/93003.htm",
        "source_owner": "河南理工大学招生就业处",
        "source_title": "河南理工大学2025年分专业录取分数情况——广西",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_major_score_rank_html",
        "source_role": "official_score_rank_html_candidate",
        "source_contains_group_code": "unknown_until_parse",
        "source_contains_min_score": "true",
        "source_contains_min_rank": "true",
        "source_contains_plan_count": "admission_count_not_plan_count",
        "special_type_detected": "unknown_until_parse",
        "collector_note": "Official-domain Guangxi score page includes major-level score/rank values and can support score/rank QA after parse.",
        "collector_confidence": "T1_official_html_extractable_score_rank_candidate",
        "source_packet_status": "web_verified_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_score_rank_reference_after_parse",
        "next_action": "parse_guangxi_major_score_rank_rows_then_join_exam_authority_group_lines_for_QA",
        "requires_manual_approval": "false",
    },
    {
        "queue_record_id": "reference_trend_520_plan_source_queue_0029",
        "queue_rank": "29",
        "university_code": "13021",
        "university_name": "浙大城市学院",
        "source_url": "https://zs.zucc.edu.cn/",
        "source_owner": "浙大城市学院本科招生网",
        "source_title": "浙大城市学院本科招生网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "official_admissions_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown_until_portal_drilldown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_portal_drilldown",
        "special_type_detected": "unknown_until_specific_asset_parse",
        "collector_note": "Official admissions portal advertises 2025 plan content, but this pass did not locate specific Guangxi physical ordinary rows.",
        "collector_confidence": "T2_official_portal_needs_endpoint_or_asset",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_guangxi_plan_rows_return",
        "next_action": "drill_down_2025_plan_content_for_guangxi_physics_rows",
        "requires_manual_approval": "false",
    },
]


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def main() -> None:
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, item in enumerate(DISCOVERED, start=1):
        row = {
            **item,
            "source_id": f"reference_trend_batch5_web_candidate_{idx:04d}",
            "raw_file_path": "",
            "intended_layer": "reference_trend_source_packet_preview_only",
            "requires_network": "true",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
            "record_id": f"reference_trend_520_p0_source_candidate_batch5_{idx:04d}",
        }
        rows.append(row)
        if row["source_packet_status"] != "official_pdf_candidate_not_parsed" and row["source_packet_status"] != "web_verified_candidate_not_parsed":
            exclusions.append(row)

    counts = Counter()
    universities = set()
    for row in rows:
        counts["batch5_candidate_rows"] += 1
        universities.add(row["university_name"])
        counts[f"source_packet_status::{row['source_packet_status']}"] += 1
        counts[f"collector_confidence::{row['collector_confidence']}"] += 1
        if row["collector_confidence"].startswith("T1_"):
            counts["t1_high_value_rows"] += 1
        if row["source_packet_status"] in {"official_portal_candidate_not_structured", "no_structured_official_plan_candidate_found_this_pass", "search_backoff_no_first_party_source"}:
            counts["needs_drilldown_or_retry_rows"] += 1

    rollup_rows = [
        {"metric": "batch5_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(sorted(universities))},
        {"metric": "t1_high_value_rows", "value": counts["t1_high_value_rows"], "note": ""},
        {"metric": "needs_drilldown_or_retry_rows", "value": counts["needs_drilldown_or_retry_rows"], "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Discovery preview only."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for key, value in sorted(counts.items()):
        if "::" in key:
            rollup_rows.append({"metric": key, "value": value, "note": ""})

    qa_rows = [
        {
            "qa_check": "batch5_candidate_rows",
            "status": "pass",
            "value": len(rows),
            "note": "Rows are source-discovery candidates only; no parsed data promoted.",
        },
        {
            "qa_check": "first_party_official_candidate_rows",
            "status": "review",
            "value": sum(1 for row in rows if row["source_url"].startswith("https://") and "third" not in row["collector_confidence"].lower()),
            "note": "Includes official portals and official-domain PDFs; structured Guangxi rows still need parse or drilldown.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION_OUT, exclusions, FIELDS)

    status_lines = "\n".join(f"- {k}: {v}" for k, v in sorted(counts.items()) if "::" in k)
    doc = f"""# P0 Official Source Discovery Batch 5

Generated: {date.today().isoformat()}

This batch records official-source discovery for P0 rows that the queue reconciliation still marked as needing source discovery. It is a source-packet preview only.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch5_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_exclusion_log.csv`

## Coverage

- Candidate rows: {len(rows)}
- Universities covered: {len(universities)}
- T1 high-value official rows: {counts['t1_high_value_rows']}
- Rows needing endpoint/asset drilldown or retry: {counts['needs_drilldown_or_retry_rows']}

## Status Rollup

{status_lines}

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Batch 5 does not write parsed group-year records or expand the 32-school decision pool.
"""
    DOC_OUT.write_text(doc, encoding="utf-8")

    handoff = f"""

## 26. {date.today().isoformat()} P0 官方来源发现 batch 5

已新增 batch5 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch5_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch5.md`

覆盖结果：候选 {len(rows)} 行，覆盖 {len(universities)} 所学校。河南理工大学出现 2 条 T1 高价值官方源：全国招生来源计划 PDF 与广西分专业录取分数页；安徽财经大学、成都工业学院、浙大城市学院为官方招生门户待端点/资产 drilldown；成都师范学院和沈阳理工大学本轮仍是 backoff/需重搜。

准入边界：本轮仍是 source discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。

下一轮优先级：优先解析河南理工大学官方 PDF/HTML；其余官方门户进入 endpoint 或资产 drilldown，backoff 学校继续定向搜索官方来源。
"""
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(handoff)

    for path in [OUT, ROLLUP_OUT, QA_OUT, EXCLUSION_OUT, DOC_OUT]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
