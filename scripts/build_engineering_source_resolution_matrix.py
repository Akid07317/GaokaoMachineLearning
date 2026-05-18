from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
    "school_key",
    "school_name",
    "engineering_tier",
    "pipeline_status",
    "plan_source_url",
    "plan_source_origin",
    "plan_source_resolution",
    "score_source_url",
    "score_source_origin",
    "score_source_resolution",
    "structured_plan_rows",
    "structured_score_major_rows",
    "structured_score_summary_rows",
    "resolution_status",
    "recommended_followup",
    "notes",
]

TARGET_TOTAL = 32


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return str(value or "").strip()


def parse_int(value: str) -> int:
    text = normalize_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def plan_resolution(url: str, origin: str, structured_plan_rows: int) -> str:
    if structured_plan_rows > 0:
        if url.endswith(".pdf"):
            return "official_pdf_structured"
        if "/api/" in url or "getEnrollmentPlan" in url or "getList" in url:
            return "official_api_structured"
        return "official_page_structured"
    if origin == "cold_queue_entry_registry":
        return "cold_queue_entry_only"
    if origin == "fallback_registry":
        return "fallback_plan_entry"
    if url.endswith(".pdf"):
        return "official_pdf_entry"
    if url:
        return "official_page_entry"
    return "missing"


def score_resolution(url: str, origin: str, score_major_rows: int, score_summary_rows: int) -> str:
    if score_major_rows > 0:
        if "/api/" in url or "getAdmissionScore" in url or "getList" in url:
            return "official_api_major_structured"
        return "official_page_major_structured"
    if score_summary_rows > 0:
        if url.endswith(".pdf"):
            return "official_pdf_summary"
        if "info/" in url or "view.aspx" in url or "html" in url:
            return "official_page_summary"
        return "official_summary_structured"
    if origin == "cold_queue_entry_registry":
        return "cold_queue_score_entry_only"
    if origin == "fallback_registry":
        return "fallback_score_entry"
    if url:
        return "official_score_entry_only"
    return "missing"


def resolution_status(plan_res: str, score_res: str) -> str:
    strong_plan = "structured" in plan_res
    strong_score = "structured" in score_res
    weak_plan = plan_res not in {"missing", "cold_queue_entry_only", "fallback_plan_entry", "official_page_entry"}
    weak_score = score_res not in {"missing", "cold_queue_score_entry_only", "fallback_score_entry", "official_score_entry_only"}
    if strong_plan and strong_score:
        return "exact_ready"
    if (strong_plan and weak_score) or (strong_score and weak_plan):
        return "mixed_ready"
    if plan_res != "missing" and score_res != "missing":
        return "fallback_ready"
    return "incomplete"


def recommended_followup(status: str) -> str:
    if status == "exact_ready":
        return "保持现状，优先用于复核和后续模型前审查"
    if status == "mixed_ready":
        return "补薄弱侧来源精度，优先把 entry/summary 提升到结构化明细"
    if status == "fallback_ready":
        return "沿现有入口继续取数，先把入口页推进到可抽结构化数据"
    return "继续补齐缺失来源"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build 32-school official source resolution matrix.")
    parser.add_argument(
        "--source-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_official_source_pack_merged.csv",
        help="Official source pack CSV.",
    )
    parser.add_argument(
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Pipeline status CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_source_resolution_matrix_merged.csv",
        help="Output resolution matrix CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_source_resolution_matrix_school_summary.csv",
        help="School summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_source_resolution_matrix_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    source_rows = read_rows(args.source_pack)
    pipeline_rows = {
        normalize_text(row.get("school_key", "")): row for row in read_rows(args.pipeline_status)
    }

    merged_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    exact_ready = 0
    mixed_ready = 0
    fallback_ready = 0

    for row in source_rows:
        key = normalize_text(row.get("school_key", ""))
        pipe = pipeline_rows.get(key, {})
        plan_rows = parse_int(pipe.get("plan_rows", "0"))
        score_major_rows = parse_int(pipe.get("score_major_rows", "0"))
        score_summary_rows = parse_int(pipe.get("score_summary_rows", "0"))
        plan_url = normalize_text(row.get("plan_source_url", ""))
        score_url = normalize_text(row.get("score_source_url", ""))
        plan_origin = normalize_text(row.get("plan_source_origin", ""))
        score_origin = normalize_text(row.get("score_source_origin", ""))
        plan_res = plan_resolution(plan_url, plan_origin, plan_rows)
        score_res = score_resolution(score_url, score_origin, score_major_rows, score_summary_rows)
        status = resolution_status(plan_res, score_res)
        if status == "exact_ready":
            exact_ready += 1
        elif status == "mixed_ready":
            mixed_ready += 1
        elif status == "fallback_ready":
            fallback_ready += 1

        merged_rows.append(
            {
                "school_key": key,
                "school_name": normalize_text(row.get("school_name", "")),
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "plan_source_url": plan_url,
                "plan_source_origin": plan_origin,
                "plan_source_resolution": plan_res,
                "score_source_url": score_url,
                "score_source_origin": score_origin,
                "score_source_resolution": score_res,
                "structured_plan_rows": str(plan_rows),
                "structured_score_major_rows": str(score_major_rows),
                "structured_score_summary_rows": str(score_summary_rows),
                "resolution_status": status,
                "recommended_followup": recommended_followup(status),
                "notes": "统一按来源类型+结构化行数判断 32 校计划/分数来源精度，服务后续高性价比补数。",
            }
        )
        school_summary_rows.append(
            {
                "school_key": key,
                "school_name": normalize_text(row.get("school_name", "")),
                "source_resolution_matrix_rows": "1",
                "resolution_status": status,
            }
        )

    write_rows(args.output, merged_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "source_resolution_matrix_rows", "resolution_status"],
    )
    write_rows(
        args.coverage_output,
        [
            {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
            {"metric": "source_resolution_matrix_schools", "value": str(len(merged_rows))},
            {"metric": "source_resolution_matrix_coverage_ratio", "value": f"{len(merged_rows) / TARGET_TOTAL:.4f}"},
            {"metric": "source_resolution_exact_ready_schools", "value": str(exact_ready)},
            {"metric": "source_resolution_mixed_ready_schools", "value": str(mixed_ready)},
            {"metric": "source_resolution_fallback_ready_schools", "value": str(fallback_ready)},
        ],
        ["metric", "value"],
    )
    print(
        "Wrote source resolution matrix for "
        f"{len(merged_rows)} schools ({exact_ready} exact, {mixed_ready} mixed, {fallback_ready} fallback)."
    )


if __name__ == "__main__":
    main()
