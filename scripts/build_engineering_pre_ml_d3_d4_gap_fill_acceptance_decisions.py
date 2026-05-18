from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


REVIEW_DATE = "2026-05-14"
SOURCE_SLUG = "pre_ml_d3_d4_gap_fill_acceptance_decisions"

FIELDS = [
    "school_key",
    "school_name",
    "decision_register_lane",
    "current_gate_status",
    "current_readiness_band",
    "preview_gate_status",
    "preview_readiness_band",
    "manual_acceptance_required",
    "decision_status",
    "review_decision",
    "reviewer",
    "decision_time",
    "evidence_grade",
    "acceptance_class",
    "acceptance_basis",
    "blocking_issues",
    "required_followups",
    "ml_boundary_note",
    "current_data_completeness",
    "preview_data_completeness",
    "current_latest_year",
    "candidate_year",
    "candidate_subject_type",
    "candidate_batch",
    "candidate_group_count",
    "candidate_group_codes",
    "candidate_minimum_score",
    "candidate_minimum_rank",
    "candidate_min_rank_low",
    "candidate_min_rank_high",
    "candidate_source_ids",
    "candidate_data_quality",
    "candidate_fill_fields",
    "candidate_use_scope",
    "candidate_notes",
    "current_gap_signature",
    "preview_gap_signature",
    "resolution_status",
    "plan_source_resolution",
    "score_source_resolution",
    "structured_plan_rows",
    "structured_score_major_rows",
    "structured_score_summary_rows",
    "plan_source_url",
    "score_source_url",
    "decision_options",
    "pass_route",
    "fail_route",
    "record_id",
    "source_record_id",
    "source_slug",
]

SUMMARY_FIELDS = [
    "school_key",
    "school_name",
    "review_decision",
    "evidence_grade",
    "acceptance_class",
    "candidate_minimum_score",
    "candidate_minimum_rank",
    "candidate_group_count",
    "preview_gate_status",
    "preview_gap_signature",
    "required_followups",
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


def keyed(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {normalize_text(row.get("school_key", "")): row for row in rows if row.get("school_key")}


def source_label_followup(school_name: str) -> list[str]:
    if any(term in school_name for term in ["招生网", "本科招生", "招生信息"]):
        return ["public_school_name_label_cleanup_optional"]
    return []


def derive_decision(
    decision_row: dict[str, str],
    preview_row: dict[str, str],
    candidate_row: dict[str, str],
    resolution_row: dict[str, str],
) -> tuple[str, str, str, str, list[str], list[str], list[str]]:
    basis: list[str] = []
    blockers: list[str] = []
    followups: list[str] = []

    lane = normalize_text(decision_row.get("decision_register_lane", ""))
    if lane not in {
        "D3_gap_fill_acceptance_pending_decision",
        "D4_gap_fill_caution_acceptance_pending_decision",
    }:
        blockers.append("not_d3_d4_lane")
    else:
        basis.append(lane)

    if normalize_text(decision_row.get("manual_acceptance_required", "")).lower() != "true":
        blockers.append("manual_acceptance_not_required")
    else:
        basis.append("manual_acceptance_required")

    if normalize_text(candidate_row.get("candidate_data_quality", "")) != "official":
        blockers.append("candidate_source_not_official")
    else:
        basis.append("official_local_gap_fill_candidate")

    if normalize_text(candidate_row.get("candidate_subject_type", "")) != "物理类":
        blockers.append("candidate_subject_type_not_physics")
    else:
        basis.append("physics_subject")

    if normalize_text(candidate_row.get("candidate_batch", "")) != "本科普通批":
        blockers.append("candidate_batch_not_regular_undergrad")
    else:
        basis.append("regular_undergrad_batch")

    if normalize_text(candidate_row.get("candidate_year", "")) != "2025":
        blockers.append("candidate_year_not_2025")
    else:
        basis.append("candidate_year_2025")

    if parse_int(candidate_row.get("candidate_group_count", "")) <= 0:
        blockers.append("candidate_group_count_missing")
    else:
        basis.append("candidate_group_codes_present")

    if parse_int(candidate_row.get("candidate_minimum_score", "")) <= 0:
        blockers.append("candidate_minimum_score_missing")
    else:
        basis.append("candidate_minimum_score_present")

    if parse_int(candidate_row.get("candidate_minimum_rank", "")) <= 0:
        blockers.append("candidate_minimum_rank_missing")
    else:
        basis.append("candidate_minimum_rank_present")

    preview_gate_status = normalize_text(preview_row.get("preview_gate_status", ""))
    preview_gap_signature = normalize_text(preview_row.get("preview_gap_signature", ""))
    preview_data_completeness = normalize_text(preview_row.get("preview_data_completeness", ""))

    if lane == "D3_gap_fill_acceptance_pending_decision":
        if preview_gate_status != "G1_ready_for_human_gpt_review_gate_candidate":
            blockers.append("preview_not_g1_candidate")
        if preview_gap_signature != "complete_enough":
            blockers.append("preview_not_complete_enough")
        if preview_data_completeness != "plan_and_score":
            blockers.append("preview_not_plan_and_score")
        if blockers:
            return (
                "hold_before_ml",
                "D_hold_gap_fill",
                "blocked_gap_fill",
                "completed_gpt_review_decision",
                basis,
                blockers,
                followups or ["none"],
            )
        return (
            "accept_gap_fill_then_review",
            "A_gap_fill_accept_g1_candidate",
            "clean_gap_fill_accept",
            "completed_gpt_review_decision",
            basis + [
                "preview_G1_candidate",
                "preview_complete_enough",
                normalize_text(resolution_row.get("resolution_status", "")) or "resolution_unknown",
            ],
            blockers,
            followups or ["none"],
        )

    followups.extend(source_label_followup(normalize_text(decision_row.get("school_name", ""))))
    if preview_gate_status != "G2_ready_with_caution_for_review_gate_candidate":
        blockers.append("preview_not_g2_caution_candidate")
    if "missing_plan" in preview_gap_signature:
        followups.append("plan_side_still_missing_keep_caution")
    if normalize_text(resolution_row.get("resolution_status", "")) == "fallback_ready":
        followups.append("fallback_source_resolution_keep_isolated")
    if blockers:
        return (
            "hold_before_ml",
            "D_hold_gap_fill",
            "blocked_gap_fill",
            "completed_gpt_review_decision",
            basis,
            blockers,
            followups or ["none"],
        )
    return (
        "accept_gap_fill_with_note",
        "B_gap_fill_accept_g2_caution_candidate",
        "caution_gap_fill_accept",
        "completed_gpt_review_decision",
        basis + ["preview_G2_caution_candidate"],
        blockers,
        followups or ["none"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build GPT-reviewed D3/D4 local gap-fill acceptance decision overlay."
    )
    parser.add_argument(
        "--decision-register",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_decision_register_merged.csv",
    )
    parser.add_argument(
        "--gap-fill-preview",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gap_fill_impact_preview_merged.csv",
    )
    parser.add_argument(
        "--local-gap-fill-candidates",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_local_gap_fill_candidates_merged.csv",
    )
    parser.add_argument(
        "--source-resolution",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_source_resolution_matrix_merged.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_school_summary.csv",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_coverage_rollup.csv",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    decision_rows = read_rows(args.decision_register)
    preview_by_key = keyed(read_rows(args.gap_fill_preview))
    candidate_by_key = keyed(read_rows(args.local_gap_fill_candidates))
    resolution_by_key = keyed(read_rows(args.source_resolution))

    output_rows: list[dict[str, str]] = []
    decision_counts: Counter[str] = Counter()
    grade_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()

    for decision_row in decision_rows:
        lane = normalize_text(decision_row.get("decision_register_lane", ""))
        if lane not in {
            "D3_gap_fill_acceptance_pending_decision",
            "D4_gap_fill_caution_acceptance_pending_decision",
        }:
            continue
        school_key = normalize_text(decision_row.get("school_key", ""))
        preview_row = preview_by_key.get(school_key, {})
        candidate_row = candidate_by_key.get(school_key, {})
        resolution_row = resolution_by_key.get(school_key, {})

        review_decision, evidence_grade, acceptance_class, decision_status, basis, blockers, followups = derive_decision(
            decision_row,
            preview_row,
            candidate_row,
            resolution_row,
        )
        decision_counts[review_decision] += 1
        grade_counts[evidence_grade] += 1
        class_counts[acceptance_class] += 1

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(decision_row.get("school_name", school_key)),
                "decision_register_lane": lane,
                "current_gate_status": normalize_text(preview_row.get("current_gate_status", "")),
                "current_readiness_band": normalize_text(preview_row.get("current_readiness_band", "")),
                "preview_gate_status": normalize_text(preview_row.get("preview_gate_status", "")),
                "preview_readiness_band": normalize_text(preview_row.get("preview_readiness_band", "")),
                "manual_acceptance_required": normalize_text(decision_row.get("manual_acceptance_required", "")),
                "decision_status": decision_status,
                "review_decision": review_decision,
                "reviewer": "codex_gpt_review",
                "decision_time": REVIEW_DATE,
                "evidence_grade": evidence_grade,
                "acceptance_class": acceptance_class,
                "acceptance_basis": "|".join(basis) if basis else "none",
                "blocking_issues": "|".join(blockers) if blockers else "none",
                "required_followups": "|".join(followups),
                "ml_boundary_note": "本地补洞接受只生成复核候选；正式补洞应用层和 canonical/ML 入口仍需后续独立重刷确认",
                "current_data_completeness": normalize_text(preview_row.get("current_data_completeness", "")),
                "preview_data_completeness": normalize_text(preview_row.get("preview_data_completeness", "")),
                "current_latest_year": normalize_text(preview_row.get("current_latest_year", "")),
                "candidate_year": normalize_text(candidate_row.get("candidate_year", "")),
                "candidate_subject_type": normalize_text(candidate_row.get("candidate_subject_type", "")),
                "candidate_batch": normalize_text(candidate_row.get("candidate_batch", "")),
                "candidate_group_count": normalize_text(candidate_row.get("candidate_group_count", "")),
                "candidate_group_codes": normalize_text(candidate_row.get("candidate_group_codes", "")),
                "candidate_minimum_score": normalize_text(candidate_row.get("candidate_minimum_score", "")),
                "candidate_minimum_rank": normalize_text(candidate_row.get("candidate_minimum_rank", "")),
                "candidate_min_rank_low": normalize_text(candidate_row.get("candidate_min_rank_low", "")),
                "candidate_min_rank_high": normalize_text(candidate_row.get("candidate_min_rank_high", "")),
                "candidate_source_ids": normalize_text(candidate_row.get("candidate_source_ids", "")),
                "candidate_data_quality": normalize_text(candidate_row.get("candidate_data_quality", "")),
                "candidate_fill_fields": normalize_text(candidate_row.get("candidate_fill_fields", "")),
                "candidate_use_scope": normalize_text(candidate_row.get("candidate_use_scope", "")),
                "candidate_notes": normalize_text(candidate_row.get("candidate_notes", "")),
                "current_gap_signature": normalize_text(preview_row.get("current_gap_signature", "")),
                "preview_gap_signature": normalize_text(preview_row.get("preview_gap_signature", "")),
                "resolution_status": normalize_text(resolution_row.get("resolution_status", "")),
                "plan_source_resolution": normalize_text(resolution_row.get("plan_source_resolution", "")),
                "score_source_resolution": normalize_text(resolution_row.get("score_source_resolution", "")),
                "structured_plan_rows": normalize_text(resolution_row.get("structured_plan_rows", "")),
                "structured_score_major_rows": normalize_text(resolution_row.get("structured_score_major_rows", "")),
                "structured_score_summary_rows": normalize_text(resolution_row.get("structured_score_summary_rows", "")),
                "plan_source_url": normalize_text(resolution_row.get("plan_source_url", "")),
                "score_source_url": normalize_text(resolution_row.get("score_source_url", "")),
                "decision_options": normalize_text(decision_row.get("decision_options", "")),
                "pass_route": normalize_text(decision_row.get("pass_route", "")),
                "fail_route": normalize_text(decision_row.get("fail_route", "")),
                "record_id": f"{school_key}-d3-d4-gap-fill-acceptance-decision",
                "source_record_id": normalize_text(decision_row.get("record_id", "")),
                "source_slug": SOURCE_SLUG,
            }
        )

    output_rows.sort(key=lambda row: (row["review_decision"], row["school_key"]))
    write_rows(args.output, output_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        [{field: row[field] for field in SUMMARY_FIELDS} for row in output_rows],
        SUMMARY_FIELDS,
    )

    coverage_rows = [
        {"metric": "d3_d4_gap_fill_acceptance_rows", "value": str(len(output_rows))},
        {"metric": "completed_gpt_review_decisions", "value": str(len(output_rows))},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    for decision, count in sorted(decision_counts.items()):
        coverage_rows.append({"metric": f"{decision}_rows", "value": str(count)})
    for grade, count in sorted(grade_counts.items()):
        coverage_rows.append({"metric": f"{grade}_rows", "value": str(count)})
    for acceptance_class, count in sorted(class_counts.items()):
        coverage_rows.append({"metric": f"{acceptance_class}_rows", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote D3/D4 gap-fill acceptance decisions for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
