#!/usr/bin/env python3
"""Build Nanhang D2/G2 reference-year and field-mapping preview.

This keeps 2025 plan rows, 2024 major scores, overview/rank-enriched rows, and
Guangxi admission-line candidates in separate review layers.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
OFFICIAL_API_DIR = ROOT / "clean_data" / "official_api_structured"
REPORT_DIR = ROOT / "reports"

STATUS_PREVIEW = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv"
QUEUE = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv"
PLAN_SEED = SEED_DIR / "guangxi_physics_plan_seed_merged.csv"
SCORE_SEED = SEED_DIR / "guangxi_physics_score_major_seed_merged.csv"
SCORE_SUMMARY_SEED = SEED_DIR / "guangxi_physics_score_summary_seed_merged.csv"
SCORE_OVERVIEW = OFFICIAL_API_DIR / "nanhang_guangxi_score_overview_rows.csv"
SCORE_MAJOR_OFFICIAL = OFFICIAL_API_DIR / "nanhang_guangxi_score_rows.csv"
PLAN_QUERY_ROWS = SEED_DIR / "nanhang_guangxi_plan_physics.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"

ROW_PREVIEW = SEED_DIR / "nanhang_reference_year_field_mapping_row_preview.csv"
MAPPING_SUMMARY = SEED_DIR / "nanhang_reference_year_field_mapping_preview.csv"
SCHOOL_SUMMARY = REPORT_DIR / "engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_school_summary.csv"
ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_coverage_rollup.csv"

SCHOOL_KEY = "nanhang_211"
SCHOOL_NAME = "南京航空航天大学"
SCHOOL_NAME_PUBLIC = "南京航空航天大学招生网"
PLAN_SOURCE_URL = (
    "https://zsservice.nuaa.edu.cn/zsw-admin/api/getEnrollmentPlan?"
    "sf=%E5%B9%BF%E8%A5%BF&year=2025&kl=%E7%89%A9%E7%90%86%E7%B1%BB&"
    "lx=%E6%99%AE%E9%80%9A%E7%B1%BB&page=1&limit=10000"
)
SCORE_SOURCE_URL = "https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScore"
OVERVIEW_SOURCE_URL = "https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScoreOverview"


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
    if group_code.startswith("3"):
        return "separate_unlabeled_group_candidate"
    return "ordinary_regular"


def rows_for() -> dict[str, list[dict[str, str]]]:
    _, plan_seed = read_csv(PLAN_SEED)
    _, score_seed = read_csv(SCORE_SEED)
    _, score_summary_seed = read_csv(SCORE_SUMMARY_SEED)
    _, score_overview = read_csv(SCORE_OVERVIEW)
    _, score_major_official = read_csv(SCORE_MAJOR_OFFICIAL)
    _, plan_query_rows = read_csv(PLAN_QUERY_ROWS)
    _, admission_lines = read_csv(ADMISSION_LINES)

    plan_rows = [
        row
        for row in plan_seed
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2025"
        and row.get("province") == "广西"
        and "物理" in row.get("subject_type", "")
    ]
    score_rows = [
        row
        for row in score_seed
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2024"
        and row.get("province") == "广西"
        and "物理" in row.get("science_category", "")
    ]
    score_summary = [
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
        if row.get("university_name") == SCHOOL_NAME
        and row.get("year") == "2025"
        and row.get("batch") == "本科普通批"
        and row.get("subject_type") == "物理类"
        and row.get("is_first_round") == "true"
        and row.get("data_quality") == "official"
    ]
    admission_2024 = [
        row
        for row in admission_lines
        if row.get("university_name") == SCHOOL_NAME
        and row.get("year") == "2024"
        and row.get("batch") == "本科普通批"
        and row.get("subject_type") == "物理类"
        and row.get("is_first_round") == "true"
        and row.get("data_quality") == "official"
    ]
    return {
        "plan_seed": plan_rows,
        "score_seed": score_rows,
        "score_summary": score_summary,
        "score_overview": [row for row in score_overview if row.get("school_key") == SCHOOL_KEY],
        "score_major_official": [row for row in score_major_official if row.get("school_key") == SCHOOL_KEY],
        "plan_query_rows": plan_query_rows,
        "admission_2025": admission_2025,
        "admission_2024": admission_2024,
    }


def build_row_preview(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    preview: list[dict[str, object]] = []

    for row in data["plan_seed"]:
        source_url = row.get("source_url", "").strip() or PLAN_SOURCE_URL
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME_PUBLIC,
                "row_layer": "official_api_plan_2025_seed",
                "source_year": row.get("year", ""),
                "source_scope": "official_api_structured_plan",
                "source_kind": "school_official_api",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "college": row.get("college", ""),
                "specialty_or_major": row.get("specialty", ""),
                "normalized_major_key": normalize_text(row.get("specialty", "")),
                "plan_count": row.get("plan_count", ""),
                "requirement": row.get("requirement", ""),
                "minimum_score": "",
                "lowest_score_ranking": "",
                "highest_score": "",
                "line_type": "ordinary_plan_row",
                "field_mapping_status": (
                    "plan_count_college_confirmed_source_url_backfilled"
                    if not row.get("source_url", "").strip()
                    else "plan_count_college_source_confirmed"
                ),
                "source_url": source_url,
                "notes": "2025 plan row from Nanhang official enrollment-plan API; group/selection fields are not exposed in seed.",
            }
        )

    for row in data["score_seed"]:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_api_major_score_2024",
                "source_year": row.get("year", ""),
                "source_scope": "official_api_major_score_no_rank",
                "source_kind": "school_official_api",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "college": "",
                "specialty_or_major": row.get("major", ""),
                "normalized_major_key": normalize_text(row.get("major", "")),
                "plan_count": "",
                "requirement": row.get("requirement", ""),
                "minimum_score": row.get("minimum_score", ""),
                "lowest_score_ranking": row.get("lowest_score_ranking", ""),
                "highest_score": row.get("highest_score", ""),
                "line_type": "major_score_reference",
                "field_mapping_status": "score_fields_confirmed_rank_missing_in_major_api",
                "source_url": row.get("source_url", SCORE_SOURCE_URL),
                "notes": "2024 major score from Nanhang official score API; rank is not exposed in major-score rows.",
            }
        )

    for row in data["score_overview"]:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "official_api_score_overview_2024",
                "source_year": row.get("year", ""),
                "source_scope": "official_api_score_overview_no_rank",
                "source_kind": "school_official_api",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "college": "",
                "specialty_or_major": "",
                "normalized_major_key": "",
                "plan_count": "",
                "requirement": row.get("subject_type", ""),
                "minimum_score": row.get("minimum_score", ""),
                "lowest_score_ranking": row.get("minimum_rank", ""),
                "highest_score": row.get("maximum_score", ""),
                "line_type": "score_overview_reference",
                "field_mapping_status": "overview_score_confirmed_rank_missing_in_overview_api",
                "source_url": row.get("source_url", OVERVIEW_SOURCE_URL),
                "notes": row.get("remarks", ""),
            }
        )

    for row in data["score_summary"]:
        preview.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "row_layer": "rank_enriched_score_summary_2024",
                "source_year": row.get("year", ""),
                "source_scope": "rank_enriched_from_official_overview",
                "source_kind": "derived_summary",
                "admission_type": row.get("type", ""),
                "group_code": "",
                "college": "",
                "specialty_or_major": "",
                "normalized_major_key": "",
                "plan_count": "",
                "requirement": row.get("subject_type", ""),
                "minimum_score": row.get("minimum_score", ""),
                "lowest_score_ranking": row.get("minimum_rank", ""),
                "highest_score": row.get("maximum_score", ""),
                "line_type": "derived_score_rank_reference",
                "field_mapping_status": "rank_derived_not_api_field",
                "source_url": row.get("source_url", OVERVIEW_SOURCE_URL),
                "notes": row.get("remarks", ""),
            }
        )

    for year_key in ("admission_2024", "admission_2025"):
        for row in data[year_key]:
            preview.append(
                {
                    "school_key": SCHOOL_KEY,
                    "school_name": SCHOOL_NAME,
                    "row_layer": f"gx_official_admission_line_candidate_{row.get('year', '')}",
                    "source_year": row.get("year", ""),
                    "source_scope": "admission_line_candidate",
                    "source_kind": "guangxi_official_admission_line",
                    "admission_type": row.get("remark", "") or "普通组",
                    "group_code": row.get("group_code", ""),
                    "college": "",
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
                    "notes": "Guangxi official admission line candidate; keep isolated unless human accepts it as line supplement.",
                }
            )

    return preview


def int_values(rows: list[dict[str, str]], field: str) -> list[int]:
    values = [to_int(row.get(field)) for row in rows]
    return [value for value in values if value is not None]


def min_int(rows: list[dict[str, str]], field: str) -> int | str:
    values = int_values(rows, field)
    return min(values) if values else ""


def max_int(rows: list[dict[str, str]], field: str) -> int | str:
    values = int_values(rows, field)
    return max(values) if values else ""


def sum_int(rows: list[dict[str, str]], field: str) -> int:
    return sum(int_values(rows, field))


def line_stats(rows: list[dict[str, str]], line_year: str) -> dict[str, object]:
    filtered = [row for row in rows if row.get("year") == line_year]
    ordinary = [row for row in filtered if line_type(row) == "ordinary_regular"]
    separate = [row for row in filtered if line_type(row) == "separate_unlabeled_group_candidate"]
    special = [row for row in filtered if line_type(row) not in {"ordinary_regular", "separate_unlabeled_group_candidate"}]
    return {
        "ordinary_count": len(ordinary),
        "ordinary_groups": "|".join(row.get("group_code", "") for row in ordinary),
        "ordinary_min_score": min_int(ordinary, "min_score"),
        "ordinary_min_rank": max_int(ordinary, "min_rank_est"),
        "separate_count": len(separate),
        "separate_groups": "|".join(row.get("group_code", "") for row in separate),
        "separate_min_score": min_int(separate, "min_score"),
        "separate_min_rank": max_int(separate, "min_rank_est"),
        "special_count": len(special),
        "special_groups": "|".join(row.get("group_code", "") for row in special),
    }


def build_summary(data: dict[str, list[dict[str, str]]]) -> dict[str, object]:
    overview_ordinary = next((row for row in data["score_overview"] if row.get("type") == "普通类"), {})
    summary_ordinary = next((row for row in data["score_summary"] if row.get("type") == "普通类"), {})
    summary_special = [row for row in data["score_summary"] if row.get("type") != "普通类"]
    lines_2025 = line_stats(data["admission_2025"], "2025")
    lines_2024 = line_stats(data["admission_2024"], "2024")

    source_url_missing_rows = sum(1 for row in data["plan_seed"] if not row.get("source_url", "").strip())
    return {
        "school_key": SCHOOL_KEY,
        "school_name": SCHOOL_NAME_PUBLIC,
        "mapping_status": "reference_year_field_mapping_preview_ready",
        "plan_year": "2025",
        "score_reference_year": "2024",
        "latest_admission_line_year": "2025",
        "plan_rows_2025": len(data["plan_seed"]),
        "plan_total_count_2025": sum_int(data["plan_seed"], "plan_count"),
        "plan_college_count_2025": len({row.get("college", "") for row in data["plan_seed"] if row.get("college", "")}),
        "plan_requirement_missing_rows_2025": sum(1 for row in data["plan_seed"] if not row.get("requirement", "").strip()),
        "plan_source_url_missing_rows_2025": source_url_missing_rows,
        "plan_source_url_backfill_used": "yes" if source_url_missing_rows else "no",
        "score_major_rows_2024": len(data["score_seed"]),
        "score_major_min_score_2024": min_int(data["score_seed"], "minimum_score"),
        "score_major_high_score_2024": max_int(data["score_seed"], "highest_score"),
        "score_rank_rows_in_major_api_2024": sum(1 for row in data["score_seed"] if row.get("lowest_score_ranking", "").strip()),
        "score_overview_rows_2024": len(data["score_overview"]),
        "overview_ordinary_min_score_2024": overview_ordinary.get("minimum_score", ""),
        "overview_ordinary_average_score_2024": overview_ordinary.get("average_score", ""),
        "overview_ordinary_high_score_2024": overview_ordinary.get("maximum_score", ""),
        "overview_vs_major_detail_delta": (
            (to_int(overview_ordinary.get("minimum_score")) or 0) - (min_int(data["score_seed"], "minimum_score") or 0)
            if overview_ordinary and data["score_seed"]
            else ""
        ),
        "rank_enriched_summary_rows_2024": len(data["score_summary"]),
        "rank_enriched_ordinary_min_score_2024": summary_ordinary.get("minimum_score", ""),
        "rank_enriched_ordinary_min_rank_2024": summary_ordinary.get("minimum_rank", ""),
        "rank_enriched_ordinary_high_score_2024": summary_ordinary.get("maximum_score", ""),
        "rank_enriched_special_min_score_2024": min_int(summary_special, "minimum_score"),
        "rank_enriched_special_min_rank_2024": max_int(summary_special, "minimum_rank"),
        "latest_regular_line_group_count_2025": lines_2025["ordinary_count"],
        "latest_regular_line_groups_2025": lines_2025["ordinary_groups"],
        "latest_regular_line_min_score_2025": lines_2025["ordinary_min_score"],
        "latest_regular_line_min_rank_2025": lines_2025["ordinary_min_rank"],
        "latest_separate_unlabeled_line_group_count_2025": lines_2025["separate_count"],
        "latest_separate_unlabeled_line_groups_2025": lines_2025["separate_groups"],
        "latest_separate_unlabeled_line_min_score_2025": lines_2025["separate_min_score"],
        "latest_separate_unlabeled_line_min_rank_2025": lines_2025["separate_min_rank"],
        "latest_special_line_count_2025": lines_2025["special_count"],
        "latest_special_line_groups_2025": lines_2025["special_groups"],
        "reference_regular_line_min_score_2024": lines_2024["ordinary_min_score"],
        "reference_regular_line_min_rank_2024": lines_2024["ordinary_min_rank"],
        "reference_separate_unlabeled_line_count_2024": lines_2024["separate_count"],
        "reference_special_line_count_2024": lines_2024["special_count"],
        "can_resolve_plan_linkage": "yes_count_ready_but_group_requirement_missing",
        "can_confirm_score_fields": "yes_major_and_overview_agree_2024",
        "can_confirm_rank_fields": "no_api_rank_derived_or_line_candidate_only",
        "can_replace_reference_year_with_2025_school_api_score": "no",
        "can_use_2025_admission_line_candidate": "requires_human_acceptance_and_group_303_scope_decision",
        "recommended_status": "keep_G2_caution_mapping_preview_ready_rank_derived_and_group_scope_caution",
        "plan_source_url": PLAN_SOURCE_URL,
        "score_source_url": SCORE_SOURCE_URL,
        "overview_source_url": OVERVIEW_SOURCE_URL,
        "admission_line_candidate_source_id": "gx_2025_admission_physics_main",
        "repair_note": (
            "2025 计划数和学院字段可确认，但选科/专业组字段缺失且 plan seed 行 source_url 为空，"
            "需使用 registry/API 查询 URL 作来源说明。2024 专业分数与概况最低分均为 618，"
            "但 API 不含 rank；3971 为一分一档派生，2025 投档线只作候选。"
        ),
        "ml_boundary_note": "reference-year field-mapping preview only; canonical/ML remain closed",
        "record_id": f"{SCHOOL_KEY}-reference-year-field-mapping-preview",
        "source_slug": "pre_ml_d2_g2_nanhang_reference_year_field_mapping",
    }


def patch_status_preview(status_rows: list[dict[str, str]], summary: dict[str, object]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in status_rows:
        patched: dict[str, object] = dict(row)
        if row.get("school_key") == SCHOOL_KEY:
            patched["fix_queue_status"] = "reference_year_field_mapping_preview_ready"
            patched["fix_priority"] = "P1_reference_year_and_field_mapping_preview_ready"
            patched["fix_class"] = (
                "2025_plan_count_confirmed|2024_api_major_and_overview_score_confirmed|"
                "rank_derived_not_api_field|2025_admission_line_candidate_isolated|plan_source_url_backfilled_from_registry"
            )
            patched["recommended_action"] = (
                "保留 2025 官方计划 API 与 2024 官方分数 API/概况接口作为当前复核口径；"
                "最低位次标记为一分一档派生，2025 投档线普通组 101 与 303 分组需人工判定是否接入。"
            )
            patched["fix_route"] = "local_field_mapping_preview_ready"
            patched["exit_condition"] = "can_reassess_g2_after_human_accepts_rank_derivation_and_line_candidate_boundary"
            patched["reference_year"] = summary["score_reference_year"]
            patched["latest_year"] = summary["plan_year"]
            patched["data_completeness"] = "latest_plan_with_2024_official_api_score_reference_rank_derived"
            patched["total_plan_count"] = summary["plan_total_count_2025"]
            patched["minimum_score"] = summary["rank_enriched_ordinary_min_score_2024"]
            patched["minimum_rank"] = summary["rank_enriched_ordinary_min_rank_2024"]
            patched["trend_available"] = "true"
            patched["trend_signal"] = "2025_plan_ready_2024_score_api_ready_rank_derived_2025_line_candidate_available"
            patched["gap_signature"] = (
                "reference_year_not_latest|rank_not_api_field|plan_group_mapping_missing|"
                "plan_seed_source_url_backfill_required|latest_group_303_scope_requires_acceptance"
            )
            patched["resolution_status"] = "mapping_preview_ready_with_rank_and_group_scope_caution"
            patched["plan_source_resolution"] = "official_api_structured"
            patched["score_source_resolution"] = "official_api_major_and_overview_structured"
            patched["structured_plan_rows"] = summary["plan_rows_2025"]
            patched["structured_score_major_rows"] = summary["score_major_rows_2024"]
            patched["structured_score_summary_rows"] = summary["score_overview_rows_2024"]
            patched["plan_source_url"] = summary["plan_source_url"]
            patched["score_source_url"] = summary["overview_source_url"]
            patched["required_row_fixes"] = (
                "rank_derivation_note_required|human_accept_or_reject_2025_admission_line_candidate|"
                "group_303_scope_decision|plan_seed_source_url_backfill_optional|professional_group_mapping_missing"
            )
            patched["residual_followups"] = "D2_request_row_fix_complete_next_G4_official_source_reachability"
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
        "admission_type",
        "group_code",
        "college",
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
        "plan_college_count_2025",
        "plan_requirement_missing_rows_2025",
        "plan_source_url_missing_rows_2025",
        "plan_source_url_backfill_used",
        "score_major_rows_2024",
        "score_major_min_score_2024",
        "score_major_high_score_2024",
        "score_rank_rows_in_major_api_2024",
        "score_overview_rows_2024",
        "overview_ordinary_min_score_2024",
        "overview_ordinary_average_score_2024",
        "overview_ordinary_high_score_2024",
        "overview_vs_major_detail_delta",
        "rank_enriched_summary_rows_2024",
        "rank_enriched_ordinary_min_score_2024",
        "rank_enriched_ordinary_min_rank_2024",
        "rank_enriched_ordinary_high_score_2024",
        "rank_enriched_special_min_score_2024",
        "rank_enriched_special_min_rank_2024",
        "latest_regular_line_group_count_2025",
        "latest_regular_line_groups_2025",
        "latest_regular_line_min_score_2025",
        "latest_regular_line_min_rank_2025",
        "latest_separate_unlabeled_line_group_count_2025",
        "latest_separate_unlabeled_line_groups_2025",
        "latest_separate_unlabeled_line_min_score_2025",
        "latest_separate_unlabeled_line_min_rank_2025",
        "latest_special_line_count_2025",
        "latest_special_line_groups_2025",
        "reference_regular_line_min_score_2024",
        "reference_regular_line_min_rank_2024",
        "reference_separate_unlabeled_line_count_2024",
        "reference_special_line_count_2024",
        "can_resolve_plan_linkage",
        "can_confirm_score_fields",
        "can_confirm_rank_fields",
        "can_replace_reference_year_with_2025_school_api_score",
        "can_use_2025_admission_line_candidate",
        "recommended_status",
        "plan_source_url",
        "score_source_url",
        "overview_source_url",
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
        {"metric": "nanhang_mapping_school_rows", "value": 1},
        {"metric": "field_mapping_row_preview_rows", "value": len(row_preview)},
        {"metric": "plan_rows_2025", "value": summary["plan_rows_2025"]},
        {"metric": "plan_total_count_2025", "value": summary["plan_total_count_2025"]},
        {"metric": "plan_source_url_missing_rows_2025", "value": summary["plan_source_url_missing_rows_2025"]},
        {"metric": "score_major_rows_2024", "value": summary["score_major_rows_2024"]},
        {"metric": "score_major_min_score_2024", "value": summary["score_major_min_score_2024"]},
        {"metric": "score_rank_rows_in_major_api_2024", "value": summary["score_rank_rows_in_major_api_2024"]},
        {"metric": "overview_ordinary_min_score_2024", "value": summary["overview_ordinary_min_score_2024"]},
        {"metric": "rank_enriched_ordinary_min_rank_2024", "value": summary["rank_enriched_ordinary_min_rank_2024"]},
        {"metric": "latest_regular_line_min_score_2025", "value": summary["latest_regular_line_min_score_2025"]},
        {"metric": "latest_regular_line_min_rank_2025", "value": summary["latest_regular_line_min_rank_2025"]},
        {"metric": "latest_separate_unlabeled_line_groups_2025", "value": summary["latest_separate_unlabeled_line_groups_2025"]},
        {"metric": "can_confirm_rank_fields", "value": summary["can_confirm_rank_fields"]},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    write_csv(ROLLUP, rollup_rows, ["metric", "value"])

    print(f"field_mapping_row_preview_rows={len(row_preview)}")
    print(f"plan_rows_2025={summary['plan_rows_2025']}")
    print(f"plan_total_count_2025={summary['plan_total_count_2025']}")
    print(f"score_major_rows_2024={summary['score_major_rows_2024']}")
    print(f"rank_enriched_ordinary_min_rank_2024={summary['rank_enriched_ordinary_min_rank_2024']}")
    print(f"latest_regular_line_min_rank_2025={summary['latest_regular_line_min_rank_2025']}")


if __name__ == "__main__":
    main()
