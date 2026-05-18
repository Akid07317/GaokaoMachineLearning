#!/usr/bin/env python3
"""Record batch-11 official PDF cache receipts and parse preflight QA.

The PDFs were fetched into raw_sources with approval after sandbox DNS failed.
This script records local file metadata and keeps the assets out of
reference_trend_pool/canonical/ML until a reliable table parser or audited
manual extraction is used.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch11_official"

OUT = SEED_DIR / "reference_trend_520_batch11_pdf_cache_receipt_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch11_pdf_cache_receipt_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch11_pdf_cache_receipt_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch11_pdf_cache_receipt_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch11_pdf_cache_receipt.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "official_asset_url",
    "raw_file_path",
    "asset_size_bytes",
    "pdf_version",
    "pdf_stream_count",
    "pdf_flate_decode_count",
    "pdf_image_marker_count",
    "pdf_font_marker_count",
    "pdf_tounicode_count",
    "web_text_layer_status",
    "local_parser_status",
    "source_contains_guangxi_column",
    "source_contains_subject_label",
    "source_contains_group_code",
    "source_contains_plan_count",
    "special_type_detected",
    "parse_preflight_status",
    "required_resolution",
    "requires_network",
    "requires_manual_approval",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def pdf_meta(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "raw_file_path": "",
            "asset_size_bytes": "",
            "pdf_version": "",
            "pdf_stream_count": "",
            "pdf_flate_decode_count": "",
            "pdf_image_marker_count": "",
            "pdf_font_marker_count": "",
            "pdf_tounicode_count": "",
        }
    data = path.read_bytes()
    first = data.splitlines()[0].decode("ascii", errors="replace") if data else ""
    return {
        "raw_file_path": rel(path),
        "asset_size_bytes": len(data),
        "pdf_version": first,
        "pdf_stream_count": data.count(b"stream"),
        "pdf_flate_decode_count": data.count(b"FlateDecode"),
        "pdf_image_marker_count": data.count(b"/Image"),
        "pdf_font_marker_count": data.count(b"/Font"),
        "pdf_tounicode_count": data.count(b"/ToUnicode"),
    }


def base(row: dict[str, object]) -> dict[str, object]:
    common = {
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_group_code": "false",
        "source_contains_plan_count": "true",
        "requires_network": "false",
        "requires_manual_approval": "false_for_local_parser_or_manual_table_review",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
    }
    common.update(row)
    return common


def build_rows() -> list[dict[str, object]]:
    sdust = RAW_DIR / "sdust_2025_plan.pdf"
    hzu = RAW_DIR / "hzu_2025_out_of_province_plan.pdf"
    return [
        base(
            {
                "record_id": "reference_trend_520_batch11_pdf_receipt_0001",
                "queue_record_id": "reference_trend_520_plan_source_queue_0076",
                "queue_rank": "76",
                "university_code": "10424",
                "university_name": "山东科技大学",
                "official_asset_url": "https://zs.sdust.edu.cn/__local/9/C5/43/9C6B02E1D7D86C60EE197EC373F_325C45C7_32086.pdf",
                **pdf_meta(sdust),
                "web_text_layer_status": "web_open_extracted_text_lines_present",
                "local_parser_status": "local_pdftotext_qpdf_mutool_gs_unavailable",
                "source_contains_guangxi_column": "true",
                "source_contains_subject_label": "false_or_not_printed",
                "special_type_detected": "art_design_boundary|sino_foreign_cooperation|ordinary_rows_mixed",
                "parse_preflight_status": "cached_text_pdf_hold_for_reliable_table_extraction",
                "required_resolution": "use reliable PDF table parser or audited manual table extraction before source-packet parse preview",
                "evidence_note": "Local PDF cached successfully. Web text layer shows 广西 header and rows, but local parser stack is unavailable and the PDF table is wide; do not infer Guangxi counts from flattened text order.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch11_pdf_receipt_0002",
                "queue_record_id": "reference_trend_520_plan_source_queue_0085",
                "queue_rank": "85",
                "university_code": "10577",
                "university_name": "惠州学院",
                "official_asset_url": "https://zs.hzu.edu.cn/_upload/article/files/a2/fb/9de322d54859b374cdc5f4e349e8/e1e67b91-542f-4e4e-8a05-52e12e565fa5.pdf",
                **pdf_meta(hzu),
                "web_text_layer_status": "web_open_extracted_text_lines_present",
                "local_parser_status": "local_pdftotext_qpdf_mutool_gs_unavailable",
                "source_contains_guangxi_column": "true",
                "source_contains_subject_label": "true_physical_history_art_model_labels",
                "special_type_detected": "ordinary_physical_rows|art_model_rows_need_isolation",
                "parse_preflight_status": "cached_text_pdf_hold_for_reliable_table_extraction",
                "required_resolution": "use reliable PDF table parser or audited manual table extraction before source-packet parse preview",
                "evidence_note": "Local PDF cached successfully. Web text layer shows 广西 and 物/理 labels, but flattened text drops column geometry; do not infer Guangxi counts without a table-aware route.",
            }
        ),
    ]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["parse_preflight_status"]) for row in rows)
    return [
        {"metric": "cached_pdf_rows", "value": len(rows), "note": "山东科技大学, 惠州学院."},
        {"metric": "cached_pdf_total_bytes", "value": sum(int(row["asset_size_bytes"] or 0) for row in rows), "note": ""},
        {"metric": "web_text_layer_present_rows", "value": sum(row["web_text_layer_status"] == "web_open_extracted_text_lines_present" for row in rows), "note": ""},
        {"metric": "local_parser_unavailable_rows", "value": sum("unavailable" in row["local_parser_status"] for row in rows), "note": "pdftotext/qpdf/mutool/gs unavailable."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Receipt/preflight only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year rows opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        *({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items())),
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "check": "local_pdf_cached",
            "status": "PASS" if all(row["raw_file_path"] for row in rows) else "FAIL",
            "detail": "Both official PDFs are cached in raw_sources/reference_trend/batch11_official.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "0" for row in rows) else "FAIL",
            "detail": "PDFs are not parsed into the trend pool.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML input opened.",
        },
        {
            "check": "table_geometry_guardrail",
            "status": "PASS",
            "detail": "Flattened text extraction is not used to guess Guangxi column values.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "queue_rank": row["queue_rank"],
            "exclusion_scope": "reference_trend_pool_and_calibration",
            "exclusion_reason": row["parse_preflight_status"],
            "required_resolution": row["required_resolution"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 Batch11 PDF Cache Receipt",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: record locally cached official PDFs and table-extraction guardrails.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Cached assets:",
    ]
    for row in rows:
        lines.append(
            f"- {row['university_name']} ({row['queue_rank']}): `{row['raw_file_path']}`, {row['asset_size_bytes']} bytes, {row['parse_preflight_status']}."
        )
    lines.extend(
        [
            "",
            "Boundary:",
            "- This is cache receipt/preflight only.",
            "- The PDFs contain visible web text layers, but local table-aware extraction is not available.",
            "- No flattened-text inference is used for Guangxi column counts.",
            "- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.",
            "",
            "Rollup:",
        ]
    )
    lines.extend(f"- {row['metric']}: {row['value']} {row['note']}".rstrip() for row in rollup)
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    exclusion = build_exclusion(rows)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "queue_rank", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup)

    marker = "## 46. 2026-05-16 batch11 PDF cache receipt"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch11 PDF cache receipt / parse preflight：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：山东科技大学、惠州学院官方 PDF 已缓存到 `raw_sources/reference_trend/batch11_official/`。网页层可见文本抽取，说明 PDF 不是死资产；但本地缺少 `pdftotext/qpdf/mutool/gs` 等表格/文本解析路线，且 PDF 是横向多列计划表，不能用扁平文本顺序硬猜广西列。

准入边界：本轮只做缓存收据和解析前置 QA，不进入 reference_trend_pool/canonical/ML；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可继续后续 P0 来源发现，或在有可靠 PDF 表格解析/人工转录路线后解析这两个 PDF。
""",
    )


if __name__ == "__main__":
    main()
