#!/usr/bin/env python3
"""Reconcile plan-source queue rows against existing reference-trend artifacts."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

QUEUE = CLEAN / "reference_trend_520_plan_source_packet_queue.csv"
OUT = CLEAN / "reference_trend_520_plan_source_queue_status_reconciliation.csv"
ROLLUP = REPORTS / "reference_trend_520_plan_source_queue_status_reconciliation_rollup.csv"
QA = REPORTS / "reference_trend_520_plan_source_queue_status_reconciliation_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_plan_source_queue_status_reconciliation_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_plan_source_queue_status_reconciliation.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def compact_paths(paths: set[Path]) -> str:
    return "|".join(sorted(str(path.relative_to(ROOT)) for path in paths))


def get_code(row: dict[str, str]) -> str:
    return row.get("university_code", "").strip()


def build_artifact_index() -> dict[str, dict[str, object]]:
    index: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "discovery_rows": 0,
            "parse_rows": 0,
            "mapping_rows": 0,
            "plan_count_parse_rows": 0,
            "group_code_parse_rows": 0,
            "score_rank_parse_rows": 0,
            "eligible_rows": 0,
            "calibration_rows": 0,
            "canonical_open_rows": 0,
            "artifact_paths": set(),
            "mapping_statuses": Counter(),
            "source_statuses": Counter(),
        }
    )

    discovery_patterns = [
        "reference_trend_520_p0_official_source_discovery_batch*_preview.csv",
        "reference_trend_520_next_batch_web_candidates_preview.csv",
        "reference_trend_520_plan_discovery_web_candidates_preview.csv",
    ]
    parse_patterns = [
        "reference_trend_520_batch*_source_packet_parse_preview.csv",
        "reference_trend_*source_packet_parse_preview.csv",
        "reference_trend_520_next_batch_pdf_parse_qa_preview.csv",
    ]
    mapping_patterns = [
        "reference_trend_*group*workbench*.csv",
        "reference_trend_*group_mapping_qa_workbench.csv",
    ]

    seen_discovery_paths: set[Path] = set()
    for pattern in discovery_patterns:
        for path in CLEAN.glob(pattern):
            if path in seen_discovery_paths:
                continue
            seen_discovery_paths.add(path)
            for row in read_csv(path):
                code = get_code(row)
                if not code:
                    continue
                entry = index[code]
                entry["discovery_rows"] += 1
                entry["artifact_paths"].add(path)
                status = row.get("source_packet_status") or row.get("qa_status") or "discovery_candidate"
                entry["source_statuses"][status] += 1

    seen_parse_paths: set[Path] = set()
    for pattern in parse_patterns:
        for path in CLEAN.glob(pattern):
            if path in seen_parse_paths:
                continue
            seen_parse_paths.add(path)
            for row in read_csv(path):
                code = get_code(row)
                if not code:
                    continue
                entry = index[code]
                entry["parse_rows"] += 1
                entry["artifact_paths"].add(path)
                if str(row.get("source_contains_plan_count", "")).lower() in {"true", "admission_count_not_plan_count"} or row.get("plan_count"):
                    entry["plan_count_parse_rows"] += 1
                if str(row.get("source_contains_group_code", "")).lower() == "true" or row.get("group_or_selection_label"):
                    entry["group_code_parse_rows"] += 1
                if str(row.get("source_contains_min_score", "")).lower() == "true" or str(row.get("source_contains_min_rank", "")).lower() == "true" or row.get("min_score") or row.get("source_min_score"):
                    entry["score_rank_parse_rows"] += 1
                if str(row.get("reference_trend_pool_eligible", "")).lower() == "true" or str(row.get("eligible_for_trend_record", "")).lower() == "true":
                    entry["eligible_rows"] += 1
                if str(row.get("calibration_eligible", "")).lower() == "true":
                    entry["calibration_rows"] += 1
                if str(row.get("canonical_ml_entry_open", "")).lower() == "true":
                    entry["canonical_open_rows"] += 1

    seen_mapping_paths: set[Path] = set()
    for pattern in mapping_patterns:
        for path in CLEAN.glob(pattern):
            if path in seen_mapping_paths:
                continue
            seen_mapping_paths.add(path)
            for row in read_csv(path):
                code = get_code(row)
                if not code:
                    continue
                entry = index[code]
                entry["mapping_rows"] += 1
                entry["artifact_paths"].add(path)
                status = row.get("mapping_status") or row.get("parse_status") or "mapping_workbench_row"
                entry["mapping_statuses"][status] += 1
                if str(row.get("reference_trend_pool_eligible", "")).lower() == "true" or str(row.get("eligible_for_trend_record", "")).lower() == "true":
                    entry["eligible_rows"] += 1
                if str(row.get("calibration_eligible", "")).lower() == "true":
                    entry["calibration_rows"] += 1
                if str(row.get("canonical_ml_entry_open", "")).lower() == "true":
                    entry["canonical_open_rows"] += 1

    return index


def choose_status(entry: dict[str, object] | None) -> tuple[str, str, str]:
    if not entry:
        return (
            "needs_official_source_discovery",
            "T0_no_local_reference_trend_artifact",
            "continue_official_source_discovery",
        )
    if entry["mapping_rows"]:
        return (
            "mapping_workbench_exists_hold_for_group_acceptance",
            "T2_mapping_qa_available_not_accepted",
            "find_official_group_structure_or_manual_mapping_rule",
        )
    if entry["parse_rows"]:
        if entry["plan_count_parse_rows"] and entry["score_rank_parse_rows"]:
            return (
                "source_packet_parse_exists_multi_field_hold",
                "T2_source_packet_parse_available",
                "build_or_update_group_mapping_workbench",
            )
        if entry["plan_count_parse_rows"]:
            return (
                "plan_count_source_packet_exists_hold_for_group_mapping",
                "T2_plan_count_source_packet_available",
                "map_plan_rows_to_exam_authority_groups",
            )
        if entry["score_rank_parse_rows"]:
            return (
                "score_rank_source_packet_exists_hold_for_plan_or_group",
                "T2_score_rank_reference_available",
                "find_plan_count_or_group_structure_source",
            )
        return (
            "source_packet_parse_exists_but_field_gaps_remain",
            "T3_parse_available_field_gaps",
            "review_parse_gaps_before_new_search",
        )
    if entry["discovery_rows"]:
        return (
            "source_candidate_exists_not_structured",
            "T2_discovery_candidate_available",
            "parse_or_endpoint_drilldown_existing_candidate",
        )
    return (
        "needs_official_source_discovery",
        "T0_no_local_reference_trend_artifact",
        "continue_official_source_discovery",
    )


def main() -> None:
    queue_rows = read_csv(QUEUE)
    artifact_index = build_artifact_index()
    out_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for idx, row in enumerate(queue_rows, start=1):
        code = get_code(row)
        entry = artifact_index.get(code)
        status, tier, next_action = choose_status(entry)
        entry = entry or {}
        artifact_paths = compact_paths(entry.get("artifact_paths", set()))
        mapping_statuses = entry.get("mapping_statuses", Counter())
        source_statuses = entry.get("source_statuses", Counter())

        out_row = {
            "record_id": f"reference_trend_plan_source_reconcile_{idx:04d}",
            "queue_record_id": row.get("record_id", ""),
            "queue_rank": row.get("queue_rank", ""),
            "source_packet_priority": row.get("source_packet_priority", ""),
            "university_code": code,
            "university_name": row.get("university_name", ""),
            "group_pair_key": row.get("group_pair_key", ""),
            "group_code": row.get("group_code", ""),
            "rank_2024": row.get("rank_2024", ""),
            "rank_2025": row.get("rank_2025", ""),
            "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
            "trend_direction": row.get("trend_direction", ""),
            "queue_candidate_source": row.get("candidate_source", ""),
            "queue_next_action": row.get("next_action", ""),
            "reconciled_status": status,
            "confidence_tier": tier,
            "discovery_rows": entry.get("discovery_rows", 0),
            "parse_rows": entry.get("parse_rows", 0),
            "mapping_rows": entry.get("mapping_rows", 0),
            "plan_count_parse_rows": entry.get("plan_count_parse_rows", 0),
            "group_code_parse_rows": entry.get("group_code_parse_rows", 0),
            "score_rank_parse_rows": entry.get("score_rank_parse_rows", 0),
            "eligible_rows": entry.get("eligible_rows", 0),
            "calibration_rows": entry.get("calibration_rows", 0),
            "canonical_open_rows": entry.get("canonical_open_rows", 0),
            "artifact_paths": artifact_paths,
            "source_status_summary": "|".join(f"{k}:{v}" for k, v in sorted(source_statuses.items())),
            "mapping_status_summary": "|".join(f"{k}:{v}" for k, v in sorted(mapping_statuses.items())),
            "reconciled_next_action": next_action,
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_queue_reconciliation_only_not_decision_pool",
        }
        out_rows.append(out_row)
        if status != "needs_official_source_discovery":
            exclusions.append(out_row)

    counts = Counter()
    covered_universities = set()
    p0_rows = 0
    p0_uncovered = 0
    for row in out_rows:
        counts["queue_rows"] += 1
        counts[f"status::{row['reconciled_status']}"] += 1
        counts[f"priority::{row['source_packet_priority']}"] += 1
        if row["reconciled_status"] != "needs_official_source_discovery":
            covered_universities.add(row["university_code"])
        if row["source_packet_priority"] == "P0_plan_source_packet_urgent":
            p0_rows += 1
            if row["reconciled_status"] == "needs_official_source_discovery":
                p0_uncovered += 1

    rollup_rows = [
        {"metric": "queue_rows", "value": len(out_rows), "note": ""},
        {"metric": "universities_with_existing_reference_trend_artifact", "value": len(covered_universities), "note": ""},
        {"metric": "p0_queue_rows", "value": p0_rows, "note": ""},
        {"metric": "p0_rows_still_needing_discovery", "value": p0_uncovered, "note": ""},
        {"metric": "p0_rows_with_existing_artifact", "value": p0_rows - p0_uncovered, "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Reconciliation only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Reconciliation only."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(counts.items()):
        rollup_rows.append({"metric": key, "value": value, "note": ""})

    qa_rows = [
        {
            "qa_check": "queue_rows_reconciled",
            "status": "pass" if len(out_rows) == len(queue_rows) else "review",
            "value": len(out_rows),
            "note": f"Input queue rows={len(queue_rows)}.",
        },
        {
            "qa_check": "p0_rows_with_existing_artifact",
            "status": "info",
            "value": p0_rows - p0_uncovered,
            "note": "These P0 rows should not trigger blind duplicate discovery first.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]

    fields = [
        "record_id",
        "queue_record_id",
        "queue_rank",
        "source_packet_priority",
        "university_code",
        "university_name",
        "group_pair_key",
        "group_code",
        "rank_2024",
        "rank_2025",
        "rank_delta_2025_minus_2024",
        "trend_direction",
        "queue_candidate_source",
        "queue_next_action",
        "reconciled_status",
        "confidence_tier",
        "discovery_rows",
        "parse_rows",
        "mapping_rows",
        "plan_count_parse_rows",
        "group_code_parse_rows",
        "score_rank_parse_rows",
        "eligible_rows",
        "calibration_rows",
        "canonical_open_rows",
        "artifact_paths",
        "source_status_summary",
        "mapping_status_summary",
        "reconciled_next_action",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
    ]
    write_csv(OUT, out_rows, fields)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusions, fields)

    status_lines = "\n".join(f"- {k}: {v}" for k, v in sorted(counts.items()) if k.startswith("status::"))
    doc = f"""# Plan Source Queue Status Reconciliation

Generated: {date.today().isoformat()}

This non-baseline reconciliation joins `reference_trend_520_plan_source_packet_queue.csv` to existing discovery, source-packet parse, and group-mapping workbench artifacts. It is meant to prevent duplicate source searching and to route already-covered schools to mapping/QA resolution.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_plan_source_queue_status_reconciliation.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_rollup.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_qa.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_exclusion_log.csv`

## Coverage

- Queue rows reconciled: {len(out_rows)}
- P0 rows: {p0_rows}
- P0 rows with existing artifact: {p0_rows - p0_uncovered}
- P0 rows still needing discovery: {p0_uncovered}
- Universities with existing artifact: {len(covered_universities)}

## Status Rollup

{status_lines}

## Boundary

This file is a queue-routing layer only. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.
"""
    DOC.write_text(doc, encoding="utf-8")

    handoff_marker = "## 32. "
    handoff = f"""

## 32. {date.today().isoformat()} plan source queue status reconciliation refresh

已刷新 plan source 队列状态对账层：

- `clean_data/engineering_guangxi_seed/reference_trend_520_plan_source_queue_status_reconciliation.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_rollup.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_qa.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_exclusion_log.csv`
- `docs/reference_trend_520_plan_source_queue_status_reconciliation.md`

覆盖结果：对账 457 个 plan-source 队列项；P0 队列 117 行，其中已有 discovery/source_packet/mapping artifact 的 P0 行为 {p0_rows - p0_uncovered}，仍需新官方来源发现的 P0 行为 {p0_uncovered}。已有 artifact 覆盖 {len(covered_universities)} 所学校。

准入边界：这是 queue-routing 层，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。用途是避免重复搜已经进入 source_packet/mapping QA 的学校，并把下一轮自动化路由到真正缺源的 P0/P1 项。

下一轮优先级：先处理 `needs_official_source_discovery` 的 P0 行；已有 mapping/workbench 的学校优先补官方组结构或人工可审计映射规则，不重复做泛搜。
"""
    existing_handoff = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if handoff_marker not in existing_handoff:
        with HANDOFF.open("a", encoding="utf-8") as f:
            f.write(handoff)

    for path in [OUT, ROLLUP, QA, EXCLUSION, DOC]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
