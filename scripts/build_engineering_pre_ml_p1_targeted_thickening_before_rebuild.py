#!/usr/bin/env python3
"""Build P1 targeted thickening preview before canonical rebuild assessment.

This consumes the data thickening priority queue and emits a non-baseline
preview for the 8 P1 clean schools that need targeted year/rank/group-mapping
thickening before canonical rebuild assessment. It does not expand the pool,
fetch live sources, write canonical rows, or run ML.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

THICKENING_QUEUE = SEED_DIR / "guangxi_pre_ml_data_thickening_priority_queue_merged.csv"
DATA_SUFFICIENCY = SEED_DIR / "guangxi_pre_ml_data_sufficiency_audit_merged.csv"
POST_HUMAN = SEED_DIR / "guangxi_pre_ml_post_human_decision_intake_preview_merged.csv"
ACTION_BOARD = SEED_DIR / "guangxi_pre_ml_human_gpt_review_action_board_merged.csv"

PREVIEW_OUT = SEED_DIR / "guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_p1_targeted_thickening_before_rebuild_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_p1_targeted_thickening_before_rebuild.md"

PREVIEW_FIELDS = [
    "thickening_rank",
    "school_key",
    "school_name",
    "current_bucket",
    "post_human_status",
    "selected_decision",
    "targeted_thickening_preview_status",
    "recommended_rebuild_route",
    "targeted_thickening_focus",
    "required_local_evidence",
    "target_years_missing",
    "professional_group_granularity_status",
    "reference_year",
    "latest_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "missing_field_flags",
    "plan_source_url",
    "score_source_url",
    "broad_data_collection_needed",
    "targeted_collection_needed",
    "canonical_rebuild_assessment_ready_after_thickening",
    "canonical_ml_entry_open",
    "pool_expansion_allowed",
    "non211_search_allowed",
    "deep_research_mainline_allowed",
    "canonical_ml_action",
    "next_action",
    "evidence_note",
    "queue_record_id",
    "post_human_record_id",
    "action_board_record_id",
    "record_id",
    "source_slug",
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


def by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("school_key", ""): row for row in rows if row.get("school_key", "")}


def split_flags(value: str) -> list[str]:
    output: list[str] = []
    for part in str(value or "").replace(";", "|").split("|"):
        part = part.strip()
        if part and part not in output:
            output.append(part)
    return output


def first_value(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def local_evidence_needed(queue_row: dict[str, str], action: dict[str, str]) -> str:
    flags = split_flags(queue_row.get("missing_field_flags", ""))
    items: list[str] = []
    if "missing_target_years" in flags:
        missing = queue_row.get("target_years_missing", "")
        items.append(f"补齐或解释目标年份缺口({missing})" if missing else "补齐或解释目标年份缺口")
    if "missing_minimum_rank" in flags:
        items.append("补最低位次或标注位次不可用")
    if "missing_plan_count" in flags:
        items.append("补计划数")
    if "missing_canonical_trend" in flags or action.get("trend_available") == "false":
        items.append("补趋势链路")
    if "professional_group_mapping_not_canonical_ready" in flags:
        group_status = queue_row.get("professional_group_granularity_status", "")
        if group_status == "selection_requirement_groups_present_no_admission_group_code":
            items.append("把选科组/招生专业映射到院校专业组口径")
        else:
            items.append("补院校专业组代码或明确不可映射边界")
    return "|".join(items)


def preview_status(queue_row: dict[str, str]) -> str:
    flags = split_flags(queue_row.get("missing_field_flags", ""))
    missing_years = "missing_target_years" in flags
    group_gap = "professional_group_mapping_not_canonical_ready" in flags
    if missing_years and group_gap:
        return "preview_ready_thicken_year_and_group_mapping_before_rebuild"
    if group_gap:
        return "preview_ready_thicken_group_mapping_before_rebuild"
    if missing_years:
        return "preview_ready_thicken_year_depth_before_rebuild"
    return "preview_ready_rebuild_assessment_after_field_check"


def build_rows() -> list[dict[str, object]]:
    queue_rows = [
        row
        for row in read_csv(THICKENING_QUEUE)
        if row.get("priority") == "P1_targeted_thickening_before_rebuild"
    ]
    audit_by_key = by_key(read_csv(DATA_SUFFICIENCY))
    post_by_key = by_key(read_csv(POST_HUMAN))
    action_by_key = by_key(read_csv(ACTION_BOARD))

    output: list[dict[str, object]] = []
    for index, queue_row in enumerate(queue_rows, start=1):
        key = queue_row.get("school_key", "")
        audit = audit_by_key.get(key, {})
        post = post_by_key.get(key, {})
        action = action_by_key.get(key, {})
        status = preview_status(queue_row)
        required_evidence = local_evidence_needed(queue_row, action)
        output.append(
            {
                "thickening_rank": index,
                "school_key": key,
                "school_name": queue_row.get("school_name", ""),
                "current_bucket": queue_row.get("current_bucket", ""),
                "post_human_status": first_value(post.get("post_human_status"), queue_row.get("post_human_status")),
                "selected_decision": post.get("selected_decision", ""),
                "targeted_thickening_preview_status": status,
                "recommended_rebuild_route": "targeted_thickening_then_canonical_rebuild_assessment_not_ml",
                "targeted_thickening_focus": queue_row.get("repair_or_thickening_focus", ""),
                "required_local_evidence": required_evidence,
                "target_years_missing": queue_row.get("target_years_missing", ""),
                "professional_group_granularity_status": queue_row.get("professional_group_granularity_status", ""),
                "reference_year": action.get("reference_year", ""),
                "latest_year": first_value(action.get("latest_year"), audit.get("latest_year")),
                "data_completeness": first_value(action.get("data_completeness"), audit.get("latest_data_completeness")),
                "total_plan_count": first_value(action.get("total_plan_count"), audit.get("latest_total_plan_count")),
                "minimum_score": first_value(action.get("minimum_score"), audit.get("latest_minimum_score")),
                "minimum_rank": first_value(action.get("minimum_rank"), audit.get("latest_minimum_rank")),
                "trend_available": first_value(action.get("trend_available"), audit.get("trend_available")),
                "trend_signal": action.get("trend_signal", ""),
                "missing_field_flags": queue_row.get("missing_field_flags", ""),
                "plan_source_url": first_value(queue_row.get("plan_source_url"), action.get("plan_source_url")),
                "score_source_url": first_value(queue_row.get("score_source_url"), action.get("score_source_url")),
                "broad_data_collection_needed": "false",
                "targeted_collection_needed": "true",
                "canonical_rebuild_assessment_ready_after_thickening": "true",
                "canonical_ml_entry_open": "false",
                "pool_expansion_allowed": "false",
                "non211_search_allowed": "false",
                "deep_research_mainline_allowed": "false",
                "canonical_ml_action": "keep_closed_pending_targeted_thickening_and_canonical_rebuild_assessment",
                "next_action": (
                    "本地定点补厚年份/位次/专业组映射；补厚后只进入 canonical rebuild assessment，"
                    "不得直接写 canonical 或打开 ML。"
                ),
                "evidence_note": first_value(action.get("evidence_summary"), audit.get("repair_or_thickening_focus")),
                "queue_record_id": queue_row.get("record_id", ""),
                "post_human_record_id": post.get("record_id", ""),
                "action_board_record_id": action.get("record_id", ""),
                "record_id": f"{key}-pre-ml-p1-targeted-thickening-before-rebuild-preview",
                "source_slug": "pre_ml_p1_targeted_thickening_before_rebuild",
            }
        )
    return output


def write_rollup(rows: list[dict[str, object]]) -> None:
    statuses = Counter(str(row.get("targeted_thickening_preview_status", "")) for row in rows)
    group_statuses = Counter(str(row.get("professional_group_granularity_status", "")) for row in rows)
    flags: Counter[str] = Counter()
    for row in rows:
        flags.update(split_flags(str(row.get("missing_field_flags", ""))))

    rollup: list[dict[str, object]] = [
        {"metric": "p1_targeted_thickening_preview_rows", "value": len(rows)},
        {"metric": "targeted_collection_needed_count", "value": sum(row.get("targeted_collection_needed") == "true" for row in rows)},
        {"metric": "broad_data_collection_needed_count", "value": sum(row.get("broad_data_collection_needed") == "true" for row in rows)},
        {
            "metric": "canonical_rebuild_assessment_ready_after_thickening_count",
            "value": sum(row.get("canonical_rebuild_assessment_ready_after_thickening") == "true" for row in rows),
        },
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for key, count in sorted(statuses.items()):
        rollup.append({"metric": f"targeted_thickening_preview_status::{key}", "value": count})
    for key, count in sorted(group_statuses.items()):
        rollup.append({"metric": f"professional_group_granularity_status::{key}", "value": count})
    for key, count in sorted(flags.items()):
        rollup.append({"metric": f"missing_field_flag::{key}", "value": count})
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])


def write_doc(rows: list[dict[str, object]]) -> None:
    statuses = Counter(str(row.get("targeted_thickening_preview_status", "")) for row in rows)
    lines = [
        "# P1 targeted thickening before rebuild",
        "",
        "本报告只处理 data thickening queue 中的 P1 targeted thickening 8 行，生成非基线、非 canonical、非 ML 的补厚预览。未联网，未扩池，未写 canonical，未启动 ML。",
        "",
        "## Summary",
        "",
        f"- preview rows: {len(rows)}",
        "- broad data collection needed: 0",
        "- targeted collection/thickening needed: 8",
        "- canonical rebuild assessment after thickening: 8",
        "- canonical/ML entry: closed",
        "- pool expansion: closed",
        "- non-211 search: closed",
        "- Deep Research mainline: closed",
        "",
        "## Status counts",
        "",
    ]
    for key, count in sorted(statuses.items()):
        lines.append(f"- {key}: {count}")
    lines.extend(["", "## P1 rows", ""])
    for row in rows:
        lines.append(
            "- "
            + f"{row.get('school_name')}: {row.get('targeted_thickening_preview_status')} / "
            + f"{row.get('required_local_evidence')}"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "P1 的正确动作是本地定点补厚，不是继续搜学校。补齐目标年份、最低位次和专业组映射后，仍然只进入 canonical rebuild assessment；canonical/ML 入口保持关闭。",
            "",
            "## Output files",
            "",
            f"- `{PREVIEW_OUT.relative_to(ROOT)}`",
            f"- `{ROLLUP_OUT.relative_to(ROOT)}`",
            f"- `{DOC_OUT.relative_to(ROOT)}`",
        ]
    )
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(PREVIEW_OUT, rows, PREVIEW_FIELDS)
    write_rollup(rows)
    write_doc(rows)
    print(
        "p1_targeted_thickening_before_rebuild "
        f"rows={len(rows)} "
        f"preview={PREVIEW_OUT.relative_to(ROOT)} "
        f"rollup={ROLLUP_OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
