#!/usr/bin/env python3
"""Write verified web-discovery candidates for 520-window plan sources.

This artifact belongs to the collection/source-packet layer only. It records
official pages discovered from web search and does not parse them into
canonical, ML, or decision-pool data.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

QUERY_PACK = SEED_DIR / "reference_trend_520_plan_discovery_query_pack.csv"
OUT = SEED_DIR / "reference_trend_520_plan_discovery_web_candidates_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_plan_discovery_web_candidates_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_plan_discovery_web_candidates.md"

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
        "university_code": "10524",
        "university_name": "中南民族大学",
        "source_url": "https://zsb.scuec.edu.cn/info/1020/2469.htm",
        "source_owner": "中南民族大学本科招生信息网",
        "source_title": "2025年普通理工/物理类招生计划（不含综合改革省份）",
        "published_date": "2025-06-17",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan",
        "source_role": "plan_count_and_major_structure_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "true",
        "special_type_detected": "contains_preparatory_row_needs_exclusion",
        "collector_confidence": "T1_official_extractable_plan_candidate",
        "source_packet_status": "web_verified_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_after_parse_and_special_type_exclusion",
        "next_action": "parse_guangxi_column_as_plan_source_packet_then_qa_group_mapping",
        "collector_note": "Official admissions page exposes 2025 ordinary science/physics plan table with Guangxi column; group-code mapping is not explicit, so use as plan-count/major-structure source only until mapped.",
    },
    {
        "university_code": "10524",
        "university_name": "中南民族大学",
        "source_url": "https://zsb.scuec.edu.cn/info/1031/2476.htm",
        "source_owner": "中南民族大学本科招生信息网",
        "source_title": "2024年“3+1+2”高考改革省份录取分数统计",
        "published_date": "2025-06-17",
        "year": "2024",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_score_reference",
        "source_role": "score_group_reference_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "true",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false",
        "special_type_detected": "contains_national_special_and_preparatory_rows_needs_exclusion",
        "collector_confidence": "T1_official_extractable_score_candidate",
        "source_packet_status": "web_verified_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_score_reference_only_no_rank",
        "next_action": "parse_guangxi_ordinary_rows_then_join_exam_rank_if_needed",
        "collector_note": "Official admissions page includes Guangxi ordinary physical-group minimum scores; no minimum rank is exposed and group labels are selection-requirement labels, not Guangxi院校专业组 codes.",
    },
    {
        "university_code": "11819",
        "university_name": "东莞理工学院",
        "source_url": "https://ee.dgut.edu.cn/info/1061/25990.htm",
        "source_owner": "东莞理工学院电信工程与智能化学院",
        "source_title": "权威发布︱东莞理工学院2025年本科招生计划",
        "published_date": "2025-06-17",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_reachability",
        "source_role": "official_plan_reachability_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown",
        "collector_confidence": "T2_official_page_shortlink_needs_manual_or_browser",
        "source_packet_status": "official_reachability_candidate_blocked_by_shortlink_or_embedded_asset",
        "eligible_for_intake_preview": "false_until_manual_or_browser_verification",
        "next_action": "open_shortlink_or_official_admission_list_with_browser_before_source_packet_intake",
        "collector_note": "Official school subdomain page announces 2025 plan and exposes a shortlink; the visible page does not expose structured Guangxi rows in text.",
    },
    {
        "university_code": "11819",
        "university_name": "东莞理工学院",
        "source_url": "https://zsb.dgut.edu.cn/bkszs/zsjh/",
        "source_owner": "东莞理工学院招生信息网",
        "source_title": "招生计划",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown",
        "collector_confidence": "T2_official_portal_needs_drilldown",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_page_found",
        "next_action": "drill_down_official_plan_portal_for_2025_guangxi_plan_page",
        "collector_note": "Official admissions portal is reachable and should be used as the first-party source root if the shortlink content needs browser verification.",
    },
    {
        "university_code": "10224",
        "university_name": "东北农业大学",
        "source_url": "https://zsbweb.neau.edu.cn/index.htm",
        "source_owner": "东北农业大学招生信息网",
        "source_title": "招生信息网_东北农业大学",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "site_lists_multiple_plan_types",
        "collector_confidence": "T2_official_portal_needs_endpoint_or_query",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_endpoint_found",
        "next_action": "locate_official_plan_query_endpoint_or_specific_guangxi_rows",
        "collector_note": "Official admissions portal is reachable and states plan types; search did not expose a direct 2025 Guangxi structured plan page in this pass.",
    },
    {
        "university_code": "10856",
        "university_name": "上海工程技术大学",
        "source_url": "https://zsb.sues.edu.cn/webrecruit/index.do",
        "source_owner": "上海工程技术大学招生网",
        "source_title": "上海工程技术大学本科招生首页",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_portal",
        "source_role": "official_plan_portal_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown",
        "special_type_detected": "unknown",
        "collector_confidence": "T2_official_portal_needs_plan_endpoint",
        "source_packet_status": "official_portal_candidate_not_structured",
        "eligible_for_intake_preview": "false_until_specific_plan_page_found",
        "next_action": "search_or_drill_down_official_webrecruit_plan_endpoint",
        "collector_note": "Official recruitment site and 2025 charter are reachable, but the plan table was not found in text search during this pass.",
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
    query_by_code = {row.get("university_code", ""): row for row in read_csv(QUERY_PACK)}
    rows: list[dict[str, object]] = []
    for index, item in enumerate(DISCOVERED, start=1):
        query = query_by_code.get(item["university_code"], {})
        rows.append(
            {
                **item,
                "source_id": f"reference_trend_web_candidate_{index:04d}",
                "query_record_id": query.get("record_id", ""),
                "query_rank": query.get("query_rank", ""),
                "raw_file_path": "",
                "intended_layer": "reference_trend_source_packet_preview_only",
                "requires_network": "true",
                "requires_manual_approval": "true"
                if "manual" in item["next_action"] or "browser" in item["next_action"]
                else "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "record_id": f"reference_trend_520_plan_web_candidate_{index:04d}",
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
                "# Reference Trend 520 Plan Discovery Web Candidates",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "本轮从 P0 query pack 中抽查并记录了 4 所学校的官方来源候选，形成 source packet 预览层。中南民族大学已有可文本抽取的官方计划/分数候选；东莞理工学院、东北农业大学、上海工程技术大学目前只落到官方入口或需浏览器/短链核验的 reachability 层。",
                "",
                "## 覆盖",
                "",
                f"- web candidate rows: {len(rows)}",
                f"- universities covered: {len(universities)} ({'、'.join(universities)})",
                f"- T1 official extractable candidates: {sum(count for key, count in confidence.items() if key.startswith('T1_'))}",
                f"- T2 portal/reachability candidates: {sum(count for key, count in confidence.items() if key.startswith('T2_'))}",
                f"- structured candidate statuses: {dict(status)}",
                "",
                "## 使用边界",
                "",
                "- 这些记录只进入 source_packet/preview/QA 层。",
                "- 未解析院校专业组-year，不打开 canonical/ML。",
                "- 东莞理工学院短链、东北农业大学查询端点、上海工程技术大学计划端点都需要后续可审计核验。",
                "- 中南民族大学计划页可先做广西列解析，但仍需特殊类型隔离和专业组映射 QA。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    confidence = Counter(row.get("collector_confidence", "") for row in rows)
    rollup = [
        {"metric": "web_candidate_rows", "value": len(rows)},
        {"metric": "universities_covered", "value": len({row.get("university_code", "") for row in rows})},
        {"metric": "t1_official_extractable_candidate_rows", "value": sum(count for key, count in confidence.items() if key.startswith("T1_"))},
        {"metric": "t2_portal_or_reachability_candidate_rows", "value": sum(count for key, count in confidence.items() if key.startswith("T2_"))},
        {"metric": "requires_manual_or_browser_approval_rows", "value": sum(1 for row in rows if row.get("requires_manual_approval") == "true")},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"web_candidate_rows={len(rows)}")


if __name__ == "__main__":
    main()
