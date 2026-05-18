#!/usr/bin/env python3
"""QA official PDF candidates from the 520-rank P0 discovery batch."""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
RAW = ROOT / "raw_sources" / "reference_trend" / "pdf_candidates"

IN_CANDIDATES = CLEAN / "reference_trend_520_next_batch_web_candidates_preview.csv"
OUT_PREVIEW = CLEAN / "reference_trend_520_next_batch_pdf_parse_qa_preview.csv"
OUT_ROLLUP = REPORTS / "reference_trend_520_next_batch_pdf_parse_qa_rollup.csv"
OUT_EXCLUSION = REPORTS / "reference_trend_520_next_batch_pdf_parse_exclusion_log.csv"
OUT_DOC = DOCS / "reference_trend_520_next_batch_pdf_parse_qa.md"


LOCAL_PDF_BY_SOURCE_ID = {
    "reference_trend_next_batch_web_candidate_0006": RAW / "njucm_2025_score_lines.pdf",
}

DOWNLOAD_FAILURE_BY_SOURCE_ID = {
    "reference_trend_next_batch_web_candidate_0001": {
        "status": "official_pdf_url_404_hold",
        "note": "Escalated curl to the official university-domain PDF URL returned HTTP 404 on 2026-05-16.",
    }
}


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


def extract_pdf_text(path: Path) -> tuple[int, str]:
    reader = PdfReader(str(path))
    chunks = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return len(reader.pages), "\n".join(chunks)


def province_hits(text: str) -> str:
    provinces = sorted(set(re.findall(r"[\u4e00-\u9fa5]{2,3}省|广西|重庆市|北京市|天津市|上海市", text)))
    return "|".join(provinces)


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[tuple[str, object]]]:
    candidates = [
        row
        for row in read_csv(IN_CANDIDATES)
        if "pdf" in row.get("source_packet_status", "").lower()
        or "PDF" in row.get("source_title", "")
    ]

    preview: list[dict[str, object]] = []
    exclusion: list[dict[str, object]] = []

    for idx, row in enumerate(candidates, start=1):
        source_id = row["source_id"]
        source_url = row["source_url"]
        university_name = row["university_name"]
        raw_path = LOCAL_PDF_BY_SOURCE_ID.get(source_id)
        pages = ""
        text_path = ""
        contains_guangxi = False
        contains_physics = False
        provinces = ""
        extracted_guangxi_rows = 0
        parse_note = ""

        if source_id in DOWNLOAD_FAILURE_BY_SOURCE_ID:
            qa_status = DOWNLOAD_FAILURE_BY_SOURCE_ID[source_id]["status"]
            parse_note = DOWNLOAD_FAILURE_BY_SOURCE_ID[source_id]["note"]
            required_resolution = "re_search_official_pdf_or_plan_page_before_any_intake"
        elif raw_path and raw_path.exists():
            pages, text = extract_pdf_text(raw_path)
            text_path = str(raw_path.with_suffix(".txt").relative_to(ROOT))
            raw_path.with_suffix(".txt").write_text(text, encoding="utf-8")
            contains_guangxi = "广西" in text
            contains_physics = "物理" in text
            provinces = province_hits(text)
            guangxi_lines = [line for line in text.splitlines() if "广西" in line]
            extracted_guangxi_rows = len(guangxi_lines)
            if contains_guangxi and extracted_guangxi_rows:
                qa_status = "parsed_guangxi_candidate_hold_for_table_structuring"
                required_resolution = "structure_guangxi_rows_then_QA_against_exam_authority"
            else:
                qa_status = "parsed_no_guangxi_rows_rejected"
                required_resolution = "exclude_pdf_for_guangxi_reference_trend_continue_official_plan_search"
                parse_note = "PDF parsed successfully but contains no Guangxi rows."
        else:
            qa_status = "local_pdf_missing_hold"
            required_resolution = "download_official_pdf_before_parse"
            parse_note = "No local PDF file found."

        record = {
            "record_id": f"reference_trend_520_next_batch_pdf_parse_{idx:04d}",
            "source_id": source_id,
            "university_code": row.get("university_code", ""),
            "university_name": university_name,
            "source_url": source_url,
            "source_title": row.get("source_title", ""),
            "raw_file_path": str(raw_path.relative_to(ROOT)) if raw_path and raw_path.exists() else "",
            "raw_text_path": text_path,
            "parsed_pages": pages,
            "province_hits": provinces,
            "contains_guangxi": str(contains_guangxi).lower(),
            "contains_physics": str(contains_physics).lower(),
            "extracted_guangxi_rows": extracted_guangxi_rows,
            "qa_status": qa_status,
            "parse_note": parse_note,
            "eligible_for_source_packet_intake": "false",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_expansion_performed": "false",
            "required_resolution": required_resolution,
        }
        preview.append(record)

        exclusion.append(
            {
                "record_id": f"reference_trend_520_next_batch_pdf_exclusion_{idx:04d}",
                "source_record_id": record["record_id"],
                "university_name": university_name,
                "source_url": source_url,
                "qa_status": qa_status,
                "exclusion_or_hold_reason": required_resolution,
                "canonical_ml_entry_open": "false",
                "reference_trend_pool_eligible": "false",
            }
        )

    rollup = [
        ("pdf_candidates_checked", len(preview)),
        ("download_404_hold_rows", sum(1 for r in preview if r["qa_status"] == "official_pdf_url_404_hold")),
        ("parsed_pdf_rows", sum(1 for r in preview if r["raw_file_path"])),
        ("parsed_no_guangxi_rows_rejected", sum(1 for r in preview if r["qa_status"] == "parsed_no_guangxi_rows_rejected")),
        ("parsed_guangxi_candidate_hold_rows", sum(1 for r in preview if r["qa_status"] == "parsed_guangxi_candidate_hold_for_table_structuring")),
        ("source_packet_intake_ready_rows", 0),
        ("reference_trend_pool_eligible_rows", 0),
        ("calibration_eligible_rows", 0),
        ("canonical_ml_entry_open", "false"),
        ("decision_pool_expansion_performed", "false"),
    ]
    return preview, exclusion, rollup


def write_doc(rollup: list[tuple[str, object]]) -> None:
    values = dict(rollup)
    OUT_DOC.write_text(
        f"""# Reference Trend 520 Next-Batch PDF Parse QA

日期：{date.today().isoformat()}

## 结论

已对上一轮 P0 官方 PDF 候选做解析/可达性 QA。云南中医药大学官方 PDF URL 当前返回 404，先进入 reachability/backoff；南京中医药大学官方 PDF 下载并解析成功，但 PDF 仅包含广东省行，未发现广西行，因此不能进入广西 reference trend source packet intake。

## 覆盖

- PDF candidates checked: {values['pdf_candidates_checked']}
- download 404 hold rows: {values['download_404_hold_rows']}
- parsed PDF rows: {values['parsed_pdf_rows']}
- parsed no-Guangxi rejected rows: {values['parsed_no_guangxi_rows_rejected']}
- source packet intake ready rows: 0
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 下一步

- 云南中医药大学需要重新定位官方招生计划/手册 PDF 或招生计划页。
- 南京中医药大学继续找官方 2025 外省招生计划页或含广西的录取统计页；当前 PDF 只保留为 rejected source clue。
- 继续处理兰州交通大学官方招生计划端点，或推进下一批 P0/P1 官方来源发现。
""",
        encoding="utf-8",
    )


def main() -> None:
    preview, exclusion, rollup = build()
    preview_fields = [
        "record_id",
        "source_id",
        "university_code",
        "university_name",
        "source_url",
        "source_title",
        "raw_file_path",
        "raw_text_path",
        "parsed_pages",
        "province_hits",
        "contains_guangxi",
        "contains_physics",
        "extracted_guangxi_rows",
        "qa_status",
        "parse_note",
        "eligible_for_source_packet_intake",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_expansion_performed",
        "required_resolution",
    ]
    exclusion_fields = [
        "record_id",
        "source_record_id",
        "university_name",
        "source_url",
        "qa_status",
        "exclusion_or_hold_reason",
        "canonical_ml_entry_open",
        "reference_trend_pool_eligible",
    ]
    write_csv(OUT_PREVIEW, preview, preview_fields)
    write_csv(OUT_EXCLUSION, exclusion, exclusion_fields)
    write_csv(
        OUT_ROLLUP,
        [{"metric": metric, "value": value} for metric, value in rollup],
        ["metric", "value"],
    )
    write_doc(rollup)
    print(f"pdf_candidates_checked={len(preview)}")
    print("source_packet_intake_ready_rows=0")


if __name__ == "__main__":
    main()
