#!/usr/bin/env python3
"""Build a manual table QA queue from local PDF text preview artifacts.

This script identifies candidate table lines in extracted PDF text. It does
not map collapsed PDF columns to Guangxi or create group-year/source_packet
rows; the output is only a manual QA queue.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

PDF_PREVIEW = CLEAN / "reference_trend_520_p0_pdf_text_extract_preview.csv"
OUT = CLEAN / "reference_trend_520_p0_pdf_manual_table_qa_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_pdf_manual_table_qa_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_pdf_manual_table_qa_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_pdf_manual_table_qa_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_pdf_manual_table_qa_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "table_qa_record_id",
    "pdf_text_record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "source_url",
    "pdf_path",
    "text_artifact_path",
    "line_number",
    "row_type",
    "raw_line",
    "major_name",
    "major_code",
    "study_years",
    "declared_total_plan",
    "numeric_sequence",
    "numeric_sequence_count",
    "remarks",
    "guangxi_column_mapping_status",
    "subject_group_mapping_status",
    "special_type_boundary_status",
    "manual_qa_decision",
    "manual_qa_notes",
    "safe_next_action",
    "expected_output_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]

MAJOR_ROW = re.compile(r"^(?P<name>.+?)\s+(?P<code>\d{6})\s+(?P<years>[345])\s+(?P<tail>.+)$")
SUMMARY_ROW = re.compile(r"^合\s*计\s+(?P<tail>.+)$")
NUM_RE = re.compile(r"\d+")
PROVINCE_ORDER = (
    "河北,山西,内蒙古,上海,江苏,浙江,安徽,福建,江西,山东,河南,湖北,湖南,广东,广西,"
    "重庆,四川,贵州,云南,陕西,甘肃,青海,国家民委专项,新疆内高班,新疆民族班,新疆预转,"
    "宁夏预转,国家专项计划,地方专项计划,宁夏"
)


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


def compact_line(line: str) -> str:
    return " ".join(str(line or "").split())


def split_tail_numbers_and_remarks(tail: str) -> tuple[list[str], str]:
    tokens = compact_line(tail).split()
    nums: list[str] = []
    remarks: list[str] = []
    seen_non_numeric = False
    for token in tokens:
        if token.isdigit() and not seen_non_numeric:
            nums.append(token)
        else:
            seen_non_numeric = True
            remarks.append(token)
    return nums, " ".join(remarks)


def row_from_line(base: dict[str, str], line_number: int, line: str) -> dict[str, object] | None:
    clean = compact_line(line)
    if not clean:
        return None
    major_match = MAJOR_ROW.match(clean)
    summary_match = SUMMARY_ROW.match(clean)
    if major_match:
        tail_nums, remarks = split_tail_numbers_and_remarks(major_match.group("tail"))
        if not tail_nums:
            return None
        row_type = "major_candidate_line"
        major_name = major_match.group("name")
        major_code = major_match.group("code")
        study_years = major_match.group("years")
        declared_total = tail_nums[0] if tail_nums else ""
        nums = tail_nums[1:]
    elif summary_match and NUM_RE.search(clean):
        nums, remarks = split_tail_numbers_and_remarks(summary_match.group("tail"))
        row_type = "summary_or_total_line"
        major_name = "合计"
        major_code = ""
        study_years = ""
        declared_total = nums[0] if nums else ""
        nums = nums[1:]
    else:
        return None

    has_special = any(token in clean for token in ["专项", "预科", "民族班", "内高班", "定向", "高职", "专科"])
    return {
        "pdf_text_record_id": base.get("pdf_text_record_id", ""),
        "queue_record_id": base.get("queue_record_id", ""),
        "queue_rank": base.get("queue_rank", ""),
        "university_code": base.get("university_code", ""),
        "university_name": base.get("university_name", ""),
        "group_pair_key": base.get("group_pair_key", ""),
        "group_code": base.get("group_code", ""),
        "source_url": base.get("source_url", ""),
        "pdf_path": base.get("pdf_path", ""),
        "text_artifact_path": base.get("text_artifact_path", ""),
        "line_number": line_number,
        "row_type": row_type,
        "raw_line": clean,
        "major_name": major_name,
        "major_code": major_code,
        "study_years": study_years,
        "declared_total_plan": declared_total,
        "numeric_sequence": "|".join(nums),
        "numeric_sequence_count": len(nums),
        "remarks": remarks,
        "guangxi_column_mapping_status": "manual_required_pdf_text_collapsed_columns",
        "subject_group_mapping_status": "manual_required_no_pdf_group_code",
        "special_type_boundary_status": "manual_check_special_type_present" if has_special else "ordinary_row_candidate_but_unverified",
        "manual_qa_decision": "",
        "manual_qa_notes": "",
        "safe_next_action": "Use PDF/page visual or original table layout to identify the Guangxi column and verify ordinary/subject/group mapping before any source_packet preview.",
        "expected_output_layer": "pdf_manual_table_qa_queue_only_not_source_packet_not_canonical",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "p0_pdf_manual_qa_only_not_32_school_decision_pool",
        "evidence_note": f"Province header order reference: {PROVINCE_ORDER}. Extracted PDF text collapses blank table cells, so numeric sequence must not be auto-indexed.",
    }


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    preview_rows = read_csv(PDF_PREVIEW)
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for preview in preview_rows:
        text_path = ROOT / preview.get("text_artifact_path", "")
        if not text_path.exists():
            exclusions.append(
                {
                    "record_id": preview.get("pdf_text_record_id", ""),
                    "university_name": preview.get("university_name", ""),
                    "reason": "text_artifact_missing",
                    "detail": preview.get("text_artifact_path", ""),
                }
            )
            continue
        text = text_path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            row = row_from_line(preview, line_number, line)
            if row is not None:
                rows.append(row)

    for index, row in enumerate(rows, start=1):
        row["table_qa_record_id"] = f"reference_trend_520_p0_pdf_table_qa_{index:04d}"

    row_type_counts = Counter(str(row["row_type"]) for row in rows)
    special_counts = Counter(str(row["special_type_boundary_status"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "input_pdf_text_preview_rows", "value": len(preview_rows), "note": "Rows read from PDF text extract preview."},
        {"metric": "manual_table_qa_rows", "value": len(rows), "note": "Candidate table lines requiring manual QA."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
    ]
    rollup_rows += [
        {"metric": f"row_type::{key}", "value": count, "note": ""}
        for key, count in sorted(row_type_counts.items())
    ]
    rollup_rows += [
        {"metric": f"special_type_boundary_status::{key}", "value": count, "note": ""}
        for key, count in sorted(special_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_pdf_text_preview_exists",
            "status": "pass" if PDF_PREVIEW.exists() else "fail",
            "value": str(PDF_PREVIEW.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "manual_table_qa_rows_generated",
            "status": "pass" if rows else "warn",
            "value": len(rows),
            "note": "Rows are not source_packet or intake rows.",
        },
        {
            "qa_check": "guangxi_column_not_auto_mapped",
            "status": "pass" if all(row["guangxi_column_mapping_status"] == "manual_required_pdf_text_collapsed_columns" for row in rows) else "fail",
            "value": "manual_required",
            "note": "Collapsed PDF text cannot safely preserve blank province cells.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    row_type_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("row_type::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 PDF Manual Table QA Queue

Date: {date.today().isoformat()}

Scope: candidate table lines extracted from the local PDF text preview. This queue is designed for human QA of the original PDF/table layout. It deliberately does not map numeric sequences to the Guangxi column because extracted PDF text can collapse blank cells.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_manual_table_qa_queue.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_rollup.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_qa.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_exclusion_log.csv`

## Coverage

- Manual QA rows: {len(rows)}
- QA status: {qa_status}

## Row Types

{row_type_lines or "- none"}

## Boundary

The next safe step is visual/table-layout QA against the PDF, not automatic intake. All rows remain outside source_packet, reference_trend_pool, canonical, ML, and the 32-school decision_pool.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 106. 2026-05-16 P0 PDF manual table QA queue"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    row_type_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("row_type::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 PDF manual table QA queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_manual_table_qa_queue.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_rollup.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_qa.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_pdf_manual_table_qa_queue.md`

覆盖结果：从宁夏医科大学 PDF text preview 派生 {len(rows)} 条人工表格 QA rows；行类型：{row_type_summary or 'none'}。QA {qa_status}。所有行均标注 `manual_required_pdf_text_collapsed_columns`，不自动映射广西列。

准入边界：本轮只做人工 QA 队列，不生成 source_packet parse rows，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。
"""
        )


def main() -> None:
    rows, rollup_rows, qa_rows, exclusions = build()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusions, ["record_id", "university_name", "reason", "detail"])
    write_doc(rows, rollup_rows, qa_rows)
    append_handoff(rows, rollup_rows, qa_rows)
    print(f"wrote {len(rows)} PDF manual table QA rows")


if __name__ == "__main__":
    main()
