#!/usr/bin/env python3
"""Assess batch-12 cached image/API assets for safe next-step readiness.

This script does not OCR images, replay forms, or parse data into the reference
trend pool. It records which official cached assets are ready for audited OCR,
manual transcription, endpoint drilldown, or browser/TLS approval.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch12_official"

OUT = SEED_DIR / "reference_trend_520_batch12_asset_api_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch12_asset_api_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch12_asset_api_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch12_asset_api_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch12_asset_api_readiness.md"
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
    "asset_type",
    "source_url",
    "raw_file_path",
    "asset_size_bytes",
    "asset_observation",
    "extracted_asset_url",
    "endpoint_or_route",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "parse_readiness_status",
    "required_tool_or_route",
    "requires_network",
    "requires_manual_approval",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
    "qa_status",
    "evidence_note",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def file_size(path: Path) -> str:
    return str(path.stat().st_size) if path.exists() else ""


def file_sizes(paths: list[Path]) -> str:
    return "|".join(file_size(path) for path in paths if path.exists())


def rels(paths: list[Path]) -> str:
    return "|".join(rel(path) for path in paths if path.exists())


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


def contains_404(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")[:3000]
    return "404 页面未找到" in text or "<title>404" in text


def extract_image_urls(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    urls = re.findall(r'<img[^>]+src="([^"]+)"', text)
    return [url for url in urls if "uploads/ueditor/image/20250609" in url or "/__local/" in url]


def base(row: dict[str, object]) -> dict[str, object]:
    common = {
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_group_code": "unknown_until_parse",
        "source_contains_plan_count": "unknown_until_parse",
        "source_contains_min_score": "unknown_until_parse",
        "source_contains_min_rank": "unknown_until_parse",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "qa_status": "hold_before_source_packet_parse",
    }
    common.update(row)
    return common


def build_rows() -> list[dict[str, object]]:
    zjou_page = RAW_DIR / "zjou_2025_guangxi_plan_score_6732.html"
    zjou_assets = [
        RAW_DIR / "zjou_guangxi_asset_1.jpg",
        RAW_DIR / "zjou_guangxi_asset_2.jpg",
    ]
    zjou_urls = extract_image_urls(zjou_page)

    cqctcm_bad = RAW_DIR / "cqctcm_2025_plan_charter.html"
    cqctcm_charter = RAW_DIR / "cqctcm_2025_charter_plan_bkzs.html"
    cqctcm_portal = RAW_DIR / "cqctcm_2025_plan_portal.html"
    cqctcm_js = [
        RAW_DIR / "cqctcm_chunk_plan.js",
        RAW_DIR / "cqctcm_chunk_commons.js",
        RAW_DIR / "cqctcm_chunk_4aed57b2.js",
    ]
    cqctcm_api = [
        RAW_DIR / "cqctcm_api_province_list_enroll_portal.json",
        RAW_DIR / "cqctcm_api_year_list_enroll_portal.json",
        RAW_DIR / "cqctcm_api_plan_guangxi_2025_enroll_portal.json",
    ]
    cqctcm_img_urls = extract_image_urls(cqctcm_charter)

    rows = [
        base(
            {
                "record_id": "reference_trend_520_batch12_asset_api_ready_0001",
                "queue_record_id": "reference_trend_520_plan_source_queue_0093|reference_trend_520_plan_source_queue_0245|reference_trend_520_plan_source_queue_0449",
                "queue_rank": "93|245|449",
                "university_code": "10340",
                "university_name": "浙江海洋大学",
                "asset_type": "official_html_embedded_plan_score_images_cached",
                "source_url": "https://zs.zjou.edu.cn/info/1346/6732.htm",
                "raw_file_path": rels([zjou_page, *zjou_assets]),
                "asset_size_bytes": file_sizes([zjou_page, *zjou_assets]),
                "asset_observation": "official_guangxi_plan_score_page_cached_with_two_large_jpeg_assets",
                "extracted_asset_url": "|".join(zjou_urls),
                "source_contains_group_code": "unknown_until_image_parse",
                "source_contains_plan_count": "true_in_image_unparsed",
                "source_contains_min_score": "true_in_image_unparsed",
                "source_contains_min_rank": "true_in_image_unparsed",
                "parse_readiness_status": "official_image_assets_cached_ocr_or_manual_parse_needed",
                "required_tool_or_route": "audited_image_ocr_or_manual_transcription",
                "requires_network": "false",
                "requires_manual_approval": "true_for_ocr_or_manual_transcription",
                "next_action": "OCR or manually transcribe official images, then keep results in source-packet parse preview until group-code QA passes.",
                "evidence_note": "Official page title is 2025年招生计划及2024年录取分数（广西）; cached images are not auto-parsed.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch12_asset_api_ready_0002",
                "queue_record_id": "reference_trend_520_plan_source_queue_0095|reference_trend_520_plan_source_queue_0316",
                "queue_rank": "95|316",
                "university_code": "10343",
                "university_name": "温州医科大学",
                "asset_type": "official_plan_url_tls_blocked_not_cached",
                "source_url": "https://recruit.wmu.edu.cn/bkzn/zsjh.htm",
                "raw_file_path": "",
                "asset_size_bytes": "",
                "asset_observation": "terminal_cache_failed_ssl_error_syscall",
                "parse_readiness_status": "tls_blocked_no_local_asset_hold",
                "required_tool_or_route": "approved_browser_or_alternate_tls_route",
                "requires_network": "true",
                "requires_manual_approval": "true",
                "next_action": "Ask before browser/TLS retry; without approval keep in source reachability backoff.",
                "evidence_note": "No local official plan asset exists from this round; no unsafe TLS bypass used.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch12_asset_api_ready_0003",
                "queue_record_id": "reference_trend_520_plan_source_queue_0106",
                "queue_rank": "106",
                "university_code": "14830",
                "university_name": "重庆中医药学院",
                "asset_type": "official_charter_images_and_plan_portal_cached_endpoint_404",
                "source_url": "https://bkzs.cqctcm.edu.cn/guide/detail/id/289.html|https://bkzs.cqctcm.edu.cn/guide/plan",
                "raw_file_path": rels([cqctcm_bad, cqctcm_charter, cqctcm_portal, *cqctcm_js, *cqctcm_api]),
                "asset_size_bytes": file_sizes([cqctcm_bad, cqctcm_charter, cqctcm_portal, *cqctcm_js, *cqctcm_api]),
                "asset_observation": "correct_bkzs_charter_and_plan_portal_cached; wrong_legacy_url_and_enroll_portal_api_attempts_returned_404",
                "extracted_asset_url": "|".join(cqctcm_img_urls),
                "endpoint_or_route": "/guide/plan plus JS/static chunks; attempted /enroll-portal/api/v1/plan/getProvinceList, /getYearList, /plan?province=广西&year=2025",
                "source_contains_group_code": "unknown_until_image_or_endpoint_parse",
                "source_contains_plan_count": "true_in_charter_images_unparsed_or_endpoint_table_if_unlocked",
                "source_contains_min_score": "false_for_plan_portal",
                "source_contains_min_rank": "false_for_plan_portal",
                "parse_readiness_status": "official_portal_cached_endpoint_shape_found_api_404_hold",
                "required_tool_or_route": "static_js_endpoint_review_or_approved_browser_form_replay",
                "requires_network": "true_if_endpoint_or_image_fetch_needed",
                "requires_manual_approval": "true_for_browser_form_header_or_image_ocr_route",
                "next_action": "Do not reuse 404 legacy URL; either OCR cached charter plan images after approval or inspect form/browser route for the plan portal.",
                "evidence_note": f"Charter page exposes {len(cqctcm_img_urls)} 2025 plan image URLs; enroll-portal API files are 404={all(contains_404(path) for path in cqctcm_api)}.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch12_asset_api_ready_0004",
                "queue_record_id": "reference_trend_520_plan_source_queue_0107",
                "queue_rank": "107",
                "university_code": "11799",
                "university_name": "重庆工商大学",
                "asset_type": "official_context_only_not_cached_this_round",
                "source_url": "",
                "raw_file_path": "",
                "asset_size_bytes": "",
                "asset_observation": "batch12_discovery_kept_as_context_or_score_only; no plan source cached in this asset pass",
                "source_contains_group_code": "unknown",
                "source_contains_plan_count": "unknown",
                "source_contains_min_score": "unknown",
                "source_contains_min_rank": "unknown",
                "parse_readiness_status": "no_parse_asset_hold",
                "required_tool_or_route": "renewed_first_party_plan_source_discovery",
                "requires_network": "true",
                "requires_manual_approval": "false_for_normal_search",
                "next_action": "Continue first-party source discovery in a later batch; do not infer plan rows from context-only evidence.",
                "evidence_note": "Included to keep queue rank 107 state explicit after nearby batch12 asset work.",
            }
        ),
    ]
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["parse_readiness_status"]) for row in rows)
    by_route = Counter(str(row["required_tool_or_route"]) for row in rows)
    return [
        {"metric": "asset_api_readiness_rows", "value": len(rows), "note": "Batch12 cached/backoff assets assessed."},
        {"metric": "cached_official_asset_rows", "value": sum(bool(row["raw_file_path"]) for row in rows), "note": "Rows with at least one local official/cache file."},
        {"metric": "image_asset_rows", "value": sum("image" in str(row["asset_type"]) for row in rows), "note": "Rows requiring OCR/manual image parse."},
        {"metric": "tls_blocked_rows", "value": sum("tls_blocked" in str(row["parse_readiness_status"]) for row in rows), "note": "Held for approval before retry."},
        {"metric": "endpoint_shape_found_rows", "value": sum("endpoint" in str(row["parse_readiness_status"]) for row in rows), "note": "Portal/API route identified but not accepted."},
        {"metric": "endpoint_data_rows", "value": 0, "note": "The attempted 重庆中医药 API route returned 404 HTML, not data JSON."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Readiness only; no source-packet parse accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year rows opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "ML/canonical remains closed."},
        {"metric": "requires_manual_approval_rows", "value": sum(str(row["requires_manual_approval"]).startswith("true") for row in rows), "note": "OCR/browser/form/TLS routes are approval-gated."},
        *({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items())),
        *({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(by_route.items())),
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    zjou = next(row for row in rows if row["university_name"] == "浙江海洋大学")
    cqctcm = next(row for row in rows if row["university_name"] == "重庆中医药学院")
    return [
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "0" for row in rows) else "FAIL",
            "detail": "All rows remain source readiness only.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(str(row["canonical_ml_entry_open"]) == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML input opened.",
        },
        {
            "check": "decision_pool_boundary",
            "status": "PASS" if all("do_not_merge" in str(row["decision_pool_boundary"]) for row in rows) else "FAIL",
            "detail": "32-school decision_pool boundary preserved.",
        },
        {
            "check": "zjou_images_cached",
            "status": "PASS" if "zjou_guangxi_asset_1.jpg" in str(zjou["raw_file_path"]) and "zjou_guangxi_asset_2.jpg" in str(zjou["raw_file_path"]) else "FAIL",
            "detail": "浙江海洋 official Guangxi plan/score image assets are local, but unparsed.",
        },
        {
            "check": "cqctcm_api_404_flagged",
            "status": "PASS" if "api_404_hold" in str(cqctcm["parse_readiness_status"]) else "FAIL",
            "detail": "重庆中医药 attempted enroll-portal API route is treated as blocked 404 HTML, not as data.",
        },
        {
            "check": "manual_approval_routes_flagged",
            "status": "PASS" if any(str(row["requires_manual_approval"]).startswith("true") for row in rows) else "WARN",
            "detail": "OCR/browser/form/TLS routes are explicitly held for approval.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "exclusion_scope": "reference_trend_pool_and_calibration",
            "exclusion_reason": row["parse_readiness_status"],
            "required_resolution": row["next_action"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 Batch12 Asset/API Readiness",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: record cached official image/API assets before any OCR, form replay, or source-packet parse.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Key findings:",
    ]
    for row in rows:
        lines.append(
            f"- {row['university_name']} ({row['queue_rank']}): {row['parse_readiness_status']}; next `{row['required_tool_or_route']}`."
        )
    lines.extend(
        [
            "",
            "Boundary:",
            "- This is an asset/API readiness packet only.",
            "- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` for every row.",
            "- OCR, browser/form replay, header/cookie replay, alternate TLS route, or manual transcription remains approval-gated.",
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
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup)

    marker = "## 49. 2026-05-16 batch12 asset/API readiness"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch12 asset/API readiness 预览：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：浙江海洋大学官方广西计划/分数页与两张大图已缓存，但仍需 OCR 或人工转录；温州医科大学官方计划页 TLS 阻塞，未形成本地资产；重庆中医药学院正确 bkzs 章程页和计划门户已缓存，章程页暴露 2 张 2025 计划图片，静态计划门户可见表头，但本轮尝试的 `/enroll-portal/api/v1/plan` 相关 API 均返回 404 HTML；重庆工商大学继续保留为无可解析资产的后续发现项。

准入边界：本轮只生成 asset/API readiness、QA 和 exclusion，不做 OCR、form replay、header/cookie replay，也不解析入 reference_trend_pool；所有行 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮若无 OCR/browser/form/TLS 批准，应继续后续 P0/P1 官方来源发现或做已缓存图片的人工转录审批准备。
""",
    )


if __name__ == "__main__":
    main()
