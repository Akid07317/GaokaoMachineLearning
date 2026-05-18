#!/usr/bin/env python3
"""Write batch-2 web-discovery candidates for 520-window P0 plan sources.

The records here come from official web search verification. They remain in
source discovery / reachability / QA layers and do not write trend records,
canonical data, ML inputs, or the 32-school decision pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

NEXT_BATCH = SEED_DIR / "reference_trend_520_plan_discovery_next_batch_workbench.csv"
OUT = SEED_DIR / "reference_trend_520_next_batch_web_candidates_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_next_batch_web_candidates_rollup.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_next_batch_web_candidates_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_next_batch_web_candidates.md"

FIELDS = [
    "source_id",
    "batch_workbench_record_id",
    "batch_rank",
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
        "university_code": "10680",
        "university_name": "云南中医药大学",
        "source_url": "https://www.ynucm.edu.cn/uploadfiles/202505/12/2025051216472093949759.pdf",
        "source_owner": "云南中医药大学",
        "source_title": "云南中医药大学2025年普通全日制本科招生章程/手册 PDF",
        "published_date": "2025-05-12",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_pdf_reachability",
        "source_role": "official_pdf_plan_or_brochure_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown_until_pdf_parse",
        "collector_note": "Official university-domain PDF surfaced for 2025 ordinary full-time undergraduate admissions. Needs PDF text/table extraction to confirm whether Guangxi physical ordinary batch plan rows and group codes are present.",
        "collector_confidence": "T2_official_pdf_needs_parse",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "false_until_pdf_parsed",
        "next_action": "download_or_parse_official_pdf_then_write_source_packet_if_guangxi_rows_exist",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "11847",
        "university_name": "佛山大学",
        "source_url": "https://guangdong.eol.cn/gdgd/202506/t20250616_2674878.shtml",
        "source_owner": "中国教育在线广东站",
        "source_title": "佛山大学2025年本科招生计划正式公布",
        "published_date": "2025-06-16",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_discovery_rejected",
        "source_role": "third_party_only_rejected_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown",
        "collector_note": "This pass found third-party reposts but no first-party 佛山大学 official admissions page exposing Guangxi plan rows. Keep as rejected clue only.",
        "collector_confidence": "T4_third_party_only_rejected",
        "source_packet_status": "rejected_third_party_only",
        "eligible_for_intake_preview": "false",
        "next_action": "continue_official_domain_search_or_use_exam_authority_plan_source_only",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10732",
        "university_name": "兰州交通大学",
        "source_url": "https://zsb.lzjtu.edu.cn/",
        "source_owner": "兰州交通大学本专科招生网",
        "source_title": "兰州交通大学本专科招生网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_portal",
        "source_role": "official_plan_portal_with_plan_link_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown",
        "collector_note": "Official admissions portal exposes 招生计划 link to zscx.lzjtu.edu.cn; needs endpoint/query drilldown for 2025 Guangxi physical ordinary rows.",
        "collector_confidence": "T2_official_portal_plan_endpoint_needed",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_endpoint_found",
        "next_action": "drill_down_zscx_plan_query_for_2025_guangxi_physics_rows",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10732",
        "university_name": "兰州交通大学",
        "source_url": "https://www.lzjtu.edu.cn/info/1063/15462.htm",
        "source_owner": "兰州交通大学",
        "source_title": "生源质量再创新高！我校2025年本科招生录取工作圆满收官",
        "published_date": "2025-08-11",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_admission_trend_narrative",
        "source_role": "official_trend_narrative_not_plan_packet",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false",
        "special_type_detected": "not_structured_plan",
        "collector_note": "Official article states Guangxi physical-category admission rank improved by over 10000 places, useful for narrative QA only; no group-year fields.",
        "collector_confidence": "T2_official_trend_narrative_only",
        "source_packet_status": "official_context_candidate_not_structured",
        "eligible_for_intake_preview": "false",
        "next_action": "keep_as_context_only_continue_plan_endpoint_search",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10315",
        "university_name": "南京中医药大学",
        "source_url": "https://zs.njucm.edu.cn/",
        "source_owner": "南京中医药大学本科招生网",
        "source_title": "南京中医药大学本科招生网",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_or_score_portal",
        "source_role": "official_admissions_portal_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown",
        "collector_note": "Official portal exposes 2025 score PDF and older out-of-province plan links; needs drilldown for 2025 out-of-province/Guangxi plan rows.",
        "collector_confidence": "T2_official_portal_needs_drilldown",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_page_found",
        "next_action": "search_official_2025_out_of_province_plan_or_parse_score_pdf_if_needed",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10315",
        "university_name": "南京中医药大学",
        "source_url": "https://zs.njucm.edu.cn/_upload/article/files/24/d1/90d5fe7a486b83f17f0f49f2a167/a8d7dffd-db01-44c3-8a07-1ca4a41b6747.pdf",
        "source_owner": "南京中医药大学本科招生网",
        "source_title": "南京中医药大学2025年本科招生专业平行志愿投档线",
        "published_date": "2025-12-24",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_score_pdf_candidate",
        "source_role": "official_score_pdf_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "true",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false",
        "special_type_detected": "unknown_until_pdf_parse",
        "collector_note": "Official score PDF is reachable; visible preview starts with Guangdong rows, so parse full PDF before deciding whether Guangxi rows exist.",
        "collector_confidence": "T2_official_score_pdf_needs_parse",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "false_until_pdf_parsed",
        "next_action": "parse_pdf_for_guangxi_physics_rows_then_QA_against_exam_authority_lines",
        "requires_manual_approval": "false",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_rows() -> list[dict[str, object]]:
    workbench = {row.get("university_code", ""): row for row in read_csv(NEXT_BATCH)}
    rows: list[dict[str, object]] = []
    for index, item in enumerate(DISCOVERED, start=1):
        base = workbench.get(item["university_code"], {})
        rows.append(
            {
                **item,
                "source_id": f"reference_trend_next_batch_web_candidate_{index:04d}",
                "batch_workbench_record_id": base.get("record_id", ""),
                "batch_rank": base.get("batch_rank", ""),
                "query_rank": base.get("query_rank", ""),
                "raw_file_path": "",
                "intended_layer": "reference_trend_source_packet_preview_only",
                "requires_network": "true",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "record_id": f"reference_trend_520_next_batch_web_candidate_{index:04d}",
            }
        )
    return rows


def write_doc(rows: list[dict[str, object]]) -> None:
    confidence = Counter(row.get("collector_confidence", "") for row in rows)
    status = Counter(row.get("source_packet_status", "") for row in rows)
    universities = sorted({str(row.get("university_name", "")) for row in rows})
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 520 Next-Batch Web Candidates",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已处理下一批 P0 工作台前 4 所学校的官方来源发现。云南中医药大学、兰州交通大学、南京中医药大学均找到官方域名候选；佛山大学本轮只发现第三方转载，先记录为 rejected clue，不能进入 source packet intake。",
                "",
                "## 覆盖",
                "",
                f"- candidate rows: {len(rows)}",
                f"- universities covered: {len(universities)} ({'、'.join(universities)})",
                f"- official-domain candidate rows: {sum(1 for row in rows if not str(row.get('collector_confidence', '')).startswith('T4_'))}",
                f"- rejected third-party-only rows: {sum(1 for row in rows if str(row.get('collector_confidence', '')).startswith('T4_'))}",
                f"- source packet statuses: {dict(status)}",
                f"- confidence counts: {dict(confidence)}",
                "",
                "## 下一步",
                "",
                "- PDF 候选先做文本/表格解析，再判断是否存在广西物理类普通批行。",
                "- 兰州交通大学优先 drilldown 官方 zscx 招生计划查询端点。",
                "- 佛山大学继续找一手官方招生域名，第三方转载不入库。",
                "- 不打开 canonical/ML，不进入 32 所 decision_pool。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    exclusions = []
    for index, row in enumerate(rows, start=1):
        rejected = str(row.get("collector_confidence", "")).startswith("T4_")
        exclusions.append(
            {
                "record_id": f"reference_trend_520_next_batch_exclusion_{index:04d}",
                "source_id": row.get("source_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_url": row.get("source_url", ""),
                "qa_status": "rejected_third_party_only" if rejected else "hold_for_parse_or_endpoint",
                "exclusion_or_hold_reason": "third_party_only_not_official" if rejected else "specific_structured_guangxi_rows_not_yet_verified",
                "required_resolution": "find_official_source" if rejected else row.get("next_action", ""),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": row.get("decision_pool_boundary", ""),
            }
        )
    write_csv(
        EXCLUSION_OUT,
        exclusions,
        [
            "record_id",
            "source_id",
            "university_code",
            "university_name",
            "source_url",
            "qa_status",
            "exclusion_or_hold_reason",
            "required_resolution",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    confidence = Counter(row.get("collector_confidence", "") for row in rows)
    rollup = [
        {"metric": "next_batch_web_candidate_rows", "value": len(rows)},
        {"metric": "universities_covered", "value": len({row.get("university_code", "") for row in rows})},
        {"metric": "official_domain_candidate_rows", "value": sum(1 for row in rows if not str(row.get("collector_confidence", "")).startswith("T4_"))},
        {"metric": "rejected_third_party_only_rows", "value": sum(1 for row in rows if str(row.get("collector_confidence", "")).startswith("T4_"))},
        {"metric": "official_pdf_needs_parse_rows", "value": sum(1 for row in rows if "pdf" in str(row.get("collector_confidence", "")).lower())},
        {"metric": "official_portal_or_endpoint_rows", "value": sum(1 for row in rows if "portal" in str(row.get("collector_confidence", "")).lower())},
        {"metric": "trend_record_eligible_rows", "value": 0},
        {"metric": "calibration_eligible_rows", "value": 0},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"next_batch_web_candidate_rows={len(rows)}")
    print(f"official_domain_candidate_rows={rollup[2]['value']}")


if __name__ == "__main__":
    main()
