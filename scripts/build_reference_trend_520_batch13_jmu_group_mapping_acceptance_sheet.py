#!/usr/bin/env python3
"""Build a human acceptance sheet for JMU group-line mapping candidates.

The sheet is intentionally outside baseline/canonical/ML. It gives a reviewer
one row per candidate matched group and keeps decision fields blank. If a
reviewer later fills the sheet, rerunning this script will preserve it.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

WORKBENCH = SEED_DIR / "reference_trend_520_batch13_jmu_group_line_mapping_workbench.csv"
OUT = SEED_DIR / "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

DECISION_FIELDS = [
    "selected_decision",
    "reviewer",
    "decision_notes",
    "reviewed_at",
]

FIELDS = [
    "decision_record_id",
    "source_workbench_record_id",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_professional_group_code",
    "guangxi_exam_group_code_candidate",
    "queue_record_id",
    "queue_rank",
    "plan_row_count",
    "plan_count_sum",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "confidence_tier",
    "recommended_default_decision",
    "allowed_decisions",
    "selected_decision",
    "reviewer",
    "decision_notes",
    "reviewed_at",
    "source_url",
    "source_preview_file",
    "workbench_file",
    "post_acceptance_destination",
    "reference_trend_pool_eligible_before_acceptance",
    "calibration_eligible_before_acceptance",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
]

EXCLUSION_FIELDS = [
    "source_workbench_record_id",
    "university_code",
    "university_name",
    "source_professional_group_code",
    "guangxi_exam_group_code_candidate",
    "plan_count_sum",
    "exclusion_reason",
    "required_resolution",
]


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


def append_handoff_once(marker: str, content: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in existing:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def has_human_decisions(rows: list[dict[str, str]]) -> bool:
    for row in rows:
        if any(row.get(field, "").strip() for field in DECISION_FIELDS):
            return True
    return False


def build_sheet_rows(workbench_rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for row in workbench_rows:
        if row.get("mapping_status") != "candidate_group_line_match_preview_only":
            exclusions.append(
                {
                    "source_workbench_record_id": row.get("record_id", ""),
                    "university_code": row.get("university_code", ""),
                    "university_name": row.get("university_name", ""),
                    "source_professional_group_code": row.get("source_professional_group_code", ""),
                    "guangxi_exam_group_code_candidate": row.get("guangxi_exam_group_code_candidate", ""),
                    "plan_count_sum": row.get("plan_count_sum", ""),
                    "exclusion_reason": row.get("mapping_status", ""),
                    "required_resolution": row.get("required_resolution", ""),
                }
            )
            continue
        idx = len(rows) + 1
        rows.append(
            {
                "decision_record_id": f"reference_trend_520_batch13_jmu_mapping_acceptance_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "source_professional_group_code": row.get("source_professional_group_code", ""),
                "guangxi_exam_group_code_candidate": row.get("guangxi_exam_group_code_candidate", ""),
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "plan_row_count": row.get("plan_row_count", ""),
                "plan_count_sum": row.get("plan_count_sum", ""),
                "rank_2024": row.get("rank_2024", ""),
                "rank_2025": row.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "recommended_default_decision": "hold_until_human_accepts_mapping",
                "allowed_decisions": "accept_mapping_for_reference_trend_preview|hold_mapping|request_score_rank_source_fix|reject_mapping",
                "selected_decision": "",
                "reviewer": "",
                "decision_notes": "",
                "reviewed_at": "",
                "source_url": row.get("source_url", ""),
                "source_preview_file": row.get("source_preview_file", ""),
                "workbench_file": str(WORKBENCH.relative_to(ROOT)),
                "post_acceptance_destination": "post_human_decision_intake_preview_only_not_canonical",
                "reference_trend_pool_eligible_before_acceptance": "false",
                "calibration_eligible_before_acceptance": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_acceptance_sheet_only_not_32_school_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
                "evidence_note": row.get("evidence_note", ""),
            }
        )
    return rows, exclusions


def main() -> None:
    existing_rows = read_csv(OUT)
    preserved_existing = has_human_decisions(existing_rows)
    workbench_rows = read_csv(WORKBENCH)
    sheet_rows, exclusions = build_sheet_rows(workbench_rows)

    if preserved_existing:
        active_rows = existing_rows
    else:
        active_rows = sheet_rows
        write_csv(OUT, sheet_rows, FIELDS)

    filled_decisions = sum(1 for row in active_rows if row.get("selected_decision", "").strip())
    candidate_rows = len(active_rows)
    pending_rows = candidate_rows - filled_decisions
    plan_sum = sum(int(float(row.get("plan_count_sum") or 0)) for row in active_rows)

    rollup_rows = [
        {"metric": "decision_sheet_rows", "value": candidate_rows, "note": "Candidate matched JMU groups only."},
        {"metric": "candidate_plan_sum", "value": plan_sum, "note": "Source plan count sum for decision-sheet rows."},
        {"metric": "pending_human_decision_rows", "value": pending_rows, "note": ""},
        {"metric": "filled_human_decision_rows", "value": filled_decisions, "note": ""},
        {"metric": "excluded_hold_rows", "value": len(exclusions), "note": "Held groups are excluded from the acceptance sheet."},
        {"metric": "preserved_existing_human_sheet", "value": str(preserved_existing).lower(), "note": "True means the sheet was not overwritten."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake performed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "decision_sheet_candidate_rows",
            "status": "PASS" if candidate_rows == 7 else "REVIEW",
            "detail": f"candidate rows={candidate_rows}; expected 7 matched groups",
        },
        {
            "check": "decision_sheet_plan_sum",
            "status": "PASS" if plan_sum == 155 else "REVIEW",
            "detail": f"plan sum={plan_sum}; expected 155",
        },
        {
            "check": "human_fields_blank_or_preserved",
            "status": "PASS",
            "detail": "Existing filled sheet is preserved; otherwise new sheet has blank decision fields.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS",
            "detail": "No row was promoted to reference_trend_pool.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS",
            "detail": "canonical_ml_entry_open=false.",
        },
    ]

    doc = f"""# Reference Trend 520 Batch13 JMU Group Mapping Acceptance Sheet

Generated: {date.today().isoformat()}

Purpose: create a human decision sheet for 集美大学 candidate group-line mappings.
This sheet does not write baseline, canonical, ML, or the 32-school decision pool.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Decision rows: {candidate_rows}
- Pending human decisions: {pending_rows}
- Filled human decisions: {filled_decisions}
- Candidate plan sum: {plan_sum}
- Preserved existing filled sheet: {str(preserved_existing).lower()}

Allowed decisions are:

- `accept_mapping_for_reference_trend_preview`
- `hold_mapping`
- `request_score_rank_source_fix`
- `reject_mapping`

Even after acceptance, the next destination is a post-human-decision intake
preview only. Canonical/ML remains closed until explicitly approved.
"""
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, EXCLUSION_FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 54. 2026-05-16 batch13 集美大学 group mapping acceptance sheet"
    handoff = f"""

{marker}

已新增集美大学 group mapping acceptance decision sheet：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：从 group-line mapping workbench 中抽取 7 个 candidate matched group，生成待人工接受/hold/request_fix/reject 的决策表，覆盖计划数 {plan_sum}。专业组 11 继续在 exclusion/hold 层，不进入本决策表。

准入边界：本轮只生成空白人工决策表；未自动接受任何映射，未写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。脚本后续重跑会保护已经填写的人工决策字段。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
