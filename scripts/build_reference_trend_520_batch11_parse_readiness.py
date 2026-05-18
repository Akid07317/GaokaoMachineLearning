#!/usr/bin/env python3
"""Assess batch-11 official candidates for parse readiness.

This moves batch-11 discoveries one step forward without ingesting any records:
which official assets are text-layer PDF candidates, which need local cache,
and which are approval-gated by captcha/browser/form routes.
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

OUT = SEED_DIR / "reference_trend_520_batch11_parse_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch11_parse_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch11_parse_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch11_parse_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch11_parse_readiness.md"
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
    "official_source_url",
    "official_asset_url",
    "asset_type",
    "web_access_status",
    "local_cache_status",
    "text_layer_status",
    "source_contains_guangxi_column",
    "source_contains_subject_label",
    "source_contains_group_code",
    "source_contains_plan_count",
    "special_type_detected",
    "parse_readiness_status",
    "required_tool_or_route",
    "requires_network",
    "requires_manual_approval",
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


def base(row: dict[str, object]) -> dict[str, object]:
    common = {
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_group_code": "false",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
    }
    common.update(row)
    return common


def build_rows() -> list[dict[str, object]]:
    return [
        base(
            {
                "record_id": "reference_trend_520_batch11_parse_ready_0001",
                "queue_record_id": "reference_trend_520_plan_source_queue_0076",
                "queue_rank": "76",
                "university_code": "10424",
                "university_name": "山东科技大学",
                "official_source_url": "https://zs.sdust.edu.cn/info/1042/4420.htm",
                "official_asset_url": "https://zs.sdust.edu.cn/__local/9/C5/43/9C6B02E1D7D86C60EE197EC373F_325C45C7_32086.pdf",
                "asset_type": "official_pdf_plan",
                "web_access_status": "article_and_pdf_accessible",
                "local_cache_status": "not_cached_in_local_raw_sources",
                "text_layer_status": "web_pdf_text_layer_visible",
                "source_contains_guangxi_column": "true",
                "source_contains_subject_label": "not_printed_in_table",
                "source_contains_plan_count": "true",
                "special_type_detected": "art_design_boundary|sino_foreign_cooperation|possible_general_rows",
                "parse_readiness_status": "text_pdf_candidate_ready_for_local_cache_then_parse_preview",
                "required_tool_or_route": "cache_pdf_then_table_parse_with_guangxi_column_validation",
                "requires_network": "true_for_pdf_cache",
                "requires_manual_approval": "false_for_normal_pdf_cache",
                "next_action": "cache official PDF and parse Guangxi column into source-packet preview; hold group-year calibration because source does not print group codes",
                "evidence_note": "Official PDF has a Guangxi column and text layer; examples include headers across pages and rows with art/cooperation boundary rows.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch11_parse_ready_0002",
                "queue_record_id": "reference_trend_520_plan_source_queue_0085",
                "queue_rank": "85",
                "university_code": "10577",
                "university_name": "惠州学院",
                "official_source_url": "https://zs.hzu.edu.cn/2025/0619/c4726a268719/page.htm",
                "official_asset_url": "https://zs.hzu.edu.cn/_upload/article/files/a2/fb/9de322d54859b374cdc5f4e349e8/e1e67b91-542f-4e4e-8a05-52e12e565fa5.pdf",
                "asset_type": "official_pdf_out_of_province_plan",
                "web_access_status": "article_and_pdf_accessible",
                "local_cache_status": "not_cached_in_local_raw_sources",
                "text_layer_status": "web_pdf_text_layer_visible",
                "source_contains_guangxi_column": "true",
                "source_contains_subject_label": "true_物理历史美术模特_labels_visible",
                "source_contains_plan_count": "true",
                "special_type_detected": "ordinary_physical_rows_visible|art_and_model_rows_need_isolation",
                "parse_readiness_status": "text_pdf_candidate_ready_for_local_cache_then_parse_preview",
                "required_tool_or_route": "cache_pdf_then_parse_subject_filtered_guangxi_rows",
                "requires_network": "true_for_pdf_cache",
                "requires_manual_approval": "false_for_normal_pdf_cache",
                "next_action": "cache official PDF and parse only 广西/物理 ordinary rows; isolate art/model rows before any trend use",
                "evidence_note": "Official PDF prints province columns including 广西 and subject labels including 物/理; no group code is printed.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch11_parse_ready_0003",
                "queue_record_id": "reference_trend_520_plan_source_queue_0088",
                "queue_rank": "88",
                "university_code": "10496",
                "university_name": "武汉轻工大学",
                "official_source_url": "https://xxgkw.whpu.edu.cn/zdgk1/zsksxx/zszcjtslxzsbf_fpc_fklzsjh.htm",
                "official_asset_url": "https://xxgkw.whpu.edu.cn/info/1095/3606.htm",
                "asset_type": "official_info_disclosure_plan_detail_page",
                "web_access_status": "list_page_accessible_detail_cache_miss",
                "local_cache_status": "not_cached_in_local_raw_sources",
                "text_layer_status": "unknown_until_detail_cached",
                "source_contains_guangxi_column": "unknown_until_detail_cached",
                "source_contains_subject_label": "unknown_until_detail_cached",
                "source_contains_plan_count": "true_in_list_entry_unparsed",
                "special_type_detected": "unknown_until_detail_cached",
                "parse_readiness_status": "detail_page_candidate_cache_miss_hold",
                "required_tool_or_route": "retry_normal_page_cache_or_browser_if_repeated_cache_miss",
                "requires_network": "true_for_detail_cache",
                "requires_manual_approval": "false_for_normal_retry_true_if_browser_needed",
                "next_action": "retry official detail cache; if still cache-miss, ask before browser-state route",
                "evidence_note": "Official information-disclosure list clearly links the 2025分省分专业招生计划数 entry, but the detail URL returned cache miss in this pass.",
            }
        ),
        base(
            {
                "record_id": "reference_trend_520_batch11_parse_ready_0004",
                "queue_record_id": "reference_trend_520_plan_source_queue_0079|reference_trend_520_plan_source_queue_0080",
                "queue_rank": "79|80",
                "university_code": "10566",
                "university_name": "广东海洋大学",
                "official_source_url": "https://zsjy.gdou.edu.cn/info/1175/1335.htm",
                "official_asset_url": "https://zsjy.gdou.edu.cn/system/_content/download.jsp?owner=2122669748&urltype=news.DownloadAttachUrl&wbfileid=15638990|https://zsjy.gdou.edu.cn/system/_content/download.jsp?owner=2122669748&urltype=news.DownloadAttachUrl&wbfileid=15638991",
                "asset_type": "official_pdf_attachments_captcha_gated",
                "web_access_status": "official_page_accessible_attachment_download_requires_captcha",
                "local_cache_status": "not_cached_due_to_captcha",
                "text_layer_status": "unknown_until_attachment_cached",
                "source_contains_guangxi_column": "unknown_until_attachment_cached",
                "source_contains_subject_label": "unknown_until_attachment_cached",
                "source_contains_plan_count": "true_in_attachment_unparsed",
                "special_type_detected": "unknown_until_attachment_cached",
                "parse_readiness_status": "captcha_gated_attachment_hold",
                "required_tool_or_route": "manual_download_or_approved_browser_captcha_route",
                "requires_network": "true",
                "requires_manual_approval": "true",
                "next_action": "wait for manual attachment download or explicit browser/captcha approval; do not retry terminal download",
                "evidence_note": "Both official attachment links return a captcha prompt before download.",
            }
        ),
    ]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_status = Counter(str(row["parse_readiness_status"]) for row in rows)
    by_tool = Counter(str(row["required_tool_or_route"]) for row in rows)
    rollup = [
        {"metric": "parse_readiness_rows", "value": len(rows), "note": "Batch11 official candidates only."},
        {"metric": "text_pdf_candidates", "value": sum("text_pdf_candidate" in str(row["parse_readiness_status"]) for row in rows), "note": "山东科技大学, 惠州学院."},
        {"metric": "captcha_gated_rows", "value": sum("captcha" in str(row["parse_readiness_status"]) for row in rows), "note": "广东海洋大学."},
        {"metric": "detail_cache_miss_rows", "value": sum("cache_miss" in str(row["parse_readiness_status"]) for row in rows), "note": "武汉轻工大学."},
        {"metric": "requires_manual_approval_rows", "value": sum(str(row["requires_manual_approval"]).startswith("true") for row in rows), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Readiness only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year rows opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
    ]
    rollup.extend({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items()))
    rollup.extend({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(by_tool.items()))
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "0" for row in rows) else "FAIL",
            "detail": "All rows are readiness only.",
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
            "check": "approval_gated_route_flagged",
            "status": "PASS" if any(str(row["requires_manual_approval"]).startswith("true") for row in rows) else "WARN",
            "detail": "广东海洋大学 captcha-gated attachments are held.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "queue_rank": row["queue_rank"],
            "exclusion_scope": "reference_trend_pool_and_calibration",
            "exclusion_reason": row["parse_readiness_status"],
            "required_resolution": row["next_action"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 Batch11 Parse Readiness",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: promote batch11 official source candidates from discovery to parse-readiness routing.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Findings:",
    ]
    for row in rows:
        lines.append(f"- {row['university_name']} ({row['queue_rank']}): {row['parse_readiness_status']}; next `{row['required_tool_or_route']}`.")
    lines.extend(
        [
            "",
            "Boundary:",
            "- This is readiness routing only; it does not parse plan rows into the trend pool.",
            "- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` for every row.",
            "- Any captcha/browser route remains approval-gated.",
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

    marker = "## 45. 2026-05-16 batch11 parse readiness"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch11 parse readiness 预览：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：山东科技大学与惠州学院的官方 PDF 均可见文本层，适合下一步缓存 PDF 后做 source-packet parse preview；武汉轻工大学官方列表可见 2025 分省分专业招生计划数入口，但明细页本轮 cache miss；广东海洋大学两个官方附件链接均返回验证码下载页，继续 approval-gated。

准入边界：本轮只做解析准备分流，不进入 reference_trend_pool/canonical/ML；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先缓存/解析山东科技大学和惠州学院 PDF；广东海洋等待人工附件或浏览器态批准。
""",
    )


if __name__ == "__main__":
    main()
