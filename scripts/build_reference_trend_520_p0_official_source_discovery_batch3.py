#!/usr/bin/env python3
"""Write batch-3 official web-discovery candidates for 520-window plan sources."""

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
OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch3_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch3_rollup.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch3_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch3.md"

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
        "university_code": "10226",
        "university_name": "哈尔滨医科大学",
        "source_url": "https://www.hrbmu.edu.cn/zhaosheng/info/1216/2608.htm",
        "source_owner": "哈尔滨医科大学普通教育招生网",
        "source_title": "哈尔滨医科大学（校本部）2025年本科招生计划",
        "published_date": "2025-06-18",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_table",
        "source_role": "official_full_plan_table_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "true",
        "special_type_detected": "contains_national_special_columns_needs_exclusion",
        "collector_note": "Official full national plan table includes Guangxi and national-special columns. It is extractable as plan-count source, but uses legacy/aggregate science labels and does not expose Guangxi院校专业组 codes.",
        "collector_confidence": "T1_official_extractable_plan_candidate",
        "source_packet_status": "web_verified_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_after_parse_and_special_type_exclusion",
        "next_action": "parse_guangxi_column_to_source_packet_then_hold_for_group_code_mapping",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10063",
        "university_name": "天津中医药大学",
        "source_url": "https://zsjy.tjutcm.edu.cn/info/1009/8608.htm",
        "source_owner": "天津中医药大学本科招生网",
        "source_title": "2025年在广西本科招生计划及2024年录取情况",
        "published_date": "2025-06-20",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_and_score_embedded_image",
        "source_role": "official_guangxi_plan_score_page_image_candidate",
        "source_contains_group_code": "unknown_until_image_ocr",
        "source_contains_min_score": "unknown_until_image_ocr",
        "source_contains_min_rank": "unknown_until_image_ocr",
        "source_contains_plan_count": "unknown_until_image_ocr",
        "special_type_detected": "unknown_until_image_ocr",
        "collector_note": "Official Guangxi-specific page exists, but content is embedded as an image in web text extraction. Needs screenshot/OCR or browser-image capture before structured source packet.",
        "collector_confidence": "T2_official_image_page_needs_ocr",
        "source_packet_status": "official_page_candidate_needs_image_ocr",
        "eligible_for_intake_preview": "false_until_ocr_extract_and_QA",
        "next_action": "request_browser_or_image_ocr_approval_if_structured_text_not_available",
        "requires_manual_approval": "true",
    },
    {
        "university_code": "10060",
        "university_name": "天津理工大学",
        "source_url": "https://zsb.tjut.edu.cn/info/1014/1627.htm",
        "source_owner": "天津理工大学本科生招生信息网",
        "source_title": "天津理工大学2025年普通本科招生计划",
        "published_date": "2025-06-18",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_query_entry",
        "source_role": "official_plan_query_entry_candidate",
        "source_contains_group_code": "unknown_until_query_endpoint",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_query_endpoint",
        "special_type_detected": "unknown_until_query_endpoint",
        "collector_note": "Official 2025 plan article links to a dedicated plan query page; direct text does not expose Guangxi rows. Query endpoint timed out in lightweight fetch and should be handled as browser/form endpoint if needed.",
        "collector_confidence": "T2_official_query_endpoint_needs_browser_or_form",
        "source_packet_status": "official_query_entry_not_structured",
        "eligible_for_intake_preview": "false_until_endpoint_returns_guangxi_rows",
        "next_action": "request_browser_or_form_endpoint_approval_before_query_replay",
        "requires_manual_approval": "true",
    },
    {
        "university_code": "16301",
        "university_name": "宁波诺丁汉大学",
        "source_url": "https://www.nottingham.edu.cn/cn/study-with-us/undergraduate/entry-requirements/plan.aspx",
        "source_owner": "宁波诺丁汉大学",
        "source_title": "高考招生计划",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_pdf_link_page",
        "source_role": "official_plan_pdf_landing_page",
        "source_contains_group_code": "links_to_pdf",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "links_to_pdf",
        "special_type_detected": "sino_foreign_university_boundary",
        "collector_note": "Official landing page states 2025 plan covers Guangxi and links to the national unified-admission plan PDF. Keep the whole-school Sino-foreign boundary explicit before any calibration use.",
        "collector_confidence": "T1_official_pdf_landing_page",
        "source_packet_status": "official_pdf_landing_page_verified",
        "eligible_for_intake_preview": "false_until_pdf_parse_and_sino_foreign_boundary_QA",
        "next_action": "parse_official_pdf_for_guangxi_plan_counts_then_keep_special_boundary",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "16301",
        "university_name": "宁波诺丁汉大学",
        "source_url": "https://www.nottingham.edu.cn/cn/study-with-us/documents/plan/unnc-gaokao-recruitment-plan-2025.pdf",
        "source_owner": "宁波诺丁汉大学",
        "source_title": "2025宁波诺丁汉大学全国28省（区、市）高考统招招生计划表",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_pdf",
        "source_role": "official_pdf_plan_table_candidate",
        "source_contains_group_code": "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "true",
        "special_type_detected": "sino_foreign_university_boundary",
        "collector_note": "Official PDF is text-readable and includes Guangxi among 28 provinces. Needs column alignment parse before source packet; no direct Guangxi院校专业组 code observed in text preview.",
        "collector_confidence": "T1_official_pdf_extractable_plan_candidate",
        "source_packet_status": "official_pdf_candidate_not_parsed",
        "eligible_for_intake_preview": "false_until_pdf_parse_and_special_boundary_QA",
        "next_action": "parse_pdf_column_layout_for_guangxi_physics_plan_counts",
        "requires_manual_approval": "false",
    },
    {
        "university_code": "10369",
        "university_name": "安徽中医药大学",
        "source_url": "https://bkzs.ahtcm.edu.cn/info/1243/4586.htm",
        "source_owner": "安徽中医药大学本科招生网",
        "source_title": "安徽中医药大学2025年普通本科招生计划",
        "published_date": "2025-06-18",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_embedded_image_or_asset",
        "source_role": "official_plan_page_image_candidate",
        "source_contains_group_code": "unknown_until_image_or_asset_extract",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "unknown_until_image_or_asset_extract",
        "special_type_detected": "unknown_until_image_or_asset_extract",
        "collector_note": "Official 2025 plan page exists but the visible structured content is embedded as an image/asset in text extraction. Needs image OCR or asset download before source packet.",
        "collector_confidence": "T2_official_image_page_needs_ocr",
        "source_packet_status": "official_page_candidate_needs_image_or_asset_extract",
        "eligible_for_intake_preview": "false_until_ocr_or_asset_extract",
        "next_action": "request_browser_or_image_asset_extraction_approval_if_needed",
        "requires_manual_approval": "true",
    },
    {
        "university_code": "10602",
        "university_name": "广西师范大学",
        "source_url": "https://bkzs.gxnu.edu.cn/pg/jh/index.php?JHLBMC=&KLDM=&NF=2025&SSDM=45",
        "source_owner": "广西师范大学本科招生网",
        "source_title": "招生计划：2025 广西",
        "published_date": "",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "round_type": "ordinary_plan_html_table",
        "source_role": "official_html_plan_table_candidate",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "true",
        "special_type_detected": "contains_national_local_special_ethnic_and_ordinary_rows_needs_filter",
        "collector_note": "Official HTML table exposes Guangxi 2025 plan rows with type, subject, batch and plan count. It contains 国家专项/地方专项/民族班/提前批 rows, so ordinary physical本科普通批 must be filtered before intake.",
        "collector_confidence": "T1_official_html_extractable_plan_candidate",
        "source_packet_status": "web_verified_candidate_not_parsed",
        "eligible_for_intake_preview": "conditional_after_parse_and_special_type_exclusion",
        "next_action": "parse_official_html_table_filter_ordinary_physics_undergraduate_batch",
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
    query_by_code = {row.get("university_code", ""): row for row in read_csv(QUERY_PACK)}
    rows: list[dict[str, object]] = []
    for index, item in enumerate(DISCOVERED, start=1):
        query = query_by_code.get(item["university_code"], {})
        rows.append(
            {
                **item,
                "source_id": f"reference_trend_batch3_web_candidate_{index:04d}",
                "query_record_id": query.get("record_id", ""),
                "query_rank": query.get("query_rank", ""),
                "raw_file_path": "",
                "intended_layer": "reference_trend_source_packet_preview_only",
                "requires_network": "true",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "record_id": f"reference_trend_520_p0_source_candidate_batch3_{index:04d}",
            }
        )
    return rows


def write_doc(rows: list[dict[str, object]]) -> None:
    confidence = Counter(row.get("collector_confidence", "") for row in rows)
    status = Counter(row.get("source_packet_status", "") for row in rows)
    manual = sum(1 for row in rows if row.get("requires_manual_approval") == "true")
    universities = sorted({str(row.get("university_name", "")) for row in rows})
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 520 P0 Official Source Discovery Batch 3",
                "",
                f"日期：{date.today().isoformat()}",
                "",
                "## 结论",
                "",
                "本轮联网核验新增一批 P0/P1 官方来源候选，只写入 source discovery preview，不进入 intake、canonical、ML 或 32 所 decision pool。",
                "",
                "## 覆盖",
                "",
                f"- candidate rows: {len(rows)}",
                f"- universities covered: {len(universities)}",
                f"- manual approval required rows: {manual}",
                f"- confidence tiers: {dict(confidence)}",
                f"- source packet statuses: {dict(status)}",
                "",
                "## 学校",
                "",
                *[f"- {name}" for name in universities],
                "",
                "## 下一步",
                "",
                "1. 对 T1 official extractable candidates 优先写 source_packet parse preview。",
                "2. 对 image/OCR 或 browser/form endpoint 候选，先等待人工批准。",
                "3. 继续保持 canonical/ML 关闭，不扩 32 所 decision pool。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)

    confidence = Counter(row.get("collector_confidence", "") for row in rows)
    status = Counter(row.get("source_packet_status", "") for row in rows)
    source_role = Counter(row.get("source_role", "") for row in rows)
    manual = sum(1 for row in rows if row.get("requires_manual_approval") == "true")
    official_extractable = sum(1 for row in rows if str(row.get("collector_confidence", "")).startswith("T1_"))

    rollup = [
        ("batch3_web_candidate_rows", len(rows)),
        ("universities_covered", len({row.get("university_code", "") for row in rows})),
        ("official_extractable_candidate_rows", official_extractable),
        ("manual_approval_required_rows", manual),
        ("trend_record_eligible_rows", 0),
        ("calibration_eligible_rows", 0),
        ("canonical_ml_entry_open", "false"),
        ("decision_pool_expansion_performed", "false"),
    ]
    for key, value in sorted(confidence.items()):
        rollup.append((f"collector_confidence:{key}", value))
    for key, value in sorted(status.items()):
        rollup.append((f"source_packet_status:{key}", value))
    for key, value in sorted(source_role.items()):
        rollup.append((f"source_role:{key}", value))
    write_csv(ROLLUP_OUT, [{"metric": metric, "value": value} for metric, value in rollup], ["metric", "value"])

    exclusion = [
        {
            "record_id": f"reference_trend_batch3_exclusion_{idx:04d}",
            "source_record_id": row["record_id"],
            "university_name": row["university_name"],
            "source_packet_status": row["source_packet_status"],
            "exclusion_or_hold_reason": row["next_action"],
            "reference_trend_pool_eligible": "false",
            "canonical_ml_entry_open": "false",
        }
        for idx, row in enumerate(rows, start=1)
    ]
    write_csv(
        EXCLUSION_OUT,
        exclusion,
        [
            "record_id",
            "source_record_id",
            "university_name",
            "source_packet_status",
            "exclusion_or_hold_reason",
            "reference_trend_pool_eligible",
            "canonical_ml_entry_open",
        ],
    )
    write_doc(rows)

    print(f"batch3_web_candidate_rows={len(rows)}")
    print(f"universities_covered={len({row.get('university_code', '') for row in rows})}")
    print(f"official_extractable_candidate_rows={official_extractable}")
    print(f"manual_approval_required_rows={manual}")
    print("trend_record_eligible_rows=0")


if __name__ == "__main__":
    main()
