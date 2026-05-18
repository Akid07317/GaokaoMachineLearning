#!/usr/bin/env python3
"""Build marker 128 batch17 official-candidate gap queue.

This derives the next safe discovery queue from marker 127 coverage rows that
still lack any official source candidate. It only writes source-packet planning,
QA, rollup, and exclusion artifacts; it does not search, fetch, cache, parse,
OCR, replay browser/form state, or open intake/canonical/ML.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

COVERAGE = SEED / "reference_trend_520_p1_batch17_coverage_rollup.csv"
EXECUTION = SEED / "reference_trend_520_p1_batch17_discovery_execution_packet.csv"

PREFIX = "reference_trend_520_p1_batch17_official_candidate_gap_queue"
OUT = SEED / f"{PREFIX}.csv"
ROLLUP = REPORTS / f"{PREFIX}_rollup.csv"
QA = REPORTS / f"{PREFIX}_qa.csv"
EXCLUSION = REPORTS / f"{PREFIX}_exclusion_log.csv"
DOC = DOCS / f"{PREFIX}.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "gap_id",
    "coverage_id",
    "workset_id",
    "queue_rank",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "trend_direction",
    "rank_delta_2025_minus_2024",
    "special_type_boundary",
    "execution_packet_id",
    "execution_lane",
    "lane_priority",
    "allowed_discovery_mode",
    "primary_search_query",
    "secondary_search_query",
    "site_search_query",
    "search_query_bundle",
    "desired_source_fields",
    "must_not_accept",
    "stop_condition",
    "manual_approval_trigger",
    "requires_network",
    "requires_browser_or_alternate_fetch",
    "requires_manual_approval_now",
    "gap_status",
    "required_next_artifact",
    "recommended_next_action",
    "source_packet_preview_eligible",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_handoff_once(marker: str, content: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in existing:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def execution_by_group_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        for key in row["group_pair_keys"].split("|"):
            index[key] = row
    return index


def build_gap_rows() -> list[dict[str, object]]:
    coverage_rows = read_csv(COVERAGE)
    execution_index = execution_by_group_key(read_csv(EXECUTION))
    gap_sources = [
        row for row in coverage_rows
        if row["coverage_stage"] == "workset_only_no_official_candidate"
    ]
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(gap_sources, 1):
        execution = execution_index.get(row["group_pair_key"], {})
        rows.append(
            {
                "gap_id": f"reference_trend_520_p1_batch17_gap_{idx:04d}",
                "coverage_id": row["coverage_id"],
                "workset_id": row["workset_id"],
                "queue_rank": row["queue_rank"],
                "group_pair_key": row["group_pair_key"],
                "university_code": row["university_code"],
                "university_name": row["university_name"],
                "group_code": row["group_code"],
                "trend_direction": row["trend_direction"],
                "rank_delta_2025_minus_2024": row["rank_delta_2025_minus_2024"],
                "special_type_boundary": row["special_type_boundary"],
                "execution_packet_id": execution.get("packet_id", ""),
                "execution_lane": execution.get("execution_lane", ""),
                "lane_priority": execution.get("lane_priority", ""),
                "allowed_discovery_mode": execution.get("allowed_discovery_mode", ""),
                "primary_search_query": execution.get("primary_search_query", ""),
                "secondary_search_query": execution.get("secondary_search_query", ""),
                "site_search_query": execution.get("site_search_query", ""),
                "search_query_bundle": execution.get("search_query_bundle", ""),
                "desired_source_fields": execution.get("desired_source_fields", ""),
                "must_not_accept": execution.get("must_not_accept", ""),
                "stop_condition": execution.get("stop_condition", ""),
                "manual_approval_trigger": execution.get("manual_approval_trigger", ""),
                "requires_network": "true",
                "requires_browser_or_alternate_fetch": "false_until_static_official_discovery_is_blocked",
                "requires_manual_approval_now": "false",
                "gap_status": "needs_official_source_candidate_discovery",
                "required_next_artifact": "official_candidate_preview_or_reachability_backoff",
                "recommended_next_action": execution.get("next_action", ""),
                "source_packet_preview_eligible": "false_until_official_candidate_found_and_QA_ready",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Derived from marker 127 workset-only rows and marker 120 execution constraints; no source found or claimed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    lane_counts = Counter(str(row["execution_lane"]) for row in rows)
    boundary_counts = Counter(str(row["special_type_boundary"]) for row in rows)
    direction_counts = Counter(str(row["trend_direction"]) for row in rows)
    rollup_rows = [
        {"metric": "gap_queue_rows", "value": len(rows), "note": "Rows still lacking official candidate after marker 127."},
        {"metric": "requires_network_rows", "value": sum(row["requires_network"] == "true" for row in rows), "note": "Future search only; no network executed in this build."},
        {"metric": "requires_browser_or_alternate_fetch_now_rows", "value": 0, "note": "All rows stop before browser/cookie/header/form state."},
        {"metric": "source_packet_preview_eligible_rows", "value": 0, "note": "No official candidate has been found yet."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Intake remains closed."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No official rank/plan join."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for lane, count in sorted(lane_counts.items()):
        rollup_rows.append({"metric": f"execution_lane::{lane}", "value": count, "note": ""})
    for boundary, count in sorted(boundary_counts.items()):
        rollup_rows.append({"metric": f"boundary::{boundary}", "value": count, "note": ""})
    for direction, count in sorted(direction_counts.items()):
        rollup_rows.append({"metric": f"trend_direction::{direction}", "value": count, "note": ""})
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    coverage_rows = read_csv(COVERAGE)
    expected_gap_count = sum(
        row["coverage_stage"] == "workset_only_no_official_candidate"
        for row in coverage_rows
    )
    group_keys = [str(row["group_pair_key"]) for row in rows]
    qa_rows = [
        {
            "check": "gap_count_matches_marker_127",
            "status": "PASS" if len(rows) == expected_gap_count == 12 else "FAIL",
            "detail": f"{len(rows)} gap rows from {expected_gap_count} marker-127 workset-only rows.",
        },
        {
            "check": "no_duplicate_group_pair_keys",
            "status": "PASS" if len(group_keys) == len(set(group_keys)) else "FAIL",
            "detail": f"{len(set(group_keys))} unique group_pair_keys for {len(group_keys)} rows.",
        },
        {
            "check": "all_rows_have_execution_constraints",
            "status": "PASS" if all(row["execution_packet_id"] for row in rows) else "FAIL",
            "detail": "Each gap row is joined back to marker 120 execution packet.",
        },
        {
            "check": "no_official_candidate_claimed",
            "status": "PASS" if all(row["gap_status"] == "needs_official_source_candidate_discovery" for row in rows) else "FAIL",
            "detail": "This artifact is a gap queue, not a source preview.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML entry opened.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusion_rows = [
        {
            "gap_id": row["gap_id"],
            "group_pair_key": row["group_pair_key"],
            "university_name": row["university_name"],
            "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": "official_source_candidate_not_yet_found",
            "safe_next_action": row["required_next_artifact"],
        }
        for row in rows
    ]
    write_csv(EXCLUSION, exclusion_rows, ["gap_id", "group_pair_key", "university_name", "excluded_from", "reason", "safe_next_action"])


def write_doc(rows: list[dict[str, object]]) -> None:
    lanes = Counter(str(row["execution_lane"]) for row in rows)
    boundaries = Counter(str(row["special_type_boundary"]) for row in rows)
    doc = [
        "# Reference trend 520 P1 batch17 official candidate gap queue",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This queue isolates batch17 group targets that still lack any official source candidate after marker 127 coverage rollup.",
        "",
        "## Outputs",
        "",
        f"- `clean_data/engineering_guangxi_seed/{OUT.name}`",
        f"- `reports/{ROLLUP.name}`",
        f"- `reports/{QA.name}`",
        f"- `reports/{EXCLUSION.name}`",
        "",
        "## Summary",
        "",
        f"- Gap rows: {len(rows)}",
        "- Source candidates claimed: 0",
        "- Browser/header/cookie/form replay required now: 0",
        "- Reference trend eligible rows: 0",
        "- Canonical/ML rows opened: 0",
        "",
        "## Execution Lanes",
        "",
    ]
    for lane, count in sorted(lanes.items()):
        doc.append(f"- `{lane}`: {count}")
    doc.extend(["", "## Boundary Mix", ""])
    for boundary, count in sorted(boundaries.items()):
        doc.append(f"- `{boundary}`: {count}")
    doc.extend([
        "",
        "## Boundary",
        "",
        "No network search, terminal fetch, cache, parse, OCR, browser/form replay, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update is performed.",
        "",
    ])
    DOC.write_text("\n".join(doc), encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 128. 2026-05-17 P1 batch17 official candidate gap queue"
    content = f"""

{marker}

已新增 P1 batch17 official-candidate gap queue：

- `clean_data/engineering_guangxi_seed/{OUT.name}`
- `reports/{ROLLUP.name}`
- `reports/{QA.name}`
- `reports/{EXCLUSION.name}`
- `docs/{DOC.name}`

覆盖结果：从 marker 127 的 coverage rollup 中抽取 12 条 `workset_only_no_official_candidate` rows，并回连 marker 120 execution packet 的搜索 query、lane、stop condition 和人工批准触发条件。QA PASS。

准入边界：本轮只生成下一轮官方来源发现 gap queue，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；不声明任何官方来源已找到；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_gap_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)
    append_handoff(rows)


if __name__ == "__main__":
    main()
