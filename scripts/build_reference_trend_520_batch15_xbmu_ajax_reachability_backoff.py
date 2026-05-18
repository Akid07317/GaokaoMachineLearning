#!/usr/bin/env python3
"""Record XBMU batch15 AJAX-plan reachability/backoff.

The official undergraduate admissions page exposes a plan-search UI and AJAX
endpoint shapes, but terminal access to the AJAX parameter endpoint is blocked
and the site's TLS certificate is expired. This script keeps the candidate in
source reachability/backoff and does not write reference_trend_pool, canonical,
ML, or decision_pool data.
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

QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

HTML_PATH = RAW_DIR / "xbmu_2025_plan_page.html"
PARAM_HEADERS = RAW_DIR / "xbmu_ajax_zsjh_param_headers.txt"
PARAM_BODY = RAW_DIR / "xbmu_ajax_zsjh_param_body.txt"

OUT = SEED_DIR / "reference_trend_520_batch15_xbmu_ajax_reachability_backoff_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_xbmu_ajax_reachability_backoff_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_xbmu_ajax_reachability_backoff_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_xbmu_ajax_reachability_backoff_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_xbmu_ajax_reachability_backoff.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PLAN_PAGE_URL = "https://zs.xbmu.edu.cn/static/front/xbmu/basic/html_web/zsjh.html"
PARAM_ENDPOINT = "https://zs.xbmu.edu.cn/f/ajax_zsjh_param"
DATA_ENDPOINT = "https://zs.xbmu.edu.cn/f/ajax_zsjh"

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
    "raw_html_path",
    "endpoint_url",
    "endpoint_role",
    "endpoint_probe_status",
    "endpoint_headers_path",
    "endpoint_body_path",
    "tls_status",
    "static_page_has_guangxi_filter",
    "static_page_has_plan_templates",
    "static_page_has_ajax_endpoint_shape",
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
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10742"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10742"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "159", all_ranks


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def header_status(headers: str) -> str:
    first = next((line.strip() for line in headers.splitlines() if line.startswith("HTTP/")), "")
    if not first:
        return "not_probed"
    match = re.search(r"HTTP/\S+\s+(\d+)", first)
    return f"http_{match.group(1)}" if match else first


def main() -> None:
    queue_ids, batch_rank, all_ranks = q_context()
    html = read_text(HTML_PATH)
    headers = read_text(PARAM_HEADERS)
    body = read_text(PARAM_BODY)
    status = header_status(headers)
    has_guangxi_filter = "data-value=\"广西\"" in html or ">广西<" in html
    has_templates = "zsjhTotal" in html and "zsjhList" in html and "zsjhs" in html
    has_endpoint_shape = "f/ajax_zsjh_param" in html and "f/ajax_zsjh" in html
    body_title = "页面不存在" if "页面不存在" in body else body[:40].replace("\n", " ")

    common = {
        "queue_record_id": queue_ids,
        "queue_rank": batch_rank,
        "related_queue_ranks": all_ranks,
        "university_code": "10742",
        "university_name": "西北民族大学",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_url": PLAN_PAGE_URL,
        "source_owner": "西北民族大学本科招生信息网",
        "source_title": "招生计划",
        "raw_html_path": rel(HTML_PATH) if HTML_PATH.exists() else "",
        "tls_status": "official_site_certificate_expired_terminal_cache_used_insecure_tls_for_evidence",
        "static_page_has_guangxi_filter": str(has_guangxi_filter).lower(),
        "static_page_has_plan_templates": str(has_templates).lower(),
        "static_page_has_ajax_endpoint_shape": str(has_endpoint_shape).lower(),
        "source_contains_group_code": "false_in_static_html_unknown_in_ajax",
        "source_contains_plan_count": "true_if_ajax_accessible_false_in_static_html",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "collector_confidence": "T2_official_ajax_plan_page_reachability_backoff",
        "source_packet_status": "official_ajax_plan_page_cached_endpoint_403_terminal_backoff",
        "eligible_for_intake_preview": "false_until_approved_browser_cookie_or_exported_table_route",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "requires_manual_approval": "true_for_browser_cookie_header_or_form_replay_route",
        "next_action": "Wait for approval before browser/cookie/header/form replay; alternatively find an official static PDF/table export for 2025 Guangxi physical plan rows.",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_reachability_backoff_only_not_32_school_decision_pool",
        "evidence_note": (
            f"Static official plan UI cached. has_guangxi_filter={has_guangxi_filter}; "
            f"has_templates={has_templates}; has_endpoint_shape={has_endpoint_shape}; "
            f"param_endpoint_status={status}; endpoint_body={body_title}."
        ),
    }
    rows = [
        {
            **common,
            "record_id": "reference_trend_520_batch15_xbmu_ajax_backoff_0001",
            "endpoint_url": PARAM_ENDPOINT,
            "endpoint_role": "ajax_filter_parameter_endpoint",
            "endpoint_probe_status": status,
            "endpoint_headers_path": rel(PARAM_HEADERS) if PARAM_HEADERS.exists() else "",
            "endpoint_body_path": rel(PARAM_BODY) if PARAM_BODY.exists() else "",
        },
        {
            **common,
            "record_id": "reference_trend_520_batch15_xbmu_ajax_backoff_0002",
            "endpoint_url": DATA_ENDPOINT,
            "endpoint_role": "ajax_plan_data_endpoint_shape_from_static_page_not_replayed",
            "endpoint_probe_status": "not_replayed_due_to_form/cookie_boundary_after_param_403",
            "endpoint_headers_path": "",
            "endpoint_body_path": "",
        },
    ]

    rollup_rows = [
        {"metric": "xbmu_official_plan_page_cached_rows", "value": 1 if HTML_PATH.exists() else 0, "note": rel(HTML_PATH) if HTML_PATH.exists() else ""},
        {"metric": "terminal_tls_certificate_issue_rows", "value": 1, "note": "First curl failed certificate verification; cached with -k and isolated as reachability evidence."},
        {"metric": "static_page_has_guangxi_filter", "value": int(has_guangxi_filter), "note": "Static UI filter text only."},
        {"metric": "static_page_has_plan_templates", "value": int(has_templates), "note": "zsjhTotal/zsjhList templates expose plan fields."},
        {"metric": "static_page_has_ajax_endpoint_shape", "value": int(has_endpoint_shape), "note": "f/ajax_zsjh_param and f/ajax_zsjh found in HTML."},
        {"metric": "ajax_param_terminal_status_403_rows", "value": 1 if status == "http_403" else 0, "note": rel(PARAM_HEADERS) if PARAM_HEADERS.exists() else ""},
        {"metric": "source_packet_eligible_rows", "value": 0, "note": "No structured rows fetched."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Browser/cookie/header/form route would require approval."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_plan_ui_cached",
            "status": "PASS" if HTML_PATH.exists() else "FAIL",
            "detail": rel(HTML_PATH) if HTML_PATH.exists() else "HTML missing.",
        },
        {
            "check": "static_ui_endpoint_shape_detected",
            "status": "PASS" if has_endpoint_shape and has_templates else "WARN",
            "detail": f"endpoint_shape={has_endpoint_shape}; templates={has_templates}",
        },
        {
            "check": "terminal_ajax_probe_blocked_recorded",
            "status": "PASS" if status == "http_403" else "WARN",
            "detail": f"status={status}; body={body_title}",
        },
        {
            "check": "browser_cookie_replay_not_attempted",
            "status": "PASS",
            "detail": "After 403 and TLS issue, no browser/header/cookie/form replay was performed.",
        },
        {
            "check": "no_structured_rows_claimed",
            "status": "PASS" if all(row["eligible_for_intake_preview"] == "false_until_approved_browser_cookie_or_exported_table_route" for row in rows) else "FAIL",
            "detail": "Static page exposes UI/templates only; no source-packet rows generated.",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No trend pool/canonical/ML writes.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 XBMU AJAX Reachability Backoff

Generated: {date.today().isoformat()}

Purpose: preserve 西北民族大学 official 2025 plan-search UI evidence without
performing browser/cookie/header/form replay or creating structured plan rows.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official plan UI: `{PLAN_PAGE_URL}`
- Cached HTML: `{HTML_PATH.relative_to(ROOT) if HTML_PATH.exists() else "not cached"}`
- AJAX parameter endpoint: `{PARAM_ENDPOINT}` -> `{status}`
- Static page has Guangxi filter: {has_guangxi_filter}
- Static page has plan templates/endpoints: {has_templates and has_endpoint_shape}

The static page contains the plan-search UI and AJAX endpoint shapes, but the
terminal probe for the parameter endpoint returned `{status}` with body marker
`{body_title}`. The site certificate also failed normal TLS validation, so the
HTML cache is treated as reachability evidence only.

## Boundary

No browser, cookie/header replay, or form replay was attempted. No source-packet
intake rows, `reference_trend_pool`, `canonical`, `ML`, or 32-school
decision_pool data were written. Continue only with explicit approval or with a
separate official static export/PDF/table source.
"""
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 67. 2026-05-16 batch15 西北民族大学 AJAX reachability backoff"
    handoff_content = f"""

{marker}

已新增西北民族大学 batch15 AJAX reachability/backoff：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方计划查询 UI 已缓存，静态页含广西筛选项、`zsjhTotal`/`zsjhList` 模板和 `f/ajax_zsjh_param`/`f/ajax_zsjh` endpoint 形状。终端访问参数接口返回 `{status}`，正文为 `{body_title}`；首次正常 TLS 校验失败，说明站点证书过期，后续只作为 reachability evidence 处理。

准入边界：本轮未做浏览器态、cookie/header replay 或表单 replay；不生成 source-packet rows，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步需要用户批准浏览器/会话态检查，或另找官方静态 PDF/table export。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
