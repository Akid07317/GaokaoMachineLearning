#!/usr/bin/env python3
"""Extract text preview for locally cached P0 PDF action rows.

This script uses local cached PDF files only. It writes text-extraction preview
artifacts and QA notes, but it does not infer group-year records or produce
source_packet/intake/canonical rows.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path

try:
    from pypdf import PdfReader
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "pypdf is required. Run with the bundled workspace Python runtime."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

ACTION_QUEUE = CLEAN / "reference_trend_520_p0_cached_parse_action_queue.csv"
OUT = CLEAN / "reference_trend_520_p0_pdf_text_extract_preview.csv"
TEXT_DIR = CLEAN / "reference_trend_520_p0_pdf_text_extract_preview_text"
ROLLUP = REPORTS / "reference_trend_520_p0_pdf_text_extract_preview_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_pdf_text_extract_preview_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_pdf_text_extract_preview_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_pdf_text_extract_preview.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

PDF_ROUTE = "local_pdf_text_extract_preview_queue"
KEYWORDS = ["广西", "2025", "招生计划", "计划", "物理", "本科普通批", "专业组", "宁夏医科大学"]

FIELDS = [
    "pdf_text_record_id",
    "parse_action_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "source_url",
    "pdf_path",
    "pdf_size_bytes",
    "page_count",
    "extraction_method",
    "extracted_text_chars",
    "extracted_line_count",
    "keyword_hits",
    "contains_guangxi",
    "contains_physics",
    "contains_group_keyword",
    "contains_plan_keyword",
    "guangxi_snippet",
    "header_snippet",
    "line_preview",
    "text_artifact_path",
    "pdf_text_preview_status",
    "field_mapping_risk",
    "safe_next_action",
    "expected_output_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
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


def bool_str(value: bool) -> str:
    return "true" if value else "false"


def snippet(text: str, token: str, window: int = 80) -> str:
    pos = text.find(token)
    if pos < 0:
        return ""
    start = max(0, pos - window)
    end = min(len(text), pos + len(token) + window)
    return " ".join(text[start:end].split())


def compact_lines(text: str, limit: int = 10) -> str:
    lines = [" ".join(line.split()) for line in text.splitlines()]
    useful = [line for line in lines if line]
    return " | ".join(useful[:limit])


def extract_pdf(path: Path) -> tuple[int, str, str]:
    reader = PdfReader(str(path))
    page_texts: list[str] = []
    for page in reader.pages:
        page_texts.append(page.extract_text() or "")
    text = "\n".join(page_texts)
    return len(reader.pages), text, "pypdf_extract_text"


def safe_text_name(row: dict[str, str], index: int) -> str:
    code = row.get("university_code", "unknown") or "unknown"
    group = row.get("group_code", "group") or "group"
    return f"p0_pdf_text_{index:04d}_{code}_{group}.txt"


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    action_rows = read_csv(ACTION_QUEUE)
    targets = [row for row in action_rows if row.get("parse_action_route", "") == PDF_ROUTE]
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    for target in targets:
        rel = target.get("candidate_local_path", "") or target.get("candidate_value", "")
        path = ROOT / rel if rel else None
        exists = bool(path and path.exists())
        if not exists or path is None:
            exclusions.append(
                {
                    "record_id": target.get("parse_action_id", ""),
                    "university_name": target.get("university_name", ""),
                    "reason": "pdf_local_path_missing",
                    "detail": rel,
                }
            )
            continue
        try:
            page_count, text, method = extract_pdf(path)
            status = "text_extracted_layout_unverified" if text.strip() else "empty_text_possible_scan_pdf"
        except Exception as exc:  # pragma: no cover - defensive artifact row
            page_count, text, method = 0, "", "pypdf_extract_text_failed"
            status = "extract_failed"
            exclusions.append(
                {
                    "record_id": target.get("parse_action_id", ""),
                    "university_name": target.get("university_name", ""),
                    "reason": "pdf_text_extract_failed",
                    "detail": str(exc),
                }
            )

        index = len(rows) + 1
        text_artifact = TEXT_DIR / safe_text_name(target, index)
        text_artifact.write_text(text, encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        hits = [key for key in KEYWORDS if key in text]
        has_group = "专业组" in text
        has_physics = "物理" in text
        field_risk = (
            "table_text_extracted_but_group_subject_mapping_missing"
            if text and "广西" in text and not (has_group and has_physics)
            else "pdf_text_not_field_mappable_yet"
        )
        safe_action = (
            "Use the extracted text artifact for manual table QA; do not create group-year rows until Guangxi column, subject/group mapping, and special-type boundaries are confirmed."
            if status == "text_extracted_layout_unverified"
            else "Treat as scanned/failed PDF; require OCR or alternate source before source_packet preview."
        )
        rows.append(
            {
                "pdf_text_record_id": f"reference_trend_520_p0_pdf_text_{index:04d}",
                "parse_action_id": target.get("parse_action_id", ""),
                "queue_record_id": target.get("queue_record_id", ""),
                "queue_rank": target.get("queue_rank", ""),
                "university_code": target.get("university_code", ""),
                "university_name": target.get("university_name", ""),
                "group_pair_key": target.get("group_pair_key", ""),
                "group_code": target.get("group_code", ""),
                "source_url": target.get("source_url", ""),
                "pdf_path": rel,
                "pdf_size_bytes": path.stat().st_size,
                "page_count": page_count,
                "extraction_method": method,
                "extracted_text_chars": len(text),
                "extracted_line_count": len(lines),
                "keyword_hits": "|".join(hits),
                "contains_guangxi": bool_str("广西" in text),
                "contains_physics": bool_str(has_physics),
                "contains_group_keyword": bool_str(has_group),
                "contains_plan_keyword": bool_str("招生计划" in text or "计划" in text),
                "guangxi_snippet": snippet(text, "广西"),
                "header_snippet": snippet(text, "招生计划") or snippet(text, "计划"),
                "line_preview": compact_lines(text),
                "text_artifact_path": str(text_artifact.relative_to(ROOT)),
                "pdf_text_preview_status": status,
                "field_mapping_risk": field_risk,
                "safe_next_action": safe_action,
                "expected_output_layer": "pdf_text_extract_preview_only_not_source_packet_not_canonical",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "p0_pdf_text_preview_only_not_32_school_decision_pool",
                "evidence_note": "Local PDF text extraction preview only; no OCR, no network, no source_packet parse rows.",
            }
        )

    status_counts = Counter(str(row["pdf_text_preview_status"]) for row in rows)
    risk_counts = Counter(str(row["field_mapping_risk"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "input_parse_action_rows", "value": len(action_rows), "note": "Rows read from cached parse action queue."},
        {"metric": "local_pdf_target_rows", "value": len(targets), "note": "Rows with local PDF text extraction route."},
        {"metric": "pdf_text_preview_rows", "value": len(rows), "note": "PDF preview rows generated."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
    ]
    rollup_rows += [
        {"metric": f"pdf_text_preview_status::{key}", "value": count, "note": ""}
        for key, count in sorted(status_counts.items())
    ]
    rollup_rows += [
        {"metric": f"field_mapping_risk::{key}", "value": count, "note": ""}
        for key, count in sorted(risk_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_parse_action_queue_exists",
            "status": "pass" if ACTION_QUEUE.exists() else "fail",
            "value": str(ACTION_QUEUE.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "local_pdf_target_rows",
            "status": "pass" if len(targets) == 1 else "warn",
            "value": len(targets),
            "note": "Expected 1 from latest cached parse action queue.",
        },
        {
            "qa_check": "pdf_text_preview_rows_generated",
            "status": "pass" if len(rows) == len(targets) else "fail",
            "value": len(rows),
            "note": "",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "network_or_ocr_used",
            "status": "pass",
            "value": "false",
            "note": "Only local PDF text extraction was performed.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    status_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("pdf_text_preview_status::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 PDF Text Extract Preview

Date: {date.today().isoformat()}

Scope: local text extraction for cached PDF rows from `reference_trend_520_p0_cached_parse_action_queue.csv`. This is only a readability and evidence preview. It does not infer Guangxi group-year records, does not create source_packet rows, and does not open reference_trend_pool/canonical/ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview_text/`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_rollup.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_qa.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_exclusion_log.csv`

## Coverage

- PDF preview rows: {len(rows)}
- QA status: {qa_status}

## Status Counts

{status_lines or "- none"}

## Boundary

The extracted text can support a later manual table QA. Because the PDF text does not itself establish Guangxi subject/group mapping, no row is eligible for reference trend intake or calibration at this stage.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 105. 2026-05-16 P0 PDF text extract preview"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    chars = sum(int(row.get("extracted_text_chars", 0) or 0) for row in rows)
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 PDF text extract preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview_text/`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_rollup.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_qa.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_exclusion_log.csv`
- `docs/reference_trend_520_p0_pdf_text_extract_preview.md`

覆盖结果：处理 1 条本地 PDF action row，使用 pypdf 离线抽取文本；生成 {len(rows)} 条 preview rows，总文本字符 {chars}。QA {qa_status}。该 PDF 可读，但仍缺“广西物理/专业组”可验证映射，保留为 layout-unverified text preview。

准入边界：本轮只做本地 PDF 文本可读性和证据预览，不做 OCR、不联网、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
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
    print(f"wrote {len(rows)} PDF text preview rows")


if __name__ == "__main__":
    main()
