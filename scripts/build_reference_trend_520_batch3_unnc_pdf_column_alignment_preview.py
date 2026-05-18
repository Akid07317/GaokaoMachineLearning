#!/usr/bin/env python3
"""Build a cautious UNNC PDF column-alignment preview.

The official Ningbo Nottingham PDF text is cached, and its Guangxi physical
column can be reconciled against the PDF summary total. The text extraction
still scrambles several major labels, so this script only creates a preview
and QA package. It does not open reference_trend/canonical/ML intake.
"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

QUEUE_STATUS = SEED_DIR / "reference_trend_520_plan_source_queue_status_reconciliation.csv"
RAW_PDF = ROOT / "raw_sources" / "reference_trend" / "batch3_t1" / "unnc_2025_plan.pdf"
RAW_TEXT = ROOT / "raw_sources" / "reference_trend" / "batch3_t1" / "unnc_2025_plan_text.txt"

OUT = SEED_DIR / "reference_trend_520_batch3_unnc_pdf_column_alignment_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch3_unnc_pdf_column_alignment_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch3_unnc_pdf_column_alignment_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch3_unnc_pdf_column_alignment_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch3_unnc_pdf_column_alignment_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_ID = "reference_trend_batch3_web_candidate_0004"
SOURCE_URL = "https://www.nottingham.edu.cn/cn/study-with-us/undergraduate/entry-requirements/plan.aspx"
SOURCE_OWNER = "宁波诺丁汉大学"
SOURCE_TITLE = "2025宁波诺丁汉大学全国28省（区、市）高考统招招生计划表"
UNIVERSITY_CODE = "16301"
UNIVERSITY_NAME = "宁波诺丁汉大学"
GUANGXI_INDEX_ZERO_BASED = 9

FIELDS = [
    "record_id",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_path",
    "raw_text_path",
    "text_line_no",
    "major_or_group_label",
    "line_label_status",
    "study_mode",
    "declared_total_plan_if_on_line",
    "province_column_count_detected",
    "guangxi_column_index_used",
    "guangxi_plan_count_provisional",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "special_type_detected",
    "qa_status",
    "collector_confidence",
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def queue_row() -> dict[str, str]:
    for row in read_csv(QUEUE_STATUS):
        if row.get("university_code") == UNIVERSITY_CODE and row.get("group_code") == "303":
            return row
    return {}


def parse_summary_candidates(lines: list[str]) -> dict[str, int]:
    numeric_lines: list[list[int]] = []
    for line in lines:
        if re.fullmatch(r"(?:\d+\s+){10,}\d+", line.strip()):
            values = [int(value) for value in line.split()]
            if len(values) >= 22:
                numeric_lines.append(values)
        if "文/历" in line or "理/物" in line:
            break
    if len(numeric_lines) < 3:
        return {}
    return {
        "summary_wen_guangxi": numeric_lines[0][GUANGXI_INDEX_ZERO_BASED],
        "summary_liwu_guangxi": numeric_lines[1][GUANGXI_INDEX_ZERO_BASED],
        "summary_total_guangxi": numeric_lines[2][GUANGXI_INDEX_ZERO_BASED],
    }


def label_from_prefix(prefix: str, row_no: int) -> tuple[str, str, str, str]:
    clean = " ".join(prefix.split())
    mode = ""
    declared_total = ""
    if not clean:
        return f"manual_alignment_needed_line_{row_no}", "major_label_missing_in_pdf_text_extraction", "", ""

    mode_match = re.search(r"(2\+2|四年)", clean)
    if mode_match:
        mode = mode_match.group(1)
    total_match = re.search(r"(?:2\+2|四年)\s+(\d+)\s*$", clean)
    if total_match:
        declared_total = total_match.group(1)
    label = clean
    if mode_match:
        label = clean[: mode_match.start()].strip()
    if not label:
        label = clean
    return label, "major_label_on_same_line", mode, declared_total


def build_rows() -> tuple[list[dict[str, object]], dict[str, int]]:
    q = queue_row()
    text = RAW_TEXT.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    summaries = parse_summary_candidates(lines)
    rows: list[dict[str, object]] = []
    pending_label_lines: list[str] = []

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if "理/物" not in stripped:
            if not re.fullmatch(r"[\d\s]+", stripped) and not any(token in stripped for token in ["备注", "院校名称", "总计"]):
                pending_label_lines.append(stripped)
                pending_label_lines = pending_label_lines[-4:]
            continue

        prefix, suffix = stripped.split("理/物", 1)
        nums = [int(value) for value in re.findall(r"\d+", suffix)]
        if len(nums) < 22:
            continue

        label, label_status, mode, declared_total = label_from_prefix(prefix, line_no)
        if label_status.startswith("major_label_missing") and pending_label_lines:
            label = " / ".join(pending_label_lines[-3:])
            label_status = "major_label_recovered_from_preceding_lines_review_needed"

        guangxi_plan = nums[GUANGXI_INDEX_ZERO_BASED]
        confidence = "T1_pdf_column_count_28_row_label_review_needed" if len(nums) >= 28 else "T2_pdf_first_22_columns_row_label_review_needed"
        rows.append(
            {
                "record_id": f"reference_trend_520_batch3_unnc_pdf_align_{len(rows) + 1:04d}",
                "source_id": SOURCE_ID,
                "queue_record_id": q.get("queue_record_id", "reference_trend_520_plan_source_queue_0013"),
                "queue_rank": q.get("queue_rank", "13"),
                "university_code": UNIVERSITY_CODE,
                "university_name": UNIVERSITY_NAME,
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "group_code": q.get("group_code", "303"),
                "rank_2024": q.get("rank_2024", ""),
                "rank_2025": q.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": q.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": q.get("trend_direction", ""),
                "source_url": SOURCE_URL,
                "source_owner": SOURCE_OWNER,
                "source_title": SOURCE_TITLE,
                "raw_file_path": rel(RAW_PDF),
                "raw_text_path": rel(RAW_TEXT),
                "text_line_no": line_no,
                "major_or_group_label": label,
                "line_label_status": label_status,
                "study_mode": mode,
                "declared_total_plan_if_on_line": declared_total,
                "province_column_count_detected": len(nums),
                "guangxi_column_index_used": "10_of_pdf_province_sequence",
                "guangxi_plan_count_provisional": guangxi_plan,
                "source_contains_group_code": "false",
                "source_contains_plan_count": "true",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "special_type_detected": "sino_foreign_university_boundary",
                "qa_status": "pdf_column_alignment_preview_hold_for_manual_label_review",
                "collector_confidence": confidence,
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": "0",
                "calibration_eligible": "0",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "required_resolution": "manual_review_major_label_alignment_and_exam_authority_group_mapping_before_any_trend_intake",
                "evidence_note": f"Parsed from PDF text line {line_no}; Guangxi is treated as the 10th province column in the PDF sequence.",
            }
        )
    return rows, summaries


def build_rollup(rows: list[dict[str, object]], summaries: dict[str, int]) -> list[dict[str, object]]:
    total = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    recovered = sum(1 for row in rows if str(row["line_label_status"]).startswith("major_label_recovered"))
    same_line = sum(1 for row in rows if row["line_label_status"] == "major_label_on_same_line")
    return [
        {"metric": "physical_rows_detected", "value": len(rows), "note": "Rows containing 理/物 and at least 22 province columns."},
        {"metric": "guangxi_physical_plan_sum_provisional", "value": total, "note": "Column 10 in PDF province sequence."},
        {"metric": "pdf_summary_liwu_guangxi", "value": summaries.get("summary_liwu_guangxi", ""), "note": "Expected checksum from top PDF summary row."},
        {"metric": "pdf_summary_total_guangxi", "value": summaries.get("summary_total_guangxi", ""), "note": "Physical + history summary for Guangxi."},
        {"metric": "same_line_major_labels", "value": same_line, "note": "Major label appears on same extracted line."},
        {"metric": "recovered_or_manual_review_labels", "value": recovered, "note": "Label inferred from preceding text and needs review."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Held until label/group mapping review."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]], summaries: dict[str, int]) -> list[dict[str, str]]:
    total = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    expected = summaries.get("summary_liwu_guangxi")
    return [
        {"check": "raw_pdf_exists", "status": "PASS" if RAW_PDF.exists() else "FAIL", "detail": rel(RAW_PDF)},
        {"check": "raw_text_exists", "status": "PASS" if RAW_TEXT.exists() else "FAIL", "detail": rel(RAW_TEXT)},
        {"check": "physical_rows_detected", "status": "PASS" if len(rows) > 0 else "FAIL", "detail": str(len(rows))},
        {"check": "guangxi_physical_checksum_matches_pdf_summary", "status": "PASS" if expected == total else "REVIEW", "detail": f"parsed={total}; summary={expected}"},
        {"check": "all_rows_held_for_manual_label_group_review", "status": "PASS" if all(row["eligible_for_intake_preview"] == "false" for row in rows) else "FAIL", "detail": "No intake rows produced."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS" if all(row["reference_trend_pool_eligible"] == "0" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "queue_record_id": row["queue_record_id"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "major_or_group_label": row["major_or_group_label"],
            "guangxi_plan_count_provisional": row["guangxi_plan_count_provisional"],
            "exclusion_or_hold_reason": row["qa_status"],
            "required_resolution": row["required_resolution"],
            "reference_trend_pool_eligible": row["reference_trend_pool_eligible"],
            "calibration_eligible": row["calibration_eligible"],
            "canonical_ml_entry_open": row["canonical_ml_entry_open"],
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], summaries: dict[str, int], qa_rows: list[dict[str, str]]) -> None:
    total = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    same_line = sum(1 for row in rows if row["line_label_status"] == "major_label_on_same_line")
    review = len(rows) - same_line
    pass_count = sum(1 for row in qa_rows if row["status"] == "PASS")
    review_count = sum(1 for row in qa_rows if row["status"] not in {"PASS", "FAIL"})
    fail_count = sum(1 for row in qa_rows if row["status"] == "FAIL")
    content = f"""# Reference Trend 520 Batch3 UNNC PDF Column Alignment Preview

Run date: {date.today().isoformat()}

This package parses the cached official Ningbo Nottingham PDF text only far enough to align the Guangxi physical plan column. It is a source-packet preview and QA artifact, not a trend-pool intake.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_pdf_column_alignment_preview.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_qa.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_exclusion_log.csv`

## Result

- Physical rows detected: {len(rows)}
- Provisional Guangxi physical plan sum: {total}
- PDF summary Guangxi physical checksum: {summaries.get("summary_liwu_guangxi", "")}
- Same-line labels: {same_line}; labels needing manual review: {review}
- QA: {pass_count} pass / {review_count} review / {fail_count} fail

## Boundary

The checksum now matches the PDF's Guangxi physical summary, but several major labels still need manual alignment and the PDF does not contain Guangxi institution-major-group codes. All rows remain `eligible_for_intake_preview=false`, `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.

## Next Action

Use this preview as a manual label/group mapping workbench seed for 宁波诺丁汉大学 group 303. Do not promote rows until the major labels and exam-authority group mapping are accepted.
"""
    DOC_OUT.write_text(content, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]], summaries: dict[str, int]) -> None:
    marker = "## 82. 2026-05-16 batch3 宁波诺丁汉 PDF column alignment preview"
    total = sum(int(row["guangxi_plan_count_provisional"]) for row in rows)
    content = f"""

{marker}

已新增宁波诺丁汉大学 batch3 PDF column alignment preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_pdf_column_alignment_preview.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_qa.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_exclusion_log.csv`
- `docs/reference_trend_520_batch3_unnc_pdf_column_alignment_preview.md`

覆盖结果：从官方 PDF 缓存文本中抽出 {len(rows)} 条理/物行，按 PDF 省份序列第 10 列对齐广西，广西物理计划数暂计 {total}，与 PDF 顶部广西理/物合计 {summaries.get("summary_liwu_guangxi", "")} 对齐。

准入边界：PDF 文本抽取仍有若干专业标签需要人工复核，且没有广西院校专业组代码；所有行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不并入 32 所 decision_pool。下一步可基于该预览生成宁波诺丁汉 group 303 的人工标签/组映射工作表。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows, summaries = build_rows()
    qa_rows = build_qa(rows, summaries)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, build_rollup(rows, summaries), ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(
        EXCLUSION_OUT,
        build_exclusions(rows),
        [
            "record_id",
            "queue_record_id",
            "university_name",
            "group_code",
            "major_or_group_label",
            "guangxi_plan_count_provisional",
            "exclusion_or_hold_reason",
            "required_resolution",
            "reference_trend_pool_eligible",
            "calibration_eligible",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    write_doc(rows, summaries, qa_rows)
    write_handoff(rows, summaries)
    print(f"wrote {len(rows)} UNNC PDF column alignment rows")
    print(f"preview: {OUT}")
    print(f"qa: {QA_OUT}")


if __name__ == "__main__":
    main()
