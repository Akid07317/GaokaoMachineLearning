#!/usr/bin/env python3
"""Build the first isolated reference trend pool seed artifacts.

This script creates non-baseline, non-canonical, non-ML preview artifacts for
the Guangxi physics ordinary undergraduate reference trend pool. It uses local
official source records and local seed tables only; live web collection should
land in source packets first.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

SOURCE_LIST = ROOT / "source_list.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"
SCORE_RANK = ROOT / "clean_data" / "score_rank_table_seed.csv"
NON211_TODO = ROOT / "reports" / "non211_authoritative_todo.csv"
NON211_DISCOVERY = ROOT / "reports" / "non211_authoritative_discovery_candidates_priority.csv"
ENGINEERING_DISCOVERY = ROOT / "reports" / "discovery_engineering_520_fullsweep_candidates_priority.csv"

SOURCE_PACKET_TEMPLATE_OUT = SEED_DIR / "reference_trend_source_packet_template.csv"
SOURCE_PACKET_SEED_OUT = SEED_DIR / "reference_trend_source_packet_local_seed_preview.csv"
SEED_QUEUE_OUT = SEED_DIR / "reference_trend_seed_queue.csv"
INTAKE_PREVIEW_OUT = SEED_DIR / "reference_trend_intake_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_pool_schema_coverage_rollup.csv"
QA_REPORT_OUT = REPORT_DIR / "reference_trend_pool_qa_report.csv"
EXCLUSION_LOG_OUT = REPORT_DIR / "reference_trend_exclusion_log.csv"
SCHEMA_DOC_OUT = DOCS_DIR / "reference_trend_pool_schema.md"
EXECUTION_DOC_OUT = DOCS_DIR / "reference_trend_pool_48h_execution_plan.md"

SOURCE_PACKET_FIELDS = [
    "source_id",
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
    "record_id",
]

SEED_QUEUE_FIELDS = [
    "queue_rank",
    "candidate_id",
    "candidate_source",
    "school_key",
    "school_name",
    "candidate_lane",
    "priority",
    "year_hint",
    "target_url",
    "target_domain",
    "source_title_or_link_text",
    "matched_reason",
    "initial_source_type",
    "initial_confidence_tier",
    "requires_network",
    "next_action",
    "decision_pool_boundary",
    "record_id",
]

INTAKE_FIELDS = [
    "trend_record_id",
    "year",
    "province",
    "batch",
    "subject_category",
    "university_code",
    "university_name",
    "group_code",
    "group_year_key",
    "min_score",
    "min_rank_est",
    "min_rank_low",
    "min_rank_high",
    "rank_source_method",
    "plan_count",
    "has_group_code",
    "has_min_score",
    "has_min_rank",
    "has_plan_count",
    "round_type",
    "special_type_detected",
    "confidence_tier",
    "trend_pool_role",
    "calibration_eligible",
    "qa_status",
    "qa_flags",
    "source_id",
    "source_url",
    "source_owner",
    "source_title",
    "raw_source_layer",
    "decision_pool_boundary",
    "canonical_ml_entry_open",
    "notes",
]

ROLLUP_FIELDS = ["metric", "value"]
QA_FIELDS = ["qa_dimension", "bucket", "row_count", "notes"]
EXCLUSION_FIELDS = [
    "trend_record_id",
    "year",
    "university_name",
    "group_code",
    "qa_status",
    "qa_flags",
    "special_type_detected",
    "source_id",
    "notes",
]

SPECIAL_PATTERNS = [
    ("中外合作", "special_type_international_cooperation"),
    ("合作办学", "special_type_international_cooperation"),
    ("民族班", "special_type_ethnic_class"),
    ("预科", "special_type_preparatory"),
    ("专项", "special_type_special_plan"),
    ("定向", "special_type_directed"),
    ("提前批", "special_type_early_batch"),
    ("艺术", "special_type_art"),
    ("体育", "special_type_sport"),
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


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def first_value(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def detect_special_type(*values: object) -> str:
    text = " ".join(str(value or "") for value in values)
    matches = []
    for pattern, label in SPECIAL_PATTERNS:
        if pattern in text and label not in matches:
            matches.append(label)
    return "|".join(matches)


def source_lookup(source_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("source_id", ""): row for row in source_rows if row.get("source_id")}


def build_source_packet_template() -> None:
    write_csv(SOURCE_PACKET_TEMPLATE_OUT, [], SOURCE_PACKET_FIELDS)


def source_packet_from_source_list(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for index, row in enumerate(source_rows, start=1):
        source_id = row.get("source_id", "")
        data_type = row.get("data_type", "")
        fetch_status = row.get("fetch_status", "")
        eligible = data_type in {"admission_line", "score_rank", "score_rank_query"} and (
            fetch_status.startswith("ok") or "confirmed" in fetch_status
        )
        needs_network = "blocked" in fetch_status or "antibot" in fetch_status or data_type.endswith("_query")
        contains_rank = data_type in {"score_rank", "score_rank_query"} or source_id.endswith("admission_physics_main")
        output.append(
            {
                "source_id": source_id,
                "source_url": row.get("primary_url", ""),
                "source_owner": row.get("source_name", ""),
                "source_title": row.get("title", ""),
                "published_date": "",
                "year": row.get("year", ""),
                "province": "广西",
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_type", ""),
                "round_type": "first_round_or_public_query",
                "university_name": "",
                "university_code": "",
                "source_contains_group_code": bool_text(data_type == "admission_line"),
                "source_contains_min_score": bool_text(data_type == "admission_line"),
                "source_contains_min_rank": bool_text(contains_rank),
                "source_contains_plan_count": "false",
                "special_type_detected": "",
                "raw_file_path": "",
                "collector_note": row.get("notes", ""),
                "collector_confidence": "T1_official_public" if row.get("is_official") == "true" else "T3_unverified",
                "source_packet_status": "local_seed_ready" if eligible else "source_only_needs_followup",
                "intended_layer": "reference_trend_pool_source_packet",
                "requires_network": bool_text(needs_network),
                "requires_manual_approval": bool_text(needs_network and "system" in row.get("access_method", "")),
                "eligible_for_intake_preview": bool_text(eligible and data_type == "admission_line"),
                "record_id": f"reference_trend_source_packet_local_{index:03d}",
            }
        )
    return output


def build_seed_queue(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    queue: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()

    def append(row: dict[str, object]) -> None:
        key = (str(row.get("school_key", "")), str(row.get("target_url", "")))
        if key in seen:
            return
        seen.add(key)
        row["queue_rank"] = len(queue) + 1
        row["record_id"] = f"reference_trend_seed_queue_{len(queue) + 1:04d}"
        queue.append(row)

    for row in source_rows:
        if row.get("data_type") not in {"admission_line", "score_rank", "score_rank_query"}:
            continue
        fetch_status = row.get("fetch_status", "")
        append(
            {
                "candidate_id": row.get("source_id", ""),
                "candidate_source": "source_list",
                "school_key": "",
                "school_name": row.get("source_name", ""),
                "candidate_lane": "gx_exam_authority_core",
                "priority": "P0_local_official_trend_backbone"
                if row.get("data_type") == "admission_line"
                else "P1_rank_conversion_or_rank_source",
                "year_hint": row.get("year", ""),
                "target_url": row.get("primary_url", ""),
                "target_domain": row.get("primary_url", "").split("/")[2] if "://" in row.get("primary_url", "") else "",
                "source_title_or_link_text": row.get("title", ""),
                "matched_reason": row.get("data_type", ""),
                "initial_source_type": "official_exam_authority",
                "initial_confidence_tier": "T1_official_public"
                if row.get("is_official") == "true"
                else "T3_unverified",
                "requires_network": bool_text("blocked" in fetch_status or "query" in row.get("data_type", "")),
                "next_action": "use_local_seed_for_intake_preview"
                if row.get("data_type") == "admission_line" and fetch_status.startswith("ok")
                else "verify_or_fetch_source_packet_before_intake",
                "decision_pool_boundary": "do_not_merge_into_32_school_decision_pool",
            }
        )

    for row in read_csv(NON211_TODO):
        append(
            {
                "candidate_id": row.get("school_key", ""),
                "candidate_source": "non211_authoritative_todo",
                "school_key": row.get("school_key", ""),
                "school_name": row.get("school_name", ""),
                "candidate_lane": "non211_reference_candidate",
                "priority": "P2_reference_trend_official_source_discovery",
                "year_hint": "2024-2025",
                "target_url": row.get("authoritative_url", ""),
                "target_domain": row.get("authoritative_url", "").split("/")[2]
                if "://" in row.get("authoritative_url", "")
                else "",
                "source_title_or_link_text": row.get("authoritative_source", ""),
                "matched_reason": row.get("selection_basis", ""),
                "initial_source_type": "official_or_authoritative_seed",
                "initial_confidence_tier": "T2_authoritative_seed_needs_admission_source",
                "requires_network": "true",
                "next_action": row.get("next_action", "find official admission plan and score source packets"),
                "decision_pool_boundary": "reference_only_not_decision_pool",
            }
        )

    for row in read_csv(NON211_DISCOVERY):
        append(
            {
                "candidate_id": row.get("seed_id", ""),
                "candidate_source": "non211_authoritative_discovery_candidates_priority",
                "school_key": row.get("seed_id", ""),
                "school_name": row.get("source_name", ""),
                "candidate_lane": "non211_discovery_source_packet_candidate",
                "priority": "P3_discovery_candidate_triage",
                "year_hint": row.get("year_hint", ""),
                "target_url": row.get("target_url", ""),
                "target_domain": row.get("target_domain", ""),
                "source_title_or_link_text": first_value(row.get("link_text"), row.get("source_page_title")),
                "matched_reason": row.get("matched_reason", ""),
                "initial_source_type": "official_school_site_discovery",
                "initial_confidence_tier": "T3_discovery_needs_source_packet",
                "requires_network": "true",
                "next_action": "verify page relevance and create source packet",
                "decision_pool_boundary": "reference_only_not_decision_pool",
            }
        )

    for row in read_csv(ENGINEERING_DISCOVERY)[:80]:
        append(
            {
                "candidate_id": row.get("seed_id", ""),
                "candidate_source": "engineering_520_fullsweep_candidates_priority_sample",
                "school_key": row.get("seed_id", ""),
                "school_name": row.get("source_name", ""),
                "candidate_lane": "decision_pool_related_source_packet_candidate",
                "priority": "P4_decision_pool_related_source_triage",
                "year_hint": row.get("year_hint", ""),
                "target_url": row.get("target_url", ""),
                "target_domain": row.get("target_domain", ""),
                "source_title_or_link_text": first_value(row.get("link_text"), row.get("source_page_title")),
                "matched_reason": row.get("matched_reason", ""),
                "initial_source_type": "official_school_site_discovery",
                "initial_confidence_tier": "T3_discovery_needs_source_packet",
                "requires_network": "true",
                "next_action": "verify source packet only; do not write decision canonical",
                "decision_pool_boundary": "source_packet_only_not_canonical",
            }
        )

    return queue


def build_intake_preview(
    admission_rows: list[dict[str, str]], sources_by_id: dict[str, dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    output: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for index, row in enumerate(admission_rows, start=1):
        year = str(row.get("year", "")).strip()
        batch = row.get("batch", "")
        subject = row.get("subject_type", "")
        group_code = row.get("group_code", "")
        min_score = row.get("min_score", "")
        min_rank = first_value(row.get("min_rank_est"), row.get("min_rank_high"), row.get("min_rank_low"))
        source_id = row.get("source_id", "")
        source = sources_by_id.get(source_id, {})
        special = detect_special_type(
            row.get("university_name", ""), group_code, row.get("remark", ""), source.get("title", "")
        )
        flags: list[str] = []
        if year not in {"2024", "2025"}:
            flags.append("not_strict_new_gaokao_year")
        if batch != "本科普通批":
            flags.append("not_undergraduate_ordinary_batch")
        if subject != "物理类":
            flags.append("not_physics_subject")
        if not group_code:
            flags.append("missing_group_code")
        if not min_score:
            flags.append("missing_min_score")
        if not min_rank:
            flags.append("missing_min_rank")
        if special:
            flags.append("special_type_detected")

        eligible = not flags
        if eligible:
            qa_status = "qa_pass_strict_2024_2025_group_year_score_rank"
            role = "strict_2024_2025_group_year"
            confidence = "T1_official_exam_authority_admission_line"
        elif special:
            qa_status = "excluded_special_type_or_mixed_type"
            role = "excluded_from_strict_trend_calibration"
            confidence = "T1_source_T4_record_scope"
        else:
            qa_status = "hold_for_field_or_scope_gap"
            role = "hold_before_trend_calibration"
            confidence = "T1_source_record_needs_qa"

        record_id = f"reference_trend_intake_{index:05d}"
        intake_row = {
            "trend_record_id": record_id,
            "year": year,
            "province": "广西",
            "batch": batch,
            "subject_category": subject,
            "university_code": row.get("university_code", ""),
            "university_name": row.get("university_name", ""),
            "group_code": group_code,
            "group_year_key": f"{row.get('university_code', '')}-{group_code}-{year}",
            "min_score": min_score,
            "min_rank_est": row.get("min_rank_est", ""),
            "min_rank_low": row.get("min_rank_low", ""),
            "min_rank_high": row.get("min_rank_high", ""),
            "rank_source_method": "local_seed_min_rank_est_from_score_rank_table",
            "plan_count": "",
            "has_group_code": bool_text(bool(group_code)),
            "has_min_score": bool_text(bool(min_score)),
            "has_min_rank": bool_text(bool(min_rank)),
            "has_plan_count": "false",
            "round_type": "first_round" if row.get("is_first_round") == "true" else "unknown_or_non_first_round",
            "special_type_detected": special,
            "confidence_tier": confidence,
            "trend_pool_role": role,
            "calibration_eligible": bool_text(eligible),
            "qa_status": qa_status,
            "qa_flags": "|".join(flags) if flags else "none",
            "source_id": source_id,
            "source_url": source.get("primary_url", ""),
            "source_owner": source.get("source_name", ""),
            "source_title": source.get("title", ""),
            "raw_source_layer": "clean_data/admission_line_table_seed.csv",
            "decision_pool_boundary": "reference_trend_pool_only_not_decision_pool_canonical",
            "canonical_ml_entry_open": "false",
            "notes": "Local preview from official Guangxi admission-line seed; plan_count intentionally blank until source packet supplies plan data.",
        }
        output.append(intake_row)
        if not eligible:
            exclusions.append(
                {
                    "trend_record_id": record_id,
                    "year": year,
                    "university_name": row.get("university_name", ""),
                    "group_code": group_code,
                    "qa_status": qa_status,
                    "qa_flags": "|".join(flags),
                    "special_type_detected": special,
                    "source_id": source_id,
                    "notes": "Excluded or held from strict trend calibration in this preview.",
                }
            )
    return output, exclusions


def build_rollup(
    source_packets: list[dict[str, object]],
    seed_queue: list[dict[str, object]],
    intake_rows: list[dict[str, object]],
    score_rank_rows: list[dict[str, str]],
    exclusions: list[dict[str, object]],
) -> list[dict[str, object]]:
    eligible = [row for row in intake_rows if row.get("calibration_eligible") == "true"]
    years = Counter(row.get("year", "") for row in intake_rows)
    eligible_years = Counter(row.get("year", "") for row in eligible)
    unique_schools = {row.get("university_code", "") for row in intake_rows if row.get("university_code")}
    eligible_schools = {row.get("university_code", "") for row in eligible if row.get("university_code")}
    return [
        {"metric": "source_packet_template_created", "value": "true"},
        {"metric": "local_source_packet_seed_rows", "value": len(source_packets)},
        {"metric": "reference_trend_seed_queue_rows", "value": len(seed_queue)},
        {"metric": "admission_line_intake_preview_rows", "value": len(intake_rows)},
        {"metric": "calibration_eligible_rows", "value": len(eligible)},
        {"metric": "excluded_or_hold_rows", "value": len(exclusions)},
        {"metric": "unique_university_codes_in_preview", "value": len(unique_schools)},
        {"metric": "eligible_unique_university_codes", "value": len(eligible_schools)},
        {"metric": "intake_rows_2024", "value": years.get("2024", 0)},
        {"metric": "intake_rows_2025", "value": years.get("2025", 0)},
        {"metric": "eligible_rows_2024", "value": eligible_years.get("2024", 0)},
        {"metric": "eligible_rows_2025", "value": eligible_years.get("2025", 0)},
        {"metric": "score_rank_seed_rows_available", "value": len(score_rank_rows)},
        {"metric": "plan_count_available_rows", "value": 0},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
        {"metric": "network_used_this_run", "value": "false"},
    ]


def build_qa_report(intake_rows: list[dict[str, object]], seed_queue: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for status, count in sorted(Counter(row.get("qa_status", "") for row in intake_rows).items()):
        rows.append(
            {
                "qa_dimension": "intake_qa_status",
                "bucket": status,
                "row_count": count,
                "notes": "Strict trend calibration accepts only pass rows.",
            }
        )
    for year, count in sorted(Counter(row.get("year", "") for row in intake_rows).items()):
        rows.append(
            {
                "qa_dimension": "intake_year",
                "bucket": year,
                "row_count": count,
                "notes": "2024/2025 are strict new-gaokao group-year samples.",
            }
        )
    for priority, count in sorted(Counter(row.get("priority", "") for row in seed_queue).items()):
        rows.append(
            {
                "qa_dimension": "seed_queue_priority",
                "bucket": priority,
                "row_count": count,
                "notes": "Queue items are source-packet work, not canonical writes.",
            }
        )
    return rows


def write_schema_doc(rollup: list[dict[str, object]]) -> None:
    metrics = {row["metric"]: row["value"] for row in rollup}
    SCHEMA_DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend Pool Schema",
                "",
                "日期：2026-05-16",
                "",
                "## 定位",
                "",
                "`reference_trend_pool` 是隔离趋势参考层，用于广西物理类本科普通批的位次波动、计划变化和院校专业组结构背景。它不等于 32 所 `decision_pool`，也不直接写 canonical/ML。",
                "",
                "## 本轮落地文件",
                "",
                "- `clean_data/engineering_guangxi_seed/reference_trend_source_packet_template.csv`",
                "- `clean_data/engineering_guangxi_seed/reference_trend_source_packet_local_seed_preview.csv`",
                "- `clean_data/engineering_guangxi_seed/reference_trend_seed_queue.csv`",
                "- `clean_data/engineering_guangxi_seed/reference_trend_intake_preview.csv`",
                "- `reports/reference_trend_pool_schema_coverage_rollup.csv`",
                "- `reports/reference_trend_pool_qa_report.csv`",
                "- `reports/reference_trend_exclusion_log.csv`",
                "",
                "## 基本单位",
                "",
                "趋势池基本单位是 `院校专业组-year`，不是学校。",
                "",
                "## Intake Preview 字段",
                "",
                ", ".join(f"`{field}`" for field in INTAKE_FIELDS),
                "",
                "## Source Packet 字段",
                "",
                ", ".join(f"`{field}`" for field in SOURCE_PACKET_FIELDS),
                "",
                "## 首轮覆盖",
                "",
                f"- intake preview rows: {metrics.get('admission_line_intake_preview_rows', 0)}",
                f"- calibration eligible rows: {metrics.get('calibration_eligible_rows', 0)}",
                f"- eligible unique university codes: {metrics.get('eligible_unique_university_codes', 0)}",
                f"- eligible rows 2024: {metrics.get('eligible_rows_2024', 0)}",
                f"- eligible rows 2025: {metrics.get('eligible_rows_2025', 0)}",
                f"- plan count available rows: {metrics.get('plan_count_available_rows', 0)}",
                "",
                "## 准入规则",
                "",
                "- 必须是广西、本科普通批、物理类。",
                "- 2024/2025 为严格新高考专业组口径样本。",
                "- 必须有院校专业组代码、最低分、最低位次或可审计位次区间。",
                "- 特殊类型、混合类型或口径不明记录只进 exclusion/hold，不进 strict calibration。",
                "- 计划数缺失不阻止作为 rank/score trend 样本，但会标注 `has_plan_count=false`，不能用于计划数变化分析。",
                "",
                "## 边界",
                "",
                "- 不覆盖人工决策表。",
                "- 不扩 32 所 decision pool。",
                "- 不打开 canonical/ML。",
                "- 联网新增资料必须先成为 source packet，再进入 intake preview 和 QA。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_execution_doc(rollup: list[dict[str, object]]) -> None:
    metrics = {row["metric"]: row["value"] for row in rollup}
    EXECUTION_DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION_DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend Pool 48h Execution Plan",
                "",
                "日期：2026-05-16",
                "",
                "## 本轮结论",
                "",
                f"本地已从广西考试院投档线种子表生成 `{metrics.get('admission_line_intake_preview_rows', 0)}` 条 intake preview，其中 `{metrics.get('calibration_eligible_rows', 0)}` 条可作为严格 2024/2025 院校专业组-year 分数/位次趋势样本。该层仍是 preview，不是 canonical/ML。",
                "",
                "## 48 小时优先级",
                "",
                "1. 把 `reference_trend_seed_queue.csv` 中 P0/P1 官方考试院来源复核为 source packet backbone。",
                "2. 用联网许可补齐 2025 一分一档物理类正式表的本地结构化缓存，先写 source packet，不直接写 final。",
                "3. 从非 211 todo 中优先处理南京信息工程大学、西南石油大学、成都理工大学、天津工业大学等官方招生网来源，产出 source packet。",
                "4. 对 source packet 逐条生成 intake preview，并按特殊类型、批次、选科、院校专业组代码、最低分/位次进行 QA。",
                "5. 计划数单独建 `plan_count_thickening` 子任务；当前投档线样本可用于 rank/score trend，但不能用于计划变化分析。",
                "6. 若需要 Deep Research，只用于定位官方来源，不直接写入趋势结论。",
                "",
                "## 两线程交接",
                "",
                "- 资料搜集线程：只写 source packet、raw_file_path、source reachability note。",
                "- 数据整理线程：只读 source packet，生成 intake preview、QA report、exclusion log、eligible flag。",
                "- 两线程都不得写 32 所 decision pool、canonical 或 ML 输入。",
                "",
                "## 下一轮建议",
                "",
                "优先补 2025 score-rank 正式结构化表，再从非 211 官方招生网中产出 10-20 个高质量 source packet。完成后重跑本脚本，比较 eligible 行数和缺 plan_count 的占比。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    source_rows = read_csv(SOURCE_LIST)
    admission_rows = read_csv(ADMISSION_LINES)
    score_rank_rows = read_csv(SCORE_RANK)
    sources_by_id = source_lookup(source_rows)

    build_source_packet_template()
    source_packets = source_packet_from_source_list(source_rows)
    seed_queue = build_seed_queue(source_rows)
    intake_rows, exclusions = build_intake_preview(admission_rows, sources_by_id)
    rollup = build_rollup(source_packets, seed_queue, intake_rows, score_rank_rows, exclusions)
    qa_report = build_qa_report(intake_rows, seed_queue)

    write_csv(SOURCE_PACKET_SEED_OUT, source_packets, SOURCE_PACKET_FIELDS)
    write_csv(SEED_QUEUE_OUT, seed_queue, SEED_QUEUE_FIELDS)
    write_csv(INTAKE_PREVIEW_OUT, intake_rows, INTAKE_FIELDS)
    write_csv(ROLLUP_OUT, rollup, ROLLUP_FIELDS)
    write_csv(QA_REPORT_OUT, qa_report, QA_FIELDS)
    write_csv(EXCLUSION_LOG_OUT, exclusions, EXCLUSION_FIELDS)
    write_schema_doc(rollup)
    write_execution_doc(rollup)

    print(f"source_packet_rows={len(source_packets)}")
    print(f"seed_queue_rows={len(seed_queue)}")
    print(f"intake_preview_rows={len(intake_rows)}")
    print(f"exclusion_or_hold_rows={len(exclusions)}")


if __name__ == "__main__":
    main()
