from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "decision_register_lane",
    "decision_priority",
    "decision_status",
    "review_decision",
    "reviewer",
    "decision_time",
    "decision_notes",
    "manual_acceptance_required",
    "human_gpt_review_gate_route",
    "checklist_lane",
    "gate_status",
    "readiness_band",
    "data_completeness",
    "minimum_score",
    "minimum_rank",
    "required_checks",
    "acceptance_question",
    "decision_options",
    "pass_route",
    "fail_route",
    "ml_boundary_note",
    "evidence_completeness",
    "plan_source_url",
    "score_source_url",
    "review_focus_flags",
    "review_gate_notes",
    "record_id",
    "source_record_id",
    "source_slug",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def parse_int(value: str) -> int:
    text = normalize_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def decision_lane(row: dict[str, str]) -> tuple[str, str]:
    checklist_lane = normalize_text(row.get("checklist_lane", ""))
    if checklist_lane == "L1_current_clean_review_checklist":
        return "D1_ready_now_clean_pending_decision", "1"
    if checklist_lane == "L2_current_caution_review_checklist":
        return "D2_ready_now_caution_pending_decision", "2"
    if checklist_lane == "L3_gap_fill_acceptance_then_clean_checklist":
        return "D3_gap_fill_acceptance_pending_decision", "3"
    if checklist_lane == "L4_gap_fill_acceptance_then_caution_checklist":
        return "D4_gap_fill_caution_acceptance_pending_decision", "4"
    return "D9_out_of_scope", "9"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a pending human/GPT review-gate decision register without entering ML."
    )
    parser.add_argument(
        "--review-gate-checklist",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_checklist_merged.csv",
        help="Review-gate checklist CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_decision_register_merged.csv",
        help="Output review-gate decision register CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_decision_register_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_decision_register_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    checklist_rows = read_rows(args.review_gate_checklist)

    output_rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    manual_acceptance_count = 0
    direct_review_count = 0

    for row in checklist_rows:
        lane, priority = decision_lane(row)
        if lane == "D9_out_of_scope":
            continue
        school_key = normalize_text(row.get("school_key", ""))
        manual_required = normalize_text(row.get("manual_acceptance_required", "")).lower() == "true"
        if manual_required:
            manual_acceptance_count += 1
        else:
            direct_review_count += 1
        lane_counts[lane] += 1

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "decision_register_lane": lane,
                "decision_priority": priority,
                "decision_status": "pending_human_gpt_review_decision",
                "review_decision": "",
                "reviewer": "",
                "decision_time": "",
                "decision_notes": "",
                "manual_acceptance_required": str(manual_required).lower(),
                "human_gpt_review_gate_route": normalize_text(row.get("human_gpt_review_gate_route", "")),
                "checklist_lane": normalize_text(row.get("checklist_lane", "")),
                "gate_status": normalize_text(row.get("gate_status", "")),
                "readiness_band": normalize_text(row.get("readiness_band", "")),
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "required_checks": normalize_text(row.get("required_checks", "")),
                "acceptance_question": normalize_text(row.get("acceptance_question", "")),
                "decision_options": normalize_text(row.get("decision_options", "")),
                "pass_route": normalize_text(row.get("pass_route", "")),
                "fail_route": normalize_text(row.get("fail_route", "")),
                "ml_boundary_note": "本登记表只记录人工/GPT复核决定；决策完成并人工确认前不得启动机器学习",
                "evidence_completeness": normalize_text(row.get("evidence_completeness", "")),
                "plan_source_url": normalize_text(row.get("plan_source_url", "")),
                "score_source_url": normalize_text(row.get("score_source_url", "")),
                "review_focus_flags": normalize_text(row.get("review_focus_flags", "")),
                "review_gate_notes": normalize_text(row.get("review_gate_notes", "")),
                "record_id": f"{school_key}-pre-ml-review-gate-decision-register",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "pre_ml_review_gate_decision_register",
            }
        )

    output_rows.sort(
        key=lambda row: (
            parse_int(row["decision_priority"]),
            row["manual_acceptance_required"],
            row["school_key"],
        )
    )
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "decision_register_lane": row["decision_register_lane"],
            "decision_status": row["decision_status"],
            "manual_acceptance_required": row["manual_acceptance_required"],
            "decision_options": row["decision_options"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "decision_register_lane",
            "decision_status",
            "manual_acceptance_required",
            "decision_options",
        ],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "review_gate_decision_register_schools", "value": str(len(output_rows))},
        {"metric": "review_gate_decision_register_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "pending_review_decisions", "value": str(len(output_rows))},
        {"metric": "completed_review_decisions", "value": "0"},
        {"metric": "direct_human_gpt_review_gate_decisions", "value": str(direct_review_count)},
        {"metric": "manual_gap_fill_acceptance_decisions", "value": str(manual_acceptance_count)},
    ]
    for lane, count in sorted(lane_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML review-gate decision register for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
