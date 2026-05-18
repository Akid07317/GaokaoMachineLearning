#!/usr/bin/env python3
"""Build BJUT D2/G2 latest plan-score alignment preview without touching baselines."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

STATUS_PREVIEW = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv"
QUEUE = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv"
PLAN_ROWS = ROOT / "clean_data" / "cached_pdf_structured" / "beijing_gongye_guangxi_plan_rows.csv"
SCORE_ROWS = ROOT / "clean_data" / "cached_pdf_structured" / "beijing_gongye_guangxi_score_rows.csv"
HISTORICAL_SUMMARY = ROOT / "clean_data" / "official_html_structured" / "beijing_gongye_guangxi_score_summary_rows.csv"

ALIGNMENT_ROWS = SEED_DIR / "beijing_gongye_latest_plan_score_alignment_row_preview.csv"
ALIGNMENT_SUMMARY = SEED_DIR / "beijing_gongye_latest_plan_score_alignment_preview.csv"
SCHOOL_SUMMARY = REPORT_DIR / "engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_school_summary.csv"
ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_coverage_rollup.csv"

SCHOOL_KEY = "beijing_gongye_211"
SCHOOL_NAME = "北京工业大学"
PLAN_SOURCE_URL = "http://admissions.bjut.edu.cn/dfiles/2025/2025gaigeshengfenjh.pdf"
SCORE_SOURCE_URL = "https://admissions.bjut.edu.cn/lnlqfs/1776.htm"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
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


def normalize_major(value: str) -> str:
    value = value.replace("（", "(").replace("）", ")")
    value = re.sub(r"\s+", "", value)
    return value


def build_alignment_rows(
    plan_rows: list[dict[str, str]], score_rows: list[dict[str, str]]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    current_plan = [
        row
        for row in plan_rows
        if row.get("school_key") == SCHOOL_KEY
        and row.get("plan_year") == "2025"
        and row.get("province") == "广西"
        and row.get("subject_type") == "物理"
    ]
    current_score = [
        row
        for row in score_rows
        if row.get("school_key") == SCHOOL_KEY
        and row.get("year") == "2025"
        and row.get("province") == "广西"
        and row.get("science_category") == "物理类"
    ]

    score_by_major: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in current_score:
        score_by_major[normalize_major(row.get("major", ""))].append(row)

    plan_by_major = {normalize_major(row.get("major_name", "")): row for row in current_plan}
    all_major_keys = sorted(set(plan_by_major) | set(score_by_major))

    alignment_rows: list[dict[str, object]] = []
    for major_key in all_major_keys:
        plan = plan_by_major.get(major_key, {})
        scores = score_by_major.get(major_key, [])
        min_scores = [to_int(row.get("minimum_score")) for row in scores]
        min_scores_int = [score for score in min_scores if score is not None]
        high_scores = [to_int(row.get("highest_score")) for row in scores]
        high_scores_int = [score for score in high_scores if score is not None]
        ranks = [row.get("lowest_score_ranking", "").strip() for row in scores if row.get("lowest_score_ranking", "").strip()]

        alignment_rows.append(
            {
                "school_key": SCHOOL_KEY,
                "school_name": SCHOOL_NAME,
                "major_key": major_key,
                "plan_major_name": plan.get("major_name", ""),
                "score_major_name": "|".join(row.get("major", "") for row in scores),
                "has_2025_plan_row": str(bool(plan)).lower(),
                "has_2025_score_row": str(bool(scores)).lower(),
                "plan_count_numeric": plan.get("plan_count_numeric", ""),
                "score_row_count": len(scores),
                "minimum_score_min": min(min_scores_int) if min_scores_int else "",
                "minimum_score_values": "|".join(str(score) for score in min_scores_int),
                "highest_score_max": max(high_scores_int) if high_scores_int else "",
                "lowest_score_ranking_values": "|".join(ranks),
                "ranking_available": str(bool(ranks)).lower(),
                "alignment_status": "plan_and_score_match" if plan and scores else "plan_only" if plan else "score_only",
                "plan_source_url": PLAN_SOURCE_URL if plan else "",
                "score_source_url": SCORE_SOURCE_URL if scores else "",
                "notes": "2025 score rows do not expose lowest rank; keep 2024 rank as best comparable reference.",
            }
        )

    total_plan_count = sum(to_int(row.get("plan_count_numeric")) or 0 for row in current_plan)
    all_min_scores = [to_int(row.get("minimum_score")) for row in current_score]
    all_min_scores = [score for score in all_min_scores if score is not None]
    all_ranks = [row.get("lowest_score_ranking", "").strip() for row in current_score if row.get("lowest_score_ranking", "").strip()]
    plan_match_count = sum(1 for row in alignment_rows if row["alignment_status"] == "plan_and_score_match")
    plan_only_count = sum(1 for row in alignment_rows if row["alignment_status"] == "plan_only")
    score_only_count = sum(1 for row in alignment_rows if row["alignment_status"] == "score_only")

    summary = {
        "school_key": SCHOOL_KEY,
        "school_name": SCHOOL_NAME,
        "alignment_status": "latest_plan_score_alignment_preview_ready",
        "plan_year": "2025",
        "score_year": "2025",
        "plan_rows_2025": len(current_plan),
        "plan_total_count_2025": total_plan_count,
        "score_rows_2025": len(current_score),
        "score_unique_majors_2025": len(score_by_major),
        "plan_score_matched_majors": plan_match_count,
        "plan_only_majors": plan_only_count,
        "score_only_majors": score_only_count,
        "minimum_score_2025": min(all_min_scores) if all_min_scores else "",
        "minimum_rank_2025": "",
        "rank_available_2025": str(bool(all_ranks)).lower(),
        "best_comparable_rank_year": "2024",
        "best_comparable_rank": "8700",
        "can_replace_2024_score": "yes_with_caution",
        "can_replace_2024_rank": "no",
        "recommended_status": "keep_G2_caution_latest_score_and_plan_ready_rank_still_2024_comparable",
        "plan_source_url": PLAN_SOURCE_URL,
        "score_source_url": SCORE_SOURCE_URL,
        "repair_note": "2025 计划侧可本地补齐；2025 分数侧可给最新最低分，但无最低位次，不能替代 2024 带位次可比记录。",
        "ml_boundary_note": "alignment preview only; canonical/ML remain closed",
        "record_id": f"{SCHOOL_KEY}-latest-plan-score-alignment-preview",
        "source_slug": "pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment",
    }
    return alignment_rows, summary


def patch_status_preview(status_rows: list[dict[str, str]], summary: dict[str, object]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in status_rows:
        patched: dict[str, object] = dict(row)
        if row.get("school_key") == SCHOOL_KEY:
            patched["fix_queue_status"] = "latest_plan_score_alignment_preview_ready"
            patched["fix_priority"] = "P1_latest_plan_score_alignment_preview_ready"
            patched["fix_class"] = "2025_plan_structured_ready|2025_score_structured_no_rank|2024_rank_remains_best_comparable"
            patched["recommended_action"] = (
                "采用 2025 官方计划 PDF 结构化计划数和 2025 官方分数页最低分；最低位次仍引用 2024 best comparable，"
                "进入复核闸门必须保留 no_2025_rank caution。"
            )
            patched["fix_route"] = "local_plan_score_alignment_ready_rank_still_comparable"
            patched["exit_condition"] = "can_reassess_g2_with_no_2025_rank_caution"
            patched["reference_year"] = "2025"
            patched["latest_year"] = "2025"
            patched["data_completeness"] = "plan_and_score_no_rank"
            patched["total_plan_count"] = summary["plan_total_count_2025"]
            patched["minimum_score"] = summary["minimum_score_2025"]
            patched["minimum_rank"] = ""
            patched["trend_available"] = "true"
            patched["trend_signal"] = "score_latest_rank_comparable_only"
            patched["gap_signature"] = "missing_2025_rank|comparable_rank_note_required"
            patched["resolution_status"] = "mixed_ready_with_rank_caution"
            patched["structured_plan_rows"] = summary["plan_rows_2025"]
            patched["structured_score_major_rows"] = summary["score_rows_2025"]
            patched["structured_score_summary_rows"] = "0"
            patched["plan_source_url"] = summary["plan_source_url"]
            patched["score_source_url"] = summary["score_source_url"]
            patched["required_row_fixes"] = "no_2025_rank_caution_required|optional_rank_inference_or_official_rank_source"
            patched["ml_boundary_note"] = "latest plan-score alignment preview only; canonical/ML remain closed"
            patched["record_id"] = f"{SCHOOL_KEY}-d2-g2-request-row-fix-status-preview"
            patched["source_slug"] = "pre_ml_d2_g2_request_row_fix_status_preview"
        output.append(patched)
    return output


def main() -> None:
    status_fields, status_rows = read_csv(STATUS_PREVIEW if STATUS_PREVIEW.exists() else QUEUE)
    _, plan_rows = read_csv(PLAN_ROWS)
    _, score_rows = read_csv(SCORE_ROWS)
    _, historical_rows = read_csv(HISTORICAL_SUMMARY)

    alignment_rows, summary = build_alignment_rows(plan_rows, score_rows)
    summary["historical_rank_rows_2022_2024"] = len(historical_rows)
    patched_status = patch_status_preview(status_rows, summary)

    alignment_fields = [
        "school_key",
        "school_name",
        "major_key",
        "plan_major_name",
        "score_major_name",
        "has_2025_plan_row",
        "has_2025_score_row",
        "plan_count_numeric",
        "score_row_count",
        "minimum_score_min",
        "minimum_score_values",
        "highest_score_max",
        "lowest_score_ranking_values",
        "ranking_available",
        "alignment_status",
        "plan_source_url",
        "score_source_url",
        "notes",
    ]
    write_csv(ALIGNMENT_ROWS, alignment_rows, alignment_fields)

    summary_fields = [
        "school_key",
        "school_name",
        "alignment_status",
        "plan_year",
        "score_year",
        "plan_rows_2025",
        "plan_total_count_2025",
        "score_rows_2025",
        "score_unique_majors_2025",
        "plan_score_matched_majors",
        "plan_only_majors",
        "score_only_majors",
        "minimum_score_2025",
        "minimum_rank_2025",
        "rank_available_2025",
        "best_comparable_rank_year",
        "best_comparable_rank",
        "can_replace_2024_score",
        "can_replace_2024_rank",
        "recommended_status",
        "plan_source_url",
        "score_source_url",
        "repair_note",
        "ml_boundary_note",
        "historical_rank_rows_2022_2024",
        "record_id",
        "source_slug",
    ]
    write_csv(ALIGNMENT_SUMMARY, [summary], summary_fields)
    write_csv(SCHOOL_SUMMARY, [summary], summary_fields)
    write_csv(STATUS_PREVIEW, patched_status, status_fields)

    rollup_rows = [
        {"metric": "beijing_gongye_alignment_school_rows", "value": 1},
        {"metric": "alignment_row_preview_rows", "value": len(alignment_rows)},
        {"metric": "plan_rows_2025", "value": summary["plan_rows_2025"]},
        {"metric": "plan_total_count_2025", "value": summary["plan_total_count_2025"]},
        {"metric": "score_rows_2025", "value": summary["score_rows_2025"]},
        {"metric": "score_unique_majors_2025", "value": summary["score_unique_majors_2025"]},
        {"metric": "plan_score_matched_majors", "value": summary["plan_score_matched_majors"]},
        {"metric": "plan_only_majors", "value": summary["plan_only_majors"]},
        {"metric": "score_only_majors", "value": summary["score_only_majors"]},
        {"metric": "minimum_score_2025", "value": summary["minimum_score_2025"]},
        {"metric": "rank_available_2025", "value": summary["rank_available_2025"]},
        {"metric": "can_replace_2024_score", "value": summary["can_replace_2024_score"]},
        {"metric": "can_replace_2024_rank", "value": summary["can_replace_2024_rank"]},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    write_csv(ROLLUP, rollup_rows, ["metric", "value"])

    print(f"alignment_row_preview_rows={len(alignment_rows)}")
    print(f"plan_rows_2025={summary['plan_rows_2025']}")
    print(f"score_rows_2025={summary['score_rows_2025']}")
    print(f"can_replace_2024_rank={summary['can_replace_2024_rank']}")


if __name__ == "__main__":
    main()
