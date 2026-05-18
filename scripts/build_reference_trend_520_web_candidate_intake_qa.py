#!/usr/bin/env python3
"""QA web-discovered 520-window plan source candidates.

This is the organizing-thread gate after source discovery. It turns web
candidate rows into source-packet intake readiness, exclusion notes, and the
next discovery batch. It does not create trend records, canonical data, or ML
inputs.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

WEB_CANDIDATES = SEED_DIR / "reference_trend_520_plan_discovery_web_candidates_preview.csv"
QUERY_PACK = SEED_DIR / "reference_trend_520_plan_discovery_query_pack.csv"

INTAKE_OUT = SEED_DIR / "reference_trend_520_plan_discovery_web_candidates_intake_preview.csv"
NEXT_BATCH_OUT = SEED_DIR / "reference_trend_520_plan_discovery_next_batch_workbench.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_plan_discovery_web_candidates_qa_rollup.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_plan_discovery_web_candidates_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_plan_discovery_web_candidates_qa.md"

INTAKE_FIELDS = [
    "source_id",
    "university_code",
    "university_name",
    "source_url",
    "source_role",
    "collector_confidence",
    "source_packet_status",
    "qa_status",
    "source_packet_intake_eligible",
    "trend_record_eligible",
    "calibration_eligible",
    "required_identity_fields_present",
    "field_gaps",
    "blocking_issues",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]

EXCLUSION_FIELDS = [
    "source_id",
    "university_code",
    "university_name",
    "source_url",
    "qa_status",
    "exclusion_or_hold_reason",
    "required_resolution",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]

NEXT_BATCH_FIELDS = [
    "batch_rank",
    "query_rank",
    "university_code",
    "university_name",
    "source_packet_priority",
    "highest_priority_score",
    "urgent_group_pairs",
    "trend_directions",
    "primary_search_query",
    "secondary_search_query",
    "site_search_query",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
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


def has_identity(row: dict[str, str]) -> bool:
    required = ["source_url", "source_owner", "source_title", "year", "province", "batch", "subject_category"]
    return all(str(row.get(field, "")).strip() for field in required)


def assess(row: dict[str, str]) -> dict[str, object]:
    gaps: list[str] = []
    issues: list[str] = []
    status = row.get("source_packet_status", "")

    if row.get("source_contains_group_code") != "true":
        gaps.append("explicit_university_group_code")
    if row.get("source_contains_plan_count") != "true":
        gaps.append("plan_count")
    if row.get("source_contains_min_score") != "true":
        gaps.append("min_score")
    if row.get("source_contains_min_rank") != "true":
        gaps.append("min_rank")

    special = row.get("special_type_detected", "")
    if "needs_exclusion" in special:
        issues.append("special_type_rows_must_be_excluded")
    if row.get("requires_manual_approval") == "true":
        issues.append("manual_or_browser_approval_required")
    if row.get("eligible_for_intake_preview", "").startswith("false"):
        issues.append("specific_structured_source_not_verified")
    if not has_identity(row):
        issues.append("identity_fields_incomplete")

    source_packet_ready = status == "web_verified_candidate_not_parsed" and has_identity(row)
    if source_packet_ready:
        qa_status = "source_packet_intake_ready_parse_required"
    elif "official_portal" in status or "reachability" in status:
        qa_status = "hold_for_specific_page_or_endpoint"
    else:
        qa_status = "hold_for_manual_review"

    return {
        "source_id": row.get("source_id", ""),
        "university_code": row.get("university_code", ""),
        "university_name": row.get("university_name", ""),
        "source_url": row.get("source_url", ""),
        "source_role": row.get("source_role", ""),
        "collector_confidence": row.get("collector_confidence", ""),
        "source_packet_status": status,
        "qa_status": qa_status,
        "source_packet_intake_eligible": "true" if source_packet_ready else "false",
        "trend_record_eligible": "false",
        "calibration_eligible": "false",
        "required_identity_fields_present": "true" if has_identity(row) else "false",
        "field_gaps": "|".join(gaps),
        "blocking_issues": "|".join(issues) if issues else "parse_required_before_trend_use",
        "next_action": row.get("next_action", ""),
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_source_packet_qa_only_not_decision_pool",
        "record_id": row.get("record_id", ""),
    }


def build_next_batch(covered_codes: set[str], limit: int = 20) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for query in read_csv(QUERY_PACK):
        if query.get("university_code", "") in covered_codes:
            continue
        if query.get("source_packet_priority") != "P0_plan_source_packet_urgent":
            continue
        rows.append(
            {
                "batch_rank": len(rows) + 1,
                "query_rank": query.get("query_rank", ""),
                "university_code": query.get("university_code", ""),
                "university_name": query.get("university_name", ""),
                "source_packet_priority": query.get("source_packet_priority", ""),
                "highest_priority_score": query.get("highest_priority_score", ""),
                "urgent_group_pairs": query.get("urgent_group_pairs", ""),
                "trend_directions": query.get("trend_directions", ""),
                "primary_search_query": query.get("primary_search_query", ""),
                "secondary_search_query": query.get("secondary_search_query", ""),
                "site_search_query": query.get("site_search_query", ""),
                "next_action": "search_official_plan_source_then_write_web_candidate_or_source_packet",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_next_batch_only_not_decision_pool",
                "record_id": f"reference_trend_520_next_batch_{len(rows) + 1:04d}",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def write_doc(intake: list[dict[str, object]], next_batch: list[dict[str, object]]) -> None:
    status = Counter(row.get("qa_status", "") for row in intake)
    ready = sum(1 for row in intake if row.get("source_packet_intake_eligible") == "true")
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 520 Web Candidate Intake QA",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已对上一轮 520 位次窗口 P0 官方来源候选做整理线程 QA。当前只有中南民族大学的 2 条官方页可进入 source packet intake 的解析准备；其余 4 条仍停留在官方入口/可达性层，不能进入趋势记录。",
                "",
                "## 覆盖",
                "",
                f"- web candidate rows QAed: {len(intake)}",
                f"- source packet intake ready rows: {ready}",
                f"- hold rows: {len(intake) - ready}",
                f"- trend record eligible rows: 0",
                f"- calibration eligible rows: 0",
                f"- QA status counts: {dict(status)}",
                f"- next P0 discovery batch rows prepared: {len(next_batch)}",
                "",
                "## 下一步",
                "",
                "- 对中南民族大学 2025 计划页解析广西列，并标注预科/专项等特殊类型排除。",
                "- 对中南民族大学 2024 分数页只作为分数参考候选，位次仍需考试院或一分一档转换。",
                "- 下一批优先继续查 P0 query pack 中未覆盖学校，仍只写 source packet/preview/QA 层。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    candidates = read_csv(WEB_CANDIDATES)
    intake = [assess(row) for row in candidates]
    covered_codes = {row.get("university_code", "") for row in candidates}
    next_batch = build_next_batch(covered_codes)

    write_csv(INTAKE_OUT, intake, INTAKE_FIELDS)
    exclusions = []
    for index, row in enumerate(intake, start=1):
        if row.get("source_packet_intake_eligible") == "true":
            reason = "not_excluded_from_source_packet_intake_but_not_trend_record"
            resolution = "parse_source_packet_then_run_field_QA"
        else:
            reason = str(row.get("blocking_issues", "hold"))
            resolution = "find_specific_structured_official_source_or_get_manual_browser_approval"
        exclusions.append(
            {
                "source_id": row.get("source_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_url": row.get("source_url", ""),
                "qa_status": row.get("qa_status", ""),
                "exclusion_or_hold_reason": reason,
                "required_resolution": resolution,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_qa_only_not_decision_pool",
                "record_id": f"reference_trend_520_web_candidate_exclusion_{index:04d}",
            }
        )
    write_csv(EXCLUSION_OUT, exclusions, EXCLUSION_FIELDS)
    write_csv(NEXT_BATCH_OUT, next_batch, NEXT_BATCH_FIELDS)

    rollup = [
        {"metric": "web_candidate_rows_qaed", "value": len(intake)},
        {"metric": "source_packet_intake_ready_rows", "value": sum(1 for row in intake if row.get("source_packet_intake_eligible") == "true")},
        {"metric": "hold_for_specific_page_or_endpoint_rows", "value": sum(1 for row in intake if row.get("qa_status") == "hold_for_specific_page_or_endpoint")},
        {"metric": "trend_record_eligible_rows", "value": 0},
        {"metric": "calibration_eligible_rows", "value": 0},
        {"metric": "next_p0_batch_rows", "value": len(next_batch)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(intake, next_batch)
    print(f"web_candidate_rows_qaed={len(intake)}")
    print(f"source_packet_intake_ready_rows={rollup[1]['value']}")
    print(f"next_p0_batch_rows={len(next_batch)}")


if __name__ == "__main__":
    main()
