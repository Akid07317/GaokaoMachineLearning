#!/usr/bin/env python3
"""Build a Nanjing University of Aeronautics and Astronautics mapping packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_nanhang_group_boundary_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_nanhang_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_nanhang_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_nanhang_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_nanhang_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_nanhang_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_nanhang_mapping_review_packet.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: object) -> int:
    try:
        return int(float(str(value or "").strip() or "0"))
    except ValueError:
        return 0


def classify(row: dict[str, str]) -> tuple[str, str]:
    kind = row.get("row_kind", "")
    evidence = row.get("mapping_evidence", "")
    cross_year = row.get("cross_year_match_status", "")

    if kind == "official_major_score_2024_candidate":
        if "score_equals_ordinary_group_floor" in evidence:
            return "score_floor_exact_rank_missing", "confirm_rank_source_and_official_group_code_before_intake"
        return "score_single_group_candidate_rank_missing", "confirm_rank_source_and_official_group_code_before_intake"

    if kind == "official_plan_2025_cross_year_candidate":
        if cross_year == "single_2024_major_score_match":
            return "plan_single_cross_year_match_303_scope_unresolved", "confirm_2025_group_101_vs_303_scope"
        if cross_year == "multiple_2024_major_score_matches_after_major_normalization":
            return "plan_multiple_cross_year_matches_303_scope_unresolved", "split_or_confirm_normalized_major_match"
        return "plan_no_2024_score_match_303_scope_unresolved", "keep_as_plan_only_until_group_scope_confirmed"

    if kind == "official_score_overview_2024_boundary":
        if evidence.startswith("ordinary_overview"):
            return "overview_ordinary_floor_boundary_only", "use_as_boundary_evidence_only"
        return "overview_special_boundary_only", "exclude_from_ordinary_group_year_trend"

    return "hold_unclassified", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_nanhang_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "source_file": row.get("source_file", ""),
                "source_row_number": row.get("source_row_number", ""),
                "row_kind": row.get("row_kind", ""),
                "year": row.get("year", ""),
                "comparison_year": row.get("comparison_year", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "college": row.get("college", ""),
                "major_or_group": row.get("major_or_group", ""),
                "normalized_major": row.get("normalized_major", ""),
                "plan_count": row.get("plan_count", ""),
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "rank_status": row.get("rank_status", ""),
                "exam_ordinary_group_codes": row.get("exam_ordinary_group_codes", ""),
                "exam_ordinary_group_floor_scores": row.get("exam_ordinary_group_floor_scores", ""),
                "exam_separate_unlabeled_group_context": row.get("exam_separate_unlabeled_group_context", ""),
                "exam_special_group_context": row.get("exam_special_group_context", ""),
                "candidate_group_codes": row.get("candidate_group_codes", ""),
                "candidate_group_count": row.get("candidate_group_count", ""),
                "mapping_evidence": row.get("mapping_evidence", ""),
                "cross_year_match_status": row.get("cross_year_match_status", ""),
                "action_class": action_class,
                "next_action": next_action,
                "qa_status": row.get("qa_status", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "nanhang_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
            }
        )
    return packet


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["row_kind"]), str(row["action_class"]))].append(row)

    rollup: list[dict[str, object]] = []
    for (kind, action), group in sorted(grouped.items()):
        rollup.append(
            {
                "row_kind": kind,
                "action_class": action,
                "rows": len(group),
                "plan_count_sum": sum(to_int(row["plan_count"]) for row in group),
                "min_score_min": min([to_int(row["minimum_score"]) for row in group if to_int(row["minimum_score"])], default=0),
                "min_score_max": max([to_int(row["minimum_score"]) for row in group if to_int(row["minimum_score"])], default=0),
                "candidate_group_codes_seen": "|".join(sorted({code for row in group for code in str(row.get("candidate_group_codes", "")).split("|") if code})),
                "canonical_ml_entry_open": "false",
            }
        )
    return rollup


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    actions = Counter(str(row["action_class"]) for row in rows)
    kinds = Counter(str(row["row_kind"]) for row in rows)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from NANHANG group boundary workbench."},
        {"metric": "official_major_score_rows_2024", "value": kinds.get("official_major_score_2024_candidate", 0), "note": "Official 2024 major-score rows; rank is missing."},
        {"metric": "official_plan_rows_2025", "value": kinds.get("official_plan_2025_cross_year_candidate", 0), "note": "Official 2025 plan rows requiring 101/303 scope decision."},
        {"metric": "official_overview_rows_2024", "value": kinds.get("official_score_overview_2024_boundary", 0), "note": "Overview boundary evidence only."},
        {"metric": "single_candidate_rows", "value": sum(1 for row in rows if to_int(row.get("candidate_group_count")) == 1), "note": "Still held pending group/rank confirmation."},
        {"metric": "unmapped_or_boundary_only_rows", "value": sum(1 for row in rows if to_int(row.get("candidate_group_count")) == 0), "note": "Plan-only no match or nonordinary overview boundary rows."},
        {"metric": "plan_count_sum", "value": sum(to_int(row["plan_count"]) for row in rows), "note": "Plan rows only; score and overview rows have blank plan count."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        *[
            {"metric": f"action_class::{key}", "value": value, "note": "Packet classification."}
            for key, value in sorted(actions.items())
        ],
    ]


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    kinds = Counter(str(row["row_kind"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 44 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "row_kind_counts_match_rollup", "status": "PASS" if kinds.get("official_major_score_2024_candidate", 0) == 19 and kinds.get("official_plan_2025_cross_year_candidate", 0) == 21 and kinds.get("official_score_overview_2024_boundary", 0) == 4 else "WARN", "detail": f"score={kinds.get('official_major_score_2024_candidate', 0)}; plan={kinds.get('official_plan_2025_cross_year_candidate', 0)}; overview={kinds.get('official_score_overview_2024_boundary', 0)}"},
        {"check": "single_candidate_rows_carried", "status": "PASS" if sum(1 for row in rows if to_int(row.get("candidate_group_count")) == 1) == 38 else "WARN", "detail": str(sum(1 for row in rows if to_int(row.get("candidate_group_count")) == 1))},
        {"check": "unmapped_or_boundary_rows_carried", "status": "PASS" if sum(1 for row in rows if to_int(row.get("candidate_group_count")) == 0) == 6 else "WARN", "detail": str(sum(1 for row in rows if to_int(row.get("candidate_group_count")) == 0))},
        {"check": "overview_boundary_split", "status": "PASS" if sum(1 for row in rows if row["action_class"] == "overview_ordinary_floor_boundary_only") == 1 and sum(1 for row in rows if row["action_class"] == "overview_special_boundary_only") == 3 else "WARN", "detail": f"ordinary={sum(1 for row in rows if row['action_class'] == 'overview_ordinary_floor_boundary_only')}; special={sum(1 for row in rows if row['action_class'] == 'overview_special_boundary_only')}"},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "row_kind": row["row_kind"],
            "major_or_group": row["major_or_group"],
            "action_class": row["action_class"],
            "exclusion_reason": "rank_or_101_303_group_scope_confirmation_pending",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# NANHANG Mapping Review Packet",
        "",
        "Scope: 南京航空航天大学 2024 official major-score rows, 2025 official plan rows, and overview boundary evidence.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- 2024 major-score rows: {sum(1 for row in rows if row['row_kind'] == 'official_major_score_2024_candidate')}",
        f"- 2025 plan rows: {sum(1 for row in rows if row['row_kind'] == 'official_plan_2025_cross_year_candidate')}",
        f"- 2024 overview rows: {sum(1 for row in rows if row['row_kind'] == 'official_score_overview_2024_boundary')}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(f"- {row['row_kind']} {row['action_class']}: {row['rows']} rows, plan_count_sum={row['plan_count_sum']}")
    lines.extend(
        [
            "",
            "QA:",
            *[f"- {item['check']}: {item['status']} ({item['detail']})" for item in qa],
            "",
            "Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def append_handoff(rollup: list[dict[str, object]]) -> None:
    marker = "## 90. 2026-05-16 NANHANG mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增南京航空航天大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_nanhang_mapping_review_packet.csv`
- `reports/reference_trend_520_nanhang_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_nanhang_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_nanhang_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_nanhang_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_nanhang_mapping_review_packet.md`

覆盖结果：从既有 NANHANG group boundary workbench 派生 {values.get('packet_rows')} 行审核包，其中 2024 专业分 rows {values.get('official_major_score_rows_2024')} 行、2025 计划 rows {values.get('official_plan_rows_2025')} 行、2024 overview boundary rows {values.get('official_overview_rows_2024')} 行；单组候选 {values.get('single_candidate_rows')} 行，未映射/边界证据 {values.get('unmapped_or_boundary_only_rows')} 行，计划行合计 {values.get('plan_count_sum')}。

准入边界：本轮只做 101/303 组边界与 rank 缺失分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No NANHANG workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "row_kind", "major_or_group", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} NANHANG mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
