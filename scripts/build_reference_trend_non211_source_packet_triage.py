#!/usr/bin/env python3
"""Triage non-211 discovery candidates into reference-trend source packets.

This is source-packet planning only. It does not fetch pages, write canonical
data, run ML, or add schools to the 32-school decision pool.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
DOCS_DIR = ROOT / "docs"

NON211_TODO = REPORT_DIR / "non211_authoritative_todo.csv"
NON211_DISCOVERY = REPORT_DIR / "non211_authoritative_discovery_candidates_priority.csv"

TRIAGE_OUT = SEED_DIR / "reference_trend_non211_source_packet_triage_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_non211_source_packet_triage_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_non211_source_packet_triage.md"

FIELDS = [
    "triage_rank",
    "school_key",
    "school_name",
    "priority_tier",
    "engineering_fit",
    "todo_status",
    "candidate_url",
    "candidate_domain",
    "candidate_title",
    "candidate_kind",
    "source_packet_priority",
    "reference_trend_use_case",
    "requires_network",
    "requires_manual_approval",
    "can_enter_intake_without_fetch",
    "next_action",
    "decision_pool_boundary",
    "canonical_ml_entry_open",
    "record_id",
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


def classify_candidate(row: dict[str, str]) -> tuple[str, str, str]:
    text = " ".join(
        [
            row.get("link_text", ""),
            row.get("source_page_title", ""),
            row.get("matched_reason", ""),
            row.get("notes", ""),
        ]
    )
    if any(token in text for token in ["历年分数", "录取分数", "分数线", "投档", "录取情况"]):
        return (
            "score_or_admission_line_candidate",
            "P0_score_rank_or_line_source_packet",
            "trend_score_rank_or_line_reference",
        )
    if any(token in text for token in ["招生计划", "分省计划", "专业计划"]):
        return (
            "plan_candidate",
            "P1_plan_count_source_packet",
            "plan_count_or_group_structure_thickening",
        )
    if any(token in text for token in ["招生章程", "章程"]):
        return (
            "admissions_regulation_candidate",
            "P3_rule_context_source_packet",
            "admission_rules_context_only",
        )
    if any(token in text for token in ["本科招生网", "招生网", "招生信息网"]):
        return (
            "official_portal_candidate",
            "P2_portal_discovery_for_plan_score_sources",
            "source_discovery_entry",
        )
    return ("low_relevance_or_noise_candidate", "P4_triage_later", "not_ready_for_intake")


def build_rows() -> list[dict[str, object]]:
    todo_by_key = {row.get("school_key", ""): row for row in read_csv(NON211_TODO)}
    discovery_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(NON211_DISCOVERY):
        discovery_by_key[row.get("seed_id", "")].append(row)

    output: list[dict[str, object]] = []
    for school_key, todo in todo_by_key.items():
        candidates = discovery_by_key.get(school_key, [])
        if not candidates:
            candidates = [
                {
                    "seed_id": school_key,
                    "source_name": todo.get("school_name", ""),
                    "target_url": todo.get("authoritative_url", ""),
                    "target_domain": todo.get("authoritative_url", "").split("/")[2]
                    if "://" in todo.get("authoritative_url", "")
                    else "",
                    "link_text": todo.get("authoritative_source", ""),
                    "source_page_title": todo.get("authoritative_source", ""),
                    "matched_reason": todo.get("selection_basis", ""),
                    "notes": todo.get("notes", ""),
                }
            ]
        for row in candidates[:12]:
            kind, priority, use_case = classify_candidate(row)
            if priority == "P4_triage_later" and len(output) > 120:
                continue
            output.append(
                {
                    "triage_rank": len(output) + 1,
                    "school_key": school_key,
                    "school_name": todo.get("school_name") or row.get("source_name", ""),
                    "priority_tier": todo.get("priority_tier", ""),
                    "engineering_fit": todo.get("engineering_fit", ""),
                    "todo_status": todo.get("todo_status", ""),
                    "candidate_url": row.get("target_url", ""),
                    "candidate_domain": row.get("target_domain", ""),
                    "candidate_title": row.get("link_text") or row.get("source_page_title", ""),
                    "candidate_kind": kind,
                    "source_packet_priority": priority,
                    "reference_trend_use_case": use_case,
                    "requires_network": "true",
                    "requires_manual_approval": "false",
                    "can_enter_intake_without_fetch": "false",
                    "next_action": "fetch_or_open_official_page_then_write_source_packet",
                    "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                    "canonical_ml_entry_open": "false",
                    "record_id": f"reference_trend_non211_source_packet_triage_{len(output) + 1:04d}",
                }
            )
    return output


def write_doc(rows: list[dict[str, object]]) -> None:
    counts = Counter(row.get("source_packet_priority", "") for row in rows)
    schools = {row.get("school_key", "") for row in rows if row.get("school_key")}
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend Non-211 Source Packet Triage",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "非 211 官方发现池已整理为 source packet triage preview。该文件只服务资料搜集线程，不进入 32 所 decision_pool，不写 canonical/ML。",
                "",
                "## 覆盖",
                "",
                f"- schools covered: {len(schools)}",
                f"- triage rows: {len(rows)}",
                f"- P0 score/line candidates: {counts.get('P0_score_rank_or_line_source_packet', 0)}",
                f"- P1 plan candidates: {counts.get('P1_plan_count_source_packet', 0)}",
                f"- P2 portal candidates: {counts.get('P2_portal_discovery_for_plan_score_sources', 0)}",
                f"- P3 regulation candidates: {counts.get('P3_rule_context_source_packet', 0)}",
                "",
                "## 下一步",
                "",
                "优先联网打开 P0/P1 候选页，只有页面能确认广西、物理类、本科普通批、院校专业组/计划/分数/位次字段时，才写正式 source packet。仍不得跳过 intake preview 和 QA。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(TRIAGE_OUT, rows, FIELDS)
    counts = Counter(row.get("source_packet_priority", "") for row in rows)
    rollup = [
        {"metric": "non211_triage_rows", "value": len(rows)},
        {"metric": "non211_triage_school_count", "value": len({row.get("school_key", "") for row in rows})},
        {"metric": "P0_score_rank_or_line_source_packet", "value": counts.get("P0_score_rank_or_line_source_packet", 0)},
        {"metric": "P1_plan_count_source_packet", "value": counts.get("P1_plan_count_source_packet", 0)},
        {"metric": "P2_portal_discovery_for_plan_score_sources", "value": counts.get("P2_portal_discovery_for_plan_score_sources", 0)},
        {"metric": "P3_rule_context_source_packet", "value": counts.get("P3_rule_context_source_packet", 0)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"non211_triage_rows={len(rows)}")


if __name__ == "__main__":
    main()
