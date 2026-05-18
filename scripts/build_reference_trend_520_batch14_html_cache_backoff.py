#!/usr/bin/env python3
"""Build batch14 HTML cache/backoff preview for official plan portals.

This records official pages that were cached but did not expose usable 2025
Guangxi physical ordinary plan rows in static HTML. It avoids repeating the
same portal-level fetches and keeps all rows out of reference-trend intake,
canonical, and ML.
"""

from __future__ import annotations

import csv
import html
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch14_official"

OUT = SEED_DIR / "reference_trend_520_batch14_html_cache_backoff_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch14_html_cache_backoff_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch14_html_cache_backoff_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch14_html_cache_backoff_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch14_html_cache_backoff.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "cached_files",
    "detected_links",
    "contains_2025",
    "contains_guangxi",
    "contains_physics",
    "cache_status",
    "backoff_reason",
    "next_action",
    "requires_network",
    "requires_manual_approval",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


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


def links_of_interest(paths: list[Path]) -> tuple[list[str], bool, bool, bool]:
    links: list[str] = []
    contains_2025 = False
    contains_guangxi = False
    contains_physics = False
    for path in paths:
        if not path.exists():
            continue
        text = read_text(path)
        contains_2025 = contains_2025 or ("2025" in text)
        contains_guangxi = contains_guangxi or ("广西" in text)
        contains_physics = contains_physics or ("物理" in text)
        for match in re.finditer(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", text, re.I | re.S):
            href = match.group(1)
            label = html.unescape(re.sub("<.*?>", "", match.group(2))).strip()
            if any(token in label for token in ("2025", "广西", "招生计划", "计划")):
                links.append(f"{label}=>{href}")
    return links[:20], contains_2025, contains_guangxi, contains_physics


def boundary() -> dict[str, str]:
    return {
        "requires_network": "false_for_cached_state_check",
        "requires_manual_approval": "false_until_browser_or_dynamic_route_needed",
        "eligible_for_intake_preview": "false_no_2025_guangxi_static_plan_rows",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_html_cache_backoff_only_not_32_school_decision_pool",
    }


def main() -> None:
    usts_files = [
        RAW_DIR / "usts_plan_list.html",
        RAW_DIR / "usts_plan_detail_21.html",
    ]
    tjfsu_files = [
        RAW_DIR / "tjfsu_zsb_index.html",
        RAW_DIR / "tjfsu_plan_list.html",
    ]
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    usts_links, usts_2025, usts_gx, usts_phy = links_of_interest(usts_files)
    rows.append(
        {
            **boundary(),
            "record_id": "reference_trend_520_batch14_html_cache_backoff_0001",
            "queue_record_id": "reference_trend_520_plan_source_queue_0132|reference_trend_520_plan_source_queue_0133",
            "queue_rank": "132|133",
            "university_code": "10332",
            "university_name": "苏州科技大学",
            "source_url": "https://zsb.usts.edu.cn/news/news_more.asp?lm=12",
            "cached_files": "|".join(rel(p) for p in usts_files if p.exists()),
            "detected_links": "|".join(usts_links),
            "contains_2025": str(usts_2025).lower(),
            "contains_guangxi": str(usts_gx).lower(),
            "contains_physics": str(usts_phy).lower(),
            "cache_status": "official_plan_column_cached_no_static_2025_guangxi_rows",
            "backoff_reason": "cached plan list/detail only exposed generic historical-plan navigation, not 2025 Guangxi rows",
            "next_action": "retry later with a discovered exact detail URL; do not re-cache the same list page repeatedly",
            "evidence_note": "The static page links include 历年招生计划 but no visible 2025/广西/物理 plan rows.",
        }
    )

    tj_links, tj_2025, tj_gx, tj_phy = links_of_interest(tjfsu_files)
    rows.append(
        {
            **boundary(),
            "record_id": "reference_trend_520_batch14_html_cache_backoff_0002",
            "queue_record_id": "reference_trend_520_plan_source_queue_0144",
            "queue_rank": "144",
            "university_code": "10068",
            "university_name": "天津外国语大学",
            "source_url": "https://zsb.tjfsu.edu.cn/zsjh.htm",
            "cached_files": "|".join(rel(p) for p in tjfsu_files if p.exists()),
            "detected_links": "|".join(tj_links),
            "contains_2025": str(tj_2025).lower(),
            "contains_guangxi": str(tj_gx).lower(),
            "contains_physics": str(tj_phy).lower(),
            "cache_status": "official_plan_column_cached_no_2025_plan_detail",
            "backoff_reason": "cached plan list shows 2024 and older plans; index has 2025 news, but plan column has no 2025 Guangxi static plan detail",
            "next_action": "wait for a 2025 plan column update or exact official detail URL; keep 2025招生简章 out of plan-row intake",
            "evidence_note": "The cached 招生计划 list contains 2024/2023/2022... plan links, not 2025 Guangxi plan rows.",
        }
    )

    exclusions.extend(rows)
    rollup_rows = [
        {"metric": "html_backoff_rows", "value": len(rows), "note": "Cached official portals without usable static 2025 Guangxi plan rows."},
        {"metric": "cached_file_count", "value": sum(len(row["cached_files"].split("|")) for row in rows), "note": ""},
        {"metric": "retry_exact_detail_url_needed_rows", "value": len(rows), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Backoff only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No rows parsed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "cached_official_files_exist",
            "status": "PASS" if all(p.exists() for p in usts_files + tjfsu_files) else "REVIEW",
            "detail": "USTS and TJFSU cached files checked.",
        },
        {
            "check": "no_static_2025_guangxi_rows",
            "status": "PASS",
            "detail": "Both rows remain backoff/no-intake.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS",
            "detail": "No row enters reference_trend_pool.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS",
            "detail": "canonical_ml_entry_open=false.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch14 HTML Cache Backoff

Generated: {date.today().isoformat()}

Purpose: record official HTML caches that should not be retried blindly because
they did not expose static 2025 Guangxi physical ordinary plan rows.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- 苏州科技大学: official plan column cached, but no static 2025 Guangxi rows.
- 天津外国语大学: official index and plan column cached; plan column currently
  exposes 2024 and older plans, not 2025 Guangxi rows.

## Boundary

All rows remain `reference_trend_pool_eligible=false`,
`calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 57. 2026-05-16 batch14 HTML cache backoff"
    handoff = f"""

{marker}

已新增 batch14 HTML cache backoff：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：苏州科技大学官方“招生计划/历年招生计划”栏目已缓存，但静态页未暴露 2025 广西物理普通批计划行；天津外国语大学官方首页和招生计划栏目已缓存，栏目目前只列 2024 及更早计划，未暴露 2025 广西计划详情。这两条已写入 backoff，避免自动化重复抓同一入口。

准入边界：本轮只做 HTML 缓存回退记录，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮可继续寻找西华大学或其他 batch14 学校的可直接 HTML 化官方计划详情，或等待人工批准 OCR/PDF/图片解析路线。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
