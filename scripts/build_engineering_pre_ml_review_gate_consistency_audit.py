from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "readiness_band",
    "gate_status",
    "candidate_pack_lane",
    "checklist_lane",
    "manual_acceptance_required",
    "readiness_row_present",
    "handoff_pack_row_present",
    "review_workbench_row_present",
    "gate_status_row_present",
    "candidate_pack_row_present",
    "review_gate_checklist_row_present",
    "pipeline_handoff_pack_rows",
    "pipeline_review_workbench_rows",
    "pipeline_gate_status_rows",
    "pipeline_candidate_pack_rows",
    "pipeline_review_gate_checklist_rows",
    "human_gpt_review_gate_readiness",
    "consistency_status",
    "consistency_issues",
    "next_local_action",
    "ml_boundary_note",
    "record_id",
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


def truthy(value: str) -> bool:
    return normalize_text(value).lower() in {"1", "true", "yes"}


def by_school(rows: list[dict[str, str]], key_field: str = "school_key") -> dict[str, dict[str, str]]:
    return {normalize_text(row.get(key_field, "")): row for row in rows if normalize_text(row.get(key_field, ""))}


def bool_text(value: bool) -> str:
    return str(bool(value)).lower()


def derive_review_readiness(
    checklist_row: dict[str, str],
    candidate_row: dict[str, str],
    gate_row: dict[str, str],
) -> str:
    if checklist_row:
        if normalize_text(checklist_row.get("manual_acceptance_required", "")).lower() == "true":
            return "needs_manual_gap_fill_acceptance_before_review_gate"
        return "ready_for_human_gpt_review_gate"
    gate_status = normalize_text(gate_row.get("gate_status", ""))
    if gate_status == "G3_local_gap_fill_needed":
        return "local_gap_fill_needed_before_review_gate"
    if gate_status == "G4_blocked_or_manual_route":
        return "blocked_or_manual_route_before_review_gate"
    if candidate_row:
        return "candidate_pack_present_checklist_missing"
    return "not_ready_for_review_gate"


def derive_next_action(readiness: str) -> str:
    if readiness == "ready_for_human_gpt_review_gate":
        return "进入人工/GPT复核闸门；复核通过前不启动机器学习"
    if readiness == "needs_manual_gap_fill_acceptance_before_review_gate":
        return "先人工接受本地补洞候选，再重刷正式层并进入复核闸门"
    if readiness == "local_gap_fill_needed_before_review_gate":
        return "继续本地补洞或保留待人工确认"
    if readiness == "blocked_or_manual_route_before_review_gate":
        return "保持冷队列或人工路线；需要新增网页/接口/登录态时停止"
    if readiness == "candidate_pack_present_checklist_missing":
        return "重刷review gate checklist"
    return "暂不进入复核闸门"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit consistency across local pre-ML review-gate artifacts without entering ML."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="Target school matrix CSV.",
    )
    parser.add_argument(
        "--readiness",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_model_readiness_merged.csv",
        help="Pre-ML readiness CSV.",
    )
    parser.add_argument(
        "--handoff-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_handoff_pack_merged.csv",
        help="Pre-ML handoff pack CSV.",
    )
    parser.add_argument(
        "--review-workbench",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_workbench_merged.csv",
        help="Pre-ML review workbench CSV.",
    )
    parser.add_argument(
        "--gate-status",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gate_status_merged.csv",
        help="Pre-ML gate status CSV.",
    )
    parser.add_argument(
        "--candidate-pack",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_candidate_pack_merged.csv",
        help="Review-gate candidate pack CSV.",
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
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Engineering pipeline status CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_consistency_audit_merged.csv",
        help="Output consistency audit CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_consistency_audit_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_consistency_audit_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    matrix_rows = read_rows(args.matrix)
    readiness_by_key = by_school(read_rows(args.readiness))
    handoff_by_key = by_school(read_rows(args.handoff_pack))
    workbench_by_key = by_school(read_rows(args.review_workbench))
    gate_by_key = by_school(read_rows(args.gate_status))
    candidate_by_key = by_school(read_rows(args.candidate_pack))
    checklist_by_key = by_school(read_rows(args.review_gate_checklist))
    pipeline_by_key = by_school(read_rows(args.pipeline_status))

    output_rows: list[dict[str, str]] = []
    issue_counts: Counter[str] = Counter()
    readiness_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()

    for target in matrix_rows:
        key = normalize_text(target.get("seed_id", ""))
        if not key:
            continue
        school_name = normalize_text(target.get("source_name", key))
        readiness_row = readiness_by_key.get(key, {})
        handoff_row = handoff_by_key.get(key, {})
        workbench_row = workbench_by_key.get(key, {})
        gate_row = gate_by_key.get(key, {})
        candidate_row = candidate_by_key.get(key, {})
        checklist_row = checklist_by_key.get(key, {})
        pipeline_row = pipeline_by_key.get(key, {})

        readiness_band = normalize_text(readiness_row.get("readiness_band", ""))
        gate_status = normalize_text(gate_row.get("gate_status", ""))
        manual_required = normalize_text(
            checklist_row.get("manual_acceptance_required")
            or candidate_row.get("manual_acceptance_required", "")
        ).lower()
        issues: list[str] = []

        if not readiness_row:
            issues.append("missing_readiness_row")
        if not gate_row:
            issues.append("missing_gate_status_row")
        if readiness_band in {"M1_ready_for_pre_ml_review", "M2_comparable_ready_with_note"}:
            if not handoff_row:
                issues.append("ready_school_missing_handoff_pack")
            if not workbench_row:
                issues.append("ready_school_missing_review_workbench")
        if gate_status in {"G1_ready_for_human_gpt_review_gate", "G2_ready_with_caution_for_review_gate"}:
            if not candidate_row:
                issues.append("direct_gate_school_missing_candidate_pack")
            if not checklist_row:
                issues.append("direct_gate_school_missing_checklist")
        if candidate_row and not checklist_row:
            issues.append("candidate_pack_without_checklist")
        if checklist_row and not candidate_row:
            issues.append("checklist_without_candidate_pack")

        pipeline_expectations = [
            ("handoff_pack", bool(handoff_row), "pre_ml_handoff_pack_rows"),
            ("review_workbench", bool(workbench_row), "pre_ml_review_workbench_rows"),
            ("gate_status", bool(gate_row), "pre_ml_gate_status_rows"),
            ("candidate_pack", bool(candidate_row), "pre_ml_review_gate_candidate_pack_rows"),
            ("review_gate_checklist", bool(checklist_row), "pre_ml_review_gate_checklist_rows"),
        ]
        for label, present, pipeline_field in pipeline_expectations:
            if present != truthy(pipeline_row.get(pipeline_field, "")):
                issues.append(f"pipeline_{label}_flag_mismatch")

        review_readiness = derive_review_readiness(checklist_row, candidate_row, gate_row)
        consistency_status = "ok" if not issues else "needs_attention"
        for issue in issues:
            issue_counts[issue] += 1
        readiness_counts[review_readiness] += 1
        status_counts[consistency_status] += 1

        output_rows.append(
            {
                "school_key": key,
                "school_name": school_name,
                "readiness_band": readiness_band,
                "gate_status": gate_status,
                "candidate_pack_lane": normalize_text(candidate_row.get("candidate_pack_lane", "")),
                "checklist_lane": normalize_text(checklist_row.get("checklist_lane", "")),
                "manual_acceptance_required": manual_required or "false",
                "readiness_row_present": bool_text(bool(readiness_row)),
                "handoff_pack_row_present": bool_text(bool(handoff_row)),
                "review_workbench_row_present": bool_text(bool(workbench_row)),
                "gate_status_row_present": bool_text(bool(gate_row)),
                "candidate_pack_row_present": bool_text(bool(candidate_row)),
                "review_gate_checklist_row_present": bool_text(bool(checklist_row)),
                "pipeline_handoff_pack_rows": normalize_text(pipeline_row.get("pre_ml_handoff_pack_rows", "")),
                "pipeline_review_workbench_rows": normalize_text(pipeline_row.get("pre_ml_review_workbench_rows", "")),
                "pipeline_gate_status_rows": normalize_text(pipeline_row.get("pre_ml_gate_status_rows", "")),
                "pipeline_candidate_pack_rows": normalize_text(
                    pipeline_row.get("pre_ml_review_gate_candidate_pack_rows", "")
                ),
                "pipeline_review_gate_checklist_rows": normalize_text(
                    pipeline_row.get("pre_ml_review_gate_checklist_rows", "")
                ),
                "human_gpt_review_gate_readiness": review_readiness,
                "consistency_status": consistency_status,
                "consistency_issues": "|".join(issues) if issues else "none",
                "next_local_action": derive_next_action(review_readiness),
                "ml_boundary_note": "只到人工/GPT复核闸门；复核通过前禁止启动机器学习",
                "record_id": f"{key}-pre-ml-review-gate-consistency-audit",
                "source_slug": "pre_ml_review_gate_consistency_audit",
            }
        )

    output_rows.sort(key=lambda row: row["school_key"])
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "human_gpt_review_gate_readiness": row["human_gpt_review_gate_readiness"],
            "consistency_status": row["consistency_status"],
            "consistency_issues": row["consistency_issues"],
            "next_local_action": row["next_local_action"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "human_gpt_review_gate_readiness",
            "consistency_status",
            "consistency_issues",
            "next_local_action",
        ],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "review_gate_consistency_audit_schools", "value": str(len(output_rows))},
        {"metric": "review_gate_consistency_audit_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "consistency_ok_schools", "value": str(status_counts.get("ok", 0))},
        {"metric": "consistency_needs_attention_schools", "value": str(status_counts.get("needs_attention", 0))},
    ]
    for readiness, count in sorted(readiness_counts.items()):
        coverage_rows.append({"metric": f"{readiness}_schools", "value": str(count)})
    for issue, count in sorted(issue_counts.items()):
        coverage_rows.append({"metric": f"{issue}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML review-gate consistency audit for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
