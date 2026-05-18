#!/usr/bin/env python3
"""Record Xihua University batch14 official-source reachability/backoff.

The official site is visible through web indexing, but terminal caching hit
server-side precondition/connectivity blocks and no static 2025 Guangxi
ordinary physical plan rows were found. This keeps the candidate out of
reference-trend intake/canonical/ML while preserving auditable next steps.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

OUT = SEED_DIR / "reference_trend_520_batch14_xhu_web_reachability_backoff_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch14_xhu_web_reachability_backoff_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch14_xhu_web_reachability_backoff_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch14_xhu_web_reachability_backoff_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch14_xhu_web_reachability_backoff.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "source_title",
    "source_owner",
    "published_date",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_role",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "terminal_cache_status",
    "web_evidence_status",
    "raw_file_path",
    "evidence_note",
    "collector_confidence",
    "source_packet_status",
    "requires_network",
    "requires_manual_approval",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


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


def boundary(next_action: str) -> dict[str, str]:
    return {
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false_for_guangxi_group_rows",
        "raw_file_path": "",
        "requires_network": "false_for_current_record_true_for_next_retry",
        "requires_manual_approval": "true_if_browser_header_cookie_or_manual_plan_lookup_is_used",
        "eligible_for_intake_preview": "false_no_static_2025_guangxi_physical_plan_rows",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "next_action": next_action,
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_source_reachability_only_not_32_school_decision_pool",
    }


def main() -> None:
    rows: list[dict[str, object]] = [
        {
            **boundary(
                "Use this as policy/context only; do not infer Guangxi plan rows. "
                "Continue only if an exact 2025 Guangxi plan URL or approved browser/header route is available."
            ),
            "record_id": "reference_trend_520_batch14_xhu_web_backoff_0001",
            "queue_record_id": "reference_trend_520_plan_source_queue_0136|reference_trend_520_plan_source_queue_0209",
            "queue_rank": "136|209",
            "university_code": "10623",
            "university_name": "西华大学",
            "source_url": "https://zb.xhu.edu.cn/72/65/c7906a225893/page.htm",
            "source_title": "西华大学2025年本科招生章程",
            "source_owner": "西华大学本科招生信息网",
            "published_date": "2025-05-09",
            "year": "2025",
            "source_role": "official_2025_policy_context_no_structured_plan_rows",
            "terminal_cache_status": "curl_not_retried_for_this_page_in_script; direct site/article curl attempts returned 412_or_ssl_empty_reply",
            "web_evidence_status": "official_page_visible_via_web_index",
            "evidence_note": "The 2025 charter says province/major plans are subject to provincial admissions authorities; it does not publish Guangxi group plan rows.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_context_found_no_source_packet_rows",
        },
        {
            **boundary(
                "Historical context only. If 2025 equivalent appears, cache and parse it; otherwise keep out of source-packet intake."
            ),
            "record_id": "reference_trend_520_batch14_xhu_web_backoff_0002",
            "queue_record_id": "reference_trend_520_plan_source_queue_0136|reference_trend_520_plan_source_queue_0209",
            "queue_rank": "136|209",
            "university_code": "10623",
            "university_name": "西华大学",
            "source_url": "https://zb.xhu.edu.cn/33/fd/c7892a209917/page.htm",
            "source_title": "西华大学2024年本科招生计划公布！",
            "source_owner": "西华大学本科招生信息网",
            "published_date": "2024-06-22",
            "year": "2024",
            "source_role": "official_historical_plan_announcement_no_static_guangxi_rows",
            "terminal_cache_status": "curl_http1_1_direct_article_returned_412_precondition_failed",
            "web_evidence_status": "official_page_visible_via_web_index",
            "evidence_note": "The 2024 official announcement gives aggregate plan context and points to the admissions site/e-guide, but the web text does not expose Guangxi physical ordinary group rows.",
            "collector_confidence": "T3_historical_context_only_no_structured_plan_rows",
            "source_packet_status": "historical_context_backoff_only",
        },
        {
            **boundary(
                "Do not repeat terminal curl on the same portal URL. Retry only with an exact 2025 Guangxi plan detail URL or approved browser/header/cookie route."
            ),
            "record_id": "reference_trend_520_batch14_xhu_web_backoff_0003",
            "queue_record_id": "reference_trend_520_plan_source_queue_0136|reference_trend_520_plan_source_queue_0209",
            "queue_rank": "136|209",
            "university_code": "10623",
            "university_name": "西华大学",
            "source_url": "https://zb.xhu.edu.cn/",
            "source_title": "西华大学本科招生信息网",
            "source_owner": "西华大学本科招生信息网",
            "published_date": "",
            "year": "2025",
            "source_role": "official_portal_with_plan_navigation_but_no_cached_rows",
            "terminal_cache_status": "curl_root_returned_412; zhaosheng_alias_https_ssl_error; zhaosheng_alias_http_empty_reply",
            "web_evidence_status": "official_portal_visible_via_web_index_with_admission_plan_navigation",
            "evidence_note": "The official portal/navigation exists, but current safe fetch path did not expose a structured 2025 Guangxi plan page.",
            "collector_confidence": "T2_official_portal_reachable_by_index_but_terminal_cache_blocked",
            "source_packet_status": "official_portal_backoff_pending_exact_detail_or_browser_route",
        },
    ]

    rollup_rows = [
        {"metric": "xhu_backoff_rows", "value": len(rows), "note": "Official XHU evidence/backoff rows."},
        {"metric": "official_2025_policy_context_rows", "value": 1, "note": "2025 charter only; no Guangxi plan rows."},
        {"metric": "historical_plan_context_rows", "value": 1, "note": "2024 aggregate announcement only."},
        {"metric": "terminal_cache_blocked_rows", "value": 2, "note": "Portal/article curl attempts hit 412/SSL/empty reply."},
        {"metric": "exact_2025_guangxi_physical_plan_rows_found", "value": 0, "note": "No usable source-packet rows."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Backoff only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No plan rows parsed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_domain_only",
            "status": "PASS",
            "detail": "All source URLs are on zb.xhu.edu.cn.",
        },
        {
            "check": "no_static_2025_guangxi_physical_plan_rows",
            "status": "PASS",
            "detail": "No row claims source-packet/intake eligibility.",
        },
        {
            "check": "terminal_fetch_blocked_recorded",
            "status": "PASS",
            "detail": "412/SSL/empty-reply terminal outcomes are recorded to avoid blind retries.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS",
            "detail": "reference_trend_pool_eligible=false for every row.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS",
            "detail": "canonical_ml_entry_open=false for every row.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch14 XHU Web Reachability Backoff

Generated: {date.today().isoformat()}

Purpose: preserve the 西华大学 batch14 official-source evidence discovered this
run without promoting it into source-packet intake, reference_trend_pool,
canonical, ML, or the 32-school decision_pool.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Evidence Summary

- Official 2025 charter found: `https://zb.xhu.edu.cn/72/65/c7906a225893/page.htm`.
  It confirms the 2025 admissions document and says province/major plans follow
  provincial admissions authorities, but it does not publish Guangxi
  院校专业组 plan rows.
- Official 2024 plan announcement found:
  `https://zb.xhu.edu.cn/33/fd/c7892a209917/page.htm`. It is useful historical
  context but only exposes aggregate/e-guide context in web text, not static
  Guangxi physical ordinary group rows.
- Official portal `https://zb.xhu.edu.cn/` exists and exposes admissions-plan
  navigation via web index, but terminal cache attempts for the portal/article
  returned 412/SSL/empty-reply outcomes. This is now a backoff state.

## Boundary

All rows remain `reference_trend_pool_eligible=false`,
`calibration_eligible=false`, and `canonical_ml_entry_open=false`.

Next safe step: do not repeat the same terminal curl URLs. Continue only if an
exact 2025 Guangxi plan detail URL is discovered, or if the user approves a
browser/header/cookie route for auditable caching.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 58. 2026-05-16 batch14 西华大学 web reachability backoff"
    handoff_content = f"""

{marker}

已新增西华大学 batch14 web reachability/backoff：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 本科招生章程和 2024 本科招生计划公告可通过网页索引确认；2025 章程只给招生计划政策边界，未发布广西物理普通批院校专业组计划行；2024 公告只保留历史/聚合计划语境。终端缓存西华大学官方入口和文章时出现 412/SSL/empty reply，已记录为 backoff，避免自动化反复硬抓。

准入边界：本轮只做 source reachability/backoff，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮应转向新的 P0/P1 候选，或在用户批准后对 SHUPL/SHOU/AHUT/XHU 执行 OCR、PDF 表格解析、浏览器态或 header/cookie 路线。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
