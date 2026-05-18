#!/usr/bin/env python3
"""Record non-211 source reachability probes for reference-trend collection.

This consolidates terminal-fetch outcomes for source-packet candidates. It is
not a scraper and does not write canonical/ML artifacts.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

TRIAGE = SEED_DIR / "reference_trend_non211_source_packet_triage_preview.csv"
REACHABILITY_OUT = REPORT_DIR / "reference_trend_non211_source_reachability.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_non211_source_reachability_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_non211_source_reachability.md"

RAW_ROOT = ROOT / "raw_data" / "reference_trend" / "non211"

FIELDS = [
    "source_reachability_rank",
    "school_key",
    "school_name",
    "candidate_url",
    "candidate_kind",
    "source_packet_priority",
    "terminal_fetch_status",
    "raw_cache_path",
    "raw_cache_bytes",
    "requires_browser_or_alternate_fetch",
    "can_write_source_packet_now",
    "can_enter_intake_without_fetch",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "triage_record_id",
    "record_id",
]

KNOWN_TIMEOUTS = {
    "http://zs.nuist.edu.cn/info/1172/2879.htm": "terminal_curl_timeout_0_bytes_after_retry",
    "http://zs.nuist.edu.cn/info/1172/2977.htm": "terminal_curl_timeout_0_bytes_after_retry",
    "http://zs.nuist.edu.cn/info/1172/2978.htm": "terminal_curl_timeout_0_bytes_after_retry",
    "http://zs.nuist.edu.cn/info/1172/2975.htm": "terminal_curl_timeout_0_bytes_after_retry",
}

RAW_PATHS = {
    "http://zs.nuist.edu.cn/info/1172/2879.htm": RAW_ROOT
    / "nanjing_xinxi_gongcheng"
    / "nuist_2024_comprehensive_plan_2879.html",
    "http://zs.nuist.edu.cn/info/1172/2977.htm": RAW_ROOT
    / "nanjing_xinxi_gongcheng"
    / "nuist_2025_jiangsu_plan_2977.html",
    "http://zs.nuist.edu.cn/info/1172/2978.htm": RAW_ROOT
    / "nanjing_xinxi_gongcheng"
    / "nuist_2025_comprehensive_plan_2978.html",
    "http://zs.nuist.edu.cn/info/1172/2975.htm": RAW_ROOT
    / "nanjing_xinxi_gongcheng"
    / "nuist_2025_atmospheric_directed_plan_2975.html",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def file_size(path: Path | None) -> int:
    if not path or not path.exists():
        return 0
    return path.stat().st_size


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for triage in read_csv(TRIAGE):
        priority = triage.get("source_packet_priority", "")
        if priority not in {"P0_score_rank_or_line_source_packet", "P1_plan_count_source_packet"}:
            continue
        url = triage.get("candidate_url", "")
        raw_path = RAW_PATHS.get(url)
        raw_bytes = file_size(raw_path)
        known_status = KNOWN_TIMEOUTS.get(url)
        if raw_bytes > 2000:
            terminal_status = "raw_cache_available"
            can_write = "true"
            needs_browser = "false"
            next_action = "parse_raw_cache_into_source_packet_preview"
        elif known_status:
            terminal_status = known_status
            can_write = "false"
            needs_browser = "true"
            next_action = "browser_or_alternate_fetch_required_before_source_packet"
        else:
            terminal_status = "not_probed_this_round"
            can_write = "false"
            needs_browser = "true"
            next_action = "probe_with_approved_method_then_write_source_packet"
        rows.append(
            {
                "source_reachability_rank": len(rows) + 1,
                "school_key": triage.get("school_key", ""),
                "school_name": triage.get("school_name", ""),
                "candidate_url": url,
                "candidate_kind": triage.get("candidate_kind", ""),
                "source_packet_priority": priority,
                "terminal_fetch_status": terminal_status,
                "raw_cache_path": str(raw_path) if raw_path else "",
                "raw_cache_bytes": raw_bytes,
                "requires_browser_or_alternate_fetch": needs_browser,
                "can_write_source_packet_now": can_write,
                "can_enter_intake_without_fetch": "false",
                "next_action": next_action,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_only_not_decision_pool",
                "triage_record_id": triage.get("record_id", ""),
                "record_id": f"reference_trend_non211_source_reachability_{len(rows) + 1:04d}",
            }
        )
    return rows


def write_doc(rows: list[dict[str, object]]) -> None:
    counts = Counter(row.get("terminal_fetch_status", "") for row in rows)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend Non-211 Source Reachability",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "非 211 P1 官方计划候选目前不能通过终端稳定落源。南京信息工程大学 4 个官方招生网计划页在本轮终端抓取中均为 0 字节超时；这些候选保留在 source reachability 层，后续需要浏览器态或其他可审计方式。",
                "",
                "## 覆盖",
                "",
                f"- checked P0/P1 candidate rows: {len(rows)}",
                f"- terminal timeout rows: {counts.get('terminal_curl_timeout_0_bytes_after_retry', 0)}",
                f"- raw cache available rows: {counts.get('raw_cache_available', 0)}",
                "- canonical/ML opened: false",
                "- decision pool expanded: false",
                "",
                "## 下一步",
                "",
                "1. 不再重复用终端 curl 抓南京信息工程大学同一批 P1 URL。",
                "2. 若用户批准浏览器态，可打开 P1 URL 并保存 raw HTML。",
                "3. 只有 raw cache 可审计且字段确认后，才写正式 source packet。",
                "4. 继续把非 211 用作 reference trend pool 来源候选，不并入 32 所 decision_pool。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(REACHABILITY_OUT, rows, FIELDS)
    counts = Counter(row.get("terminal_fetch_status", "") for row in rows)
    rollup = [
        {"metric": "checked_p0_p1_non211_candidate_rows", "value": len(rows)},
        {
            "metric": "terminal_timeout_0_byte_rows",
            "value": counts.get("terminal_curl_timeout_0_bytes_after_retry", 0),
        },
        {"metric": "raw_cache_available_rows", "value": counts.get("raw_cache_available", 0)},
        {
            "metric": "requires_browser_or_alternate_fetch_rows",
            "value": sum(1 for row in rows if row.get("requires_browser_or_alternate_fetch") == "true"),
        },
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"non211_source_reachability_rows={len(rows)}")


if __name__ == "__main__":
    main()
