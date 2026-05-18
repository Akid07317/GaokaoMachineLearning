#!/usr/bin/env python3
"""Build source-packet queue for plan-count thickening in the 520 rank window.

This queue identifies high-priority 2024/2025 matched group pairs near the
target rank window and attaches any existing official-source candidates. It is
planning only: no canonical, ML, or decision-pool writes.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

DELTA_WINDOW = SEED_DIR / "reference_trend_520_rank_window_delta_preview.csv"
FOCUS_TARGETS = REPORT_DIR / "engineering_focus_targets_520.csv"
NON211_TRIAGE = SEED_DIR / "reference_trend_non211_source_packet_triage_preview.csv"

QUEUE_OUT = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_plan_source_packet_queue_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_plan_source_packet_queue.md"

TARGET_RANKS = {"2024": 42944, "2025": 42339}

FIELDS = [
    "queue_rank",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "source_packet_priority",
    "priority_score",
    "priority_reason",
    "candidate_source",
    "candidate_url",
    "candidate_title",
    "candidate_kind",
    "candidate_confidence_tier",
    "requires_network",
    "requires_browser_or_alternate_fetch",
    "can_enter_intake_without_source_packet",
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


def parse_int(value: object) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def norm_name(value: object) -> str:
    text = str(value or "")
    for token in ["本科招生网", "招生网", "本科生招生信息公开", "招生与就业工作处"]:
        text = text.replace(token, "")
    return text.strip()


def source_kind(text: str) -> tuple[str, str]:
    if "招生计划" in text or "分省分专业" in text or "zsjh" in text.lower() or "plan" in text.lower():
        return "plan_candidate", "P1_existing_official_plan_candidate"
    if "历年分数" in text or "录取" in text or "分数" in text:
        return "score_candidate", "P2_existing_score_candidate"
    if "章程" in text:
        return "regulation_context_candidate", "P4_rule_context_only"
    return "official_source_candidate", "P3_existing_portal_candidate"


def build_candidate_index() -> dict[str, list[dict[str, str]]]:
    candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(FOCUS_TARGETS):
        school_name = norm_name(row.get("source_name", ""))
        text = " ".join([row.get("target_url", ""), row.get("link_text", ""), row.get("matched_reason", "")])
        kind, tier = source_kind(text)
        candidates[school_name].append(
            {
                "candidate_source": "engineering_focus_targets_520",
                "candidate_url": row.get("target_url", ""),
                "candidate_title": row.get("link_text", ""),
                "candidate_kind": kind,
                "candidate_confidence_tier": tier,
                "fetch_priority": row.get("fetch_priority", ""),
            }
        )
    for row in read_csv(NON211_TRIAGE):
        school_name = norm_name(row.get("school_name", ""))
        candidates[school_name].append(
            {
                "candidate_source": "reference_trend_non211_source_packet_triage",
                "candidate_url": row.get("candidate_url", ""),
                "candidate_title": row.get("candidate_title", ""),
                "candidate_kind": row.get("candidate_kind", ""),
                "candidate_confidence_tier": row.get("source_packet_priority", ""),
                "fetch_priority": "30",
            }
        )
    return candidates


def best_candidate(university_name: str, index: dict[str, list[dict[str, str]]]) -> dict[str, str]:
    name = norm_name(university_name)
    direct = index.get(name, [])
    if not direct:
        for candidate_name, rows in index.items():
            if candidate_name and (candidate_name in name or name in candidate_name):
                direct = rows
                break
    if not direct:
        return {}

    def score(row: dict[str, str]) -> tuple[int, int]:
        kind = row.get("candidate_kind", "")
        kind_score = 3 if kind == "plan_candidate" else 2 if kind == "score_candidate" else 1
        return (kind_score, parse_int(row.get("fetch_priority")))

    return sorted(direct, key=score, reverse=True)[0]


def priority_for_delta(row: dict[str, str]) -> tuple[str, int, str]:
    rank_2024 = parse_int(row.get("rank_2024"))
    rank_2025 = parse_int(row.get("rank_2025"))
    delta = abs(parse_int(row.get("rank_delta_2025_minus_2024")))
    in_both = row.get("in_2024_520_window") == "true" and row.get("in_2025_520_window") == "true"
    min_distance = min(abs(rank_2024 - TARGET_RANKS["2024"]), abs(rank_2025 - TARGET_RANKS["2025"]))
    score = 0
    reasons = []
    if in_both:
        score += 40
        reasons.append("both_years_in_520_window")
    else:
        score += 15
        reasons.append("one_year_in_520_window")
    if min_distance <= 5000:
        score += 30
        reasons.append("near_target_rank_0_5000")
    elif min_distance <= 10000:
        score += 20
        reasons.append("near_target_rank_5001_10000")
    else:
        score += 10
        reasons.append("outer_target_rank_10001_20000")
    if delta >= 10000:
        score += 25
        reasons.append("large_rank_delta_ge_10000")
    elif delta >= 5000:
        score += 15
        reasons.append("medium_rank_delta_ge_5000")
    elif delta >= 2000:
        score += 8
        reasons.append("small_rank_delta_ge_2000")
    if row.get("trend_direction") in {"hotter_or_higher_selectivity", "cooler_or_lower_selectivity"}:
        score += 5
        reasons.append("clear_direction")
    if score >= 85:
        lane = "P0_plan_source_packet_urgent"
    elif score >= 70:
        lane = "P1_plan_source_packet_high"
    elif score >= 55:
        lane = "P2_plan_source_packet_medium"
    else:
        lane = "P3_plan_source_packet_backlog"
    return lane, score, "|".join(reasons)


def build_rows() -> list[dict[str, object]]:
    index = build_candidate_index()
    rows: list[dict[str, object]] = []
    for delta_row in read_csv(DELTA_WINDOW):
        lane, score, reason = priority_for_delta(delta_row)
        university_name = delta_row.get("university_name_2025") or delta_row.get("university_name_2024", "")
        candidate = best_candidate(university_name, index)
        rows.append(
            {
                "queue_rank": 0,
                "group_pair_key": delta_row.get("group_pair_key", ""),
                "university_code": delta_row.get("university_code", ""),
                "university_name": university_name,
                "group_code": delta_row.get("group_code", ""),
                "rank_2024": delta_row.get("rank_2024", ""),
                "rank_2025": delta_row.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": delta_row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": delta_row.get("trend_direction", ""),
                "source_packet_priority": lane,
                "priority_score": score,
                "priority_reason": reason,
                "candidate_source": candidate.get("candidate_source", "no_existing_candidate_matched"),
                "candidate_url": candidate.get("candidate_url", ""),
                "candidate_title": candidate.get("candidate_title", ""),
                "candidate_kind": candidate.get("candidate_kind", "needs_official_plan_source_discovery"),
                "candidate_confidence_tier": candidate.get("candidate_confidence_tier", "T0_no_candidate_yet"),
                "requires_network": "true",
                "requires_browser_or_alternate_fetch": "true" if not candidate else "false",
                "can_enter_intake_without_source_packet": "false",
                "next_action": "fetch_or_open_candidate_and_write_plan_source_packet"
                if candidate
                else "discover_official_school_plan_source_packet",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_plan_source_queue_only_not_decision_pool",
                "record_id": "",
            }
        )
    rows.sort(
        key=lambda row: (
            -parse_int(row.get("priority_score")),
            row.get("candidate_source") == "no_existing_candidate_matched",
            row.get("university_name", ""),
        )
    )
    for index_value, row in enumerate(rows, start=1):
        row["queue_rank"] = index_value
        row["record_id"] = f"reference_trend_520_plan_source_queue_{index_value:04d}"
    return rows


def write_doc(rows: list[dict[str, object]]) -> None:
    priorities = Counter(row.get("source_packet_priority", "") for row in rows)
    candidate_sources = Counter(row.get("candidate_source", "") for row in rows)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend 520 Plan Source Packet Queue",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已从 520 位次窗口的 457 个跨年专业组对生成计划数补厚 source packet 队列。该队列只决定下一步去哪里找官方计划/专业组结构来源，不写 canonical/ML，也不并入 32 所 decision_pool。",
                "",
                "## 覆盖",
                "",
                f"- queue rows: {len(rows)}",
                f"- P0 urgent rows: {priorities.get('P0_plan_source_packet_urgent', 0)}",
                f"- P1 high rows: {priorities.get('P1_plan_source_packet_high', 0)}",
                f"- P2 medium rows: {priorities.get('P2_plan_source_packet_medium', 0)}",
                f"- rows with existing official-source candidates: {len(rows) - candidate_sources.get('no_existing_candidate_matched', 0)}",
                f"- rows needing new official-source discovery: {candidate_sources.get('no_existing_candidate_matched', 0)}",
                "",
                "## 下一步",
                "",
                "优先处理 P0/P1 中已有 `plan_candidate` 的学校；若候选 URL 已知终端阻塞，则不要重复硬抓，改走浏览器态或人工批准路线。只要 source packet 没落地，就不能把计划数写入 intake/canonical。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    rows = build_rows()
    write_csv(QUEUE_OUT, rows, FIELDS)
    priorities = Counter(row.get("source_packet_priority", "") for row in rows)
    candidate_sources = Counter(row.get("candidate_source", "") for row in rows)
    rollup = [
        {"metric": "plan_source_queue_rows", "value": len(rows)},
        {"metric": "P0_plan_source_packet_urgent", "value": priorities.get("P0_plan_source_packet_urgent", 0)},
        {"metric": "P1_plan_source_packet_high", "value": priorities.get("P1_plan_source_packet_high", 0)},
        {"metric": "P2_plan_source_packet_medium", "value": priorities.get("P2_plan_source_packet_medium", 0)},
        {"metric": "P3_plan_source_packet_backlog", "value": priorities.get("P3_plan_source_packet_backlog", 0)},
        {
            "metric": "rows_with_existing_source_candidate",
            "value": len(rows) - candidate_sources.get("no_existing_candidate_matched", 0),
        },
        {"metric": "rows_needing_new_official_source_discovery", "value": candidate_sources.get("no_existing_candidate_matched", 0)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])
    write_doc(rows)
    print(f"plan_source_queue_rows={len(rows)}")


if __name__ == "__main__":
    main()
