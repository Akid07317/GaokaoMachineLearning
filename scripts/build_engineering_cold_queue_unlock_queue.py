from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "engineering_tier",
    "pipeline_status",
    "block_type",
    "unlock_priority",
    "unlock_route",
    "plan_entry_url",
    "score_entry_url",
    "score_alt_url",
    "cached_plan_evidence_path",
    "cached_score_evidence_path",
    "cached_support_evidence_path",
    "extracted_api_hint",
    "recommended_next_action",
    "manual_probe_target",
    "queue_notes",
    "record_id",
    "source_slug",
]


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a cold-queue unlock work queue for blocked engineering schools."
    )
    parser.add_argument(
        "--entry-registry",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_cold_queue_entry_registry_merged.csv",
        help="Cold-queue official entry registry CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_cold_queue_unlock_queue_merged.csv",
        help="Output merged unlock queue CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_cold_queue_unlock_queue_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_cold_queue_unlock_queue_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def derive_unlock_fields(row: dict[str, str]) -> tuple[str, str, str, str]:
    school_key = normalize_text(row.get("school_key", ""))
    block_type = normalize_text(row.get("block_type", ""))
    api_hint = normalize_text(row.get("extracted_api_hint", ""))
    if school_key == "jiangnan_211" and api_hint:
        return (
            "P1_js_endpoint_exposed",
            "cached_js_endpoint",
            "优先用缓存JS暴露出的官方端点补参数字典，再做短超时单接口验证",
            "front_recruitmentPlan_and_recruitmentResult",
        )
    if block_type == "ajax_family_page_only":
        return (
            "P1_static_family_ready",
            "static_entry_with_family_params",
            "优先基于同家族静态入口页与现有cookie/Referer经验做短超时单学校验证",
            "plan_entry_then_score_entry",
        )
    if block_type == "ajax_blocked_403":
        return (
            "P2_cached_entry_waiting_headers",
            "cached_entry_then_header_replay",
            "先保留官方入口与缓存证据，等待更像浏览器的头部或人工登录态，不再长时间硬探测",
            "plan_entry_and_score_entry",
        )
    return (
        "P3_manual_review",
        "manual_source_review",
        "保留现有官方入口，后续人工确认参数或改走页面摘要/PDF路线",
        "cached_support_evidence",
    )


def main() -> None:
    args = build_parser().parse_args()
    entry_rows = read_rows(args.entry_registry)

    merged_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    priority_counts: dict[str, int] = {}

    for row in entry_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        unlock_priority, unlock_route, next_action, probe_target = derive_unlock_fields(row)
        priority_counts[unlock_priority] = priority_counts.get(unlock_priority, 0) + 1
        merged_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", "")),
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "block_type": normalize_text(row.get("block_type", "")),
                "unlock_priority": unlock_priority,
                "unlock_route": unlock_route,
                "plan_entry_url": normalize_text(row.get("plan_entry_url", "")),
                "score_entry_url": normalize_text(row.get("score_entry_url", "")),
                "score_alt_url": normalize_text(row.get("score_alt_url", "")),
                "cached_plan_evidence_path": normalize_text(row.get("cached_plan_evidence_path", "")),
                "cached_score_evidence_path": normalize_text(row.get("cached_score_evidence_path", "")),
                "cached_support_evidence_path": normalize_text(row.get("cached_support_evidence_path", "")),
                "extracted_api_hint": normalize_text(row.get("extracted_api_hint", "")),
                "recommended_next_action": next_action,
                "manual_probe_target": probe_target,
                "queue_notes": "冷队列解锁工单：不要求本轮直接拿到广西行，而是把官方入口、阻塞类型和下一步短链路动作固定下来，供后续低风险补抓使用",
                "record_id": f"{school_key}-cold-queue-unlock-queue",
                "source_slug": "official_cold_queue_unlock_queue",
            }
        )
        school_summary_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", "")),
                "cold_queue_unlock_rows": "1",
            }
        )

    merged_rows.sort(key=lambda item: (item["unlock_priority"], item["engineering_tier"], item["school_key"]))
    school_summary_rows.sort(key=lambda item: item["school_key"])

    write_rows(args.output, merged_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "cold_queue_unlock_rows"],
    )
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "cold_queue_unlock_schools", "value": str(len(merged_rows))},
        {"metric": "cold_queue_unlock_coverage_ratio", "value": f"{len(merged_rows) / TARGET_TOTAL:.4f}"},
    ]
    for priority, count in sorted(priority_counts.items()):
        coverage_rows.append({"metric": f"{priority}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote cold-queue unlock queue for {len(merged_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
