#!/usr/bin/env python3
"""Build Changan D2/G2 reference-year and field-mapping preview.

This only writes review previews and patches the row-fix status preview. It does
not alter canonical, ML, or baseline readiness artifacts.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

STATUS_PREVIEW = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv"
QUEUE = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv"
PLAN_SEED = SEED_DIR / "guangxi_physics_plan_seed_merged.csv"
SCORE_SEED = SEED_DIR / "guangxi_physics_score_major_seed_merged.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"
DERIVED_SCORE_SUMMARY = ROOT / "clean_data" / "derived_summary_structured" / "changan_211_derived_score_summary_rows.csv"

ROW_PREVIEW = SEED_DIR / "changan_reference_year_field_mapping_row_preview.csv"
MAPPING_SUMMARY = SEED_DIR / "changan_reference_year_field_mapping_preview.csv"
SCHOOL_SUMMARY = REPORT_DIR / "engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_school_summary.csv"
ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_coverage_rollup.csv"

SCHOOL_KEY = "changan_211"
SCHOOL_NAME = "长安大学"
OFFICIAL_API_URL = "https://zsdata.chd.edu.cn/lqxx/s/api/front/lqxx/getList"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def to_int(value: object) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def normalize_text(value: str) -> str:
    value = value.replace("（", "(").replace("）", ")")
    value = re.sub(r"\s+", "", value)
    return value


def line_type(row: dict[str, str]) -> str:
    group_code = row.get("group_code", "").strip()
    remark = row.get("remark", "").strip()
    if "国家专项" in remark or group_code.startswith("5"):
        return "special_national_project"
    if "预科" in remark or group_code.startswith("7"):
        return "special_preparatory"
    return "ordinary_regular"


def source_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    _, plan_rows = read_csv(PLAN_SEED)
    _, score_rows = read_csv(SCORE_SEED)
    _, line_rows = read_csv(ADMISSION_LINES)
    _, derived_summary = read_csv(DERIVED_SCORE_SUMMARY)

    plan_current = [
        row
        for row in plan_rows
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2025"
        and row.get("province") == "广西"
        and "物理" in row.get("subject_type", "")
        and row.get("type") == "本科普通批"
    ]
    score_reference = [
        row
        for row in score_rows
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2024"
        and row.get("province") == "广西"
        and "物理" in row.get("science_category", "")
        and row.get("type") == "本科普通批"
    ]
    latest_lines = [
        row
        for row in line_rows
        if row.get("university_name") == SCHOOL_NAME
        and row.get("year") == "2025"
        and row.get("batch") == "本科普通批"
        and row.get("subject_type") == "物理类"
        and row.get("is_first_round") == "true"
        and row.get("data_quality") == "official"
    ]
    return plan_current, score_reference, latest_lines, derived_summary


def build_row_preview(
    plan_rows: list[dict[str, str]],
    score_rows: list[dict[str, str]],
    line_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    preview: list[dict[str, object]] = []

    for row in plan_rows:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_api_plan_2025",
                "source_year": row.get("year", ""),
                "source_scope": "official_api_structured_plan",
                "source_kind": "school_official_api",
                "group_code": "",
                "specialty_or_major": row.get("specialty", ""),
                "normalized_major_key": normalize_text(row.get("specialty", "")),
                "plan_count": row.get("plan_count", ""),
                "requirement": row.get("requirement", ""),
                "minimum_score": "",
                "lowest_score_ranking": "",
                "highest_score": "",
                "line_type": "ordinary_plan_row",
                "field_mapping_status": "plan_count_requirement_source_confirmed_2025",
                "source_url": row.get("source_url", OFFICIAL_API_URL),
                "notes": "Latest 2025 plan row from Changan official API; safe for review preview, not canonical/ML.",
            }
        )

    for row in score_rows:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_api_score_rank_2024",
                "source_year": row.get("year", ""),
                "source_scope": "official_api_major_score_rank_reference",
                "source_kind": "school_official_api",
                "group_code": "",
                "specialty_or_major": row.get("major", ""),
                "normalized_major_key": normalize_text(row.get("major", "")),
                "plan_count": "",
                "requirement": row.get("requirement", ""),
                "minimum_score": row.get("minimum_score", ""),
                "lowest_score_ranking": row.get("lowest_score_ranking", ""),
                "highest_score": row.get("highest_score", ""),
                "line_type": "ordinary_score_rank_reference",
                "field_mapping_status": "score_rank_fields_confirmed_2024_reference",
                "source_url": row.get("source_url", OFFICIAL_API_URL),
                "notes": "Comparable 2024 major score/rank reference from Changan official API; reference year must remain explicit.",
            }
        )

    for row in line_rows:
        candidate_type = line_type(row)
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "gx_official_admission_line_candidate_2025",
                "source_year": row.get("year", ""),
                "source_scope": "latest_admission_line_candidate",
                "source_kind": "guangxi_official_admission_line",
                "group_code": row.get("group_code", ""),
                "specialty_or_major": "",
                "normalized_major_key": "",
                "plan_count": "",
                "requirement": row.get("subject_type", ""),
                "minimum_score": row.get("min_score", ""),
                "lowest_score_ranking": row.get("min_rank_est", ""),
                "highest_score": "",
                "line_type": candidate_type,
                "field_mapping_status": "candidate_only_requires_human_acceptance",
                "source_url": row.get("source_id", ""),
                "notes": "Latest 2025 Guangxi official line candidate; keep isolated unless human accepts it as local line supplement.",
            }
        )

    return preview


def build_summary(
    plan_rows: list[dict[str, str]],
    score_rows: list[dict[str, str]],
    line_rows: list[dict[str, str]],
    derived_summary: list[dict[str, str]],
) -> dict[str, object]:
    plan_counts = [to_int(row.get("plan_count")) for row in plan_rows]
    plan_counts = [value for value in plan_counts if value is not None]
    plan_groups = sorted({row.get("requirement", "").strip() for row in plan_rows if row.get("requirement", "").strip()})

    min_scores = [to_int(row.get("minimum_score")) for row in score_rows]
    min_scores = [value for value in min_scores if value is not None]
    ranks = [to_int(row.get("lowest_score_ranking")) for row in score_rows]
    ranks = [value for value in ranks if value is not None]
    high_scores = [to_int(row.get("highest_score")) for row in score_rows]
    high_scores = [value for value in high_scores if value is not None]

    regular_lines = [row for row in line_rows if line_type(row) == "ordinary_regular"]
    isolated_lines = [row for row in line_rows if line_type(row) != "ordinary_regular"]
    regular_scores = [to_int(row.get("min_score")) for row in regular_lines]
    regular_scores = [value for value in regular_scores if value is not None]
    regular_ranks = [to_int(row.get("min_rank_est")) for row in regular_lines]
    regular_ranks = [value for value in regular_ranks if value is not None]

    return {
        "school_key": SCHOOL_KEY,
        "school_name": SCHOOL_NAME,
        "mapping_status": "reference_year_field_mapping_preview_ready",
        "plan_year": "2025",
        "score_reference_year": "2024",
        "latest_admission_line_year": "2025",
        "plan_rows_2025": len(plan_rows),
        "plan_total_count_2025": sum(plan_counts),
        "plan_requirement_group_count": len(plan_groups),
        "plan_requirement_groups": "|".join(plan_groups),
        "score_reference_rows_2024": len(score_rows),
        "score_reference_major_count_2024": len({normalize_text(row.get("major", "")) for row in score_rows}),
        "score_reference_min_score_2024": min(min_scores) if min_scores else "",
        "score_reference_min_rank_2024": max(ranks) if ranks else "",
        "score_reference_high_score_2024": max(high_scores) if high_scores else "",
        "score_reference_rank_rows_2024": len(ranks),
        "derived_score_summary_rows": len(derived_summary),
        "latest_admission_line_rows_2025": len(line_rows),
        "latest_regular_line_group_count_2025": len(regular_lines),
        "latest_regular_line_groups_2025": "|".join(row.get("group_code", "") for row in regular_lines),
        "latest_regular_line_min_score_2025": min(regular_scores) if regular_scores else "",
        "latest_regular_line_min_rank_2025": max(regular_ranks) if regular_ranks else "",
        "isolated_special_line_count_2025": len(isolated_lines),
        "isolated_special_line_groups_2025": "|".join(row.get("group_code", "") for row in isolated_lines),
        "can_resolve_plan_linkage": "yes",
        "can_confirm_score_fields": "yes_2024_official_api",
        "can_confirm_rank_fields": "yes_2024_official_api",
        "can_replace_reference_year_with_2025_official_api_score": "no",
        "can_use_2025_admission_line_candidate": "requires_human_acceptance_or_gap_fill_policy",
        "recommended_status": "keep_G2_caution_with_latest_plan_and_2024_official_api_rank_reference",
        "plan_source_url": OFFICIAL_API_URL,
        "score_source_url": OFFICIAL_API_URL,
        "admission_line_candidate_source_id": "gx_2025_admission_physics_main",
        "repair_note": (
            "2025 计划数/选科/来源可确认；2024 校方 API 专业最低分、最高分、最低位次字段可确认。"
            "2025 广西官方投档线可做最新分数/位次候选，但需人工接受后才能作为本地补充，不可直接替代校方 API 分数字段。"
        ),
        "ml_boundary_note": "reference-year field-mapping preview only; canonical/ML remain closed",
        "record_id": f"{SCHOOL_KEY}-reference-year-field-mapping-preview",
        "source_slug": "pre_ml_d2_g2_changan_reference_year_field_mapping",
    }


def patch_status_preview(status_rows: list[dict[str, str]], summary: dict[str, object]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in status_rows:
        patched: dict[str, object] = dict(row)
        if row.get("school_key") == SCHOOL_KEY:
            patched["fix_queue_status"] = "reference_year_field_mapping_preview_ready"
            patched["fix_priority"] = "P1_reference_year_and_field_mapping_preview_ready"
            patched["fix_class"] = (
                "2025_plan_confirmed|2024_official_api_score_rank_confirmed|"
                "2025_admission_line_candidate_isolated"
            )
            patched["recommended_action"] = (
                "保留 2025 官方 API 计划与 2024 官方 API 专业分数/位次作为当前复核口径；"
                "若要启用 2025 广西投档线最低分/位次，需另行人工接受为本地 line supplement，并隔离专项/预科组。"
            )
            patched["fix_route"] = "local_field_mapping_preview_ready"
            patched["exit_condition"] = "can_reassess_g2_after_human_accepts_reference_year_note"
            patched["reference_year"] = summary["score_reference_year"]
            patched["latest_year"] = summary["plan_year"]
            patched["data_completeness"] = "latest_plan_with_2024_official_api_score_rank_reference"
            patched["total_plan_count"] = summary["plan_total_count_2025"]
            patched["minimum_score"] = summary["score_reference_min_score_2024"]
            patched["minimum_rank"] = summary["score_reference_min_rank_2024"]
            patched["trend_available"] = "true"
            patched["trend_signal"] = "2025_plan_ready_2024_rank_comparable_2025_line_candidate_available"
            patched["gap_signature"] = "reference_year_not_latest|latest_score_rank_candidate_requires_acceptance"
            patched["resolution_status"] = "mapping_preview_ready_with_reference_year_caution"
            patched["plan_source_resolution"] = "official_api_structured"
            patched["score_source_resolution"] = "official_api_major_structured"
            patched["structured_plan_rows"] = summary["plan_rows_2025"]
            patched["structured_score_major_rows"] = summary["score_reference_rows_2024"]
            patched["structured_score_summary_rows"] = summary["derived_score_summary_rows"]
            patched["plan_source_url"] = summary["plan_source_url"]
            patched["score_source_url"] = summary["score_source_url"]
            patched["required_row_fixes"] = "human_accept_or_reject_2025_admission_line_candidate|reference_year_note_required"
            patched["residual_followups"] = "hefei_gongye_P1_reference_year_and_field_mapping"
            patched["ml_boundary_note"] = "reference-year mapping preview only; canonical/ML remain closed"
            patched["record_id"] = f"{SCHOOL_KEY}-d2-g2-request-row-fix-status-preview"
            patched["source_slug"] = "pre_ml_d2_g2_request_row_fix_status_preview"
        output.append(patched)
    return output


def main() -> None:
    status_fields, status_rows = read_csv(STATUS_PREVIEW if STATUS_PREVIEW.exists() else QUEUE)
    plan_rows, score_rows, line_rows, derived_summary = source_rows()

    row_preview = build_row_preview(plan_rows, score_rows, line_rows)
    summary = build_summary(plan_rows, score_rows, line_rows, derived_summary)
    patched_status = patch_status_preview(status_rows, summary)

    preview_fields = [
        "school_key",
        "school_name",
        "row_layer",
        "source_year",
        "source_scope",
        "source_kind",
        "group_code",
        "specialty_or_major",
        "normalized_major_key",
        "plan_count",
        "requirement",
        "minimum_score",
        "lowest_score_ranking",
        "highest_score",
        "line_type",
        "field_mapping_status",
        "source_url",
        "notes",
    ]
    write_csv(ROW_PREVIEW, row_preview, preview_fields)

    summary_fields = [
        "school_key",
        "school_name",
        "mapping_status",
        "plan_year",
        "score_reference_year",
        "latest_admission_line_year",
        "plan_rows_2025",
        "plan_total_count_2025",
        "plan_requirement_group_count",
        "plan_requirement_groups",
        "score_reference_rows_2024",
        "score_reference_major_count_2024",
        "score_reference_min_score_2024",
        "score_reference_min_rank_2024",
        "score_reference_high_score_2024",
        "score_reference_rank_rows_2024",
        "derived_score_summary_rows",
        "latest_admission_line_rows_2025",
        "latest_regular_line_group_count_2025",
        "latest_regular_line_groups_2025",
        "latest_regular_line_min_score_2025",
        "latest_regular_line_min_rank_2025",
        "isolated_special_line_count_2025",
        "isolated_special_line_groups_2025",
        "can_resolve_plan_linkage",
        "can_confirm_score_fields",
        "can_confirm_rank_fields",
        "can_replace_reference_year_with_2025_official_api_score",
        "can_use_2025_admission_line_candidate",
        "recommended_status",
        "plan_source_url",
        "score_source_url",
        "admission_line_candidate_source_id",
        "repair_note",
        "ml_boundary_note",
        "record_id",
        "source_slug",
    ]
    write_csv(MAPPING_SUMMARY, [summary], summary_fields)
    write_csv(SCHOOL_SUMMARY, [summary], summary_fields)
    write_csv(STATUS_PREVIEW, patched_status, status_fields)

    rollup_rows = [
        {"metric": "changan_mapping_school_rows", "value": 1},
        {"metric": "field_mapping_row_preview_rows", "value": len(row_preview)},
        {"metric": "plan_rows_2025", "value": summary["plan_rows_2025"]},
        {"metric": "plan_total_count_2025", "value": summary["plan_total_count_2025"]},
        {"metric": "score_reference_rows_2024", "value": summary["score_reference_rows_2024"]},
        {"metric": "score_reference_min_score_2024", "value": summary["score_reference_min_score_2024"]},
        {"metric": "score_reference_min_rank_2024", "value": summary["score_reference_min_rank_2024"]},
        {"metric": "latest_regular_line_group_count_2025", "value": summary["latest_regular_line_group_count_2025"]},
        {"metric": "latest_regular_line_min_score_2025", "value": summary["latest_regular_line_min_score_2025"]},
        {"metric": "latest_regular_line_min_rank_2025", "value": summary["latest_regular_line_min_rank_2025"]},
        {"metric": "isolated_special_line_count_2025", "value": summary["isolated_special_line_count_2025"]},
        {"metric": "can_replace_reference_year_with_2025_official_api_score", "value": summary["can_replace_reference_year_with_2025_official_api_score"]},
        {"metric": "can_use_2025_admission_line_candidate", "value": summary["can_use_2025_admission_line_candidate"]},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    write_csv(ROLLUP, rollup_rows, ["metric", "value"])

    print(f"field_mapping_row_preview_rows={len(row_preview)}")
    print(f"plan_rows_2025={summary['plan_rows_2025']}")
    print(f"score_reference_rows_2024={summary['score_reference_rows_2024']}")
    print(f"latest_regular_line_min_rank_2025={summary['latest_regular_line_min_rank_2025']}")
    print(f"can_replace_reference_year_with_2025_official_api_score={summary['can_replace_reference_year_with_2025_official_api_score']}")


if __name__ == "__main__":
    main()
