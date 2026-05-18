#!/usr/bin/env python3
"""Record Yangtze University batch15 official aggregate PDF backoff.

The batch15 candidate pointed to an official 2025 PDF. After caching and text
extraction, the PDF is a whole-school batch/category plan summary rather than a
Guangxi province / professional-group plan source. Keep it as audited context
and out of source-packet intake, reference_trend_pool, canonical, and ML.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

PDF_PATH = RAW_DIR / "yangtzeu_2025_plan_pdf.pdf"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PLAN_COLUMN_URL = "https://zszc.yangtzeu.edu.cn/bkzn/zsjh.htm"
PDF_URL = "https://xxgk.yangtzeu.edu.cn/__local/3/55/84/AED89C4A8BF7FC02EED72A7D670_3AD1D955_3EF0F.pdf"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "related_queue_ranks",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_path",
    "pdf_pages",
    "aggregate_batch",
    "aggregate_subject",
    "aggregate_plan_count",
    "source_contains_guangxi",
    "source_contains_group_code",
    "source_contains_major_rows",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "collector_confidence",
    "source_packet_status",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "requires_manual_approval",
    "next_action",
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


def q_context() -> tuple[str, str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10489"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10489"]
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "162", all_ranks


def extract_text() -> tuple[str, int, str]:
    if not PDF_PATH.exists():
        return "", 0, "pdf_not_cached"
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover
        return "", 0, f"pypdf_unavailable:{exc.__class__.__name__}"
    try:
        reader = PdfReader(str(PDF_PATH))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text, len(reader.pages), "pypdf_text_extracted"
    except Exception as exc:  # pragma: no cover
        return "", 0, f"pypdf_extract_failed:{exc.__class__.__name__}"


def parse_aggregate_rows(text: str) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("2025年") or line.startswith("批次"):
            continue
        match = re.match(r"^(?P<batch>\S+)(?:\s+(?P<subject>\S+))?\s+(?P<count>\d+)$", line)
        if not match:
            continue
        rows.append((match.group("batch"), match.group("subject") or "", int(match.group("count"))))
    return rows


def main() -> None:
    queue_ids, batch_rank, all_ranks = q_context()
    text, pdf_pages, parse_status = extract_text()
    aggregate_rows = parse_aggregate_rows(text)
    has_guangxi = "广西" in text
    out_rows: list[dict[str, object]] = []
    for idx, (batch, subject, count) in enumerate(aggregate_rows, start=1):
        out_rows.append(
            {
                "record_id": f"reference_trend_520_batch15_yangtzeu_pdf_aggregate_{idx:04d}",
                "queue_record_id": queue_ids,
                "queue_rank": batch_rank,
                "related_queue_ranks": all_ranks,
                "university_code": "10489",
                "university_name": "长江大学",
                "year": "2025",
                "province": "not_province_specific",
                "batch": "aggregate_batch_summary",
                "subject_category": "aggregate_subject_summary",
                "source_url": PDF_URL,
                "source_owner": "长江大学本科招生信息网/信息公开网",
                "source_title": "2025年长江大学分批次、分科类招生计划",
                "raw_file_path": rel(PDF_PATH) if PDF_PATH.exists() else "",
                "pdf_pages": pdf_pages,
                "aggregate_batch": batch,
                "aggregate_subject": subject,
                "aggregate_plan_count": count,
                "source_contains_guangxi": str(has_guangxi).lower(),
                "source_contains_group_code": "false",
                "source_contains_major_rows": "false",
                "source_contains_plan_count": "true_aggregate_only",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "collector_confidence": "T3_official_aggregate_context_only_not_guangxi_rows",
                "source_packet_status": "official_pdf_cached_aggregate_context_not_source_packet_rows",
                "eligible_for_intake_preview": "false_no_guangxi_group_or_major_rows",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "requires_manual_approval": "false_for_backoff_true_if_new_exact_guangxi_source_is_found",
                "next_action": "Search/cache exact official Guangxi province/major/group plan source; do not infer from aggregate PDF.",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_aggregate_context_only_not_32_school_decision_pool",
                "evidence_note": "Official PDF is whole-school batch/category plan summary; no Guangxi, major rows, professional group, score, or rank fields.",
            }
        )

    total_row = next((row for row in out_rows if row["aggregate_batch"] == "总计"), {})
    general_physics = next(
        (row for row in out_rows if row["aggregate_batch"] == "普本" and row["aggregate_subject"] == "物理组"),
        {},
    )
    rollup_rows = [
        {"metric": "yangtzeu_pdf_cached_rows", "value": 1 if PDF_PATH.exists() else 0, "note": rel(PDF_PATH) if PDF_PATH.exists() else ""},
        {"metric": "pdf_pages", "value": pdf_pages, "note": parse_status},
        {"metric": "aggregate_rows_extracted", "value": len(out_rows), "note": "Whole-school batch/category rows."},
        {"metric": "general_undergraduate_physics_plan_count", "value": general_physics.get("aggregate_plan_count", ""), "note": "Aggregate only, not Guangxi."},
        {"metric": "total_plan_count", "value": total_row.get("aggregate_plan_count", ""), "note": "Aggregate total row."},
        {"metric": "source_contains_guangxi", "value": int(has_guangxi), "note": "No Guangxi rows in extracted PDF text."},
        {"metric": "source_packet_eligible_rows", "value": 0, "note": "No province/group/major rows for Guangxi."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Backoff only."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_pdf_cached",
            "status": "PASS" if PDF_PATH.exists() else "FAIL",
            "detail": rel(PDF_PATH) if PDF_PATH.exists() else "PDF missing.",
        },
        {
            "check": "pdf_text_extraction",
            "status": "PASS" if text and parse_status == "pypdf_text_extracted" else "FAIL",
            "detail": parse_status,
        },
        {
            "check": "aggregate_only_detected",
            "status": "PASS" if out_rows and not has_guangxi else "WARN",
            "detail": f"aggregate_rows={len(out_rows)}; contains_guangxi={has_guangxi}",
        },
        {
            "check": "no_source_packet_intake",
            "status": "PASS" if all(row["eligible_for_intake_preview"] == "false_no_guangxi_group_or_major_rows" for row in out_rows) else "FAIL",
            "detail": "Rows are context-only and not source-packet intake rows.",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in out_rows) else "FAIL",
            "detail": "No pool/canonical/ML writes.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 Yangtze University Aggregate PDF Backoff

Generated: {date.today().isoformat()}

Purpose: cache and audit the official 长江大学 2025 plan PDF discovered in
batch15 while preventing it from being mistaken for a Guangxi source-packet.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official plan column: `{PLAN_COLUMN_URL}`
- Official PDF: `{PDF_URL}`
- Cached PDF: `{PDF_PATH.relative_to(ROOT) if PDF_PATH.exists() else "not cached"}`
- PDF pages: {pdf_pages}; parse status: `{parse_status}`
- Aggregate rows extracted: {len(out_rows)}
- 普本物理组 aggregate plan: {general_physics.get("aggregate_plan_count", "")}
- Total aggregate plan: {total_row.get("aggregate_plan_count", "")}

The PDF is useful official context but does not contain Guangxi province rows,
major rows, professional-group codes, minimum scores, or ranks. It is therefore
excluded from source-packet intake and kept as a backoff/context artifact.
"""

    write_csv(OUT, out_rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, out_rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 64. 2026-05-16 batch15 长江大学 aggregate PDF backoff"
    handoff_content = f"""

{marker}

已新增长江大学 batch15 aggregate PDF backoff：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025“分批次、分科类招生计划”PDF 已缓存并用 pypdf 抽取文本；该 PDF 只有全校汇总口径，例如普本物理组 {general_physics.get("aggregate_plan_count", "")}、总计 {total_row.get("aggregate_plan_count", "")}，不含广西、专业行、院校专业组、最低分或最低位次。

准入边界：本轮只写 aggregate context/backoff；不写 source-packet intake、reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步应继续寻找长江大学官方广西分省/分专业/专业组计划源，不能从该汇总 PDF 推断广西计划。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
