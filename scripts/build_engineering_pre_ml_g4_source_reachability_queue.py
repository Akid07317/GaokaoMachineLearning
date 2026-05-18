#!/usr/bin/env python3
"""Build a G4 official-source reachability queue from post-gap-fill gate status."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

GATE_STATUS = SEED_DIR / "guangxi_pre_ml_gate_status_post_gap_fill_merged.csv"
QUEUE_OUT = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_queue_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_g4_source_reachability_queue_coverage_rollup.csv"


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


def action_for(row: dict[str, str]) -> tuple[str, str]:
    lane = row.get("operating_lane", "")
    blocker = row.get("blocker_class", "")
    if lane == "P1_static_family_ready":
        return (
            "P1_static_family_extraction_preview",
            "从已缓存静态页或同家族脚本检查可抽取表格/API，不联网，不并入 canonical。",
        )
    if lane == "P1_js_endpoint_exposed":
        return (
            "P1_js_endpoint_shape_audit",
            "复核已暴露 JS/API endpoint 的参数和返回结构，先生成本地来源可达性预览。",
        )
    if lane == "P2_cached_entry_waiting_headers":
        return (
            "P2_cached_entry_header_route_audit",
            "基于缓存入口和已知 URL 记录 header/payload 路线；如需联网，单独人工批准。",
        )
    if blocker == "form_replay_blocked":
        return (
            "P3_form_replay_manual_review",
            "仅记录官方入口、表单字段和可替代缓存/PDF；不回放表单，不扩池。",
        )
    return (
        "P3_manual_official_source_review",
        "人工复核官方招生计划/历年分数入口是否可达，记录静态页、PDF、JS、缓存或 403 原因。",
    )


def main() -> None:
    _, rows = read_csv(GATE_STATUS)
    g4_rows = [row for row in rows if row.get("gate_status") == "G4_blocked_or_manual_route"]

    queue_rows: list[dict[str, object]] = []
    for index, row in enumerate(g4_rows, start=1):
        task_type, next_action = action_for(row)
        queue_rows.append(
            {
                "queue_rank": index,
                "school_key": row.get("school_key", ""),
                "school_name": row.get("school_name", ""),
                "engineering_tier": row.get("engineering_tier", ""),
                "gate_status": row.get("gate_status", ""),
                "readiness_band": row.get("readiness_band", ""),
                "operating_lane": row.get("operating_lane", ""),
                "source_reachability_task_type": task_type,
                "blocker_class": row.get("blocker_class", ""),
                "gap_signature": row.get("gap_signature", ""),
                "backfill_route": row.get("backfill_route", ""),
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "remaining_local_action": row.get("remaining_local_action", ""),
                "next_action": next_action,
                "deep_research_boundary": "optional_for_official_source_reachability_only_no_pool_expansion",
                "ml_boundary_note": "G4 reachability queue only; canonical/ML remain closed",
                "record_id": f"{row.get('school_key', '')}-g4-source-reachability-queue",
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_g4_source_reachability_queue",
            }
        )

    fields = [
        "queue_rank",
        "school_key",
        "school_name",
        "engineering_tier",
        "gate_status",
        "readiness_band",
        "operating_lane",
        "source_reachability_task_type",
        "blocker_class",
        "gap_signature",
        "backfill_route",
        "plan_source_url",
        "score_source_url",
        "remaining_local_action",
        "next_action",
        "deep_research_boundary",
        "ml_boundary_note",
        "record_id",
        "source_record_id",
        "source_slug",
    ]
    write_csv(QUEUE_OUT, queue_rows, fields)

    lane_counts = Counter(row["operating_lane"] for row in queue_rows)
    blocker_counts = Counter(row["blocker_class"] for row in queue_rows)
    task_counts = Counter(row["source_reachability_task_type"] for row in queue_rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "g4_source_reachability_queue_schools", "value": len(queue_rows)},
        {"metric": "ml_boundary_still_closed", "value": "true"},
        {"metric": "deep_research_boundary", "value": "official_source_reachability_only_no_pool_expansion"},
    ]
    rollup_rows.extend({"metric": f"operating_lane__{key}", "value": value} for key, value in sorted(lane_counts.items()))
    rollup_rows.extend({"metric": f"blocker_class__{key}", "value": value} for key, value in sorted(blocker_counts.items()))
    rollup_rows.extend({"metric": f"task_type__{key}", "value": value} for key, value in sorted(task_counts.items()))
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value"])

    print(f"g4_source_reachability_queue_schools={len(queue_rows)}")
    for key, value in sorted(lane_counts.items()):
        print(f"operating_lane__{key}={value}")


if __name__ == "__main__":
    main()
