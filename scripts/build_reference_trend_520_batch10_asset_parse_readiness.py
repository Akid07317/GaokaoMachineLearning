#!/usr/bin/env python3
"""Assess batch-10 cached official assets for safe parse readiness.

This script does not parse data into the reference pool. It records which
cached official assets need PDF parsing, OCR/image parsing, API/form drilldown,
or manual approval before a structured source-packet parse can happen.
"""

from __future__ import annotations

import csv
import html
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch10_official"

OUT = SEED_DIR / "reference_trend_520_batch10_asset_parse_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch10_asset_parse_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch10_asset_parse_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch10_asset_parse_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch10_asset_parse_readiness.md"
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


def pdf_observation(path: Path) -> str:
    if not path.exists():
        return "pdf_not_cached"
    data = path.read_bytes()
    return "; ".join(
        [
            "pdf_cached",
            f"bytes={len(data)}",
            f"streams={data.count(b'stream')}",
            f"flate_decode={data.count(b'FlateDecode')}",
            f"image_markers={data.count(b'/Image')}",
            f"text_markers={data.count(b'/ToUnicode') + data.count(b'/Font')}",
        ]
    )


def extract_image_url(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    images = re.findall(r"<img[^>]+>", text)
    # Batch10 source inspection identified this local image id as the Guangxi
    # plan panel. Prefer it over the page's first image, which can be unrelated.
    for image in images:
        if "AB414C4D0A533B79182D1A74644AAC32" in image or "A/B4/14/C4D0A533" in image:
            match = re.search(r'data-src="([^"]*mmbiz[^"]+)"', image)
            if match:
                return html.unescape(match.group(1))
            match = re.search(r'orisrc="([^"]*mmbiz[^"]+)"', image)
            if match:
                return html.unescape(match.group(1))
    match = re.search(r'data-src="([^"]*mmbiz[^"]+)"', text)
    if match:
        return html.unescape(match.group(1))
    match = re.search(r'orisrc="([^"]*mmbiz[^"]+)"', text)
    return html.unescape(match.group(1)) if match else ""


def base(row: dict[str, object]) -> dict[str, object]:
    common = {
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "qa_status": "hold_before_source_packet_parse",
    }
    common.update(row)
    return common


def build_rows() -> list[dict[str, object]]:
    nxmu_pdf = RAW_DIR / "nxmu_2025_plan.pdf"
    nxmu_page = RAW_DIR / "nxmu_2025_plan_page.html"
    sdupsl_page = RAW_DIR / "sdupsl_2025_plan.html"
    nxu_portal = RAW_DIR / "nxu_plan_portal.html"
    tjfsu_files = [
        RAW_DIR / "tjfsu_2025_charter.html",
        RAW_DIR / "tjfsu_plan_index.html",
    ]

    rows = [
        base(
            {
                "record_id": "reference_trend_520_batch10_asset_ready_0001",
                "queue_record_id": "reference_trend_520_plan_source_queue_0070",
                "queue_rank": "70",
                "university_code": "10752",
                "university_name": "宁夏医科大学",
                "asset_type": "official_pdf_plan_cached",
                "source_url": "https://www.nxmu.edu.cn/zsxxw/info/1049/2714.htm",
                "raw_file_path": rel(nxmu_pdf),
                "asset_size_bytes": file_size(nxmu_pdf),
                "asset_observation": pdf_observation(nxmu_pdf),
                "source_contains_group_code": "unknown_until_pdf_parse",
                "source_contains_plan_count": "true_in_pdf_unparsed",
                "parse_readiness_status": "cached_pdf_parser_unavailable_hold",
                "required_tool_or_route": "pdf_text_parser_or_audited_pdf_render_ocr",
                "requires_network": "false",
                "requires_manual_approval": "false_if_local_pdf_parser_available",
                "next_action": "install/use approved PDF parser or render/OCR route; filter Guangxi本科普通批物理类 rows only",
                "evidence_note": f"Plan page also cached at {rel(nxmu_page)}. Local environment currently lacks pdftotext/pypdf/pdfplumber/fitz.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch10_asset_ready_0002",
                "queue_record_id": "reference_trend_520_plan_source_queue_0075",
                "queue_rank": "75",
                "university_code": "14100",
                "university_name": "山东政法学院",
                "asset_type": "official_html_embedded_plan_image",
                "source_url": "https://zs.sdupsl.edu.cn/info/1006/8552.htm",
                "raw_file_path": rel(sdupsl_page),
                "asset_size_bytes": file_size(sdupsl_page),
                "asset_observation": "cached_html_contains_guangxi_plan_image_reference",
                "extracted_asset_url": extract_image_url(sdupsl_page),
                "source_contains_group_code": "unknown_until_image_parse",
                "source_contains_plan_count": "true_in_embedded_image_unparsed",
                "parse_readiness_status": "guangxi_image_url_extracted_ocr_unavailable_hold",
                "required_tool_or_route": "audited_image_download_plus_ocr_or_manual_transcription",
                "requires_network": "true_for_remote_image_fetch",
                "requires_manual_approval": "true_for_image_download_or_browser_ocr_route",
                "next_action": "with approval, fetch/render embedded official image and OCR/transcribe Guangxi rows into parse preview",
                "evidence_note": "The official page stores the Guangxi plan as an embedded mmbiz image, not a local HTML table.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch10_asset_ready_0003",
                "queue_record_id": "reference_trend_520_plan_source_queue_0071",
                "queue_rank": "71",
                "university_code": "10749",
                "university_name": "宁夏大学",
                "asset_type": "official_parameterized_plan_portal_cached",
                "source_url": "http://zscx.nxu.edu.cn/zsw/zsjh.html",
                "raw_file_path": rel(nxu_portal),
                "asset_size_bytes": file_size(nxu_portal),
                "asset_observation": "portal_html_cached; province/year parameters or backend endpoint not yet resolved",
                "source_contains_group_code": "unknown_until_endpoint_parse",
                "source_contains_plan_count": "unknown_until_endpoint_parse",
                "parse_readiness_status": "parameterized_portal_cached_needs_api_or_form_drilldown",
                "required_tool_or_route": "static_js_endpoint_inspection_or_approved_form_replay",
                "requires_network": "true_if_endpoint_probe_needed",
                "requires_manual_approval": "true_for_form_or_browser_replay",
                "next_action": "inspect cached portal JS first; if endpoint requires live form replay, request approval before probing",
                "evidence_note": "Official portal and charter are cached, but no structured Guangxi rows are accepted yet.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch10_asset_ready_0004",
                "queue_record_id": "reference_trend_520_plan_source_queue_0067|reference_trend_520_plan_source_queue_0068",
                "queue_rank": "67|68",
                "university_code": "10068",
                "university_name": "天津外国语大学",
                "asset_type": "official_plan_index_and_charter_context",
                "source_url": "https://zsb.tjfsu.edu.cn/zsjh.htm",
                "raw_file_path": "|".join(rel(path) for path in tjfsu_files if path.exists()),
                "asset_size_bytes": "|".join(file_size(path) for path in tjfsu_files if path.exists()),
                "asset_observation": "cached_context_no_structured_guangxi_rows",
                "source_contains_group_code": "false",
                "source_contains_plan_count": "false",
                "parse_readiness_status": "cached_context_no_structured_guangxi_rows_hold",
                "required_tool_or_route": "find_official_province_plan_attachment_or_endpoint",
                "requires_network": "true_for_further_source_discovery",
                "requires_manual_approval": "true_if_form_or_browser_replay_needed",
                "next_action": "continue first-party plan source discovery; do not parse charter as plan data",
                "evidence_note": "Official context supports source identity only; it is not a plan-row source packet.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch10_asset_ready_0005",
                "queue_record_id": "reference_trend_520_plan_source_queue_0065",
                "queue_rank": "65",
                "university_code": "13212",
                "university_name": "大连医科大学中山学院",
                "asset_type": "official_plan_url_tls_blocked_not_cached",
                "source_url": "https://recruit.dmuzs.edu.cn/NewsDetail/5973426.html",
                "raw_file_path": "",
                "asset_size_bytes": "",
                "asset_observation": "terminal_cache_failed_certificate_verification",
                "source_contains_group_code": "unknown_until_cached",
                "source_contains_plan_count": "true_in_search_snippet_unparsed",
                "parse_readiness_status": "tls_blocked_no_local_asset_hold",
                "required_tool_or_route": "approved_browser_or_certificate_audited_retry",
                "requires_network": "true",
                "requires_manual_approval": "true",
                "next_action": "ask before any TLS bypass/browser retry; otherwise keep in reachability backoff",
                "evidence_note": "No unsafe TLS bypass used; no local structured source exists.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch10_asset_ready_0006",
                "queue_record_id": "reference_trend_520_plan_source_queue_0074",
                "queue_rank": "74",
                "university_code": "10361",
                "university_name": "安徽理工大学",
                "asset_type": "official_candidate_404_not_cached",
                "source_url": "",
                "raw_file_path": "",
                "asset_size_bytes": "",
                "asset_observation": "official_candidate_page_returned_404_in_batch10_discovery",
                "source_contains_group_code": "unknown",
                "source_contains_plan_count": "unknown",
                "parse_readiness_status": "no_parse_asset_hold",
                "required_tool_or_route": "renewed_first_party_source_discovery",
                "requires_network": "true",
                "requires_manual_approval": "false_for_normal_search",
                "next_action": "retry official source discovery in later batch; do not infer plan rows from 404 candidate",
                "evidence_note": "Kept out of intake preview until a first-party asset is found.",
            }
        ),
    ]
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["parse_readiness_status"]) for row in rows)
    by_route = Counter(str(row["required_tool_or_route"]) for row in rows)
    rollup = [
        {"metric": "asset_readiness_rows", "value": len(rows), "note": "Batch10 cached/backoff assets assessed."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Readiness only; no parse accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year rows opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "ML/canonical remains closed."},
        {"metric": "requires_manual_approval_rows", "value": sum(str(row["requires_manual_approval"]).startswith("true") for row in rows), "note": "Routes involving remote image/browser/form/TLS need approval."},
    ]
    rollup.extend({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items()))
    rollup.extend({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(by_route.items()))
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
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
            "check": "manual_approval_routes_flagged",
            "status": "PASS" if any(str(row["requires_manual_approval"]).startswith("true") for row in rows) else "WARN",
            "detail": "Remote image/TLS/form routes are explicitly held for approval.",
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
        "# Reference Trend 520 Batch10 Asset Parse Readiness",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: assess batch10 cached/backoff official assets before any structured source-packet parse.",
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
            "- This is a source readiness packet only.",
            "- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` for every row.",
            "- Remote image fetch, TLS retry, browser/form replay, or OCR route remains approval-gated.",
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

    marker = "## 43. 2026-05-16 batch10 asset parse readiness"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch10 asset parse readiness 预览：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：宁夏医科大学官方 PDF 已缓存，但本地缺少 PDF text parser；山东政法学院官方页面已提取广西计划嵌入图片 URL，但远程图片/OCR 需审批；宁夏大学官方计划门户已缓存但还需 API/form drilldown；天津外国语大学仅有官方上下文，未暴露结构化广西计划行；大连医科大学中山学院 TLS 阻塞、安徽理工大学候选页 404 均保留在 backoff。

准入边界：本轮只生成 asset readiness/exclusion，不解析入 reference_trend_pool；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮若无 PDF parser/OCR/browser/form 批准，应继续后续 P0 官方来源发现批次。
""",
    )


if __name__ == "__main__":
    main()
