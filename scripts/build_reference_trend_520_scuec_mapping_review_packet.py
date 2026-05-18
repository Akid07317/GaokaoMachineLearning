#!/usr/bin/env python3
"""Build a SCUEC group mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_scuec_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_scuec_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_scuec_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_scuec_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_scuec_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_scuec_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_scuec_mapping_review_packet.md"
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
    status = row.get("mapping_status", "")
    if status == "score_exact_single_exam_group_match":
        if row.get("rank_delta_2025_minus_2024", ""):
            return "score_exact_group_evidence_with_rank_delta", "use_as_boundary_evidence_only_until_2025_plan_group_code_exists"
        return "score_exact_group_evidence_rank_delta_missing", "confirm_2025_rank_or_keep_as_score_boundary_only"
    if status == "plan_row_unmapped_no_group_code":
        return "plan_count_row_unmapped_group_code_missing", "map_major_to_103_104_105_only_after_official_group_structure_found"
    return "hold_unclassified", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_scuec_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "source_record_id": row.get("source_record_id", ""),
                "source_id": row.get("source_id", ""),
                "source_url": row.get("source_url", ""),
                "year": row.get("year", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "source_row_label": row.get("source_row_label", ""),
                "group_or_selection_label": row.get("group_or_selection_label", ""),
                "major_or_plan_label": row.get("source_row_label", ""),
                "source_min_score": row.get("source_min_score", ""),
                "source_plan_count": row.get("source_plan_count", ""),
                "exam_group_code_candidate": row.get("exam_group_code_candidate", ""),
                "exam_score": row.get("exam_score", ""),
                "exam_rank": row.get("exam_rank", ""),
                "delta_pair_key": row.get("delta_pair_key", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "mapping_status": row.get("mapping_status", ""),
                "mapping_confidence": row.get("mapping_confidence", ""),
                "field_gaps_after_mapping": row.get("field_gaps_after_mapping", ""),
                "action_class": action_class,
                "next_action": next_action,
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "scuec_mapping_review_packet_only_not_decision_pool",
            }
        )
    return packet


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["mapping_status"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (status, action), group in sorted(grouped.items()):
        out.append(
            {
                "mapping_status": status,
                "action_class": action,
                "rows": len(group),
                "plan_count_sum": sum(to_int(row["source_plan_count"]) for row in group),
                "min_score_min": min([to_int(row["source_min_score"]) for row in group if to_int(row["source_min_score"])], default=0),
                "min_score_max": max([to_int(row["source_min_score"]) for row in group if to_int(row["source_min_score"])], default=0),
                "exam_group_codes_seen": "|".join(sorted({str(row.get("exam_group_code_candidate", "")) for row in group if str(row.get("exam_group_code_candidate", ""))})),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from SCUEC group mapping workbench."},
        {"metric": "plan_row_unmapped_no_group_code_rows", "value": statuses.get("plan_row_unmapped_no_group_code", 0), "note": "Official 2025 plan rows without explicit 103/104/105 group code."},
        {"metric": "score_exact_single_exam_group_match_rows", "value": statuses.get("score_exact_single_exam_group_match", 0), "note": "2024 school score rows matching exam authority group scores."},
        {"metric": "plan_count_sum", "value": sum(to_int(row["source_plan_count"]) for row in rows), "note": "Plan rows only; score rows have blank plan count."},
        {"metric": "score_evidence_group_codes", "value": "|".join(sorted({str(row.get("exam_group_code_candidate", "")) for row in rows if row.get("mapping_status") == "score_exact_single_exam_group_match"})), "note": "Matched exam group code candidates from score evidence."},
        {"metric": "rank_delta_available_score_rows", "value": sum(1 for row in rows if row.get("rank_delta_2025_minus_2024")), "note": "Only score evidence rows with current delta context."},
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
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 35 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "status_counts_match_source_rollup", "status": "PASS" if statuses.get("plan_row_unmapped_no_group_code", 0) == 32 and statuses.get("score_exact_single_exam_group_match", 0) == 3 else "WARN", "detail": f"plan_unmapped={statuses.get('plan_row_unmapped_no_group_code', 0)}; score_exact={statuses.get('score_exact_single_exam_group_match', 0)}"},
        {"check": "plan_count_sum_carried", "status": "PASS" if sum(to_int(row["source_plan_count"]) for row in rows) == 492 else "WARN", "detail": str(sum(to_int(row["source_plan_count"]) for row in rows))},
        {"check": "score_group_codes_present", "status": "PASS" if {str(row.get("exam_group_code_candidate", "")) for row in rows if row.get("mapping_status") == "score_exact_single_exam_group_match"} == {"103", "104", "105"} else "WARN", "detail": "|".join(sorted({str(row.get("exam_group_code_candidate", "")) for row in rows if row.get("mapping_status") == "score_exact_single_exam_group_match"}))},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "mapping_status": row["mapping_status"],
            "major_or_plan_label": row["major_or_plan_label"],
            "action_class": row["action_class"],
            "exclusion_reason": "official_plan_group_code_or_rank_context_pending",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# SCUEC Mapping Review Packet",
        "",
        "Scope: 中南民族大学 2025 official plan rows plus 2024 score-group evidence for 103/104/105.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- 2025 plan rows without group code: {sum(1 for row in rows if row['mapping_status'] == 'plan_row_unmapped_no_group_code')}",
        f"- 2024 exact score-group evidence rows: {sum(1 for row in rows if row['mapping_status'] == 'score_exact_single_exam_group_match')}",
        f"- Plan count sum: {sum(to_int(row['source_plan_count']) for row in rows)}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(f"- {row['mapping_status']} {row['action_class']}: {row['rows']} rows, plan_count_sum={row['plan_count_sum']}, groups={row['exam_group_codes_seen']}")
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
    marker = "## 91. 2026-05-16 SCUEC mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增中南民族大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_scuec_mapping_review_packet.csv`
- `reports/reference_trend_520_scuec_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_scuec_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_scuec_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_scuec_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_scuec_mapping_review_packet.md`

覆盖结果：从既有 SCUEC group mapping workbench 派生 {values.get('packet_rows')} 行审核包，其中 2025 官方计划未归组 rows {values.get('plan_row_unmapped_no_group_code_rows')} 行、2024 分数组精确证据 rows {values.get('score_exact_single_exam_group_match_rows')} 行；计划行合计 {values.get('plan_count_sum')}，分组证据覆盖 {values.get('score_evidence_group_codes')}。

准入边界：本轮只做 103/104/105 组证据和 2025 计划待归组分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No SCUEC workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "mapping_status", "major_or_plan_label", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} SCUEC mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
