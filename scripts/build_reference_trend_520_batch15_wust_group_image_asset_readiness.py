#!/usr/bin/env python3
"""Record WUST Guangxi group-setting image assets as reachability evidence.

No OCR or manual transcription is performed here. The outputs remain in the
source reachability / asset-readiness layer.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

PAGE = RAW_DIR / "wust_2025_group_setting_page.html"
IMAGE = RAW_DIR / "wust_2025_guangxi_group_setting_image.jpg"
IMAGE_ORIGINAL = RAW_DIR / "wust_2025_guangxi_group_setting_image_original.jpg"
OUT = SEED_DIR / "reference_trend_520_batch15_wust_group_image_asset_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_wust_group_image_asset_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_wust_group_image_asset_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_wust_group_image_asset_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_wust_group_image_asset_readiness.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zs.wust.edu.cn/info/1891/8181.htm"
IMAGE_URL = "https://zs.wust.edu.cn/__local/7/FF/E4/01E7F41BF63464B04DAD19DAB06_32265C85_65CDF.jpg"
IMAGE_ORIGINAL_URL = "https://zs.wust.edu.cn/__local/A/83/05/3421365D50A1B5F758133923D4F_70D28343_7AEE9.jpg"


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


def main() -> None:
    row = {
        "record_id": "reference_trend_520_batch15_wust_group_image_asset_0001",
        "row_scope": "official_group_setting_image_asset",
        "source_id": "reference_trend_520_p0_batch15_0002",
        "queue_record_id": "reference_trend_520_plan_source_queue_0152",
        "queue_rank": "152",
        "source_url": SOURCE_URL,
        "source_owner": "武汉科技大学本科招生网",
        "source_title": "武汉科技大学2025年部分省（区、市）院校专业组设置一览！",
        "raw_page_path": rel(PAGE),
        "image_url": IMAGE_URL,
        "raw_image_path": rel(IMAGE),
        "original_image_url": IMAGE_ORIGINAL_URL,
        "raw_original_image_path": rel(IMAGE_ORIGINAL),
        "image_size_bytes": IMAGE.stat().st_size if IMAGE.exists() else "",
        "original_image_size_bytes": IMAGE_ORIGINAL.stat().st_size if IMAGE_ORIGINAL.exists() else "",
        "university_code": "10488",
        "university_name": "武汉科技大学",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "unknown_until_image_transcription",
        "source_contains_group_code": "true_in_image_unparsed",
        "source_contains_plan_count": "unknown_until_image_transcription",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "special_type_detected": "unknown_until_image_transcription",
        "collector_confidence": "T2_official_group_setting_image_asset_cached_no_ocr",
        "source_packet_status": "asset_readiness_only_no_ocr",
        "intended_layer": "reference_trend_source_reachability_preview_only",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "required_resolution": "OCR_or_manual_transcription_then_QA_before_group_mapping",
        "evidence_note": "Official WUST page publishes Guangxi professional-group setting as image. Cached page and image only; no OCR/manual transcription in this run.",
    }
    fields = list(row.keys())
    write_csv(OUT, [row], fields)

    rollup = [
        {"metric": "official_page_cached_rows", "value": 1 if PAGE.exists() else 0, "note": rel(PAGE)},
        {"metric": "guangxi_image_assets_cached", "value": int(IMAGE.exists()) + int(IMAGE_ORIGINAL.exists()), "note": f"{rel(IMAGE)} | {rel(IMAGE_ORIGINAL)}"},
        {"metric": "text_rows_extracted", "value": 0, "note": "No OCR or manual transcription performed."},
        {"metric": "group_code_available_text_rows", "value": 0, "note": "Group code may be in image; not transcribed."},
        {"metric": "plan_count_available_text_rows", "value": 0, "note": "Plan count may be in image; not transcribed."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Asset readiness only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])

    qa = [
        {"check": "official_page_cached", "status": "PASS" if PAGE.exists() else "FAIL", "detail": rel(PAGE)},
        {"check": "guangxi_display_image_cached", "status": "PASS" if IMAGE.exists() else "FAIL", "detail": rel(IMAGE)},
        {"check": "guangxi_original_image_cached", "status": "PASS" if IMAGE_ORIGINAL.exists() else "FAIL", "detail": rel(IMAGE_ORIGINAL)},
        {"check": "no_ocr_or_manual_transcription", "status": "PASS", "detail": "Image assets cached only."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]
    write_csv(QA_OUT, qa, ["check", "status", "detail"])

    exclusion = [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "exclusion_reason": "image_asset_not_transcribed_or_QA_accepted",
            "next_action": "request OCR/manual transcription approval or find official text/PDF table",
            "asset_path": row["raw_original_image_path"],
        }
    ]
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "exclusion_reason", "next_action", "asset_path"])

    DOC_OUT.write_text(
        "\n".join(
            [
                "# reference_trend_520 batch15 WUST group image asset readiness",
                "",
                f"Generated: {date.today().isoformat()}",
                "",
                "## Scope",
                "",
                "武汉科技大学官方 2025 院校专业组设置页已缓存，广西图片资产已落地。"
                "本轮不做 OCR 或人工转录，只记录 source reachability / asset readiness。",
                "",
                "## Result",
                "",
                f"- Official source URL: {SOURCE_URL}",
                f"- Cached page: `{rel(PAGE)}`",
                f"- Cached image: `{rel(IMAGE)}`",
                f"- Cached original image: `{rel(IMAGE_ORIGINAL)}`",
                "- Text rows extracted: 0",
                "- Reference trend pool eligible rows: 0",
                "- Canonical/ML entry: false",
                "",
                "## Outputs",
                "",
                f"- `{rel(OUT)}`",
                f"- `{rel(ROLLUP_OUT)}`",
                f"- `{rel(QA_OUT)}`",
                f"- `{rel(EXCLUSION_OUT)}`",
                "",
                "## Gate Boundary",
                "",
                "该来源可能包含广西专业组设置与组内信息，但目前仍是图片资产。必须经过 OCR/人工转录及 QA 后，"
                "才能进入 group mapping workbench；不得直接写入 reference_trend_pool、canonical 或 ML。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    marker = "## 72. 2026-05-16 batch15 武汉科技大学 group image asset readiness"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增武汉科技大学 batch15 group image asset readiness：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 院校专业组设置页已缓存，广西对应展示图和原图均已落地。该来源是 group mapping 的强候选，但目前仍为图片资产。

准入边界：本轮不做 OCR/人工转录，不提取文本行，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步需要 OCR/人工转录批准，或另找官方文本/PDF 表格。
""",
    )


if __name__ == "__main__":
    main()
