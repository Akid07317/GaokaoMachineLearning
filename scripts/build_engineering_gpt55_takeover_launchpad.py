from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "takeover_lane",
    "takeover_priority",
    "decision_status",
    "manual_acceptance_required",
    "human_gpt_review_gate_route",
    "gate_status",
    "readiness_band",
    "candidate_pack_lane",
    "checklist_lane",
    "review_lane",
    "review_risk_score",
    "latest_year",
    "reference_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "plan_source_url",
    "score_source_url",
    "takeover_primary_doc_path",
    "takeover_project_plan_path",
    "takeover_data_root_path",
    "takeover_rule",
    "switch_back_trigger",
    "takeover_notes",
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


def build_notes(
    decision_row: dict[str, str],
    checklist_row: dict[str, str],
    workbench_row: dict[str, str],
) -> str:
    notes = []
    if normalize_text(decision_row.get("manual_acceptance_required", "")) == "true":
        notes.append("先做人类接受本地补洞候选")
    if normalize_text(workbench_row.get("review_lane", "")) == "R1_clean_ready":
        notes.append("本地证据链较干净")
    else:
        prompt = normalize_text(workbench_row.get("review_prompt", ""))
        if prompt:
            notes.append(prompt)
    ml_boundary = normalize_text(checklist_row.get("ml_boundary_note", ""))
    if ml_boundary:
        notes.append(ml_boundary)
    if not notes:
        notes.append("只使用本地成果推进 pre-ML 复核，不做新增网页搜集")
    return "；".join(notes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a GPT-5.5 takeover launchpad for pre-ML Guangxi engineering schools."
    )
    parser.add_argument(
        "--decision-register",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_gate_decision_register_merged.csv",
        help="Review gate decision register CSV.",
    )
    parser.add_argument(
        "--candidate-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_gate_candidate_pack_merged.csv",
        help="Review gate candidate pack CSV.",
    )
    parser.add_argument(
        "--checklist",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_gate_checklist_merged.csv",
        help="Review gate checklist CSV.",
    )
    parser.add_argument(
        "--workbench",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_workbench_merged.csv",
        help="Pre-ML review workbench CSV.",
    )
    parser.add_argument(
        "--handoff-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_handoff_pack_merged.csv",
        help="Pre-ML handoff pack CSV.",
    )
    parser.add_argument(
        "--primary-doc-path",
        type=str,
        default="/Users/don/Documents/New project/docs/gpt55_takeover_handoff.md",
        help="Absolute path to the main GPT-5.5 takeover doc.",
    )
    parser.add_argument(
        "--project-plan-doc-path",
        type=str,
        default="/Users/don/Documents/New project/docs/guangxi_gaokao_project_plan.md",
        help="Absolute path to the project plan doc.",
    )
    parser.add_argument(
        "--data-root-path",
        type=str,
        default="/Users/don/Documents/New project/clean_data/engineering_guangxi_seed",
        help="Absolute path to the local data root for handoff tables.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_gpt55_takeover_launchpad_merged.csv",
        help="Output takeover launchpad CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_gpt55_takeover_launchpad_school_summary.csv",
        help="School summary CSV output.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_gpt55_takeover_launchpad_coverage_rollup.csv",
        help="Coverage rollup CSV output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    decision_rows = read_rows(args.decision_register)
    candidate_rows = read_rows(args.candidate_pack)
    checklist_rows = read_rows(args.checklist)
    workbench_rows = read_rows(args.workbench)
    handoff_rows = read_rows(args.handoff_pack)

    candidate_by_key = {normalize_text(row.get("school_key", "")): row for row in candidate_rows}
    checklist_by_key = {normalize_text(row.get("school_key", "")): row for row in checklist_rows}
    workbench_by_key = {normalize_text(row.get("school_key", "")): row for row in workbench_rows}
    handoff_by_key = {normalize_text(row.get("school_key", "")): row for row in handoff_rows}

    rows: list[dict[str, str]] = []
    manual_accept_count = 0
    ready_now_count = 0
    with_note_count = 0
    with_plan_source = 0
    with_score_source = 0

    for decision_row in decision_rows:
        school_key = normalize_text(decision_row.get("school_key", ""))
        if not school_key:
            continue
        candidate_row = candidate_by_key.get(school_key, {})
        checklist_row = checklist_by_key.get(school_key, {})
        workbench_row = workbench_by_key.get(school_key, {})
        handoff_row = handoff_by_key.get(school_key, {})

        manual_accept = normalize_text(decision_row.get("manual_acceptance_required", ""))
        if manual_accept == "true":
            manual_accept_count += 1
        lane = normalize_text(decision_row.get("decision_register_lane", ""))
        if lane.startswith("D1") or lane.startswith("D2"):
            ready_now_count += 1
        if lane.startswith("D2") or lane.startswith("D4"):
            with_note_count += 1

        plan_source_url = normalize_text(handoff_row.get("plan_source_url", "") or workbench_row.get("plan_source_url", ""))
        score_source_url = normalize_text(handoff_row.get("score_source_url", "") or workbench_row.get("score_source_url", ""))
        if plan_source_url:
            with_plan_source += 1
        if score_source_url:
            with_score_source += 1

        rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(decision_row.get("school_name", school_key)),
                "takeover_lane": lane,
                "takeover_priority": normalize_text(decision_row.get("decision_priority", "")),
                "decision_status": normalize_text(decision_row.get("decision_status", "")),
                "manual_acceptance_required": manual_accept,
                "human_gpt_review_gate_route": normalize_text(decision_row.get("human_gpt_review_gate_route", "")),
                "gate_status": normalize_text(decision_row.get("gate_status", "")),
                "readiness_band": normalize_text(decision_row.get("readiness_band", "")),
                "candidate_pack_lane": normalize_text(candidate_row.get("candidate_pack_lane", "")),
                "checklist_lane": normalize_text(checklist_row.get("checklist_lane", "")),
                "review_lane": normalize_text(workbench_row.get("review_lane", "")),
                "review_risk_score": normalize_text(workbench_row.get("review_risk_score", "")),
                "latest_year": normalize_text(candidate_row.get("latest_year", "")),
                "reference_year": normalize_text(candidate_row.get("reference_year", "")),
                "data_completeness": normalize_text(candidate_row.get("data_completeness", "")),
                "total_plan_count": normalize_text(candidate_row.get("total_plan_count", "")),
                "minimum_score": normalize_text(candidate_row.get("minimum_score", "")),
                "minimum_rank": normalize_text(candidate_row.get("minimum_rank", "")),
                "trend_available": normalize_text(candidate_row.get("trend_available", "")),
                "trend_signal": normalize_text(candidate_row.get("trend_signal", "")),
                "plan_source_url": plan_source_url,
                "score_source_url": score_source_url,
                "takeover_primary_doc_path": args.primary_doc_path,
                "takeover_project_plan_path": args.project_plan_doc_path,
                "takeover_data_root_path": args.data_root_path,
                "takeover_rule": "NO_NETWORK_COLLECTION_USE_LOCAL_ARTIFACTS_ONLY",
                "switch_back_trigger": "new_web_needed|403_unlock|login_required|machine_learning_gate",
                "takeover_notes": build_notes(decision_row, checklist_row, workbench_row),
                "record_id": f"{school_key}-gpt55-takeover-launchpad",
                "source_record_id": normalize_text(decision_row.get("record_id", "")),
                "source_slug": "gpt55_takeover_launchpad",
            }
        )

    rows.sort(key=lambda item: (item["takeover_priority"], item["school_key"]))
    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "gpt55_takeover_launchpad_rows": "1",
        }
        for row in rows
    ]

    write_rows(args.output, rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "gpt55_takeover_launchpad_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "gpt55_takeover_launchpad_schools", "value": str(len(rows))},
        {"metric": "gpt55_takeover_launchpad_coverage_ratio", "value": f"{len(rows) / TARGET_TOTAL:.4f}"},
        {"metric": "gpt55_takeover_ready_now_schools", "value": str(ready_now_count)},
        {"metric": "gpt55_takeover_with_note_schools", "value": str(with_note_count)},
        {"metric": "gpt55_takeover_manual_acceptance_required_schools", "value": str(manual_accept_count)},
        {"metric": "gpt55_takeover_with_plan_source_schools", "value": str(with_plan_source)},
        {"metric": "gpt55_takeover_with_score_source_schools", "value": str(with_score_source)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(
        f"Wrote GPT-5.5 takeover launchpad for {len(rows)} schools "
        f"({ready_now_count} ready-now, {manual_accept_count} manual-acceptance-required)."
    )


if __name__ == "__main__":
    main()
