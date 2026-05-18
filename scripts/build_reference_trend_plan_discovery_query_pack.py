#!/usr/bin/env python3
"""Build official-source discovery queries for 520-window plan packets.

This is a search/query worklist for the collection thread. It does not fetch,
write source packets, canonicalize data, or run ML.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
QUERY_PACK_OUT = SEED_DIR / "reference_trend_520_plan_discovery_query_pack.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_plan_discovery_query_pack_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_plan_discovery_query_pack.md"

FIELDS = [
    "query_rank",
    "university_code",
    "university_name",
    "source_packet_priority",
    "highest_priority_score",
    "urgent_group_pairs",
    "trend_directions",
    "candidate_source_status",
    "primary_search_query",
    "secondary_search_query",
    "site_search_query",
    "desired_source_fields",
    "must_not_accept",
    "requires_network",
    "requires_browser_or_alternate_fetch",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]

PRIORITY_ORDER = {
    "P0_plan_source_packet_urgent": 0,
    "P1_plan_source_packet_high": 1,
    "P2_plan_source_packet_medium": 2,
    "P3_plan_source_packet_backlog": 3,
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


def parse_int(value: object) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def top_priority(rows: list[dict[str, str]]) -> str:
    return sorted(
        {row.get("source_packet_priority", "") for row in rows},
        key=lambda value: PRIORITY_ORDER.get(value, 99),
    )[0]


def build_rows() -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(QUEUE):
        priority = row.get("source_packet_priority", "")
        if priority not in {"P0_plan_source_packet_urgent", "P1_plan_source_packet_high"}:
            continue
        grouped[(row.get("university_code", ""), row.get("university_name", ""))].append(row)

    output: list[dict[str, object]] = []
    for (code, name), rows in grouped.items():
        priority = top_priority(rows)
        highest_score = max(parse_int(row.get("priority_score")) for row in rows)
        group_pairs = "|".join(row.get("group_pair_key", "") for row in rows[:8])
        directions = "|".join(sorted({row.get("trend_direction", "") for row in rows if row.get("trend_direction")}))
        has_existing = any(row.get("candidate_source") != "no_existing_candidate_matched" for row in rows)
        output.append(
            {
                "query_rank": 0,
                "university_code": code,
                "university_name": name,
                "source_packet_priority": priority,
                "highest_priority_score": highest_score,
                "urgent_group_pairs": group_pairs,
                "trend_directions": directions,
                "candidate_source_status": "has_existing_candidate" if has_existing else "needs_official_source_discovery",
                "primary_search_query": f"{name} 2025 广西 物理类 本科普通批 招生计划 院校专业组",
                "secondary_search_query": f"{name} 2024 广西 物理类 本科普通批 招生计划 专业组",
                "site_search_query": f"site:edu.cn {name} 广西 物理类 招生计划 2025",
                "desired_source_fields": "year|province=广西|batch=本科普通批|subject=物理类|university_group_code|plan_count|major_or_group_structure|source_url|published_date",
                "must_not_accept": "third_party_only|special_type_mixed|no_group_code_when_multiple_groups|school_minimum_only|canonical_or_ml_write",
                "requires_network": "true",
                "requires_browser_or_alternate_fetch": "false" if has_existing else "true",
                "next_action": "verify_existing_candidate_then_write_source_packet"
                if has_existing
                else "search_official_admission_site_then_write_source_packet",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_plan_discovery_only_not_decision_pool",
                "record_id": "",
            }
        )
    output.sort(
        key=lambda row: (
            PRIORITY_ORDER.get(str(row.get("source_packet_priority")), 99),
            -parse_int(row.get("highest_priority_score")),
            row.get("university_name", ""),
        )
    )
    for index, row in enumerate(output, start=1):
        row["query_rank"] = index
        row["record_id"] = f"reference_trend_plan_discovery_query_{index:04d}"
    return output


def write_doc(rows: list[dict[str, object]]) -> None:
    priorities = Counter(row.get("source_packet_priority", "") for row in rows)
    status_counts = Counter(row.get("candidate_source_status", "") for row in rows)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 520 Plan Discovery Query Pack",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已把 520 位次窗口 P0/P1 计划数补厚队列压缩成按学校去重的官方来源发现 query pack。它只服务资料搜集线程，目标是找到并写 source packet；不能跳过 source packet 直接写 intake/canonical/ML。",
                "",
                "## 覆盖",
                "",
                f"- query rows: {len(rows)}",
                f"- P0 university queries: {priorities.get('P0_plan_source_packet_urgent', 0)}",
                f"- P1 university queries: {priorities.get('P1_plan_source_packet_high', 0)}",
                f"- queries with existing candidate: {status_counts.get('has_existing_candidate', 0)}",
                f"- queries needing new official discovery: {status_counts.get('needs_official_source_discovery', 0)}",
                "",
                "## 使用边界",
                "",
                "- 只接受官方招生网、考试院、学校信息公开等可审计来源。",
                "- 不接受第三方汇总页直接入库。",
                "- 不接受无法区分本科普通批、物理类、特殊类型的混合页面。",
                "- 找到网页后先写 source packet，再进入 intake preview 和 QA。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(QUERY_PACK_OUT, rows, FIELDS)
    priorities = Counter(row.get("source_packet_priority", "") for row in rows)
    status_counts = Counter(row.get("candidate_source_status", "") for row in rows)
    rollup = [
        {"metric": "plan_discovery_query_rows", "value": len(rows)},
        {"metric": "P0_university_query_rows", "value": priorities.get("P0_plan_source_packet_urgent", 0)},
        {"metric": "P1_university_query_rows", "value": priorities.get("P1_plan_source_packet_high", 0)},
        {"metric": "queries_with_existing_candidate", "value": status_counts.get("has_existing_candidate", 0)},
        {"metric": "queries_needing_new_official_discovery", "value": status_counts.get("needs_official_source_discovery", 0)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"plan_discovery_query_rows={len(rows)}")


if __name__ == "__main__":
    main()
