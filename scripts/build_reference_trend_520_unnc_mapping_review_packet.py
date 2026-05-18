#!/usr/bin/env python3
"""Build a UNNC label/group mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_unnc_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_unnc_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_unnc_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_unnc_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_unnc_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_unnc_mapping_review_packet.md"
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
    plan = to_int(row.get("guangxi_plan_count_provisional", ""))
    label_conf = row.get("proposed_label_confidence", "")
    if status == "ready_for_manual_accept_if_label_and_group303_are_confirmed" and plan > 0:
        if label_conf.startswith("T1"):
            return "ready_positive_plan_group303_t1_label", "manual_accept_or_edit_label_then_accept_group303"
        return "ready_positive_plan_group303_t2_label", "manual_accept_only_after_pdf_visual_label_check"
    if status == "zero_plan_or_label_review_hold":
        if plan == 0:
            return "zero_plan_hold_group303_label_context", "keep_out_of_intake_unless_pdf_review_changes_plan_count"
        return "label_review_hold_positive_plan", "manual_review"
    return "hold_unclassified", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_unnc_review_{idx:04d}",
                "source_workbench_record_id": row.get("workbench_record_id", ""),
                "source_alignment_record_id": row.get("source_alignment_record_id", ""),
                "queue_record_id": row.get("queue_record_id", ""),
                "queue_rank": row.get("queue_rank", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "exam_authority_group_code": row.get("exam_authority_group_code", ""),
                "rank_2024": row.get("rank_2024", ""),
                "rank_2025": row.get("rank_2025", ""),
                "rank_delta_2025_minus_2024": row.get("rank_delta_2025_minus_2024", ""),
                "trend_direction": row.get("trend_direction", ""),
                "text_line_no": row.get("text_line_no", ""),
                "raw_extracted_label": row.get("raw_extracted_label", ""),
                "line_label_status": row.get("line_label_status", ""),
                "proposed_clean_major_label": row.get("proposed_clean_major_label", ""),
                "proposed_label_confidence": row.get("proposed_label_confidence", ""),
                "study_mode": row.get("study_mode", ""),
                "declared_total_plan_if_on_line": row.get("declared_total_plan_if_on_line", ""),
                "guangxi_plan_count_provisional": row.get("guangxi_plan_count_provisional", ""),
                "source_url": row.get("source_url", ""),
                "raw_file_path": row.get("raw_file_path", ""),
                "raw_text_path": row.get("raw_text_path", ""),
                "mapping_status": row.get("mapping_status", ""),
                "suggested_decision_options": row.get("suggested_decision_options", ""),
                "selected_decision": row.get("selected_decision", ""),
                "reviewer": row.get("reviewer", ""),
                "decision_notes": row.get("decision_notes", ""),
                "action_class": action_class,
                "next_action": next_action,
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "unnc_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
                "evidence_note": row.get("evidence_note", ""),
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
                "guangxi_plan_count_sum": sum(to_int(row["guangxi_plan_count_provisional"]) for row in group),
                "label_confidence_seen": "|".join(sorted({str(row.get("proposed_label_confidence", "")) for row in group if str(row.get("proposed_label_confidence", ""))})),
                "exam_group_codes_seen": "|".join(sorted({str(row.get("exam_authority_group_code", "")) for row in group if str(row.get("exam_authority_group_code", ""))})),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    label_conf = Counter(str(row["proposed_label_confidence"]) for row in rows)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from UNNC label/group mapping workbench."},
        {"metric": "ready_for_manual_accept_rows", "value": statuses.get("ready_for_manual_accept_if_label_and_group303_are_confirmed", 0), "note": "Positive-plan rows requiring human label/group acceptance."},
        {"metric": "zero_plan_or_label_review_hold_rows", "value": statuses.get("zero_plan_or_label_review_hold", 0), "note": "Rows with zero Guangxi plan or label review hold."},
        {"metric": "positive_guangxi_plan_rows", "value": sum(1 for row in rows if to_int(row["guangxi_plan_count_provisional"]) > 0), "note": "Rows carrying positive Guangxi physical plan count."},
        {"metric": "guangxi_physical_plan_sum_provisional", "value": sum(to_int(row["guangxi_plan_count_provisional"]) for row in rows), "note": "Checksum from official PDF alignment preview."},
        {"metric": "t1_label_cleanup_rows", "value": sum(v for k, v in label_conf.items() if k.startswith("T1")), "note": "Same-line label cleanup rows."},
        {"metric": "t2_inferred_label_rows", "value": sum(v for k, v in label_conf.items() if k.startswith("T2")), "note": "Rows inferred from preceding PDF label block."},
        {"metric": "manual_decision_rows_present", "value": sum(1 for row in rows if str(row.get("selected_decision", "")).strip()), "note": "Should stay zero until human review."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan source only; no score/rank calibration."},
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
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 17 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "status_counts_match_source_rollup", "status": "PASS" if statuses.get("ready_for_manual_accept_if_label_and_group303_are_confirmed", 0) == 8 and statuses.get("zero_plan_or_label_review_hold", 0) == 9 else "WARN", "detail": f"ready={statuses.get('ready_for_manual_accept_if_label_and_group303_are_confirmed', 0)}; hold={statuses.get('zero_plan_or_label_review_hold', 0)}"},
        {"check": "guangxi_plan_checksum_carried", "status": "PASS" if sum(to_int(row["guangxi_plan_count_provisional"]) for row in rows) == 20 else "WARN", "detail": str(sum(to_int(row["guangxi_plan_count_provisional"]) for row in rows))},
        {"check": "all_rows_group303_context", "status": "PASS" if {str(row.get("exam_authority_group_code", "")) for row in rows} == {"303"} else "WARN", "detail": "|".join(sorted({str(row.get("exam_authority_group_code", "")) for row in rows}))},
        {"check": "manual_decision_fields_blank", "status": "PASS" if not any(str(row.get("selected_decision", "")).strip() or str(row.get("reviewer", "")).strip() or str(row.get("decision_notes", "")).strip() for row in rows) else "WARN", "detail": "selected_decision/reviewer/decision_notes checked"},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "mapping_status": row["mapping_status"],
            "proposed_clean_major_label": row["proposed_clean_major_label"],
            "action_class": row["action_class"],
            "exclusion_reason": "human_label_group303_acceptance_pending",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# UNNC Mapping Review Packet",
        "",
        "Scope: 宁波诺丁汉大学 2025 official PDF label/group303 mapping review packet.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Ready positive-plan rows: {sum(1 for row in rows if row['mapping_status'] == 'ready_for_manual_accept_if_label_and_group303_are_confirmed')}",
        f"- Zero-plan or label-review hold rows: {sum(1 for row in rows if row['mapping_status'] == 'zero_plan_or_label_review_hold')}",
        f"- Provisional Guangxi physical plan sum: {sum(to_int(row['guangxi_plan_count_provisional']) for row in rows)}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(f"- {row['mapping_status']} {row['action_class']}: {row['rows']} rows, plan_sum={row['guangxi_plan_count_sum']}, groups={row['exam_group_codes_seen']}")
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
    marker = "## 93. 2026-05-16 UNNC mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增宁波诺丁汉大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_unnc_mapping_review_packet.csv`
- `reports/reference_trend_520_unnc_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_unnc_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_unnc_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_unnc_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_unnc_mapping_review_packet.md`

覆盖结果：从既有 UNNC label/group mapping workbench 派生 {values.get('packet_rows')} 行审核包，其中可人工接受的正计划 rows {values.get('ready_for_manual_accept_rows')} 行，zero-plan/label-review hold rows {values.get('zero_plan_or_label_review_hold_rows')} 行；广西物理计划 checksum 仍为 {values.get('guangxi_physical_plan_sum_provisional')}。

准入边界：本轮只做 PDF 标签清洗与 303 组人工接受分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No UNNC workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "mapping_status", "proposed_clean_major_label", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} UNNC mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
