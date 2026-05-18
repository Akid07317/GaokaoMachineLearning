#!/usr/bin/env python3
"""Build reachability status for reference-trend score-rank source packets.

The heartbeat may try live fetches, but this script only records the current
local source-packet status. It never writes canonical/ML artifacts.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

SOURCE_PACKETS = SEED_DIR / "reference_trend_source_packet_local_seed_preview.csv"
REACHABILITY_OUT = REPORT_DIR / "reference_trend_2025_score_rank_reachability.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_2025_score_rank_reachability_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_2025_score_rank_reachability.md"

RAW_QG = ROOT / "raw_data" / "reference_trend" / "gx_2025_yifenyidang_wuli_qg_339.html"
RAW_QG_HTTP = ROOT / "raw_data" / "reference_trend" / "gx_2025_yifenyidang_wuli_qg_339_http.html"
RAW_QN = ROOT / "raw_data" / "reference_trend" / "gx_2025_yifenyidang_wuli_qn_382.html"

FIELDS = [
    "source_id",
    "year",
    "source_url",
    "source_owner",
    "source_title",
    "source_packet_status_before",
    "terminal_fetch_status",
    "raw_cache_path",
    "raw_cache_bytes",
    "requires_browser_or_alternate_fetch",
    "can_structure_now",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]


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


def file_size(path: Path) -> int:
    if not path.exists():
        return 0
    return path.stat().st_size


def build_rows() -> list[dict[str, object]]:
    rows = []
    raw_map = {
        "gx_2025_score_rank_physics_index": "",
        "gx_2025_score_rank_query_index": str(RAW_QG),
        "gx_2025_score_rank_release_notice": "",
    }
    status_map = {
        "gx_2025_score_rank_physics_index": "known_chsi_antibot_from_prior_terminal_probe",
        "gx_2025_score_rank_query_index": (
            "terminal_fetch_blocked_https_ssl_error_syscall_and_http_empty_reply;"
            "qg_raw_bytes="
            f"{file_size(RAW_QG)};qn_raw_bytes={file_size(RAW_QN)};qg_http_raw_bytes={file_size(RAW_QG_HTTP)}"
        ),
        "gx_2025_score_rank_release_notice": "notice_only_not_score_rank_table",
    }
    for index, row in enumerate(read_csv(SOURCE_PACKETS), start=1):
        source_id = row.get("source_id", "")
        if not source_id.startswith("gx_2025_score_rank"):
            continue
        raw_path = raw_map.get(source_id, "")
        raw_bytes = file_size(Path(raw_path)) if raw_path else 0
        can_structure = raw_bytes > 2000
        requires_browser = not can_structure
        rows.append(
            {
                "source_id": source_id,
                "year": row.get("year", ""),
                "source_url": row.get("source_url", ""),
                "source_owner": row.get("source_owner", ""),
                "source_title": row.get("source_title", ""),
                "source_packet_status_before": row.get("source_packet_status", ""),
                "terminal_fetch_status": status_map.get(source_id, "not_tested_this_round"),
                "raw_cache_path": raw_path,
                "raw_cache_bytes": raw_bytes,
                "requires_browser_or_alternate_fetch": "true" if requires_browser else "false",
                "can_structure_now": "true" if can_structure else "false",
                "next_action": "use_raw_cache_to_parse_score_rank"
                if can_structure
                else "browser_or_alternate_fetch_required_before_structure",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_only_not_decision_pool",
                "record_id": f"reference_trend_score_rank_reachability_{index:03d}",
            }
        )
    return rows


def write_doc(rows: list[dict[str, object]]) -> None:
    blocked = [row for row in rows if row.get("can_structure_now") != "true"]
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 2025 Score Rank Reachability",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "2025 物理类一分一档目前仍停留在 source-packet 可达性层，不能结构化入 reference trend intake。命令行抓取官方细分页时，HTTPS 返回 `SSL_ERROR_SYSCALL`，HTTP 返回 `Empty reply from server`；此前 CHSI 汇总页也有终端反爬记录。",
                "",
                "## 本轮边界",
                "",
                "- 未写 canonical。",
                "- 未写 ML。",
                "- 未并入 32 所 decision_pool。",
                "- 未用第三方页面替代官方来源。",
                "",
                "## 状态",
                "",
                f"- checked rows: {len(rows)}",
                f"- blocked rows: {len(blocked)}",
                "- can structure now: 0",
                "",
                "## 下一步",
                "",
                "1. 使用浏览器态或其他可审计方式打开广西招生考试院 2025 一分一档细分页。",
                "2. 保存 raw HTML/PDF/表格缓存，并补 `raw_file_path`。",
                "3. 再生成 `reference_trend_score_rank_2025_preview.csv`。",
                "4. 仍只进入 source packet/preview/QA，不打开 canonical/ML。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(REACHABILITY_OUT, rows, FIELDS)
    rollup = [
        {"metric": "checked_2025_score_rank_source_rows", "value": len(rows)},
        {
            "metric": "can_structure_now_rows",
            "value": sum(1 for row in rows if row.get("can_structure_now") == "true"),
        },
        {
            "metric": "requires_browser_or_alternate_fetch_rows",
            "value": sum(1 for row in rows if row.get("requires_browser_or_alternate_fetch") == "true"),
        },
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"reachability_rows={len(rows)}")


if __name__ == "__main__":
    main()
