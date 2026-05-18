#!/usr/bin/env python3
"""Build P0 caution repair / G2 reassessment preview.

This consumes the post-human decision layer and the data thickening priority
queue, then emits a non-baseline preview for the 8 P0 caution/row-fix schools.
It does not fetch live sources, expand the pool, write canonical rows, or run
ML.
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
ROW_FIX_DECISION = SEED_DIR / "guangxi_pre_ml_d2_row_fix_acceptance_decision_sheet_merged.csv"
ACTION_BOARD = SEED_DIR / "guangxi_pre_ml_human_gpt_review_action_board_merged.csv"

PREVIEW_OUT = SEED_DIR / "guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_p0_caution_repair_reassessment_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_p0_caution_repair_reassessment.md"

PREVIEW_FIELDS = [
    "reassessment_rank",
    "school_key",
    "school_name",
    "p0_source_type",
    "current_bucket",
    "post_human_status",
    "selected_decision",
    "reassessment_preview_status",
    "recommended_reassessment_route",
    "mandatory_review_items",
    "remaining_caution_flags",
    "accepted_fix_boundary",
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
    "gap_signature",
    "plan_source_url",
    "score_source_url",
    "broad_data_collection_needed",
    "targeted_repair_needed",
    "canonical_ml_entry_open",
    "pool_expansion_allowed",
    "non211_search_allowed",
    "deep_research_mainline_allowed",
    "canonical_ml_action",
    "next_action",
    "evidence_note",
    "queue_record_id",
    "row_fix_record_id",
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
    flags: list[str] = []
    for part in str(value or "").replace(";", "|").split("|"):
        part = part.strip()
        if part and part not in flags:
            flags.append(part)
    return flags


def join_unique(*values: object) -> str:
    output: list[str] = []
    for value in values:
        if isinstance(value, (list, tuple, set)):
            parts = value
        else:
            parts = split_flags(str(value or ""))
        for part in parts:
            text = str(part or "").strip()
            if text and text not in output:
                output.append(text)
    return "|".join(output)


def first_value(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def mandatory_items(queue_row: dict[str, str], row_fix: dict[str, str], action: dict[str, str]) -> str:
    flags = split_flags(queue_row.get("missing_field_flags", ""))
    items: list[str] = []
    if "missing_target_years" in flags:
        missing = queue_row.get("target_years_missing", "")
        items.append(f"补齐或解释目标年份缺口({missing})" if missing else "补齐或解释目标年份缺口")
    if "missing_plan_count" in flags:
        items.append("补齐计划数或保留计划数缺失 caution")
    if "missing_canonical_trend" in flags:
        items.append("补齐趋势链路或保留 no_trend caution")
    if "professional_group_mapping_not_canonical_ready" in flags:
        items.append("补专业组/选科组到 canonical 口径的映射说明")
    if row_fix:
        gap = row_fix.get("gap_signature", "")
        if "missing_2025_rank" in gap:
            items.append("确认 2025 分数不能替代 2024 位次")
        if "reference_year_not_latest" in gap:
            items.append("确认 reference_year 不是 latest_year 的可比边界")
        if "rank_not_page_provided" in gap or "rank_not_api_field" in gap:
            items.append("确认最低位次为派生值而非页面/API 字段")
        if "overview_min_vs_major_detail_min" in gap:
            items.append("人工判定概览最低分与专业明细最低分口径")
        if "source_identity" in row_fix.get("fix_priority", "") or "detail_urls_inferred" in row_fix.get("evidence_note", ""):
            items.append("确认官方 payload URL 替代占位/推断 detail URL")
    if action.get("trend_available", "") == "false" and "补齐趋势链路或保留 no_trend caution" not in items:
        items.append("补齐趋势链路或保留 no_trend caution")
    return "|".join(items)


def reassessment_route(
    queue_row: dict[str, str],
    row_fix: dict[str, str],
    post_human: dict[str, str],
) -> tuple[str, str, str]:
    if row_fix:
        exit_condition = row_fix.get("row_fix_exit_condition", "")
        boundary = first_value(row_fix.get("recommended_action"), row_fix.get("decision_notes"))
        gap = row_fix.get("gap_signature", "")
        if (
            "rank_source" in exit_condition
            or "rank_derived" in gap
            or "rank_not_page_provided" in gap
            or "rank_not_api_field" in gap
            or "missing_2025_rank" in gap
        ):
            status = "preview_ready_reassess_g2_after_rank_boundary_note"
        elif "reference_year" in exit_condition or "reference_year_not_latest" in gap:
            status = "preview_ready_reassess_g2_after_reference_year_note"
        elif "source_identity" in row_fix.get("fix_priority", ""):
            status = "preview_ready_reassess_g2_after_source_identity_fix"
        else:
            status = "preview_ready_reassess_g2_after_row_fix_acceptance"
        return (
            status,
            "row_fix_accepted_reassess_g2_before_canonical_rebuild",
            boundary,
        )

    status = post_human.get("post_human_status", "")
    if status == "post_human_gate_confirmed_caution_with_note":
        return (
            "preview_ready_reassess_g2_after_caution_note",
            "caution_gate_confirmed_repair_then_rebuild_assessment",
            first_value(post_human.get("decision_notes"), queue_row.get("recommended_next_action")),
        )

    return (
        "manual_check_needed_before_reassessment",
        "manual_route_before_canonical_rebuild",
        queue_row.get("recommended_next_action", ""),
    )


def build_rows() -> list[dict[str, object]]:
    queue_rows = [
        row
        for row in read_csv(THICKENING_QUEUE)
        if row.get("priority") == "P0_caution_repair_or_g2_reassessment"
    ]
    data_by_key = by_key(read_csv(DATA_SUFFICIENCY))
    post_by_key = by_key(read_csv(POST_HUMAN))
    row_fix_by_key = by_key(read_csv(ROW_FIX_DECISION))
    action_by_key = by_key(read_csv(ACTION_BOARD))

    output: list[dict[str, object]] = []
    for index, queue_row in enumerate(queue_rows, start=1):
        key = queue_row.get("school_key", "")
        audit = data_by_key.get(key, {})
        post = post_by_key.get(key, {})
        row_fix = row_fix_by_key.get(key, {})
        action = action_by_key.get(key, {})
        status, route, boundary = reassessment_route(queue_row, row_fix, post)
        p0_source_type = "row_fix_accepted_for_g2_reassessment" if row_fix else "caution_gate_confirmed_with_note"

        gap_signature = first_value(row_fix.get("gap_signature"), action.get("gap_signature"), audit.get("missing_field_flags"))
        evidence_note = join_unique(
            row_fix.get("evidence_note", ""),
            post.get("evidence_note", ""),
            action.get("evidence_summary", ""),
            queue_row.get("repair_or_thickening_focus", ""),
        )
        flags = join_unique(queue_row.get("missing_field_flags", ""), gap_signature)

        output.append(
            {
                "reassessment_rank": index,
                "school_key": key,
                "school_name": queue_row.get("school_name", ""),
                "p0_source_type": p0_source_type,
                "current_bucket": queue_row.get("current_bucket", ""),
                "post_human_status": first_value(post.get("post_human_status"), queue_row.get("post_human_status")),
                "selected_decision": first_value(row_fix.get("selected_decision"), post.get("selected_decision")),
                "reassessment_preview_status": status,
                "recommended_reassessment_route": route,
                "mandatory_review_items": mandatory_items(queue_row, row_fix, action),
                "remaining_caution_flags": flags,
                "accepted_fix_boundary": boundary,
                "target_years_missing": queue_row.get("target_years_missing", ""),
                "professional_group_granularity_status": queue_row.get("professional_group_granularity_status", ""),
                "reference_year": first_value(row_fix.get("reference_year"), action.get("reference_year")),
                "latest_year": first_value(row_fix.get("latest_year"), action.get("latest_year"), audit.get("latest_year")),
                "data_completeness": first_value(
                    row_fix.get("data_completeness"), action.get("data_completeness"), audit.get("latest_data_completeness")
                ),
                "total_plan_count": first_value(
                    row_fix.get("total_plan_count"), action.get("total_plan_count"), audit.get("latest_total_plan_count")
                ),
                "minimum_score": first_value(
                    row_fix.get("minimum_score"), action.get("minimum_score"), audit.get("latest_minimum_score")
                ),
                "minimum_rank": first_value(
                    row_fix.get("minimum_rank"), action.get("minimum_rank"), audit.get("latest_minimum_rank")
                ),
                "trend_available": first_value(row_fix.get("trend_available"), action.get("trend_available"), audit.get("trend_available")),
                "trend_signal": first_value(row_fix.get("trend_signal"), action.get("trend_signal")),
                "gap_signature": gap_signature,
                "plan_source_url": first_value(row_fix.get("plan_source_url"), queue_row.get("plan_source_url"), action.get("plan_source_url")),
                "score_source_url": first_value(row_fix.get("score_source_url"), queue_row.get("score_source_url"), action.get("score_source_url")),
                "broad_data_collection_needed": "false",
                "targeted_repair_needed": "true",
                "canonical_ml_entry_open": "false",
                "pool_expansion_allowed": "false",
                "non211_search_allowed": "false",
                "deep_research_mainline_allowed": "false",
                "canonical_ml_action": "keep_closed_pending_p0_reassessment_and_canonical_rebuild_assessment",
                "next_action": (
                    "人工/GPT 复评 P0 caution 边界；只接受字段备注、来源身份、年份/位次/专业组映射修复，"
                    "不得直接写 canonical 或打开 ML。"
                ),
                "evidence_note": evidence_note,
                "queue_record_id": queue_row.get("record_id", ""),
                "row_fix_record_id": row_fix.get("record_id", ""),
                "post_human_record_id": post.get("record_id", ""),
                "action_board_record_id": action.get("record_id", ""),
                "record_id": f"{key}-pre-ml-p0-caution-repair-reassessment-preview",
                "source_slug": "pre_ml_p0_caution_repair_reassessment",
            }
        )
    return output


def write_rollup(rows: list[dict[str, object]]) -> None:
    p0_source = Counter(str(row.get("p0_source_type", "")) for row in rows)
    status = Counter(str(row.get("reassessment_preview_status", "")) for row in rows)
    group_status = Counter(str(row.get("professional_group_granularity_status", "")) for row in rows)
    flags: Counter[str] = Counter()
    for row in rows:
        flags.update(split_flags(str(row.get("remaining_caution_flags", ""))))

    rollup: list[dict[str, object]] = [
        {"metric": "p0_caution_repair_reassessment_preview_rows", "value": len(rows)},
        {"metric": "row_fix_accepted_for_reassessment_rows", "value": p0_source.get("row_fix_accepted_for_g2_reassessment", 0)},
        {"metric": "caution_gate_confirmed_with_note_rows", "value": p0_source.get("caution_gate_confirmed_with_note", 0)},
        {"metric": "targeted_repair_needed_count", "value": sum(row.get("targeted_repair_needed") == "true" for row in rows)},
        {"metric": "broad_data_collection_needed_count", "value": sum(row.get("broad_data_collection_needed") == "true" for row in rows)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for key, count in sorted(status.items()):
        rollup.append({"metric": f"reassessment_preview_status::{key}", "value": count})
    for key, count in sorted(group_status.items()):
        rollup.append({"metric": f"professional_group_granularity_status::{key}", "value": count})
    for key, count in sorted(flags.items()):
        rollup.append({"metric": f"remaining_caution_flag::{key}", "value": count})
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])


def write_doc(rows: list[dict[str, object]]) -> None:
    p0_source = Counter(str(row.get("p0_source_type", "")) for row in rows)
    lines = [
        "# P0 caution repair / G2 reassessment preview",
        "",
        "本报告只处理 data thickening queue 中的 P0 caution/row-fix 8 行，生成非基线、非 canonical、非 ML 的复评预览。未联网，未扩池，未写 canonical，未启动 ML。",
        "",
        "## Summary",
        "",
        f"- preview rows: {len(rows)}",
        f"- row fix accepted for reassessment: {p0_source.get('row_fix_accepted_for_g2_reassessment', 0)}",
        f"- caution gate confirmed with note: {p0_source.get('caution_gate_confirmed_with_note', 0)}",
        "- broad data collection needed: 0",
        "- targeted repair needed: 8",
        "- canonical/ML entry: closed",
        "- pool expansion: closed",
        "- non-211 search: closed",
        "- Deep Research mainline: closed",
        "",
        "## P0 rows",
        "",
    ]
    for row in rows:
        lines.append(
            "- "
            + f"{row.get('school_name')}: {row.get('reassessment_preview_status')} / "
            + f"{row.get('mandatory_review_items')}"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "P0 的正确动作不是扩池，而是把已接受的 row-fix preview 和已确认的 caution note 转成 G2 复评边界。复评只处理年份、位次、趋势、专业组映射和来源身份备注；通过后也只能进入 canonical rebuild assessment，不能直接写 canonical/ML。",
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
        "p0_caution_repair_reassessment "
        f"rows={len(rows)} "
        f"preview={PREVIEW_OUT.relative_to(ROOT)} "
        f"rollup={ROLLUP_OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
