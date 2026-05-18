#!/usr/bin/env python3
"""Build a manual label/group mapping workbench for UNNC group 303.

Input is the cautious PDF column-alignment preview. This script does not promote
anything to reference_trend/canonical/ML. It adds proposed clean labels where the
PDF layout is decipherable and leaves reviewer decision fields for manual use.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

INPUT = SEED_DIR / "reference_trend_520_batch3_unnc_pdf_column_alignment_preview.csv"
OUT = SEED_DIR / "reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch3_unnc_label_group_mapping_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch3_unnc_label_group_mapping_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch3_unnc_label_group_mapping_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch3_unnc_label_group_mapping_workbench.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

MANUAL_FIELDS = ["selected_decision", "reviewer", "decision_notes"]

PROPOSED_LABEL_BY_LINE = {
    "68": ("国际事务与国际关系", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "70": ("英语", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "72": ("传播学", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "74": ("国际经济与贸易", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "76": ("经济学", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "78": ("国际商务", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "81": ("英语(2+2)", "T2_inferred_from_pdf_layout_preceding_label_block"),
    "82": ("建筑学", "T1_same_line_label_cleanup"),
    "83": ("计算机科学与技术(2+2)", "T1_same_line_label_cleanup"),
    "84": ("计算机科学与技术", "T1_same_line_label_cleanup"),
    "85": ("数学与应用数学(2+2)", "T1_same_line_label_cleanup"),
    "86": ("数学与应用数学", "T1_same_line_label_cleanup"),
    "91": ("电气类(2+2)", "T1_same_line_label_cleanup"),
    "93": ("电气类", "T1_same_line_label_cleanup"),
    "94": ("环境科学(2+2)", "T1_same_line_label_cleanup"),
    "95": ("统计学(2+2)", "T1_same_line_label_cleanup"),
    "96": ("化学(2+2)", "T1_same_line_label_cleanup"),
}

FIELDS = [
    "workbench_record_id",
    "source_alignment_record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "exam_authority_group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "text_line_no",
    "raw_extracted_label",
    "line_label_status",
    "proposed_clean_major_label",
    "proposed_label_confidence",
    "study_mode",
    "declared_total_plan_if_on_line",
    "guangxi_plan_count_provisional",
    "source_url",
    "raw_file_path",
    "raw_text_path",
    "mapping_status",
    "suggested_decision_options",
    "selected_decision",
    "reviewer",
    "decision_notes",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
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


def protect_human_decisions() -> None:
    if not OUT.exists():
        return
    rows = read_csv(OUT)
    touched = [
        row
        for row in rows
        if any(str(row.get(field, "")).strip() for field in MANUAL_FIELDS)
    ]
    if touched:
        raise SystemExit(
            f"Refusing to overwrite {OUT}: {len(touched)} manual decision rows detected."
        )


def build_rows() -> list[dict[str, object]]:
    source_rows = read_csv(INPUT)
    rows: list[dict[str, object]] = []
    for index, row in enumerate(source_rows, start=1):
        line_no = row.get("text_line_no", "")
        proposed_label, confidence = PROPOSED_LABEL_BY_LINE.get(
            line_no,
            ("", "manual_label_required"),
        )
        plan = int(row.get("guangxi_plan_count_provisional") or "0")
        mapping_status = (
            "ready_for_manual_accept_if_label_and_group303_are_confirmed"
            if proposed_label and plan > 0
            else "zero_plan_or_label_review_hold"
        )
        rows.append(
            {
                "workbench_record_id": f"reference_trend_520_batch3_unnc_mapping_{index:04d}",
                "source_alignment_record_id": row.get("record_id", ""),
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "exam_authority_group_code": row.get("group_code", ""),
                "rank_2024": row.get("rank_2024", ""),
                "rank_2025": row.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "text_line_no": line_no,
                "raw_extracted_label": row.get("major_or_group_label", ""),
                "line_label_status": row.get("line_label_status", ""),
                "proposed_clean_major_label": proposed_label,
                "proposed_label_confidence": confidence,
                "study_mode": row.get("study_mode", ""),
                "declared_total_plan_if_on_line": row.get("declared_total_plan_if_on_line", ""),
                "guangxi_plan_count_provisional": plan,
                "source_url": row.get("source_url", ""),
                "raw_file_path": row.get("raw_file_path", ""),
                "raw_text_path": row.get("raw_text_path", ""),
                "mapping_status": mapping_status,
                "suggested_decision_options": "accept_label_group303_mapping|edit_label_then_accept|reject_row|hold_for_pdf_visual_review",
                "selected_decision": "",
                "reviewer": "",
                "decision_notes": "",
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": "0",
                "calibration_eligible": "0",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "required_resolution": "human_accept_or_edit_label_and_confirm_group303_mapping_before_any_source_packet_intake",
                "evidence_note": (
                    "Workbench row generated from the official PDF column-alignment preview; "
                    "Guangxi physical column checksum already matched the PDF summary."
                ),
            }
        )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    status_counts = Counter(str(row["mapping_status"]) for row in rows)
    confidence_counts = Counter(str(row["proposed_label_confidence"]) for row in rows)
    positive = sum(1 for row in rows if int(row["guangxi_plan_count_provisional"]) > 0)
    total_plan = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    return [
        {"metric": "workbench_rows", "value": len(rows), "note": "Manual label/group mapping rows."},
        {"metric": "positive_guangxi_plan_rows", "value": positive, "note": "Rows with Guangxi physical plan count > 0."},
        {"metric": "guangxi_physical_plan_sum_provisional", "value": total_plan, "note": "Checksum remains 20 from alignment preview."},
        {"metric": "ready_for_manual_accept_rows", "value": status_counts.get("ready_for_manual_accept_if_label_and_group303_are_confirmed", 0), "note": "Still requires human selected_decision."},
        {"metric": "zero_plan_or_label_review_hold_rows", "value": status_counts.get("zero_plan_or_label_review_hold", 0), "note": "Usually zero-plan or lower-confidence label rows."},
        {"metric": "t1_label_cleanup_rows", "value": confidence_counts.get("T1_same_line_label_cleanup", 0), "note": "Same-line labels cleaned."},
        {"metric": "t2_inferred_label_rows", "value": confidence_counts.get("T2_inferred_from_pdf_layout_preceding_label_block", 0), "note": "Inferred from preceding label block."},
        {"metric": "manual_decision_rows_present", "value": 0, "note": "Fresh workbench; no reviewer decisions filled."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Held until human acceptance."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    total_plan = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    manual_fields_empty = all(
        not any(str(row.get(field, "")).strip() for field in MANUAL_FIELDS)
        for row in rows
    )
    return [
        {"check": "input_alignment_preview_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "workbench_rows_match_alignment_rows", "status": "PASS" if len(rows) == len(read_csv(INPUT)) else "FAIL", "detail": f"{len(rows)} rows"},
        {"check": "guangxi_physical_checksum_carried_forward", "status": "PASS" if total_plan == 20 else "REVIEW", "detail": str(total_plan)},
        {"check": "proposed_labels_populated", "status": "PASS" if all(row["proposed_clean_major_label"] for row in rows) else "REVIEW", "detail": "All rows have a proposed label."},
        {"check": "manual_decision_fields_blank", "status": "PASS" if manual_fields_empty else "FAIL", "detail": "selected_decision/reviewer/decision_notes remain blank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS" if all(row["reference_trend_pool_eligible"] == "0" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "workbench_record_id": row["workbench_record_id"],
            "source_alignment_record_id": row["source_alignment_record_id"],
            "university_name": row["university_name"],
            "exam_authority_group_code": row["exam_authority_group_code"],
            "proposed_clean_major_label": row["proposed_clean_major_label"],
            "guangxi_plan_count_provisional": row["guangxi_plan_count_provisional"],
            "exclusion_or_hold_reason": "pending_human_label_group_mapping_decision",
            "required_resolution": row["required_resolution"],
            "reference_trend_pool_eligible": row["reference_trend_pool_eligible"],
            "calibration_eligible": row["calibration_eligible"],
            "canonical_ml_entry_open": row["canonical_ml_entry_open"],
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], qa_rows: list[dict[str, str]]) -> None:
    total_plan = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    positive = [row for row in rows if int(row["guangxi_plan_count_provisional"]) > 0]
    pass_count = sum(1 for row in qa_rows if row["status"] == "PASS")
    review_count = sum(1 for row in qa_rows if row["status"] not in {"PASS", "FAIL"})
    fail_count = sum(1 for row in qa_rows if row["status"] == "FAIL")
    positive_labels = ", ".join(
        f"{row['proposed_clean_major_label']}={row['guangxi_plan_count_provisional']}"
        for row in positive
    )
    content = f"""# Reference Trend 520 Batch3 UNNC Label/Group Mapping Workbench

Run date: {date.today().isoformat()}

This workbench turns the Ningbo Nottingham PDF column-alignment preview into human-review rows. It protects manual decision fields and does not write reference_trend, canonical, or ML inputs.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_qa.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_exclusion_log.csv`

## Result

- Workbench rows: {len(rows)}
- Rows with positive Guangxi physical plan count: {len(positive)}
- Provisional Guangxi physical plan sum: {total_plan}
- Positive rows: {positive_labels}
- QA: {pass_count} pass / {review_count} review / {fail_count} fail

## Manual Fields

Fill `selected_decision`, `reviewer`, and `decision_notes` only after checking the PDF visual layout and confirming that these rows map to exam-authority group 303. Valid decisions are `accept_label_group303_mapping`, `edit_label_then_accept`, `reject_row`, or `hold_for_pdf_visual_review`.

## Boundary

All rows remain `eligible_for_intake_preview=false`, `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` until human acceptance.
"""
    DOC_OUT.write_text(content, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 83. 2026-05-16 batch3 宁波诺丁汉 label/group mapping workbench"
    positive = sum(1 for row in rows if int(row["guangxi_plan_count_provisional"]) > 0)
    total_plan = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    content = f"""

{marker}

已新增宁波诺丁汉大学 label/group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_qa.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch3_unnc_label_group_mapping_workbench.md`

覆盖结果：将 17 条 PDF column alignment 行转成可人工确认的标签/专业组映射工作表，其中 {positive} 行广西物理计划数大于 0，计划数合计 {total_plan}。工作表包含 `selected_decision/reviewer/decision_notes`，后续脚本检测到人工填写会拒绝覆盖。

准入边界：这仍是人工映射工作表，不是 source-packet intake；所有行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不并入 32 所 decision_pool。下一步需要人工接受、修正或驳回标签与 group 303 映射。
"""
    append_handoff_once(marker, content)


def main() -> None:
    protect_human_decisions()
    rows = build_rows()
    qa_rows = build_qa(rows)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, build_rollup(rows), ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(
        EXCLUSION_OUT,
        build_exclusions(rows),
        [
            "workbench_record_id",
            "source_alignment_record_id",
            "university_name",
            "exam_authority_group_code",
            "proposed_clean_major_label",
            "guangxi_plan_count_provisional",
            "exclusion_or_hold_reason",
            "required_resolution",
            "reference_trend_pool_eligible",
            "calibration_eligible",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    write_doc(rows, qa_rows)
    write_handoff(rows)
    print(f"wrote {len(rows)} UNNC label/group mapping workbench rows")
    print(f"workbench: {OUT}")
    print(f"qa: {QA_OUT}")


if __name__ == "__main__":
    main()
