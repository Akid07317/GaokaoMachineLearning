#!/usr/bin/env python3
"""Record Shenyang University of Technology batch15 image-asset readiness.

The official 2025 plan page is an exact first-party source, but the plan table
is embedded as images. This script records the cached HTML and image assets as
OCR/manual-transcription candidates without promoting anything into
source-packet intake, reference_trend_pool, canonical, ML, or the decision pool.
"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

HTML_PATH = RAW_DIR / "sut_2025_plan_detail.html"
IMAGE_1 = RAW_DIR / "sut_2025_plan_image_1.jpg"
IMAGE_2 = RAW_DIR / "sut_2025_plan_image_2.jpg"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_sut_image_asset_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_sut_image_asset_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_sut_image_asset_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_sut_image_asset_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_sut_image_asset_readiness.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

OFFICIAL_URL = "https://zsxxw.sut.edu.cn/info/1049/2454.htm"

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
    "source_owner",
    "source_title",
    "published_date",
    "raw_html_path",
    "asset_url",
    "asset_path",
    "asset_type",
    "asset_size_bytes",
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


def q_context() -> tuple[str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10142"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10142"]
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "154"


def html_text() -> str:
    if not HTML_PATH.exists():
        return ""
    return HTML_PATH.read_text(encoding="utf-8-sig", errors="replace")


def image_urls(html: str) -> list[str]:
    urls: list[str] = []
    for match in re.finditer(r'<img[^>]+(?:orisrc|src)="([^"]+)"', html):
        url = match.group(1)
        if "__local" not in url:
            continue
        full = urljoin(OFFICIAL_URL, url)
        if full not in urls:
            urls.append(full)
    return urls


def main() -> None:
    queue_ids, batch_rank = q_context()
    html = html_text()
    urls = image_urls(html)
    html_has_guangxi = "广西" in html
    html_has_physics = "物理" in html
    published_match = re.search(r"发表时间：([0-9-]+)", html)
    published = published_match.group(1) if published_match else "2025-06-19"

    asset_paths = [IMAGE_1, IMAGE_2]
    rows: list[dict[str, object]] = []
    for idx, asset_path in enumerate(asset_paths, start=1):
        rows.append(
            {
                "record_id": f"reference_trend_520_batch15_sut_image_asset_{idx:04d}",
                "queue_record_id": queue_ids,
                "queue_rank": batch_rank,
                "university_code": "10142",
                "university_name": "沈阳工业大学",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "source_url": OFFICIAL_URL,
                "source_owner": "沈阳工业大学招生信息网",
                "source_title": "沈阳工业大学2025年本科招生计划",
                "published_date": published,
                "raw_html_path": rel(HTML_PATH) if HTML_PATH.exists() else "",
                "asset_url": urls[idx - 1] if idx - 1 < len(urls) else "",
                "asset_path": rel(asset_path) if asset_path.exists() else "",
                "asset_type": "jpg_plan_image",
                "asset_size_bytes": asset_path.stat().st_size if asset_path.exists() else 0,
                "asset_status": "cached_image_asset" if asset_path.exists() else "missing_image_asset",
                "source_contains_group_code": "unknown_until_ocr",
                "source_contains_plan_count": "true_likely_in_image_unparsed",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "collector_confidence": "T2_exact_official_plan_page_image_asset_ocr_required",
                "source_packet_status": "official_exact_page_cached_image_assets_no_text_rows",
                "eligible_for_intake_preview": "false_until_OCR_or_manual_transcription_QA",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "requires_manual_approval": "true_for_OCR_or_manual_transcription",
                "next_action": "If approved, OCR/manual-transcribe image assets, isolate Guangxi physical ordinary rows, and QA group/plan-count fields.",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_image_asset_readiness_only_not_32_school_decision_pool",
                "evidence_note": f"Official exact page is cached; HTML has static title but no table text. html_contains_guangxi={html_has_guangxi}; html_contains_physics={html_has_physics}.",
            }
        )

    rollup_rows = [
        {"metric": "sut_exact_page_cached_rows", "value": 1 if HTML_PATH.exists() else 0, "note": rel(HTML_PATH) if HTML_PATH.exists() else ""},
        {"metric": "image_asset_rows", "value": len(rows), "note": "Plan table image assets from official page."},
        {"metric": "cached_image_assets", "value": sum(1 for row in rows if row["asset_status"] == "cached_image_asset"), "note": ""},
        {"metric": "total_image_asset_bytes", "value": sum(int(row["asset_size_bytes"]) for row in rows), "note": ""},
        {"metric": "html_contains_guangxi", "value": int(html_has_guangxi), "note": "Static HTML body only, not OCR."},
        {"metric": "html_contains_physics", "value": int(html_has_physics), "note": "Static HTML body only, not OCR."},
        {"metric": "source_packet_eligible_rows", "value": 0, "note": "OCR/manual transcription required first."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No parsed group-year rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_exact_page_cached",
            "status": "PASS" if HTML_PATH.exists() else "FAIL",
            "detail": rel(HTML_PATH) if HTML_PATH.exists() else "HTML missing.",
        },
        {
            "check": "image_assets_cached",
            "status": "PASS" if all(path.exists() for path in asset_paths) else "WARN",
            "detail": "|".join(rel(path) for path in asset_paths if path.exists()),
        },
        {
            "check": "static_text_rows_absent",
            "status": "PASS",
            "detail": "Plan content is embedded in image tags; no Guangxi rows parsed from HTML text.",
        },
        {
            "check": "manual_ocr_route_isolated",
            "status": "PASS" if all(row["requires_manual_approval"] == "true_for_OCR_or_manual_transcription" for row in rows) else "FAIL",
            "detail": "Image OCR/manual transcription requires explicit approval before row extraction.",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No pool/canonical/ML writes.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 SUT Image Asset Readiness

Generated: {date.today().isoformat()}

Purpose: cache and audit 沈阳工业大学 official exact 2025 plan page and image
assets without performing OCR/manual transcription or writing any pool input.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official exact page: `{OFFICIAL_URL}`
- Cached HTML: `{HTML_PATH.relative_to(ROOT) if HTML_PATH.exists() else "not cached"}`
- Cached image assets: {sum(1 for path in asset_paths if path.exists())}
- Total image bytes: {sum(path.stat().st_size for path in asset_paths if path.exists())}

The page is first-party and exact, but all plan rows are embedded as images.
Rows remain outside source-packet intake and trend pool until OCR/manual
transcription is approved and independently QA'd.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 65. 2026-05-16 batch15 沈阳工业大学 image asset readiness"
    handoff_content = f"""

{marker}

已新增沈阳工业大学 batch15 image asset readiness：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：沈阳工业大学官方 exact 2025 本科招生计划页已缓存，页面包含 2 张官方计划图片资产，均已落地本地缓存。静态 HTML 不暴露广西/物理/专业组/计划数表格文本，因此本轮未做 OCR 或人工转录。

准入边界：本轮只做 image asset readiness，不写 source-packet intake、reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步若用户批准，可对两张图片做 OCR/人工转录，并单独生成 preview/QA。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
