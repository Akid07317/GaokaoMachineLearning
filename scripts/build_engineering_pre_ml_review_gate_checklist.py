from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "checklist_lane",
    "checklist_priority",
    "checklist_status",
    "manual_acceptance_required",
    "human_gpt_review_gate_route",
    "source_layer",
    "candidate_pack_lane",
    "gate_status",
    "readiness_band",
    "data_completeness",
    "required_checks",
    "acceptance_question",
    "decision_options",
    "pass_route",
    "fail_route",
    "ml_boundary_note",
    "review_focus_flags",
    "latest_year",
    "reference_year",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "gap_signature",
    "resolution_status",
    "evidence_completeness",
    "plan_source_url",
    "score_source_url",
    "review_gate_action",
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


def evidence_completeness(row: dict[str, str]) -> str:
    plan_url = normalize_text(row.get("plan_source_url", ""))
    score_url = normalize_text(row.get("score_source_url", ""))
    if plan_url and score_url:
        return "plan_and_score_source_links_present"
    if plan_url:
        return "plan_source_link_present_score_link_missing"
    if score_url:
        return "score_source_link_present_plan_link_missing"
    if normalize_text(row.get("source_layer", "")) == "gap_fill_impact_preview":
        return "local_gap_fill_preview_source_record_only"
    return "source_links_missing"


def checklist_profile(candidate_lane: str, manual_acceptance_required: str) -> dict[str, str]:
    lane = normalize_text(candidate_lane)
    manual_required = normalize_text(manual_acceptance_required).lower() == "true"
    if lane == "C1_current_clean_review_gate":
        return {
            "checklist_lane": "L1_current_clean_review_checklist",
            "checklist_priority": "1",
            "human_gpt_review_gate_route": "ready_now",
            "required_checks": "核对学校名|核对2025计划数|核对最低分/位次|核对计划与分数来源回链|确认复核通过前不进ML",
            "acceptance_question": "是否确认当前G1完整口径可进入人工/GPT复核闸门",
            "decision_options": "accept_for_review_gate|request_row_fix|hold_before_ml",
            "pass_route": "标记为复核闸门通过候选；由人工决定是否进入下一阶段ML准备",
            "fail_route": "退回对应来源层或字段缺口层修正",
        }
    if lane == "C2_current_caution_review_gate":
        return {
            "checklist_lane": "L2_current_caution_review_checklist",
            "checklist_priority": "2",
            "human_gpt_review_gate_route": "ready_now_with_caution",
            "required_checks": "核对可比年份|核对缺字段备注|核对来源精度|核对趋势/分数/位次一致性|确认风险备注足够清楚",
            "acceptance_question": "是否接受当前G2带备注口径进入人工/GPT复核闸门",
            "decision_options": "accept_with_note|request_note_fix|hold_before_ml",
            "pass_route": "带备注进入复核闸门；复核通过前仍不生成ML输入",
            "fail_route": "退回review workbench或backlog补备注/补字段",
        }
    if lane == "C3_candidate_clean_after_gap_fill_acceptance":
        return {
            "checklist_lane": "L3_gap_fill_acceptance_then_clean_checklist",
            "checklist_priority": "3",
            "human_gpt_review_gate_route": "after_manual_gap_fill_acceptance",
            "required_checks": "先接受本地补洞候选|核对投档线种子来源|核对最低分/位次候选|确认补洞不自动写入ML|接受后重刷正式层",
            "acceptance_question": "是否接受本地补洞候选并把该校推进为G1候选",
            "decision_options": "accept_gap_fill_then_review|reject_gap_fill|hold_before_ml",
            "pass_route": "生成正式补洞应用层后重刷readiness/handoff/workbench/gate status",
            "fail_route": "保持G3本地补洞待处理状态",
        }
    if lane == "C4_candidate_caution_after_gap_fill_acceptance":
        return {
            "checklist_lane": "L4_gap_fill_acceptance_then_caution_checklist",
            "checklist_priority": "4",
            "human_gpt_review_gate_route": "after_manual_gap_fill_acceptance_with_caution",
            "required_checks": "先接受本地补洞候选|核对仍缺计划侧字段|核对投档线种子来源|确认G2备注充分|接受后重刷正式层",
            "acceptance_question": "是否接受本地补洞候选并把该校推进为G2带备注候选",
            "decision_options": "accept_gap_fill_with_note|reject_gap_fill|hold_before_ml",
            "pass_route": "生成正式补洞应用层后以带备注状态重刷闸门材料",
            "fail_route": "保持G3本地补洞待处理状态",
        }
    return {
        "checklist_lane": "L9_out_of_scope",
        "checklist_priority": "9",
        "human_gpt_review_gate_route": "not_ready",
        "required_checks": "暂不进入复核闸门",
        "acceptance_question": "是否保持在闸门外",
        "decision_options": "hold_before_ml",
        "pass_route": "保持闸门外",
        "fail_route": "保持闸门外",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a per-school human/GPT review-gate checklist without entering ML."
    )
    parser.add_argument(
        "--candidate-pack",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_candidate_pack_merged.csv",
        help="Pre-ML review gate candidate pack CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_checklist_merged.csv",
        help="Output review-gate checklist CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_checklist_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_checklist_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    candidate_rows = read_rows(args.candidate_pack)

    output_rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    manual_acceptance_count = 0
    direct_review_count = 0

    for row in candidate_rows:
        profile = checklist_profile(
            row.get("candidate_pack_lane", ""),
            row.get("manual_acceptance_required", ""),
        )
        if profile["checklist_lane"] == "L9_out_of_scope":
            continue
        school_key = normalize_text(row.get("school_key", ""))
        manual_required = normalize_text(row.get("manual_acceptance_required", "")).lower() == "true"
        if manual_required:
            manual_acceptance_count += 1
        else:
            direct_review_count += 1
        lane_counts[profile["checklist_lane"]] += 1
        route_counts[profile["human_gpt_review_gate_route"]] += 1

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "checklist_lane": profile["checklist_lane"],
                "checklist_priority": profile["checklist_priority"],
                "checklist_status": "pending_human_gpt_review",
                "manual_acceptance_required": str(manual_required).lower(),
                "human_gpt_review_gate_route": profile["human_gpt_review_gate_route"],
                "source_layer": normalize_text(row.get("source_layer", "")),
                "candidate_pack_lane": normalize_text(row.get("candidate_pack_lane", "")),
                "gate_status": normalize_text(row.get("gate_status", "")),
                "readiness_band": normalize_text(row.get("readiness_band", "")),
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "required_checks": profile["required_checks"],
                "acceptance_question": profile["acceptance_question"],
                "decision_options": profile["decision_options"],
                "pass_route": profile["pass_route"],
                "fail_route": profile["fail_route"],
                "ml_boundary_note": "本表只服务人工/GPT复核闸门；复核与人工确认前不得训练、特征选择、校准或回测",
                "review_focus_flags": normalize_text(row.get("review_focus_flags", "")),
                "latest_year": normalize_text(row.get("latest_year", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "gap_signature": normalize_text(row.get("gap_signature", "")),
                "resolution_status": normalize_text(row.get("resolution_status", "")),
                "evidence_completeness": evidence_completeness(row),
                "plan_source_url": normalize_text(row.get("plan_source_url", "")),
                "score_source_url": normalize_text(row.get("score_source_url", "")),
                "review_gate_action": normalize_text(row.get("review_gate_action", "")),
                "review_gate_notes": normalize_text(row.get("review_gate_notes", "")),
                "record_id": f"{school_key}-pre-ml-review-gate-checklist",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "pre_ml_review_gate_checklist",
            }
        )

    output_rows.sort(
        key=lambda row: (
            parse_int(row["checklist_priority"]),
            row["manual_acceptance_required"],
            row["school_key"],
        )
    )
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "checklist_lane": row["checklist_lane"],
            "manual_acceptance_required": row["manual_acceptance_required"],
            "human_gpt_review_gate_route": row["human_gpt_review_gate_route"],
            "gate_status": row["gate_status"],
            "minimum_score": row["minimum_score"],
            "minimum_rank": row["minimum_rank"],
            "checklist_status": row["checklist_status"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "checklist_lane",
            "manual_acceptance_required",
            "human_gpt_review_gate_route",
            "gate_status",
            "minimum_score",
            "minimum_rank",
            "checklist_status",
        ],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "review_gate_checklist_schools", "value": str(len(output_rows))},
        {"metric": "review_gate_checklist_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "direct_human_gpt_review_gate_candidates", "value": str(direct_review_count)},
        {"metric": "manual_gap_fill_acceptance_required_schools", "value": str(manual_acceptance_count)},
        {"metric": "not_in_review_gate_checklist_schools", "value": str(TARGET_TOTAL - len(output_rows))},
    ]
    for lane, count in sorted(lane_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    for route, count in sorted(route_counts.items()):
        coverage_rows.append({"metric": f"{route}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML review-gate checklist for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
