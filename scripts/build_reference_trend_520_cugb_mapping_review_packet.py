#!/usr/bin/env python3
"""Build a CUGB group mapping review packet.

This packet separates official major score rows and official plan rows from
their threshold-based group candidates. It is a review aid only.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_cugb_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_cugb_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_cugb_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_cugb_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_cugb_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_cugb_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_cugb_mapping_review_packet.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def to_int(value: object) -> int:
    try:
        return int(float(str(value or "").strip() or "0"))
    except ValueError:
        return 0


def classify(row: dict[str, str]) -> tuple[str, str]:
    row_kind = row.get("row_kind", "")
    candidate_count = to_int(row.get("candidate_group_count", ""))
    has_match = bool(str(row.get("matched_score_evidence", "")).strip())
    has_special_collision = bool(str(row.get("special_group_collision_context", "")).strip())

    if row_kind == "score_major_mapping_candidate":
        if candidate_count == 1:
            action = "score_single_group_floor_candidate_unconfirmed"
            next_action = "manual_accept_only_if_official_group_structure_confirms"
        elif candidate_count > 1:
            action = "score_ambiguous_multi_group_floor_candidate"
            next_action = "need_official_group_structure_or_manual_boundary_rule"
        else:
            action = "score_unmapped_no_floor_candidate"
            next_action = "hold_for_source_review"
    elif row_kind == "plan_major_mapping_candidate":
        if has_match and candidate_count == 1:
            action = "plan_matched_single_floor_candidate_unconfirmed"
            next_action = "manual_accept_only_if_major_score_match_and_group_structure_confirm"
        elif has_match and candidate_count > 1:
            action = "plan_matched_ambiguous_floor_candidate"
            next_action = "need_official_group_structure_before_plan_group_use"
        else:
            action = "plan_unmapped_no_score_match"
            next_action = "hold_or_find_official_plan_group_structure"
    else:
        action = "unknown_hold"
        next_action = "manual_review"

    if has_special_collision:
        action = f"{action}__special_collision_context"
        next_action = f"{next_action}; keep_special_group_collision_isolated"

    return action, next_action


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    out: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action, next_action = classify(row)
        out.append(
            {
                "packet_record_id": f"reference_trend_520_cugb_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "source_file": row.get("source_file", ""),
                "source_row_number": row.get("source_row_number", ""),
                "row_kind": row.get("row_kind", ""),
                "year": row.get("year", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_group_label": row.get("source_group_label", ""),
                "major_or_group": row.get("major_or_group", ""),
                "normalized_major": row.get("normalized_major", ""),
                "plan_count": row.get("plan_count", ""),
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "exam_ordinary_group_codes": row.get("exam_ordinary_group_codes", ""),
                "exam_ordinary_group_floor_scores": row.get("exam_ordinary_group_floor_scores", ""),
                "exam_special_group_context": row.get("exam_special_group_context", ""),
                "candidate_group_codes": row.get("candidate_group_codes", ""),
                "candidate_group_count": row.get("candidate_group_count", ""),
                "mapping_evidence": row.get("mapping_evidence", ""),
                "matched_score_evidence": row.get("matched_score_evidence", ""),
                "special_group_collision_context": row.get("special_group_collision_context", ""),
                "action_class": action,
                "next_action": next_action,
                "confidence_tier": row.get("confidence_tier", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "cugb_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
            }
        )
    return out


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["year"]), str(row["row_kind"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (year, row_kind, action), group in sorted(grouped.items()):
        out.append(
            {
                "year": year,
                "row_kind": row_kind,
                "action_class": action,
                "rows": len(group),
                "plan_count_sum": sum(to_int(row["plan_count"]) for row in group),
                "min_score_min": min([to_int(row["minimum_score"]) for row in group if to_int(row["minimum_score"])], default=0),
                "min_score_max": max([to_int(row["minimum_score"]) for row in group if to_int(row["minimum_score"])], default=0),
                "candidate_group_codes_seen": "|".join(
                    sorted({code for row in group for code in str(row.get("candidate_group_codes", "")).split("|") if code})
                ),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    actions = Counter(str(row["action_class"]) for row in rows)
    kinds = Counter(str(row["row_kind"]) for row in rows)
    out = [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from CUGB group mapping workbench."},
        {"metric": "score_major_rows", "value": kinds.get("score_major_mapping_candidate", 0), "note": "Official major score/rank mapping candidates."},
        {"metric": "plan_major_rows", "value": kinds.get("plan_major_mapping_candidate", 0), "note": "Official plan row mapping candidates."},
        {"metric": "single_candidate_rows", "value": sum(v for k, v in actions.items() if "single" in k), "note": "Still unconfirmed; needs official group structure."},
        {"metric": "ambiguous_candidate_rows", "value": sum(v for k, v in actions.items() if "ambiguous" in k), "note": "Multiple ordinary groups possible."},
        {"metric": "unmapped_plan_rows", "value": actions.get("plan_unmapped_no_score_match", 0), "note": "No matched major score row same year."},
        {"metric": "special_collision_rows", "value": sum(v for k, v in actions.items() if "special_collision" in k), "note": "Score/rank collides with special group floor context; keep isolated."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(actions.items()):
        out.append({"metric": f"action_class::{key}", "value": value, "note": "Packet classification."})
    return out


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    actions = Counter(str(row["action_class"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 53 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "score_major_rows_classified", "status": "PASS" if sum(1 for row in rows if row["row_kind"] == "score_major_mapping_candidate") == 9 else "WARN", "detail": str(sum(1 for row in rows if row["row_kind"] == "score_major_mapping_candidate"))},
        {"check": "plan_major_rows_classified", "status": "PASS" if sum(1 for row in rows if row["row_kind"] == "plan_major_mapping_candidate") == 44 else "WARN", "detail": str(sum(1 for row in rows if row["row_kind"] == "plan_major_mapping_candidate"))},
        {"check": "special_collision_rows_carried", "status": "PASS" if sum(v for k, v in actions.items() if "special_collision" in k) == 3 else "WARN", "detail": str(sum(v for k, v in actions.items() if "special_collision" in k))},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "year": row["year"],
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
    actions = Counter(str(row["action_class"]) for row in rows)
    lines = [
        "# CUGB Mapping Review Packet",
        "",
        "Scope: 中国地质大学(北京) 2024/2025 official major score and plan mapping candidates.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Score-major rows: {sum(1 for row in rows if row['row_kind'] == 'score_major_mapping_candidate')}",
        f"- Plan-major rows: {sum(1 for row in rows if row['row_kind'] == 'plan_major_mapping_candidate')}",
        f"- Special collision rows: {sum(v for k, v in actions.items() if 'special_collision' in k)}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(
            f"- {row['year']} {row['row_kind']} {row['action_class']}: "
            f"{row['rows']} rows, plan_count_sum={row['plan_count_sum']}"
        )
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
    marker = "## 88. 2026-05-16 CUGB mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增中国地质大学(北京) mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_cugb_mapping_review_packet.csv`
- `reports/reference_trend_520_cugb_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_cugb_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_cugb_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_cugb_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_cugb_mapping_review_packet.md`

覆盖结果：从既有 CUGB group mapping workbench 派生 {values.get('packet_rows')} 行审核包，其中 score-major {values.get('score_major_rows')} 行、plan-major {values.get('plan_major_rows')} 行；单组候选 {values.get('single_candidate_rows')} 行、多组歧义 {values.get('ambiguous_candidate_rows')} 行、未匹配计划行 {values.get('unmapped_plan_rows')} 行，另有 {values.get('special_collision_rows')} 行存在特殊组 floor 碰撞上下文。

准入边界：本轮只做阈值候选和特殊组碰撞分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No CUGB workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)

    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "year", "row_kind", "major_or_group", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} CUGB mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
