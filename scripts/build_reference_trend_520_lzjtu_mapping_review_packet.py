#!/usr/bin/env python3
"""Build a Lanzhou Jiaotong University mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_lzjtu_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_lzjtu_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_lzjtu_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_lzjtu_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_lzjtu_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_lzjtu_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_lzjtu_mapping_review_packet.md"
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
    count = to_int(row.get("candidate_group_count", ""))
    evidence = row.get("mapping_evidence", "")
    if count == 1 and "score_equals_exam_group_floor" in evidence:
        return "score_floor_exact_single_candidate", "manual_accept_only_if_group_structure_confirms"
    if count == 2 and "score_equals_exam_group_floor" in evidence:
        return "score_floor_exact_but_still_two_group_candidate", "inspect_floor_match_and_official_group_structure"
    if kind == "score_major_mapping_candidate" and count == 1:
        return "score_single_threshold_candidate", "manual_accept_or_hold_after_group_structure_review"
    if kind == "score_major_mapping_candidate" and count > 1:
        return "score_ambiguous_two_group_threshold_candidate", "need_official_group_structure"
    if kind == "plan_major_mapping_candidate" and count == 1:
        return "plan_single_candidate_from_exact_major_score_match", "manual_accept_only_if_score_match_valid"
    if kind == "plan_major_mapping_candidate" and count > 1:
        return "plan_ambiguous_candidate_from_exact_major_score_match", "need_official_group_structure"
    return "hold_unclassified", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    out: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action, next_action = classify(row)
        out.append(
            {
                "packet_record_id": f"reference_trend_520_lzjtu_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "source_record_id": row.get("source_record_id", ""),
                "row_kind": row.get("row_kind", ""),
                "year": row.get("year", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "major_or_group": row.get("major_or_group", ""),
                "normalized_major": row.get("normalized_major", ""),
                "plan_count": row.get("plan_count", ""),
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "exam_group_codes_2024": row.get("exam_group_codes_2024", ""),
                "exam_group_floor_scores_2024": row.get("exam_group_floor_scores_2024", ""),
                "candidate_group_codes": row.get("candidate_group_codes", ""),
                "candidate_group_count": row.get("candidate_group_count", ""),
                "mapping_evidence": row.get("mapping_evidence", ""),
                "action_class": action,
                "next_action": next_action,
                "mapping_status": row.get("mapping_status", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "lzjtu_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
            }
        )
    return out


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["row_kind"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (kind, action), group in sorted(grouped.items()):
        out.append(
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
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    actions = Counter(str(row["action_class"]) for row in rows)
    kinds = Counter(str(row["row_kind"]) for row in rows)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from LZJTU group mapping workbench."},
        {"metric": "score_major_rows", "value": kinds.get("score_major_mapping_candidate", 0), "note": "Official API score/rank mapping candidates."},
        {"metric": "plan_major_rows", "value": kinds.get("plan_major_mapping_candidate", 0), "note": "Official API plan rows matched by major label."},
        {"metric": "single_candidate_rows", "value": sum(v for k, v in actions.items() if "single" in k), "note": "Still unconfirmed without official group structure."},
        {"metric": "ambiguous_candidate_rows", "value": sum(v for k, v in actions.items() if "ambiguous" in k or "two_group" in k), "note": "101/102 candidates both possible."},
        {"metric": "plan_count_sum", "value": sum(to_int(row["plan_count"]) for row in rows), "note": "Plan rows only; score rows have blank plan count."},
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
    actions = Counter(str(row["action_class"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 52 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "score_and_plan_rows_classified", "status": "PASS" if sum(1 for row in rows if row["row_kind"] == "score_major_mapping_candidate") == 26 and sum(1 for row in rows if row["row_kind"] == "plan_major_mapping_candidate") == 26 else "WARN", "detail": "score=26; plan=26 expected"},
        {"check": "single_candidate_rows_carried", "status": "PASS" if sum(v for k, v in actions.items() if "single" in k) == 12 else "WARN", "detail": str(sum(v for k, v in actions.items() if "single" in k))},
        {"check": "ambiguous_candidate_rows_carried", "status": "PASS" if sum(v for k, v in actions.items() if "ambiguous" in k or "two_group" in k) == 40 else "WARN", "detail": str(sum(v for k, v in actions.items() if "ambiguous" in k or "two_group" in k))},
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
            "exclusion_reason": "official_group_structure_confirmation_pending",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# LZJTU Mapping Review Packet",
        "",
        "Scope: 兰州交通大学 2024 official API score/plan rows with 101/102 group-candidate ambiguity.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Score rows: {sum(1 for row in rows if row['row_kind'] == 'score_major_mapping_candidate')}",
        f"- Plan rows: {sum(1 for row in rows if row['row_kind'] == 'plan_major_mapping_candidate')}",
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
    marker = "## 89. 2026-05-16 LZJTU mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增兰州交通大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_lzjtu_mapping_review_packet.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_lzjtu_mapping_review_packet.md`

覆盖结果：从既有 LZJTU group mapping workbench 派生 {values.get('packet_rows')} 行审核包，其中 score-major {values.get('score_major_rows')} 行、plan-major {values.get('plan_major_rows')} 行；单组候选 {values.get('single_candidate_rows')} 行、多组歧义 {values.get('ambiguous_candidate_rows')} 行，计划行合计 {values.get('plan_count_sum')}。

准入边界：本轮只做 101/102 组候选分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No LZJTU workbench rows found.")
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
    print(f"wrote {len(rows)} LZJTU mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
