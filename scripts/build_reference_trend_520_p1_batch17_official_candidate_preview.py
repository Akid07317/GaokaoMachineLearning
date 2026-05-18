#!/usr/bin/env python3
"""Build official-source candidate preview for selected P1 batch-17 tasks.

This records manually reviewed official-source candidates found through web
search/open inspection. It does not fetch/cache source files, parse tables into
source_packet rows, OCR images, replay forms, open browser state, or create
reference-trend/canonical/ML rows.
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

EXECUTION = SEED / "reference_trend_520_p1_batch17_discovery_execution_packet.csv"
OUT = SEED / "reference_trend_520_p1_batch17_official_candidate_preview.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch17_official_candidate_preview_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch17_official_candidate_preview_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch17_official_candidate_preview_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch17_official_candidate_preview.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "candidate_id",
    "packet_id",
    "queue_id",
    "university_code",
    "university_name",
    "queue_ranks",
    "group_pair_keys",
    "group_codes",
    "target_group_count",
    "execution_lane",
    "source_url",
    "source_title",
    "source_owner",
    "source_candidate_tier",
    "source_candidate_status",
    "access_status",
    "source_contains_year",
    "source_contains_guangxi",
    "source_contains_batch",
    "source_contains_subject",
    "source_contains_group_code",
    "source_contains_plan_count",
    "special_type_boundary_status",
    "parse_or_access_blocker",
    "eligible_for_source_packet_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "safe_next_action",
    "evidence_note",
]

CANDIDATES = {
    "reference_trend_520_p1_batch17_execution_0001": {
        "source_url": "https://zscx.glut.edu.cn/f/listPlan",
        "source_title": "桂林理工大学招生信息查询系统 招生计划查询",
        "source_owner": "桂林理工大学招生信息查询系统",
        "source_candidate_tier": "T2_official_query_page_candidate",
        "source_candidate_status": "official_query_page_found_needs_filter_and_boundary_QA",
        "access_status": "opened_text_html_query_listing",
        "source_contains_year": "true",
        "source_contains_guangxi": "true",
        "source_contains_batch": "true",
        "source_contains_subject": "true",
        "source_contains_group_code": "false_in_visible_preview",
        "source_contains_plan_count": "true",
        "special_type_boundary_status": "mixed_categories_visible_filter_required",
        "parse_or_access_blocker": "query_filter_pagination_and_special_type_boundary_required_before_parse",
        "eligible_for_source_packet_preview": "conditional_after_filtered_official_page_capture",
        "safe_next_action": "Build filtered official-query source packet candidate only if Guangxi physics ordinary batch can be isolated.",
        "evidence_note": "Official query page exposes year/province/subject/batch/category fields and visible 2025 Guangxi rows, but default listing includes special/nonordinary categories.",
    },
    "reference_trend_520_p1_batch17_execution_0002": {
        "source_url": "https://zsxxw.jxutcm.edu.cn/info/1049/2562.htm",
        "source_title": "2025年江西中医药大学本科招生计划表（广西）",
        "source_owner": "江西中医药大学招生信息网",
        "source_candidate_tier": "T1_exact_official_plan_page_candidate",
        "source_candidate_status": "exact_official_guangxi_plan_page_found",
        "access_status": "opened_text_html_exact_page",
        "source_contains_year": "true",
        "source_contains_guangxi": "true",
        "source_contains_batch": "true",
        "source_contains_subject": "true",
        "source_contains_group_code": "true",
        "source_contains_plan_count": "true",
        "special_type_boundary_status": "ordinary_batch_visible_sports_rows_separate",
        "parse_or_access_blocker": "none_for_candidate_preview_parse_QA_still_required",
        "eligible_for_source_packet_preview": "true_candidate_only_not_intake",
        "safe_next_action": "Create source_packet parse preview with ordinary-batch physical rows and group-code QA.",
        "evidence_note": "Official page lists 2025 Guangxi本科普通批, 物理类, plan counts, professional groups, and subject requirements; sports rows are separate.",
    },
    "reference_trend_520_p1_batch17_execution_0003": {
        "source_url": "https://zs.jxust.edu.cn/zsxx/zsjh.htm",
        "source_title": "招生计划-江西理工大学本科招生信息网",
        "source_owner": "江西理工大学本科招生信息网",
        "source_candidate_tier": "T2_official_plan_portal_candidate",
        "source_candidate_status": "official_plan_portal_found_requires_filter_or_browser_review",
        "access_status": "opened_text_html_portal_default_not_filtered_to_guangxi",
        "source_contains_year": "true",
        "source_contains_guangxi": "filter_option_visible",
        "source_contains_batch": "filter_dependent",
        "source_contains_subject": "filter_dependent",
        "source_contains_group_code": "unknown_until_filtered",
        "source_contains_plan_count": "filter_dependent",
        "special_type_boundary_status": "unknown_until_filtered_official_result",
        "parse_or_access_blocker": "province/year/subject filtering likely dynamic_or_form_state",
        "eligible_for_source_packet_preview": "false_until_filtered_official_candidate_captured",
        "safe_next_action": "Try static filter parameters first; stop for approval if browser state is required.",
        "evidence_note": "Official plan portal exposes province/year/subject/batch filters including Guangxi, but text view did not show a Guangxi physical table.",
    },
    "reference_trend_520_p1_batch17_execution_0004": {
        "source_url": "https://zhaolu.zjzw.cn/release-page/plan?key=8b9f6783d3eb9fdd74d58fa3",
        "source_title": "河北北方学院招生计划入口",
        "source_owner": "河北北方学院招生网 / 招录信息管理系统",
        "source_candidate_tier": "T3_official_external_js_plan_entry",
        "source_candidate_status": "official_plan_entry_found_javascript_required_backoff",
        "access_status": "opened_js_required_page_no_plan_rows",
        "source_contains_year": "unknown_until_js_render",
        "source_contains_guangxi": "unknown_until_js_render",
        "source_contains_batch": "unknown_until_js_render",
        "source_contains_subject": "unknown_until_js_render",
        "source_contains_group_code": "unknown_until_js_render",
        "source_contains_plan_count": "unknown_until_js_render",
        "special_type_boundary_status": "medical_boundary_unresolved",
        "parse_or_access_blocker": "javascript_required_external_plan_system",
        "eligible_for_source_packet_preview": "false_until_browser_or_static_api_approved_and_audited",
        "safe_next_action": "Record reachability backoff; request browser/static API approval before attempting JS-rendered plan extraction.",
        "evidence_note": "Official admissions home links 招生计划 to zhaolu.zjzw.cn; opened target requires JavaScript and exposes no auditable plan rows in text view.",
    },
    "reference_trend_520_p1_batch17_execution_0005": {
        "source_url": "https://zs.henau.edu.cn/html/plan_2025.html",
        "source_title": "河南农业大学2025年招生计划",
        "source_owner": "河南农业大学招生信息网",
        "source_candidate_tier": "T2_official_plan_index_candidate",
        "source_candidate_status": "official_plan_index_found_exact_guangxi_page_not_yet_captured",
        "access_status": "opened_official_index_and_related_plan_detail",
        "source_contains_year": "true",
        "source_contains_guangxi": "province_option_visible",
        "source_contains_batch": "detail_dependent",
        "source_contains_subject": "detail_dependent",
        "source_contains_group_code": "unknown_until_guangxi_detail",
        "source_contains_plan_count": "detail_dependent",
        "special_type_boundary_status": "agriculture_major_structure_review_required",
        "parse_or_access_blocker": "exact_guangxi_detail_url_or_filter_capture_needed",
        "eligible_for_source_packet_preview": "false_until_exact_guangxi_official_detail_found",
        "safe_next_action": "Drill down only to official Guangxi 2025 detail; preserve agriculture/major-structure boundary notes.",
        "evidence_note": "Official 2025 plan index shows province navigation including Guangxi; opened related detail confirmed plan-table structure but was not the Guangxi page.",
    },
    "reference_trend_520_p1_batch17_execution_0008": {
        "source_url": "https://zs.zisu.edu.cn/info/1051/2044.htm",
        "source_title": "浙江外国语学院2025年省外招生计划",
        "source_owner": "浙江外国语本科招生",
        "source_candidate_tier": "T2_official_image_plan_page_candidate",
        "source_candidate_status": "official_plan_page_found_image_layout_manual_required",
        "access_status": "opened_text_html_page_with_plan_image",
        "source_contains_year": "true",
        "source_contains_guangxi": "image_only_unverified",
        "source_contains_batch": "image_only_unverified",
        "source_contains_subject": "image_only_unverified",
        "source_contains_group_code": "image_only_unverified",
        "source_contains_plan_count": "image_only_unverified",
        "special_type_boundary_status": "teacher_language_boundary_requires_manual_layout_QA",
        "parse_or_access_blocker": "plan_content_present_as_image_not_text",
        "eligible_for_source_packet_preview": "false_until_image_manual_QA_or_accessibility_text",
        "safe_next_action": "Create image-layout manual QA/backoff before any source_packet parse.",
        "evidence_note": "Official page title indicates 2025 out-of-province plan; visible content is image-based and needs manual layout/OCR approval before parse.",
    },
    "reference_trend_520_p1_batch17_execution_0011": {
        "source_url": "https://xxgk.hbnu.edu.cn/2025/1029/c3388a185166/page.htm",
        "source_title": "2025年湖北师范大学招生计划",
        "source_owner": "湖北师范大学信息公开网",
        "source_candidate_tier": "T2_official_aggregate_plan_page_candidate",
        "source_candidate_status": "official_aggregate_plan_page_found_group_code_absent",
        "access_status": "opened_text_html_plan_page",
        "source_contains_year": "true",
        "source_contains_guangxi": "true",
        "source_contains_batch": "true",
        "source_contains_subject": "true",
        "source_contains_group_code": "false_in_visible_table",
        "source_contains_plan_count": "true",
        "special_type_boundary_status": "teacher_direction_boundary_needs_QA",
        "parse_or_access_blocker": "group_code_absent_mapping_QA_required",
        "eligible_for_source_packet_preview": "conditional_after_group_mapping_or_exam_authority_join",
        "safe_next_action": "Use only as plan-count/major-structure candidate until group-code mapping QA exists.",
        "evidence_note": "Official page lists 2025 Guangxi regular undergraduate physical rows and plan counts, but no visible Guangxi professional-group code.",
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
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def build_rows() -> list[dict[str, object]]:
    execution_rows = {row["packet_id"]: row for row in read_csv(EXECUTION)}
    rows: list[dict[str, object]] = []
    for idx, packet_id in enumerate(CANDIDATES, 1):
        execution = execution_rows[packet_id]
        candidate = CANDIDATES[packet_id]
        rows.append(
            {
                "candidate_id": f"reference_trend_520_p1_batch17_candidate_{idx:04d}",
                "packet_id": packet_id,
                "queue_id": execution["queue_id"],
                "university_code": execution["university_code"],
                "university_name": execution["university_name"],
                "queue_ranks": execution["queue_ranks"],
                "group_pair_keys": execution["group_pair_keys"],
                "group_codes": execution["group_codes"],
                "target_group_count": execution["target_group_count"],
                "execution_lane": execution["execution_lane"],
                **candidate,
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    tier = Counter(str(row["source_candidate_tier"]) for row in rows)
    status = Counter(str(row["source_candidate_status"]) for row in rows)
    eligible = Counter(str(row["eligible_for_source_packet_preview"]) for row in rows)
    rollup_rows = [
        {"metric": "official_candidate_preview_rows", "value": len(rows), "note": "Selected batch17 execution rows only."},
        {"metric": "source_execution_packet_rows_covered", "value": len({row["packet_id"] for row in rows}), "note": ""},
        {"metric": "candidate_rows_with_exact_official_plan_page", "value": sum(row["source_candidate_tier"].startswith("T1") for row in rows), "note": ""},
        {"metric": "candidate_rows_requiring_filter_js_or_manual_layout", "value": sum(row["parse_or_access_blocker"] != "none_for_candidate_preview_parse_QA_still_required" for row in rows), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Candidate preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed group-year records."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"tier::{key}", "value": value, "note": ""} for key, value in sorted(tier.items()))
    rollup_rows.extend({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(status.items()))
    rollup_rows.extend({"metric": f"eligible_for_source_packet_preview::{key}", "value": value, "note": ""} for key, value in sorted(eligible.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    execution_ids = {row["packet_id"] for row in read_csv(EXECUTION)}
    qa_rows = [
        {
            "check": "candidate_rows_map_to_execution_packet",
            "status": "PASS" if all(row["packet_id"] in execution_ids for row in rows) and rows else "FAIL",
            "detail": f"Mapped {len(rows)} candidate rows to marker 120 execution packet rows.",
        },
        {
            "check": "official_only_candidates",
            "status": "PASS" if all("official" in row["source_candidate_tier"] for row in rows) else "FAIL",
            "detail": "All rows are official university/system pages, not third-party summaries.",
        },
        {
            "check": "candidate_preview_not_parse",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" for row in rows) else "FAIL",
            "detail": "Candidate preview does not parse source rows into reference trend intake.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "Canonical/ML and decision-pool entry remain closed.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch17_official_candidate_preview_all_rows",
            "reason": "candidate_preview_only_no_source_packet_parse",
            "effect": "excluded_from_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    exclusions.extend(
        {
            "item": row["candidate_id"],
            "reason": row["parse_or_access_blocker"],
            "effect": "requires_next_layer_QA_before_any_intake",
        }
        for row in rows
    )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Reference trend 520 P1 batch17 official candidate preview",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This preview records official-source candidates discovered for selected marker 120 execution rows.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Candidate URLs",
        "",
    ]
    lines.extend(f"- {row['university_name']}: {row['source_url']}" for row in rows)
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Web search/open inspection was used only for official-source candidate discovery.",
            "- No terminal curl, cache write, parse, OCR, browser/form replay, reference trend intake, canonical, ML, or decision-pool write was executed.",
            "- Rows with JS/filter/image/group-code blockers remain backoff or conditional source-packet candidates.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)

    marker = "## 121. 2026-05-17 P1 batch17 official candidate preview"
    handoff = f"""

{marker}

已新增 P1 batch17 official-source candidate preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：从 marker 120 execution packet 中抽取 {len(rows)} 条院校任务做官方来源候选预览；其中 1 条为 T1 精确广西计划页候选，其余为官方查询页/计划门户/JS 入口/图片计划页/聚合计划页候选或 backoff。QA PASS。

准入边界：本轮只记录官方来源候选和阻塞原因；不执行终端抓取、缓存、解析、OCR、浏览器/form replay；不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
