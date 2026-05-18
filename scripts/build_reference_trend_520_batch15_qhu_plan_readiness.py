#!/usr/bin/env python3
"""Record Qinghai University batch15 plan-page readiness/backoff.

The official Qinghai University page is cacheable and points to a third-party
Eqxiu poster for the 2025 plan. The cached first-party page does not expose
structured Guangxi physical ordinary-batch rows, so this keeps the candidate in
source reachability / manual approval territory until a browser/OCR route is
approved and audited.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend"

QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"
RAW_HTML = RAW_DIR / "batch15_qhu_2025_plan_official_page.html"

OUT = SEED_DIR / "reference_trend_520_batch15_qhu_plan_readiness_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_qhu_plan_readiness_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_qhu_plan_readiness_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_qhu_plan_readiness_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_qhu_plan_readiness.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

OFFICIAL_URL = "https://zsw.qhu.edu.cn/zsxx/zszc/92a9bb561a4e4253a01988aec41e7333.htm"
EQXIU_URL = "https://s.eqxiu.com/s/yHplm9Zh?bt=yxy&eip=true"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "carry_forward_queue_ranks",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_url",
    "source_title",
    "source_owner",
    "source_role",
    "source_type",
    "terminal_cache_status",
    "raw_file_path",
    "html_bytes",
    "external_url",
    "external_route_status",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "structured_guangxi_physical_rows_found",
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


def html_text() -> str:
    if not RAW_HTML.exists():
        return ""
    return RAW_HTML.read_text(encoding="utf-8", errors="replace")


def queue_context() -> tuple[str, str]:
    qhu_rows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10743"]
    batch15_rows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10743"]
    current_ranks = "|".join(sorted({row.get("queue_rank", "") for row in batch15_rows if row.get("queue_rank")}))
    carry_forward = "|".join(sorted({row.get("queue_rank", "") for row in qhu_rows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qhu_rows if row.get("record_id")}))
    return queue_ids, current_ranks or "164", carry_forward


def base_row() -> dict[str, object]:
    queue_ids, current_ranks, carry_forward = queue_context()
    html = html_text()
    has_html = bool(html)
    has_eqxiu = "s.eqxiu.com" in html or "yHplm9Zh" in html
    has_guangxi = "广西" in html
    has_physics = "物理" in html
    external = next((match.group(0).replace("&amp;", "&") for match in re.finditer(r"https://s\.eqxiu\.com/s/[^\"]+", html)), "")
    if external and " " in external:
        external = external.split()[0]

    return {
        "queue_record_id": queue_ids,
        "queue_rank": current_ranks,
        "carry_forward_queue_ranks": carry_forward,
        "university_code": "10743",
        "university_name": "青海大学",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_owner": "青海大学本科招生网",
        "terminal_cache_status": "cached_first_party_official_page" if has_html else "official_page_not_cached",
        "raw_file_path": rel(RAW_HTML) if RAW_HTML.exists() else "",
        "html_bytes": RAW_HTML.stat().st_size if RAW_HTML.exists() else 0,
        "external_url": external or EQXIU_URL if has_eqxiu else "",
        "source_contains_group_code": "false",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "source_contains_plan_count": "false_for_static_guangxi_physical_rows",
        "structured_guangxi_physical_rows_found": 0,
        "collector_confidence": "T2_first_party_page_cached_external_poster_required" if has_html else "T2_first_party_page_discovered_cache_missing",
        "requires_network": "false_for_cached_official_page_true_for_external_poster_if_approved",
        "requires_manual_approval": "true_for_external_poster_browser_or_ocr_route",
        "eligible_for_intake_preview": "false_until_external_poster_render_parse_and_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_source_readiness_only_not_32_school_decision_pool",
        "evidence_note": (
            "Cached official page contains Eqxiu poster link but no static Guangxi/physical structured rows. "
            f"html_contains_guangxi={has_guangxi}; html_contains_physics={has_physics}; html_contains_eqxiu={has_eqxiu}."
        ),
    }


def main() -> None:
    common = base_row()
    rows: list[dict[str, object]] = [
        {
            **common,
            "record_id": "reference_trend_520_batch15_qhu_plan_readiness_0001",
            "source_url": OFFICIAL_URL,
            "source_title": "青海大学2025年招生计划",
            "source_role": "first_party_official_plan_landing_page",
            "source_type": "official_html_landing_page",
            "external_route_status": "points_to_eqxiu_poster_but_static_page_has_no_table_rows",
            "source_packet_status": "official_page_cached_no_structured_rows",
            "next_action": "Do not intake; use cached official page as source-chain evidence and wait for approved external poster browser/OCR route.",
        },
        {
            **common,
            "record_id": "reference_trend_520_batch15_qhu_plan_readiness_0002",
            "source_url": common.get("external_url") or EQXIU_URL,
            "source_title": "青海大学2025年招生计划 external poster",
            "source_role": "external_poster_referenced_by_first_party_page",
            "source_type": "external_dynamic_poster",
            "terminal_cache_status": "not_cached_by_terminal_in_this_run",
            "raw_file_path": "",
            "html_bytes": 0,
            "external_route_status": "requires_approved_browser_render_or_manual_OCR_before_any_structured_extraction",
            "source_packet_status": "external_poster_backoff_pending_manual_approval",
            "next_action": "If user approves, render/capture Eqxiu poster in browser or perform OCR/manual transcription, then isolate Guangxi physical ordinary rows with QA.",
        },
    ]

    rollup_rows = [
        {"metric": "qhu_readiness_rows", "value": len(rows), "note": "Official landing page plus external poster route."},
        {"metric": "official_page_cached_rows", "value": 1 if RAW_HTML.exists() else 0, "note": rel(RAW_HTML) if RAW_HTML.exists() else ""},
        {"metric": "external_poster_routes", "value": 1, "note": common.get("external_url") or EQXIU_URL},
        {"metric": "structured_guangxi_physical_rows_found", "value": 0, "note": "No static rows in cached first-party HTML."},
        {"metric": "manual_approval_required_rows", "value": 1, "note": "Eqxiu browser/OCR/manual transcription route."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Backoff only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No row-level plan/rank match."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_page_cached",
            "status": "PASS" if RAW_HTML.exists() else "FAIL",
            "detail": rel(RAW_HTML) if RAW_HTML.exists() else "No cached first-party HTML.",
        },
        {
            "check": "first_party_to_external_chain_recorded",
            "status": "PASS" if common.get("external_url") else "WARN",
            "detail": common.get("external_url") or "No Eqxiu URL detected in cached HTML.",
        },
        {
            "check": "no_static_guangxi_physical_rows_claimed",
            "status": "PASS",
            "detail": "structured_guangxi_physical_rows_found=0 and eligible_for_intake_preview=false.",
        },
        {
            "check": "manual_route_isolated",
            "status": "PASS",
            "detail": "External poster requires approved browser/OCR/manual route before extraction.",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS",
            "detail": "reference_trend_pool_eligible=false; canonical_ml_entry_open=false.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 Qinghai University Plan Readiness

Generated: {date.today().isoformat()}

Purpose: preserve the 青海大学 batch15 2025 plan source chain without promoting
it into source-packet intake, reference_trend_pool, canonical, ML, or the
32-school decision_pool.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Evidence Summary

- First-party official page cached: `{RAW_HTML.relative_to(ROOT) if RAW_HTML.exists() else "not cached"}`
- Official URL: `{OFFICIAL_URL}`
- The cached official page title is 青海大学2025年招生计划 and it references an
  external Eqxiu poster: `{common.get("external_url") or EQXIU_URL}`.
- The static first-party HTML does not expose structured 广西/物理/院校专业组
  plan rows, minimum score, minimum rank, or group code.

## Boundary

All rows remain `eligible_for_intake_preview=false`,
`reference_trend_pool_eligible=false`, `calibration_eligible=false`, and
`canonical_ml_entry_open=false`.

Next safe step: wait for approval before using browser render, OCR, or manual
transcription on the external poster. If approved, extract only auditable
广西物理类本科普通批 rows into a new preview/QA layer.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 62. 2026-05-16 batch15 青海大学 plan readiness/backoff"
    handoff_content = f"""

{marker}

已新增青海大学 batch15 plan readiness/backoff：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：青海大学第一方官方 2025 招生计划页已缓存，页面正文只暴露外部 Eqxiu 海报入口；静态 HTML 没有可直接入库的广西物理类本科普通批院校专业组计划行、最低分、最低位次或专业组代码。

准入边界：本轮只做 source-chain/readiness/backoff，不做浏览器渲染、OCR 或人工转录；不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步若用户批准，可对 Eqxiu 海报执行浏览器态截图/OCR/人工转录，并单独生成 preview/QA。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
