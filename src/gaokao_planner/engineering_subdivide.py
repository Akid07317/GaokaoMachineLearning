from __future__ import annotations

from pathlib import Path

import csv


def read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def classify_row(row: dict[str, str]) -> dict[str, str]:
    tier = row["engineering_tier"]
    ok_count = int(row["fetched_ok_count"])
    has_plan = row["has_plan_page"] == "true"
    has_score = row["has_score_page"] == "true"
    has_rule = row["has_rule_page"] == "true"

    if tier == "core" and has_plan and has_score and has_rule:
        segment = "A1_core_complete"
        action = "优先进入520阈值数值抽取"
    elif tier == "core" and ok_count >= 3 and sum([has_plan, has_score, has_rule]) >= 2:
        segment = "A2_core_near_complete"
        action = "补齐缺页后进入520阈值数值抽取"
    elif tier == "core" and ok_count >= 1:
        segment = "B1_core_partial"
        action = "保留，先补计划页或分数页"
    elif tier == "core":
        segment = "B2_core_missing"
        action = "重新定向补抓"
    elif has_plan and has_score and has_rule:
        segment = "C1_support_complete"
        action = "作为520阈值补充池进入数值抽取"
    elif ok_count >= 2:
        segment = "C2_support_partial"
        action = "保留，视时间补齐"
    else:
        segment = "C3_support_missing"
        action = "暂列观察"

    return {
        **row,
        "second_round_segment": segment,
        "next_action": action,
        "score_threshold_status": "pending_520_extraction",
    }


def write_rows(rows: list[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {output_path}")
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
