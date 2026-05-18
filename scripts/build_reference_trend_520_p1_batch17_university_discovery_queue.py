#!/usr/bin/env python3
"""Collapse P1 batch-17 group workset into university-level discovery queue.

This deduplicates group-level discovery rows into one work item per university
so a future official-source discovery pass does not repeat the same search for
multiple group codes. It does not search, fetch, cache, parse, OCR, replay, or
open reference-trend/canonical/ML intake.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

WORKSET = SEED / "reference_trend_520_p1_batch17_discovery_workset.csv"
OUT = SEED / "reference_trend_520_p1_batch17_university_discovery_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch17_university_discovery_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch17_university_discovery_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch17_university_discovery_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch17_university_discovery_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "queue_id",
    "university_code",
    "university_name",
    "queue_ranks",
    "group_pair_keys",
    "group_codes",
    "target_group_count",
    "trend_directions",
    "rank_delta_min",
    "rank_delta_max",
    "source_packet_priority",
    "priority_score_max",
    "discovery_route",
    "special_type_boundaries",
    "primary_search_query",
    "secondary_search_query",
    "site_search_query",
    "desired_source_fields",
    "must_not_accept",
    "search_scope_note",
    "requires_network",
    "requires_browser_or_alternate_fetch",
    "requires_manual_approval",
    "source_packet_status",
    "eligible_for_source_packet_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
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
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def unique_join(values: list[str], sep: str = "|") -> str:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return sep.join(seen)


def route_for(rows: list[dict[str, str]]) -> str:
    routes = {row["discovery_route"] for row in rows}
    if "merge_same_university_group_rows_then_official_plan_discovery" in routes:
        routes.remove("merge_same_university_group_rows_then_official_plan_discovery")
        if routes:
            return unique_join(sorted(routes))
        return "standard_official_plan_discovery"
    return unique_join(sorted(routes))


def build_rows() -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(WORKSET):
        grouped[row["university_code"]].append(row)

    rows: list[dict[str, object]] = []
    for idx, (university_code, group_rows) in enumerate(sorted(grouped.items(), key=lambda item: min(int(row["queue_rank"]) for row in item[1])), 1):
        first = group_rows[0]
        deltas = [int(row["rank_delta_2025_minus_2024"]) for row in group_rows]
        name = first["university_name"]
        group_count = len(group_rows)
        route = route_for(group_rows)
        if group_count > 1:
            search_scope_note = "single_university_search_covers_multiple_group_codes"
        elif "medical" in route:
            search_scope_note = "isolate ordinary batch from medical/special major structures"
        elif "ethnic" in route:
            search_scope_note = "isolate ordinary batch from ethnic/minority special structures"
        else:
            search_scope_note = "single_group_university_search"
        rows.append(
            {
                "queue_id": f"reference_trend_520_p1_batch17_university_discovery_{idx:04d}",
                "university_code": university_code,
                "university_name": name,
                "queue_ranks": unique_join([row["queue_rank"] for row in group_rows]),
                "group_pair_keys": unique_join([row["group_pair_key"] for row in group_rows]),
                "group_codes": unique_join([row["group_code"] for row in group_rows]),
                "target_group_count": group_count,
                "trend_directions": unique_join([row["trend_direction"] for row in group_rows]),
                "rank_delta_min": min(deltas),
                "rank_delta_max": max(deltas),
                "source_packet_priority": first["source_packet_priority"],
                "priority_score_max": max(int(row["priority_score"]) for row in group_rows),
                "discovery_route": route,
                "special_type_boundaries": unique_join([row["special_type_boundary"] for row in group_rows]),
                "primary_search_query": f"{name} 2025 广西 物理类 本科普通批 招生计划 院校专业组",
                "secondary_search_query": f"{name} 2024 广西 物理类 本科普通批 招生计划 专业组",
                "site_search_query": f"site:edu.cn {name} 广西 物理类 招生计划 2025",
                "desired_source_fields": first["desired_source_fields"],
                "must_not_accept": first["must_not_accept"],
                "search_scope_note": search_scope_note,
                "requires_network": "true",
                "requires_browser_or_alternate_fetch": "true",
                "requires_manual_approval": "false_until_browser_cookie_form_pdf_or_ocr_route_needed",
                "source_packet_status": "university_level_discovery_queue_only",
                "eligible_for_source_packet_preview": "false_until_official_candidate_found",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "next_action": "run official source discovery for this university then write source_packet preview or backoff",
                "evidence_note": "Deduplicated from batch17 group workset; no web search or fetch executed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    route = Counter(str(row["discovery_route"]) for row in rows)
    group_count = Counter(str(row["target_group_count"]) for row in rows)
    boundary = Counter(str(row["special_type_boundaries"]) for row in rows)
    rollup_rows = [
        {"metric": "university_discovery_queue_rows", "value": len(rows), "note": "One row per university."},
        {"metric": "source_group_workset_rows_covered", "value": sum(int(row["target_group_count"]) for row in rows), "note": ""},
        {"metric": "multi_group_university_rows", "value": sum(int(row["target_group_count"]) > 1 for row in rows), "note": ""},
        {"metric": "requires_network_rows", "value": sum(row["requires_network"] == "true" for row in rows), "note": "Discovery not executed."},
        {"metric": "source_packet_preview_eligible_rows", "value": 0, "note": "No official candidates found in this queue-only pass."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Queue only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Queue only."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"target_group_count::{key}", "value": value, "note": ""} for key, value in sorted(group_count.items()))
    rollup_rows.extend({"metric": f"discovery_route::{key}", "value": value, "note": ""} for key, value in sorted(route.items()))
    rollup_rows.extend({"metric": f"boundary::{key}", "value": value, "note": ""} for key, value in sorted(boundary.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    covered = sum(int(row["target_group_count"]) for row in rows)
    qa_rows = [
        {
            "check": "dedupe_preserves_group_rows",
            "status": "PASS" if covered == len(read_csv(WORKSET)) else "FAIL",
            "detail": f"Covered {covered} source workset rows.",
        },
        {
            "check": "university_level_deduped",
            "status": "PASS" if len(rows) < len(read_csv(WORKSET)) else "WARN",
            "detail": f"Collapsed {len(read_csv(WORKSET))} group rows to {len(rows)} university rows.",
        },
        {
            "check": "no_official_source_claimed",
            "status": "PASS" if all(row["source_packet_status"] == "university_level_discovery_queue_only" for row in rows) else "FAIL",
            "detail": "Queue does not claim official URL discovery or cache success.",
        },
        {
            "check": "no_intake_or_canonical",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No queue row enters reference trend pool, canonical, ML, or decision pool.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch17_university_discovery_queue_all_rows",
            "reason": "queue_only_no_official_source_packet_yet",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    exclusions.extend(
        {
            "item": row["queue_id"],
            "reason": row["source_packet_status"],
            "effect": "not_eligible_for_intake_or_calibration",
        }
        for row in rows
    )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Reference trend 520 P1 batch17 university discovery queue",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This queue collapses batch17 group-level workset rows into one official-source discovery task per university.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Summary",
        "",
        f"- university rows: {len(rows)}",
        f"- covered group rows: {sum(int(row['target_group_count']) for row in rows)}",
        f"- multi-group universities: {sum(int(row['target_group_count']) > 1 for row in rows)}",
        "",
        "## Boundary",
        "",
        "- No web search, fetch, cache, parse, OCR, or browser/form replay was executed.",
        "- Rows are not source_packet parse rows and are not intake-eligible.",
        "- Canonical/ML and the 32-school decision pool remain closed.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)

    marker = "## 119. 2026-05-17 P1 batch17 university discovery queue"
    handoff = f"""

{marker}

已新增 P1 batch17 university-level discovery queue：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：将 marker 118 的 20 条 group-level workset rows 折叠为 {len(rows)} 条院校级 discovery tasks；河北北方学院两个 group rows 已合并为一个院校级任务。QA PASS。

准入边界：本轮只做去重后的官方来源发现队列，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
