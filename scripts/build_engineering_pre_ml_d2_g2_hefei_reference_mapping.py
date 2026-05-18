#!/usr/bin/env python3
"""Build HFUT D2/G2 reference-year and field-mapping preview.

The preview keeps direct-page major scores, overview scores, derived ranks, and
Guangxi official admission-line candidates in separate layers.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
DIRECT_DIR = ROOT / "clean_data" / "direct_page_structured"
DERIVED_DIR = ROOT / "clean_data" / "derived_summary_structured"
REPORT_DIR = ROOT / "reports"

STATUS_PREVIEW = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv"
QUEUE = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv"
PLAN_SEED = SEED_DIR / "guangxi_physics_plan_seed_merged.csv"
SCORE_SEED = SEED_DIR / "guangxi_physics_score_major_seed_merged.csv"
SCORE_SUMMARY_SEED = SEED_DIR / "guangxi_physics_score_summary_seed_merged.csv"
DIRECT_PLAN = DIRECT_DIR / "hfut_guangxi_plan_rows.csv"
DIRECT_SCORE = DIRECT_DIR / "hfut_guangxi_score_rows.csv"
DIRECT_OVERVIEW = DIRECT_DIR / "hfut_guangxi_overview_rows.csv"
DIRECT_SUMMARY = REPORT_DIR / "hfut_guangxi_direct_page_summary.csv"
DERIVED_SUMMARY = DERIVED_DIR / "hefei_gongda_211_derived_score_summary_rows.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"

ROW_PREVIEW = SEED_DIR / "hefei_gongda_reference_year_field_mapping_row_preview.csv"
MAPPING_SUMMARY = SEED_DIR / "hefei_gongda_reference_year_field_mapping_preview.csv"
SCHOOL_SUMMARY = REPORT_DIR / "engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_school_summary.csv"
ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_coverage_rollup.csv"

SCHOOL_KEY = "hefei_gongda_211"
SCHOOL_NAME = "合肥工业大学"
SCHOOL_NAME_PUBLIC = "合肥工业大学本科招生"
SOURCE_URL = "http://bkzs.hfut.edu.cn/f/zsjhAndLqfs/广西"
XUANCHENG_NAME = "合肥工业大学(宣城校区)"


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


def rows_for() -> dict[str, list[dict[str, str]]]:
    _, plan_seed = read_csv(PLAN_SEED)
    _, score_seed = read_csv(SCORE_SEED)
    _, score_summary_seed = read_csv(SCORE_SUMMARY_SEED)
    _, direct_plan = read_csv(DIRECT_PLAN)
    _, direct_score = read_csv(DIRECT_SCORE)
    _, direct_overview = read_csv(DIRECT_OVERVIEW)
    _, direct_summary = read_csv(DIRECT_SUMMARY)
    _, derived_summary = read_csv(DERIVED_SUMMARY)
    _, admission_lines = read_csv(ADMISSION_LINES)

    plan_seed_rows = [
        row
        for row in plan_seed
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2025"
        and row.get("province") == "广西"
        and "物理" in row.get("subject_type", "")
    ]
    score_seed_rows = [
        row
        for row in score_seed
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2024"
        and row.get("province") == "广西"
        and "物理" in row.get("science_category", "")
    ]
    score_summary_rows = [
        row
        for row in score_summary_seed
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2024"
        and row.get("province") == "广西"
        and "物理" in row.get("subject_type", "")
    ]
    admission_2025 = [
        row
        for row in admission_lines
        if row.get("year") == "2025"
        and row.get("batch") == "本科普通批"
        and row.get("subject_type") == "物理类"
        and row.get("university_name") in {SCHOOL_NAME, XUANCHENG_NAME}
        and row.get("is_first_round") == "true"
        and row.get("data_quality") == "official"
    ]
    admission_2024 = [
        row
        for row in admission_lines
        if row.get("year") == "2024"
        and row.get("batch") == "本科普通批"
        and row.get("subject_type") == "物理类"
        and row.get("university_name") in {SCHOOL_NAME, XUANCHENG_NAME}
        and row.get("is_first_round") == "true"
        and row.get("data_quality") == "official"
    ]
    return {
        "plan_seed": plan_seed_rows,
        "score_seed": score_seed_rows,
        "score_summary_seed": score_summary_rows,
        "direct_plan": direct_plan,
        "direct_score": direct_score,
        "direct_overview": direct_overview,
        "direct_summary": direct_summary,
        "derived_summary": derived_summary,
        "admission_2025": admission_2025,
        "admission_2024": admission_2024,
    }


def build_row_preview(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    preview: list[dict[str, object]] = []

    for row in data["plan_seed"]:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_direct_page_plan_2025_unique_seed",
                "source_year": row.get("year", ""),
                "source_scope": "official_direct_page_plan",
                "source_kind": "school_official_direct_page",
                "school_scope": "hfut_direct_page_scope_unsplit",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "specialty_or_major": row.get("specialty", ""),
                "normalized_major_key": normalize_text(row.get("specialty", "")),
                "plan_count": row.get("plan_count", ""),
                "requirement": row.get("requirement", ""),
                "minimum_score": "",
                "lowest_score_ranking": "",
                "highest_score": "",
                "line_type": "plan_row",
                "field_mapping_status": "plan_count_source_confirmed_requirement_missing",
                "source_url": row.get("source_url", SOURCE_URL),
                "notes": "2025 plan row from HFUT direct Guangxi page; unique seed layer dedupes repeated major rows.",
            }
        )

    for row in data["score_seed"]:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_direct_page_major_score_2024_unique_seed",
                "source_year": row.get("year", ""),
                "source_scope": "official_direct_page_major_score_no_rank",
                "source_kind": "school_official_direct_page",
                "school_scope": "hfut_direct_page_scope_unsplit",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "specialty_or_major": row.get("major", ""),
                "normalized_major_key": normalize_text(row.get("major", "")),
                "plan_count": "",
                "requirement": row.get("requirement", ""),
                "minimum_score": row.get("minimum_score", ""),
                "lowest_score_ranking": row.get("lowest_score_ranking", ""),
                "highest_score": row.get("highest_score", ""),
                "line_type": "major_score_reference",
                "field_mapping_status": "score_fields_confirmed_rank_missing_in_page",
                "source_url": row.get("source_url", SOURCE_URL),
                "notes": "2024 major score from HFUT direct Guangxi page; rank is not present in row source.",
            }
        )

    for row in data["direct_overview"]:
        if row.get("year") != "2024":
            continue
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_direct_page_overview_2024",
                "source_year": row.get("year", ""),
                "source_scope": "official_direct_page_school_overview",
                "source_kind": "school_official_direct_page",
                "school_scope": "hfut_direct_page_scope_unsplit",
                "admission_type": row.get("physics_type", ""),
                "group_code": "",
                "specialty_or_major": "",
                "normalized_major_key": "",
                "plan_count": "",
                "requirement": "物理类",
                "minimum_score": row.get("physics_minimum_score", ""),
                "lowest_score_ranking": "",
                "highest_score": "",
                "line_type": "overview_school_min_score",
                "field_mapping_status": "overview_min_score_conflicts_with_major_detail_min",
                "source_url": row.get("source_url", SOURCE_URL),
                "notes": "Overview table exposes 2024 physics minimum score 550, lower than major-detail min 572; needs scope/campus decision.",
            }
        )

    for row in data["score_summary_seed"]:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "derived_major_score_summary_2024",
                "source_year": row.get("year", ""),
                "source_scope": "derived_from_major_detail_and_score_rank_table",
                "source_kind": "derived_summary",
                "school_scope": "hfut_direct_page_scope_unsplit",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "specialty_or_major": "",
                "normalized_major_key": "",
                "plan_count": "",
                "requirement": row.get("subject_type", ""),
                "minimum_score": row.get("minimum_score", ""),
                "lowest_score_ranking": row.get("minimum_rank", ""),
                "highest_score": row.get("maximum_score", ""),
                "line_type": "derived_score_rank_reference",
                "field_mapping_status": "rank_derived_not_page_provided",
                "source_url": row.get("source_url", SOURCE_URL),
                "notes": row.get("remarks", ""),
            }
        )

    for year_key in ("admission_2024", "admission_2025"):
        for row in data[year_key]:
            school_scope = "exact_school_name" if row.get("university_name") == SCHOOL_NAME else "separate_xuancheng_campus"
            preview.append(
                {
                    "school_key": SCHOOL_KEY,
                    "school_name": row.get("university_name", SCHOOL_NAME),
                    "row_layer": f"gx_official_admission_line_candidate_{row.get('year', '')}",
                    "source_year": row.get("year", ""),
                    "source_scope": "admission_line_candidate",
                    "source_kind": "guangxi_official_admission_line",
                    "school_scope": school_scope,
                    "admission_type": row.get("remark", "") or "普通组",
                    "group_code": row.get("group_code", ""),
                    "specialty_or_major": "",
                    "normalized_major_key": "",
                    "plan_count": "",
                    "requirement": row.get("subject_type", ""),
                    "minimum_score": row.get("min_score", ""),
                    "lowest_score_ranking": row.get("min_rank_est", ""),
                    "highest_score": "",
                    "line_type": line_type(row),
                    "field_mapping_status": "candidate_only_requires_human_acceptance",
                    "source_url": row.get("source_id", ""),
                    "notes": "Guangxi official admission line candidate; keep isolated until school/campus scope is accepted.",
                }
            )

    return preview


def min_int(rows: list[dict[str, str]], field: str) -> int | str:
    values = [to_int(row.get(field)) for row in rows]
    values = [value for value in values if value is not None]
    return min(values) if values else ""


def max_int(rows: list[dict[str, str]], field: str) -> int | str:
    values = [to_int(row.get(field)) for row in rows]
    values = [value for value in values if value is not None]
    return max(values) if values else ""


def sum_int(rows: list[dict[str, str]], field: str) -> int:
    values = [to_int(row.get(field)) for row in rows]
    return sum(value for value in values if value is not None)


def summary_line_stats(rows: list[dict[str, str]], school_name: str, line_year: str) -> dict[str, object]:
    filtered = [row for row in rows if row.get("university_name") == school_name and row.get("year") == line_year]
    ordinary = [row for row in filtered if line_type(row) == "ordinary_regular"]
    special = [row for row in filtered if line_type(row) != "ordinary_regular"]
    return {
        "ordinary_count": len(ordinary),
        "ordinary_groups": "|".join(row.get("group_code", "") for row in ordinary),
        "ordinary_min_score": min_int(ordinary, "min_score"),
        "ordinary_min_rank": max_int(ordinary, "min_rank_est"),
        "special_count": len(special),
        "special_groups": "|".join(row.get("group_code", "") for row in special),
    }


def build_summary(data: dict[str, list[dict[str, str]]]) -> dict[str, object]:
    plan_ordinary = [row for row in data["plan_seed"] if row.get("type") == "普通批"]
    plan_special = [row for row in data["plan_seed"] if row.get("type") != "普通批"]
    score_ordinary = [row for row in data["score_seed"] if row.get("type") == "普通批"]
    score_special = [row for row in data["score_seed"] if row.get("type") != "普通批"]
    overview_2024 = next((row for row in data["direct_overview"] if row.get("year") == "2024"), {})
    derived_ordinary = next((row for row in data["score_summary_seed"] if row.get("type") == "普通批"), {})
    derived_special = [row for row in data["score_summary_seed"] if row.get("type") != "普通批"]
    exact_2025 = summary_line_stats(data["admission_2025"], SCHOOL_NAME, "2025")
    xuancheng_2025 = summary_line_stats(data["admission_2025"], XUANCHENG_NAME, "2025")
    exact_2024 = summary_line_stats(data["admission_2024"], SCHOOL_NAME, "2024")
    xuancheng_2024 = summary_line_stats(data["admission_2024"], XUANCHENG_NAME, "2024")
    direct_summary = data["direct_summary"][0] if data["direct_summary"] else {}

    return {
        "school_key": SCHOOL_KEY,
        "school_name": SCHOOL_NAME_PUBLIC,
        "mapping_status": "reference_year_field_mapping_preview_ready",
        "plan_year": "2025",
        "score_reference_year": "2024",
        "latest_admission_line_year": "2025",
        "direct_page_plan_rows_raw": direct_summary.get("plan_rows_2025_physics", ""),
        "plan_seed_rows_2025": len(data["plan_seed"]),
        "plan_ordinary_rows_2025": len(plan_ordinary),
        "plan_ordinary_total_count_2025": sum_int(plan_ordinary, "plan_count"),
        "plan_special_rows_2025": len(plan_special),
        "plan_special_total_count_2025": sum_int(plan_special, "plan_count"),
        "plan_requirement_missing_rows_2025": sum(1 for row in data["plan_seed"] if not row.get("requirement", "").strip()),
        "direct_page_score_rows_raw": direct_summary.get("score_rows_physics_expanded", ""),
        "score_seed_rows_2024": len(data["score_seed"]),
        "score_ordinary_rows_2024": len(score_ordinary),
        "score_special_rows_2024": len(score_special),
        "score_ordinary_min_score_2024": min_int(score_ordinary, "minimum_score"),
        "score_ordinary_high_score_2024": max_int(score_ordinary, "highest_score"),
        "score_rank_rows_in_page_2024": sum(1 for row in data["score_seed"] if row.get("lowest_score_ranking", "").strip()),
        "overview_2024_physics_min_score": overview_2024.get("physics_minimum_score", ""),
        "overview_2024_physics_control_line": overview_2024.get("physics_control_line", ""),
        "overview_vs_major_detail_delta": (
            (to_int(derived_ordinary.get("minimum_score")) or 0)
            - (to_int(overview_2024.get("physics_minimum_score")) or 0)
            if derived_ordinary and overview_2024
            else ""
        ),
        "derived_summary_rows_2024": len(data["score_summary_seed"]),
        "derived_ordinary_min_score_2024": derived_ordinary.get("minimum_score", ""),
        "derived_ordinary_min_rank_2024": derived_ordinary.get("minimum_rank", ""),
        "derived_ordinary_high_score_2024": derived_ordinary.get("maximum_score", ""),
        "derived_special_min_score_2024": min_int(derived_special, "minimum_score"),
        "derived_special_min_rank_2024": max_int(derived_special, "minimum_rank"),
        "latest_exact_regular_line_group_count_2025": exact_2025["ordinary_count"],
        "latest_exact_regular_line_groups_2025": exact_2025["ordinary_groups"],
        "latest_exact_regular_line_min_score_2025": exact_2025["ordinary_min_score"],
        "latest_exact_regular_line_min_rank_2025": exact_2025["ordinary_min_rank"],
        "latest_exact_special_line_count_2025": exact_2025["special_count"],
        "latest_exact_special_line_groups_2025": exact_2025["special_groups"],
        "latest_xuancheng_regular_line_group_count_2025": xuancheng_2025["ordinary_count"],
        "latest_xuancheng_regular_line_min_score_2025": xuancheng_2025["ordinary_min_score"],
        "latest_xuancheng_regular_line_min_rank_2025": xuancheng_2025["ordinary_min_rank"],
        "reference_exact_regular_line_min_score_2024": exact_2024["ordinary_min_score"],
        "reference_exact_regular_line_min_rank_2024": exact_2024["ordinary_min_rank"],
        "reference_xuancheng_regular_line_min_score_2024": xuancheng_2024["ordinary_min_score"],
        "reference_xuancheng_regular_line_min_rank_2024": xuancheng_2024["ordinary_min_rank"],
        "can_resolve_plan_linkage": "yes_count_ready_but_group_requirement_missing",
        "can_confirm_score_fields": "partial_major_detail_and_overview_conflict",
        "can_confirm_rank_fields": "no_page_rank_derived_rank_or_line_candidate_only",
        "can_replace_reference_year_with_2025_school_page_score": "no",
        "can_use_2025_admission_line_candidate": "requires_human_acceptance_and_campus_scope_decision",
        "recommended_status": "keep_G2_caution_mapping_preview_ready_rank_and_campus_scope_caution",
        "plan_source_url": SOURCE_URL,
        "score_source_url": SOURCE_URL,
        "admission_line_candidate_source_id": "gx_2025_admission_physics_main",
        "repair_note": (
            "2025 计划数可确认，但选科/专业组字段缺失；2024 专业分数可确认但页面不含位次，"
            "当前 rank 来自一分一档推导。2024 概览最低分 550 与专业明细最低分 572 不一致，"
            "需人工决定是否按学校/校区投档线补充。"
        ),
        "ml_boundary_note": "reference-year field-mapping preview only; canonical/ML remain closed",
        "record_id": f"{SCHOOL_KEY}-reference-year-field-mapping-preview",
        "source_slug": "pre_ml_d2_g2_hefei_reference_year_field_mapping",
    }


def patch_status_preview(status_rows: list[dict[str, str]], summary: dict[str, object]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in status_rows:
        patched: dict[str, object] = dict(row)
        if row.get("school_key") == SCHOOL_KEY:
            patched["fix_queue_status"] = "reference_year_field_mapping_preview_ready"
            patched["fix_priority"] = "P1_reference_year_and_field_mapping_preview_ready"
            patched["fix_class"] = (
                "2025_plan_count_confirmed|2024_direct_page_major_score_confirmed|"
                "rank_derived_not_page_provided|overview_min_score_conflict|campus_scope_candidate_isolated"
            )
            patched["recommended_action"] = (
                "保留 2025 直达页计划与 2024 专业明细分数作为当前复核口径；"
                "位次标记为一分一档推导，不是页面字段；概览最低分 550 与专业明细最低分 572 需人工判定口径。"
            )
            patched["fix_route"] = "local_field_mapping_preview_ready"
            patched["exit_condition"] = "can_reassess_g2_after_human_resolves_overview_vs_major_detail_and_rank_source"
            patched["reference_year"] = summary["score_reference_year"]
            patched["latest_year"] = summary["plan_year"]
            patched["data_completeness"] = "latest_plan_with_2024_direct_page_score_reference_rank_derived"
            patched["total_plan_count"] = summary["plan_ordinary_total_count_2025"]
            patched["minimum_score"] = summary["derived_ordinary_min_score_2024"]
            patched["minimum_rank"] = summary["derived_ordinary_min_rank_2024"]
            patched["trend_available"] = "true"
            patched["trend_signal"] = "2025_plan_ready_2024_score_detail_ready_rank_derived_line_candidate_available"
            patched["gap_signature"] = (
                "reference_year_not_latest|rank_not_page_provided|overview_min_vs_major_detail_min|"
                "campus_scope_cleanup_required|professional_group_mapping_missing"
            )
            patched["resolution_status"] = "mapping_preview_ready_with_rank_and_scope_caution"
            patched["plan_source_resolution"] = "official_page_structured"
            patched["score_source_resolution"] = "official_page_major_structured"
            patched["structured_plan_rows"] = summary["plan_seed_rows_2025"]
            patched["structured_score_major_rows"] = summary["score_seed_rows_2024"]
            patched["structured_score_summary_rows"] = summary["derived_summary_rows_2024"]
            patched["plan_source_url"] = summary["plan_source_url"]
            patched["score_source_url"] = summary["score_source_url"]
            patched["required_row_fixes"] = (
                "human_resolve_overview_min_score_vs_major_detail_min|rank_derivation_note_required|"
                "campus_scope_cleanup|professional_group_mapping_missing"
            )
            patched["residual_followups"] = "nanhang_211_P1_reference_year_and_field_mapping"
            patched["ml_boundary_note"] = "reference-year mapping preview only; canonical/ML remain closed"
            patched["record_id"] = f"{SCHOOL_KEY}-d2-g2-request-row-fix-status-preview"
            patched["source_slug"] = "pre_ml_d2_g2_request_row_fix_status_preview"
        output.append(patched)
    return output


def main() -> None:
    status_fields, status_rows = read_csv(STATUS_PREVIEW if STATUS_PREVIEW.exists() else QUEUE)
    data = rows_for()
    row_preview = build_row_preview(data)
    summary = build_summary(data)
    patched_status = patch_status_preview(status_rows, summary)

    preview_fields = [
        "school_key",
        "school_name",
        "row_layer",
        "source_year",
        "source_scope",
        "source_kind",
        "school_scope",
        "admission_type",
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
        "direct_page_plan_rows_raw",
        "plan_seed_rows_2025",
        "plan_ordinary_rows_2025",
        "plan_ordinary_total_count_2025",
        "plan_special_rows_2025",
        "plan_special_total_count_2025",
        "plan_requirement_missing_rows_2025",
        "direct_page_score_rows_raw",
        "score_seed_rows_2024",
        "score_ordinary_rows_2024",
        "score_special_rows_2024",
        "score_ordinary_min_score_2024",
        "score_ordinary_high_score_2024",
        "score_rank_rows_in_page_2024",
        "overview_2024_physics_min_score",
        "overview_2024_physics_control_line",
        "overview_vs_major_detail_delta",
        "derived_summary_rows_2024",
        "derived_ordinary_min_score_2024",
        "derived_ordinary_min_rank_2024",
        "derived_ordinary_high_score_2024",
        "derived_special_min_score_2024",
        "derived_special_min_rank_2024",
        "latest_exact_regular_line_group_count_2025",
        "latest_exact_regular_line_groups_2025",
        "latest_exact_regular_line_min_score_2025",
        "latest_exact_regular_line_min_rank_2025",
        "latest_exact_special_line_count_2025",
        "latest_exact_special_line_groups_2025",
        "latest_xuancheng_regular_line_group_count_2025",
        "latest_xuancheng_regular_line_min_score_2025",
        "latest_xuancheng_regular_line_min_rank_2025",
        "reference_exact_regular_line_min_score_2024",
        "reference_exact_regular_line_min_rank_2024",
        "reference_xuancheng_regular_line_min_score_2024",
        "reference_xuancheng_regular_line_min_rank_2024",
        "can_resolve_plan_linkage",
        "can_confirm_score_fields",
        "can_confirm_rank_fields",
        "can_replace_reference_year_with_2025_school_page_score",
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
        {"metric": "hefei_mapping_school_rows", "value": 1},
        {"metric": "field_mapping_row_preview_rows", "value": len(row_preview)},
        {"metric": "direct_page_plan_rows_raw", "value": summary["direct_page_plan_rows_raw"]},
        {"metric": "plan_seed_rows_2025", "value": summary["plan_seed_rows_2025"]},
        {"metric": "plan_ordinary_total_count_2025", "value": summary["plan_ordinary_total_count_2025"]},
        {"metric": "score_seed_rows_2024", "value": summary["score_seed_rows_2024"]},
        {"metric": "score_rank_rows_in_page_2024", "value": summary["score_rank_rows_in_page_2024"]},
        {"metric": "overview_2024_physics_min_score", "value": summary["overview_2024_physics_min_score"]},
        {"metric": "derived_ordinary_min_score_2024", "value": summary["derived_ordinary_min_score_2024"]},
        {"metric": "derived_ordinary_min_rank_2024", "value": summary["derived_ordinary_min_rank_2024"]},
        {"metric": "overview_vs_major_detail_delta", "value": summary["overview_vs_major_detail_delta"]},
        {"metric": "latest_exact_regular_line_min_score_2025", "value": summary["latest_exact_regular_line_min_score_2025"]},
        {"metric": "latest_exact_regular_line_min_rank_2025", "value": summary["latest_exact_regular_line_min_rank_2025"]},
        {"metric": "can_confirm_rank_fields", "value": summary["can_confirm_rank_fields"]},
        {"metric": "can_use_2025_admission_line_candidate", "value": summary["can_use_2025_admission_line_candidate"]},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    write_csv(ROLLUP, rollup_rows, ["metric", "value"])

    print(f"field_mapping_row_preview_rows={len(row_preview)}")
    print(f"plan_seed_rows_2025={summary['plan_seed_rows_2025']}")
    print(f"plan_ordinary_total_count_2025={summary['plan_ordinary_total_count_2025']}")
    print(f"overview_2024_physics_min_score={summary['overview_2024_physics_min_score']}")
    print(f"derived_ordinary_min_score_2024={summary['derived_ordinary_min_score_2024']}")
    print(f"derived_ordinary_min_rank_2024={summary['derived_ordinary_min_rank_2024']}")


if __name__ == "__main__":
    main()
