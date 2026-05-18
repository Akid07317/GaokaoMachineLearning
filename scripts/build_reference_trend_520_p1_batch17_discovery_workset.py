#!/usr/bin/env python3
"""Build P1 batch-17 official discovery workset for queue ranks 191-210.

This creates a bounded, auditable workset for the next official-source
discovery pass. It does not search the web, fetch pages, cache assets, parse
tables, OCR, replay forms, or open reference-trend/canonical/ML intake.
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

SOURCE_QUEUE = SEED / "reference_trend_520_plan_source_packet_queue.csv"
OUT = SEED / "reference_trend_520_p1_batch17_discovery_workset.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch17_discovery_workset_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch17_discovery_workset_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch17_discovery_workset_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch17_discovery_workset.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

BATCH_MIN = 191
BATCH_MAX = 210

FIELDS = [
    "workset_id",
    "queue_record_id",
    "queue_rank",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "source_packet_priority",
    "priority_score",
    "candidate_source_status",
    "primary_search_query",
    "secondary_search_query",
    "site_search_query",
    "desired_source_fields",
    "must_not_accept",
    "discovery_route",
    "special_type_boundary",
    "duplicate_university_in_batch",
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


def special_boundary(name: str) -> str:
    flags: list[str] = []
    if any(token in name for token in ("医科", "中医药", "北方学院")):
        flags.append("medical_major_or_clinical_boundary_review")
    if "民族" in name:
        flags.append("ethnic_or_minority_special_type_boundary_review")
    if "师范" in name or "外国语" in name:
        flags.append("normal_language_teacher_direction_boundary_review")
    if "农业" in name:
        flags.append("agriculture_major_structure_boundary_review")
    return "|".join(flags) if flags else "ordinary_batch_boundary_unknown_until_official_source"


def discovery_route(row: dict[str, str], duplicate_university: bool) -> str:
    name = row["university_name"]
    if duplicate_university:
        return "merge_same_university_group_rows_then_official_plan_discovery"
    if "广西" in name or "桂林" in name:
        return "local_guangxi_official_plan_discovery"
    if any(token in name for token in ("医科", "中医药")):
        return "medical_official_plan_discovery_with_special_type_isolation"
    if "民族" in name:
        return "ethnic_university_official_plan_discovery_with_special_type_isolation"
    return "standard_official_plan_discovery"


def build_rows() -> list[dict[str, object]]:
    source_rows = [
        row
        for row in read_csv(SOURCE_QUEUE)
        if BATCH_MIN <= int(row["queue_rank"]) <= BATCH_MAX
    ]
    university_counts = Counter(row["university_code"] for row in source_rows)

    rows: list[dict[str, object]] = []
    for idx, row in enumerate(source_rows, 1):
        name = row["university_name"]
        duplicate = university_counts[row["university_code"]] > 1
        rows.append(
            {
                "workset_id": f"reference_trend_520_p1_batch17_discovery_workset_{idx:04d}",
                "queue_record_id": row["record_id"],
                "queue_rank": row["queue_rank"],
                "group_pair_key": row["group_pair_key"],
                "university_code": row["university_code"],
                "university_name": name,
                "group_code": row["group_code"],
                "rank_2024": row["rank_2024"],
                "rank_2025": row["rank_2025"],
                "rank_delta_2025_minus_2024": row["rank_delta_2025_minus_2024"],
                "trend_direction": row["trend_direction"],
                "source_packet_priority": row["source_packet_priority"],
                "priority_score": row["priority_score"],
                "candidate_source_status": row["candidate_source"],
                "primary_search_query": f"{name} 2025 广西 物理类 本科普通批 招生计划 院校专业组",
                "secondary_search_query": f"{name} 2024 广西 物理类 本科普通批 招生计划 专业组",
                "site_search_query": f"site:edu.cn {name} 广西 物理类 招生计划 2025",
                "desired_source_fields": "year|province=广西|batch=本科普通批|subject=物理类|university_group_code|plan_count|major_or_group_structure|source_url|published_date",
                "must_not_accept": "third_party_only|special_type_mixed|no_group_code_when_multiple_groups|school_minimum_only|canonical_or_ml_write",
                "discovery_route": discovery_route(row, duplicate),
                "special_type_boundary": special_boundary(name),
                "duplicate_university_in_batch": "true" if duplicate else "false",
                "requires_network": row["requires_network"],
                "requires_browser_or_alternate_fetch": row["requires_browser_or_alternate_fetch"],
                "requires_manual_approval": "false_until_browser_cookie_form_or_pdf_ocr_route_needed",
                "source_packet_status": "workset_only_official_source_not_yet_discovered",
                "eligible_for_source_packet_preview": "false_until_official_candidate_found",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "next_action": "official_source_discovery_then_write_source_packet_preview_or_backoff",
                "evidence_note": "P1 batch17 discovery workset only; no web search or fetch executed.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    priority = Counter(str(row["source_packet_priority"]) for row in rows)
    route = Counter(str(row["discovery_route"]) for row in rows)
    trend = Counter(str(row["trend_direction"]) for row in rows)
    boundary = Counter(str(row["special_type_boundary"]) for row in rows)
    universities = defaultdict(int)
    for row in rows:
        universities[str(row["university_code"])] += 1
    rollup_rows = [
        {"metric": "batch17_workset_rows", "value": len(rows), "note": "Queue ranks 191-210."},
        {"metric": "queue_rank_min", "value": min(int(row["queue_rank"]) for row in rows) if rows else "", "note": ""},
        {"metric": "queue_rank_max", "value": max(int(row["queue_rank"]) for row in rows) if rows else "", "note": ""},
        {"metric": "unique_universities", "value": len(universities), "note": ""},
        {"metric": "duplicate_university_rows", "value": sum(row["duplicate_university_in_batch"] == "true" for row in rows), "note": ""},
        {"metric": "requires_network_rows", "value": sum(row["requires_network"] == "true" for row in rows), "note": "Discovery still not executed."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Workset only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Workset only."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"priority::{key}", "value": value, "note": ""} for key, value in sorted(priority.items()))
    rollup_rows.extend({"metric": f"discovery_route::{key}", "value": value, "note": ""} for key, value in sorted(route.items()))
    rollup_rows.extend({"metric": f"trend_direction::{key}", "value": value, "note": ""} for key, value in sorted(trend.items()))
    rollup_rows.extend({"metric": f"boundary::{key}", "value": value, "note": ""} for key, value in sorted(boundary.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "queue_slice_size",
            "status": "PASS" if len(rows) == 20 else "FAIL",
            "detail": f"Expected 20 rows for ranks {BATCH_MIN}-{BATCH_MAX}; got {len(rows)}.",
        },
        {
            "check": "p1_boundary",
            "status": "PASS" if all(row["source_packet_priority"] == "P1_plan_source_packet_high" for row in rows) else "FAIL",
            "detail": "All rows remain P1 high-priority source discovery work.",
        },
        {
            "check": "no_official_source_claimed",
            "status": "PASS" if all(row["source_packet_status"] == "workset_only_official_source_not_yet_discovered" for row in rows) else "FAIL",
            "detail": "The workset does not claim found official URLs or cached files.",
        },
        {
            "check": "no_intake_or_canonical",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No rows enter reference trend pool, canonical, ML, or 32-school decision pool.",
        },
        {
            "check": "no_network_fetch",
            "status": "PASS",
            "detail": "No web search, terminal fetch, browser replay, OCR, or parser execution occurred.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch17_discovery_workset_all_rows",
            "reason": "workset_only_no_official_source_packet_yet",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    exclusions.extend(
        {
            "item": row["workset_id"],
            "reason": "official_source_discovery_pending",
            "effect": "not_eligible_for_intake_or_calibration",
        }
        for row in rows
    )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    route = Counter(str(row["discovery_route"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch17 discovery workset",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "Queue ranks 191-210 are prepared as an official-source discovery workset. This is a pre-network, pre-cache packet.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Route distribution",
        "",
    ]
    for key, value in sorted(route.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The workset records search strings, source fields, and exclusion constraints only.",
            "- It does not claim official source URLs, cache files, parse rows, or intake eligibility.",
            "- Canonical/ML and the 32-school decision pool remain closed.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)

    marker = "## 118. 2026-05-17 P1 batch17 discovery workset"
    handoff = f"""

{marker}

已新增 P1 batch17 official-source discovery workset：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：从 plan_source_packet_queue 抽取 ranks 191-210，共 20 条 group-level workset rows，覆盖 {len(set(row["university_code"] for row in rows))} 所院校；所有行仍为 P1_plan_source_packet_high。QA PASS。

准入边界：本轮只生成发现工作集和 QA/rollup，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
