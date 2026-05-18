#!/usr/bin/env python3
"""Build batch14 asset/PDF readiness preview for cached official sources.

This script extracts local assets from already cached official pages and records
readiness only. It does not OCR, parse PDF tables, open reference-trend intake,
or write canonical/ML.
"""

from __future__ import annotations

import base64
import csv
import re
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch14_official"

SHUPL_HTML = RAW_DIR / "shupl_2025_plan_detail.html"
SHOU_HTML = RAW_DIR / "shou_2025_plan_detail.html"
SHOU_PDF = RAW_DIR / "shou_2025_plan_pdf.pdf"

OUT = SEED_DIR / "reference_trend_520_batch14_asset_pdf_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch14_asset_pdf_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch14_asset_pdf_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch14_asset_pdf_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch14_asset_pdf_readiness.md"
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
    "source_url",
    "source_title",
    "cached_html_path",
    "asset_path",
    "asset_type",
    "asset_status",
    "asset_count",
    "file_size_bytes",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "parser_readiness",
    "requires_manual_approval",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
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


def extract_shupl_images() -> list[Path]:
    if not SHUPL_HTML.exists():
        return []
    text = SHUPL_HTML.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"data:image/png;base64,([A-Za-z0-9+/=]+)")
    out_paths: list[Path] = []
    for idx, payload in enumerate(pattern.findall(text), start=1):
        out_path = RAW_DIR / f"shupl_2025_plan_embedded_image_{idx}.png"
        out_path.write_bytes(base64.b64decode(payload))
        out_paths.append(out_path)
    return out_paths


def shou_pdfsrc() -> str:
    if not SHOU_HTML.exists():
        return ""
    text = SHOU_HTML.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'pdfsrc="([^"]+)"', text)
    if not match:
        return ""
    return "https://zsjy.shou.edu.cn" + match.group(1)


def common_boundary() -> dict[str, str]:
    return {
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "eligible_for_intake_preview": "false_until_asset_parse_and_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_asset_readiness_only_not_32_school_decision_pool",
    }


def main() -> None:
    image_paths = extract_shupl_images()
    pdftotext_available = shutil.which("pdftotext") is not None
    pdf_url = shou_pdfsrc()

    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    rows.append(
        {
            **common_boundary(),
            "record_id": "reference_trend_520_batch14_asset_pdf_readiness_0001",
            "queue_record_id": "reference_trend_520_plan_source_queue_0139",
            "queue_rank": "139",
            "university_code": "11835",
            "university_name": "上海政法学院",
            "source_url": "https://zs.shupl.edu.cn/Pages/Detail.aspx?DetailId=e120418d-6e7a-4663-8fd0-928b9dd2832b",
            "source_title": "上海政法学院2025年分省分专业本科招生计划",
            "cached_html_path": rel(SHUPL_HTML) if SHUPL_HTML.exists() else "",
            "asset_path": "|".join(rel(p) for p in image_paths),
            "asset_type": "embedded_png_plan_image",
            "asset_status": "cached_and_extracted_from_official_html" if image_paths else "missing_or_not_extracted",
            "asset_count": len(image_paths),
            "file_size_bytes": sum(p.stat().st_size for p in image_paths if p.exists()),
            "source_contains_group_code": "unknown_until_ocr_or_manual_transcription",
            "source_contains_plan_count": "true_in_embedded_image_unparsed",
            "parser_readiness": "needs_ocr_or_manual_transcription_approval",
            "requires_manual_approval": "true_for_ocr_or_manual_transcription",
            "next_action": "Ask before OCR/manual transcription; then isolate Guangxi physical ordinary rows.",
            "evidence_note": "Official detail page embeds plan as base64 PNG, not HTML table.",
        }
    )

    rows.append(
        {
            **common_boundary(),
            "record_id": "reference_trend_520_batch14_asset_pdf_readiness_0002",
            "queue_record_id": "reference_trend_520_plan_source_queue_0140",
            "queue_rank": "140",
            "university_code": "10264",
            "university_name": "上海海洋大学",
            "source_url": "https://zsjy.shou.edu.cn/2025/0620/c13793a341831/page.htm",
            "source_title": "2025年上海海洋大学普通本科分省招生计划",
            "cached_html_path": rel(SHOU_HTML) if SHOU_HTML.exists() else "",
            "asset_path": rel(SHOU_PDF) if SHOU_PDF.exists() else "",
            "asset_type": "official_pdf_plan_attachment",
            "asset_status": "cached_pdf_from_official_pdfsrc" if SHOU_PDF.exists() else "pdf_missing",
            "asset_count": 1 if SHOU_PDF.exists() else 0,
            "file_size_bytes": SHOU_PDF.stat().st_size if SHOU_PDF.exists() else 0,
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "parser_readiness": "needs_pdf_table_parser_or_manual_transcription",
            "requires_manual_approval": "true_for_pdf_table_parse_or_manual_transcription",
            "next_action": "Use a reliable PDF table parser or manual transcription route before row-level preview.",
            "evidence_note": f"Official page exposes pdfsrc={pdf_url}; local pdftotext available={str(pdftotext_available).lower()}.",
        }
    )

    exclusions.append(
        {
            **common_boundary(),
            "record_id": "reference_trend_520_batch14_asset_pdf_readiness_excluded_old_shou_pdf_url",
            "queue_record_id": "reference_trend_520_plan_source_queue_0140",
            "queue_rank": "140",
            "university_code": "10264",
            "university_name": "上海海洋大学",
            "source_url": "https://zsjy.shou.edu.cn/_upload/article/files/1e/f9/0f4acc7e475cacb985fc52d1e4c0/2406264b-18ff-4ef4-8e1c-52d6eb477f6d.pdf",
            "source_title": "stale/incorrect PDF URL from prior search surface",
            "cached_html_path": "",
            "asset_path": "",
            "asset_type": "stale_pdf_url",
            "asset_status": "curl_404_rejected",
            "asset_count": 0,
            "file_size_bytes": 0,
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "parser_readiness": "rejected",
            "requires_manual_approval": "false",
            "next_action": "Use pdfsrc from cached official HTML instead.",
            "evidence_note": "The stale URL returned HTTP 404 and is not used.",
        }
    )

    rollup_rows = [
        {"metric": "cached_official_html_rows", "value": sum(1 for p in [SHUPL_HTML, SHOU_HTML] if p.exists()), "note": ""},
        {"metric": "extracted_shupl_png_assets", "value": len(image_paths), "note": "|".join(rel(p) for p in image_paths)},
        {"metric": "cached_shou_pdf_assets", "value": 1 if SHOU_PDF.exists() else 0, "note": rel(SHOU_PDF) if SHOU_PDF.exists() else ""},
        {"metric": "manual_approval_rows", "value": len(rows), "note": "Both routes need OCR/PDF table parse or manual transcription approval."},
        {"metric": "parser_ready_without_approval_rows", "value": 0, "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Asset readiness only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No score/rank or accepted rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "shupl_html_cached",
            "status": "PASS" if SHUPL_HTML.exists() else "REVIEW",
            "detail": rel(SHUPL_HTML) if SHUPL_HTML.exists() else "missing",
        },
        {
            "check": "shupl_images_extracted",
            "status": "PASS" if image_paths else "REVIEW",
            "detail": f"images={len(image_paths)}",
        },
        {
            "check": "shou_pdf_cached",
            "status": "PASS" if SHOU_PDF.exists() else "REVIEW",
            "detail": f"pdfsrc={pdf_url}",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS",
            "detail": "No row enters reference_trend_pool.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS",
            "detail": "canonical_ml_entry_open=false for all rows.",
        },
    ]

    doc = f"""# Reference Trend 520 Batch14 Asset/PDF Readiness

Generated: {date.today().isoformat()}

Purpose: record cached official assets for 上海政法学院 and 上海海洋大学 as
source-packet readiness only. No OCR, PDF table parsing, manual transcription,
reference-trend intake, canonical, or ML output was opened.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- 上海政法学院 official detail HTML cached; embedded PNG assets extracted: {len(image_paths)}
- 上海海洋大学 official detail HTML cached; official PDF cached: {str(SHOU_PDF.exists()).lower()}
- Manual approval required rows: {len(rows)}

## Boundary

All rows remain `reference_trend_pool_eligible=false`,
`calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 56. 2026-05-16 batch14 asset/PDF readiness"
    handoff = f"""

{marker}

已新增 batch14 asset/PDF readiness：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：上海政法学院官方详情页已缓存，并从页面嵌入 base64 PNG 中提取本地计划图片资产 {len(image_paths)} 个；上海海洋大学官方详情页已缓存，并根据页面 `pdfsrc` 成功缓存 2025 分省招生计划 PDF。一个旧搜索面暴露的上海海洋 PDF URL 返回 404，已写入 exclusion。

准入边界：本轮只做资产/PDF 解析前置，不做 OCR、PDF 表格解析或人工转录，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮如果没有人工批准 OCR/PDF 解析，应继续缓存/解析 batch14 中其他可直接 HTML 化的官方计划详情。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
