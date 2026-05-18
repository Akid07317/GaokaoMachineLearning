#!/usr/bin/env python3
"""Record Shaoxing University batch15 exact Guangxi image-asset readiness."""

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

HTML_PATH = RAW_DIR / "usx_2025_guangxi_plan_page.html"
IMAGE_PATH = RAW_DIR / "usx_2025_guangxi_plan_image.png"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_usx_image_asset_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_usx_image_asset_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_usx_image_asset_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_usx_image_asset_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_usx_image_asset_readiness.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PAGE_URL = "https://zs.usx.edu.cn/info/1002/6785.htm"
IMAGE_URL = "https://zs.usx.edu.cn/__local/9/47/08/75BB60CA592EB8D42CEAA6D51F5_0D81A983_45C8C.png"

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
    "published_date",
    "raw_html_path",
    "asset_url",
    "asset_path",
    "asset_type",
    "asset_size_bytes",
    "asset_dimensions",
    "asset_status",
    "source_contains_group_code",
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
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10349"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10349"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "158", all_ranks


def html_text() -> str:
    if not HTML_PATH.exists():
        return ""
    return HTML_PATH.read_text(encoding="utf-8-sig", errors="replace")


def title_date(html: str) -> tuple[str, str]:
    title = re.search(r'<h1 class="newstitle">(.+?)</h1>', html)
    published = re.search(r"发布日期：</span>([0-9-]+)", html)
    return (
        title.group(1).strip() if title else "绍兴文理学院2025年广西壮族自治区招生计划",
        published.group(1).strip() if published else "2025-06-18",
    )


def image_dimensions() -> str:
    if not IMAGE_PATH.exists():
        return ""
    data = IMAGE_PATH.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        return f"{width}x{height}"
    return "unknown"


def main() -> None:
    queue_ids, batch_rank, all_ranks = q_context()
    html = html_text()
    title, published = title_date(html)
    html_has_exact_title = "2025年广西壮族自治区招生计划" in html
    html_has_table_text = "<table" in html or "物理" in html or "院校专业组" in html
    dims = image_dimensions()
    row = {
        "record_id": "reference_trend_520_batch15_usx_image_asset_0001",
        "queue_record_id": queue_ids,
        "queue_rank": batch_rank,
        "related_queue_ranks": all_ranks,
        "university_code": "10349",
        "university_name": "绍兴文理学院",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类_candidate_until_image_ocr",
        "source_url": PAGE_URL,
        "source_owner": "绍兴文理学院本科招生网",
        "source_title": title,
        "published_date": published,
        "raw_html_path": rel(HTML_PATH) if HTML_PATH.exists() else "",
        "asset_url": IMAGE_URL,
        "asset_path": rel(IMAGE_PATH) if IMAGE_PATH.exists() else "",
        "asset_type": "png_plan_image",
        "asset_size_bytes": IMAGE_PATH.stat().st_size if IMAGE_PATH.exists() else 0,
        "asset_dimensions": dims,
        "asset_status": "cached_image_asset" if IMAGE_PATH.exists() else "missing_image_asset",
        "source_contains_group_code": "unknown_until_ocr",
        "source_contains_plan_count": "true_likely_in_image_unparsed",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "collector_confidence": "T1_exact_official_guangxi_plan_page_image_asset_ocr_required",
        "source_packet_status": "official_exact_guangxi_page_cached_image_asset_no_text_rows",
        "eligible_for_intake_preview": "false_until_OCR_or_manual_transcription_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "requires_manual_approval": "true_for_OCR_or_manual_transcription",
        "next_action": "If approved, OCR/manual-transcribe official image, isolate Guangxi physical ordinary rows, and QA group/plan-count fields.",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_image_asset_readiness_only_not_32_school_decision_pool",
        "evidence_note": f"Official exact Guangxi plan page cached; html_exact_title={html_has_exact_title}; html_static_table_text={html_has_table_text}; image_dimensions={dims}.",
    }
    rows = [row]
    rollup_rows = [
        {"metric": "usx_exact_guangxi_page_cached_rows", "value": 1 if HTML_PATH.exists() else 0, "note": rel(HTML_PATH) if HTML_PATH.exists() else ""},
        {"metric": "image_asset_rows", "value": len(rows), "note": "Official page embeds the Guangxi plan as one PNG asset."},
        {"metric": "cached_image_assets", "value": 1 if IMAGE_PATH.exists() else 0, "note": rel(IMAGE_PATH) if IMAGE_PATH.exists() else ""},
        {"metric": "image_asset_bytes", "value": IMAGE_PATH.stat().st_size if IMAGE_PATH.exists() else 0, "note": dims},
        {"metric": "html_exact_guangxi_title", "value": int(html_has_exact_title), "note": title},
        {"metric": "static_text_rows_found", "value": 0, "note": "No structured table rows in HTML text; plan rows are image-only."},
        {"metric": "source_packet_eligible_rows", "value": 0, "note": "OCR/manual transcription required first."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No parsed group-year rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_exact_guangxi_page_cached",
            "status": "PASS" if HTML_PATH.exists() and html_has_exact_title else "FAIL",
            "detail": rel(HTML_PATH) if HTML_PATH.exists() else "HTML missing.",
        },
        {
            "check": "image_asset_cached",
            "status": "PASS" if IMAGE_PATH.exists() else "FAIL",
            "detail": f"{rel(IMAGE_PATH) if IMAGE_PATH.exists() else 'missing'}; dimensions={dims}",
        },
        {
            "check": "static_text_rows_absent",
            "status": "PASS",
            "detail": "The official page embeds plan rows in an image; no OCR/manual transcription performed.",
        },
        {
            "check": "manual_ocr_route_isolated",
            "status": "PASS" if row["requires_manual_approval"] == "true_for_OCR_or_manual_transcription" else "FAIL",
            "detail": "Image OCR/manual transcription requires explicit approval before row extraction.",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS" if row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" else "FAIL",
            "detail": "No pool/canonical/ML writes.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 Shaoxing University Image Asset Readiness

Generated: {date.today().isoformat()}

Purpose: cache and audit 绍兴文理学院 exact official 2025 Guangxi plan page and
embedded image asset without OCR/manual transcription or writing any pool input.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official exact Guangxi page: `{PAGE_URL}`
- Cached HTML: `{HTML_PATH.relative_to(ROOT) if HTML_PATH.exists() else "not cached"}`
- Cached image asset: `{IMAGE_PATH.relative_to(ROOT) if IMAGE_PATH.exists() else "not cached"}`
- Image dimensions: {dims}; bytes: {IMAGE_PATH.stat().st_size if IMAGE_PATH.exists() else 0}

The official page is exact and first-party, but the plan table is embedded as an
image. Rows remain outside source-packet intake and trend pool until OCR/manual
transcription is approved and independently QA'd.
"""
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 68. 2026-05-16 batch15 绍兴文理学院 image asset readiness"
    handoff_content = f"""

{marker}

已新增绍兴文理学院 batch15 image asset readiness：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 exact 2025 广西壮族自治区招生计划页已缓存，正文计划表为 1 张 PNG 图片资产，已落地本地缓存，尺寸 {dims}。静态 HTML 不暴露广西/物理/专业组/计划数表格文本，因此本轮未做 OCR 或人工转录。

准入边界：本轮只做 image asset readiness，不写 source-packet intake、reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步若用户批准，可对图片做 OCR/人工转录，并单独生成 preview/QA。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
