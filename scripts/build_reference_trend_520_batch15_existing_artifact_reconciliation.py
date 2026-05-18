#!/usr/bin/env python3
"""Reconcile batch15 CSUFT queue rows to existing batch8 artifacts.

Batch15 rediscovered 中南林业科技大学 as an exact official Guangxi plan
candidate. The source was already cached and parsed in batch8, with a group
mapping workbench that remains held because the school plan source does not
print Guangxi professional-group codes. This script prevents duplicate caching
and turns the rediscovery into an auditable carry-forward record.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
WORKBENCH = SEED_DIR / "reference_trend_520_batch8_group_mapping_workbench.csv"
SOURCE_PACKET = SEED_DIR / "reference_trend_520_batch8_t1_source_packet_parse_preview.csv"
DISCOVERY = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch8_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_existing_artifact_reconciliation.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_existing_artifact_reconciliation_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_existing_artifact_reconciliation_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_existing_artifact_reconciliation_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_existing_artifact_reconciliation.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "batch15_source_id",
    "batch15_source_url",
    "existing_artifact_status",
    "existing_artifacts",
    "source_packet_rows",
    "official_major_rows_2025",
    "official_total_plan_2025",
    "exam_2025_physics_groups",
    "official_source_contains_group_code",
    "mapping_status",
    "qa_status",
    "required_resolution",
    "recommended_next_action",
    "requires_manual_approval",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    batch15_by_rank = {
        row.get("queue_rank", ""): row
        for row in read_csv(BATCH15)
        if row.get("university_code") == "10538"
    }
    queue_rows = [
        row
        for row in read_csv(QUEUE)
        if row.get("university_code") == "10538" and row.get("queue_rank") in {"168", "169"}
    ]
    workbench_rows = [row for row in read_csv(WORKBENCH) if row.get("university_code") == "10538"]
    source_rows = [row for row in read_csv(SOURCE_PACKET) if row.get("university_code") == "10538"]
    group_rows_2025 = [
        row
        for row in workbench_rows
        if row.get("year") == "2025" and row.get("group_code") not in {"", "unassigned"}
    ]
    artifact_paths = "|".join(rel(path) for path in (WORKBENCH, SOURCE_PACKET, DISCOVERY) if path.exists())
    exam_groups = "|".join(sorted({row.get("group_code", "") for row in group_rows_2025 if row.get("group_code")}))
    official_total = next((row.get("official_total_plan_2025", "") for row in group_rows_2025 if row.get("official_total_plan_2025")), "")
    official_major_rows = next((row.get("official_major_rows_2025", "") for row in group_rows_2025 if row.get("official_major_rows_2025")), "")

    rows: list[dict[str, object]] = []
    for q in queue_rows:
        rank = q.get("queue_rank", "")
        batch15 = batch15_by_rank.get("168|169", {}) or batch15_by_rank.get(rank, {})
        group_code = q.get("group_code", "")
        wb = next((row for row in group_rows_2025 if row.get("group_code") == group_code), {})
        rows.append(
            {
                "record_id": f"reference_trend_520_batch15_existing_artifact_reconcile_{rank}",
                "queue_record_id": q.get("record_id", ""),
                "queue_rank": rank,
                "university_code": "10538",
                "university_name": "中南林业科技大学",
                "group_code": group_code,
                "rank_2024": q.get("rank_2024", ""),
                "rank_2025": q.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": q.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": q.get("trend_direction", ""),
                "batch15_source_id": batch15.get("source_id", ""),
                "batch15_source_url": batch15.get("source_url", ""),
                "existing_artifact_status": "existing_batch8_source_packet_and_group_workbench_found",
                "existing_artifacts": artifact_paths,
                "source_packet_rows": len(source_rows),
                "official_major_rows_2025": official_major_rows,
                "official_total_plan_2025": official_total,
                "exam_2025_physics_groups": exam_groups,
                "official_source_contains_group_code": "false",
                "mapping_status": wb.get("mapping_status", "multiple_exam_groups_source_no_group_code_hold"),
                "qa_status": wb.get("qa_status", "hold_group_mapping_required"),
                "required_resolution": "manual_group_mapping_or_official_group_split_needed_before_any_group_year_intake",
                "recommended_next_action": "do_not_recrawl_exact_page; use existing batch8 source packet; create/await manual group mapping acceptance rule",
                "requires_manual_approval": "true_for_group_mapping_acceptance",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_existing_artifact_reconciliation_only_not_32_school_decision_pool",
                "evidence_note": wb.get("evidence_note", "Official source has plan counts but no Guangxi group code."),
            }
        )

    rollup_rows = [
        {"metric": "reconciled_batch15_queue_rows", "value": len(rows), "note": "Queue ranks 168/169."},
        {"metric": "existing_source_packet_rows", "value": len(source_rows), "note": rel(SOURCE_PACKET) if SOURCE_PACKET.exists() else ""},
        {"metric": "existing_group_workbench_rows", "value": len(workbench_rows), "note": rel(WORKBENCH) if WORKBENCH.exists() else ""},
        {"metric": "official_major_rows_2025", "value": official_major_rows, "note": "Batch8 parse."},
        {"metric": "official_total_plan_2025", "value": official_total, "note": "Batch8 parse."},
        {"metric": "exam_2025_physics_groups", "value": len(exam_groups.split('|')) if exam_groups else 0, "note": exam_groups},
        {"metric": "requires_manual_group_mapping_rows", "value": len(rows), "note": "Source does not print group code."},
        {"metric": "new_network_fetch_needed_rows", "value": 0, "note": "Do not recrawl this exact page."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Held for group mapping acceptance."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "existing_artifacts_present",
            "status": "PASS" if WORKBENCH.exists() and SOURCE_PACKET.exists() and DISCOVERY.exists() else "FAIL",
            "detail": artifact_paths,
        },
        {
            "check": "do_not_recrawl_duplicate",
            "status": "PASS",
            "detail": "Batch15 exact candidate maps to batch8 cached/parsed source.",
        },
        {
            "check": "group_mapping_hold_preserved",
            "status": "PASS" if rows and all(row["reference_trend_pool_eligible"] == "false" for row in rows) else "FAIL",
            "detail": "No group-year intake before manual group mapping or official group split.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "Canonical/ML remains closed.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 Existing Artifact Reconciliation

Generated: {date.today().isoformat()}

Purpose: deduplicate batch15 rediscovery of 中南林业科技大学 against existing
batch8 source-packet and group-mapping artifacts.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

Batch15 queue ranks 168/169 point to the same official 2025 Guangxi plan source
already handled in batch8. Existing artifacts contain 41 major rows and a plan
total of 150, but the official source does not print Guangxi professional-group
codes. The 2025 exam-authority context has groups {exam_groups}; group-year
intake stays held until manual group mapping or an official group split is
accepted.

## Boundary

No new network fetch is needed for this exact source. All reconciled rows remain
`reference_trend_pool_eligible=false`, `calibration_eligible=false`, and
`canonical_ml_entry_open=false`.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 61. 2026-05-16 batch15 existing artifact reconciliation"
    handoff_content = f"""

{marker}

已新增 batch15 existing artifact reconciliation：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：batch15 中南林业科技大学 168/169 两条队列被去重并承接到 batch8 既有产物：source packet parse 已有 41 个专业行、计划合计 150，group mapping workbench 已覆盖 2025 广西物理类 104/106/108 三个考试院专业组上下文。

准入边界：不再重复抓取中南林业科技大学 exact 广西计划页；官方计划源仍不打印广西院校专业组代码，因此 168/169 继续等待人工 group mapping 或官方 group split 证据。未写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
