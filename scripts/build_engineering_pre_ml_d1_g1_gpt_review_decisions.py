from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


REVIEW_DATE = "2026-05-13"
SOURCE_SLUG = "pre_ml_d1_g1_gpt_review_decisions"

FIELDS = [
    "school_key",
    "school_name",
    "decision_register_lane",
    "gate_status",
    "readiness_band",
    "review_lane",
    "review_risk_score",
    "decision_status",
    "review_decision",
    "reviewer",
    "decision_time",
    "evidence_grade",
    "acceptance_basis",
    "blocking_issues",
    "residual_followups",
    "ml_boundary_note",
    "reference_year",
    "latest_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "resolution_status",
    "plan_source_resolution",
    "score_source_resolution",
    "structured_plan_rows",
    "structured_score_major_rows",
    "structured_score_summary_rows",
    "plan_source_url",
    "score_source_url",
    "required_checks",
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
    "minimum_score",
    "minimum_rank",
    "total_plan_count",
    "trend_signal",
    "resolution_status",
    "residual_followups",
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


def derive_decision(
    decision_row: dict[str, str],
    gate_row: dict[str, str],
    workbench_row: dict[str, str],
    resolution_row: dict[str, str],
) -> tuple[str, str, str, list[str], list[str], list[str]]:
    blockers: list[str] = []
    basis: list[str] = []
    followups: list[str] = []

    if normalize_text(decision_row.get("decision_register_lane", "")) != "D1_ready_now_clean_pending_decision":
        blockers.append("not_d1_lane")
    else:
        basis.append("D1_ready_now_clean_pending_decision")

    if normalize_text(gate_row.get("gate_status", "")) != "G1_ready_for_human_gpt_review_gate":
        blockers.append("not_g1_gate")
    else:
        basis.append("G1_ready_for_human_gpt_review_gate")

    if normalize_text(gate_row.get("readiness_band", "")) != "M1_ready_for_pre_ml_review":
        blockers.append("not_m1_readiness")
    else:
        basis.append("M1_ready_for_pre_ml_review")

    if normalize_text(gate_row.get("data_completeness", "")) != "plan_and_score":
        blockers.append("missing_plan_or_score")
    else:
        basis.append("plan_and_score")

    if normalize_text(gate_row.get("reference_year", "")) != normalize_text(gate_row.get("latest_year", "")):
        blockers.append("reference_year_not_latest")
    elif normalize_text(gate_row.get("reference_year", "")) == "2025":
        basis.append("reference_year_2025")

    if normalize_text(gate_row.get("trend_available", "")) != "true":
        blockers.append("trend_missing")
    else:
        basis.append(f"trend:{normalize_text(gate_row.get('trend_signal', ''))}")

    if normalize_text(gate_row.get("resolution_status", "")) != "exact_ready":
        blockers.append("not_exact_ready")
    else:
        basis.append("exact_ready")

    if normalize_text(gate_row.get("blocker_class", "")) not in {"", "none"}:
        blockers.append(f"blocker:{normalize_text(gate_row.get('blocker_class', ''))}")
    else:
        basis.append("no_blocker")

    if parse_int(gate_row.get("gap_count", "")) > 0:
        blockers.append("field_gap_present")
    elif normalize_text(gate_row.get("gap_signature", "")) == "complete_enough":
        basis.append("complete_enough")

    if parse_int(gate_row.get("total_plan_count", "")) <= 0:
        blockers.append("plan_count_missing")
    if parse_int(gate_row.get("minimum_rank", "")) <= 0:
        blockers.append("minimum_rank_missing")
    if parse_int(resolution_row.get("structured_plan_rows", "")) <= 0:
        blockers.append("structured_plan_rows_missing")
    if parse_int(resolution_row.get("structured_score_major_rows", "")) <= 0:
        blockers.append("structured_score_major_rows_missing")

    if not normalize_text(decision_row.get("plan_source_url", "")):
        blockers.append("plan_source_url_missing")
    if not normalize_text(decision_row.get("score_source_url", "")):
        blockers.append("score_source_url_missing")

    if normalize_text(workbench_row.get("review_focus_flags", "")) == "clean_pre_ml_review":
        basis.append("clean_pre_ml_review")
    else:
        followups.append(f"review_focus:{normalize_text(workbench_row.get('review_focus_flags', ''))}")

    school_name = normalize_text(decision_row.get("school_name", ""))
    source_label_terms = ["招生网", "招生信息网", "招生与就业工作处", "招生信息公开"]
    if any(term in school_name for term in source_label_terms):
        followups.append("public_school_name_label_cleanup_optional")

    if blockers:
        return (
            "hold_before_ml",
            "completed_gpt_review_decision",
            "B_blocked_or_needs_fix",
            basis,
            blockers,
            followups,
        )

    return (
        "accept_for_review_gate",
        "completed_gpt_review_decision",
        "A_clean_gate_accept",
        basis,
        blockers,
        followups or ["none"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build GPT-reviewed D1/G1 pre-ML review-gate decision overlay."
    )
    parser.add_argument(
        "--decision-register",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_decision_register_merged.csv",
        help="Generated pending review-gate decision register.",
    )
    parser.add_argument(
        "--gate-status",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gate_status_merged.csv",
        help="Pre-ML gate status CSV.",
    )
    parser.add_argument(
        "--workbench",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_workbench_merged.csv",
        help="Pre-ML review workbench CSV.",
    )
    parser.add_argument(
        "--source-resolution",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_source_resolution_matrix_merged.csv",
        help="Source resolution matrix CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_d1_g1_gpt_review_decisions_merged.csv",
        help="Output D1/G1 GPT review decision overlay CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_d1_g1_gpt_review_decisions_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_d1_g1_gpt_review_decisions_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    decision_rows = read_rows(args.decision_register)
    gate_by_key = keyed(read_rows(args.gate_status))
    workbench_by_key = keyed(read_rows(args.workbench))
    resolution_by_key = keyed(read_rows(args.source_resolution))

    output_rows: list[dict[str, str]] = []
    decision_counts: Counter[str] = Counter()
    evidence_counts: Counter[str] = Counter()

    for decision_row in decision_rows:
        if normalize_text(decision_row.get("decision_register_lane", "")) != "D1_ready_now_clean_pending_decision":
            continue
        school_key = normalize_text(decision_row.get("school_key", ""))
        gate_row = gate_by_key.get(school_key, {})
        workbench_row = workbench_by_key.get(school_key, {})
        resolution_row = resolution_by_key.get(school_key, {})

        review_decision, decision_status, evidence_grade, basis, blockers, followups = derive_decision(
            decision_row,
            gate_row,
            workbench_row,
            resolution_row,
        )
        decision_counts[review_decision] += 1
        evidence_counts[evidence_grade] += 1

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(decision_row.get("school_name", school_key)),
                "decision_register_lane": normalize_text(decision_row.get("decision_register_lane", "")),
                "gate_status": normalize_text(gate_row.get("gate_status", "")),
                "readiness_band": normalize_text(gate_row.get("readiness_band", "")),
                "review_lane": normalize_text(workbench_row.get("review_lane", "")),
                "review_risk_score": normalize_text(workbench_row.get("review_risk_score", "")),
                "decision_status": decision_status,
                "review_decision": review_decision,
                "reviewer": "codex_gpt_review",
                "decision_time": REVIEW_DATE,
                "evidence_grade": evidence_grade,
                "acceptance_basis": "|".join(basis),
                "blocking_issues": "|".join(blockers) if blockers else "none",
                "residual_followups": "|".join(followups),
                "ml_boundary_note": "D1/G1 决策仅打开复核闸门；进入 ML 前仍需汇总 accepted/caution canonical 层并单独确认",
                "reference_year": normalize_text(gate_row.get("reference_year", "")),
                "latest_year": normalize_text(gate_row.get("latest_year", "")),
                "data_completeness": normalize_text(gate_row.get("data_completeness", "")),
                "total_plan_count": normalize_text(gate_row.get("total_plan_count", "")),
                "minimum_score": normalize_text(gate_row.get("minimum_score", decision_row.get("minimum_score", ""))),
                "minimum_rank": normalize_text(gate_row.get("minimum_rank", decision_row.get("minimum_rank", ""))),
                "trend_available": normalize_text(gate_row.get("trend_available", "")),
                "trend_signal": normalize_text(gate_row.get("trend_signal", "")),
                "resolution_status": normalize_text(gate_row.get("resolution_status", "")),
                "plan_source_resolution": normalize_text(gate_row.get("plan_source_resolution", "")),
                "score_source_resolution": normalize_text(gate_row.get("score_source_resolution", "")),
                "structured_plan_rows": normalize_text(resolution_row.get("structured_plan_rows", "")),
                "structured_score_major_rows": normalize_text(resolution_row.get("structured_score_major_rows", "")),
                "structured_score_summary_rows": normalize_text(resolution_row.get("structured_score_summary_rows", "")),
                "plan_source_url": normalize_text(decision_row.get("plan_source_url", "")),
                "score_source_url": normalize_text(decision_row.get("score_source_url", "")),
                "required_checks": normalize_text(decision_row.get("required_checks", "")),
                "pass_route": normalize_text(decision_row.get("pass_route", "")),
                "fail_route": normalize_text(decision_row.get("fail_route", "")),
                "record_id": f"{school_key}-d1-g1-gpt-review-decision",
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
        {"metric": "d1_g1_review_decision_rows", "value": str(len(output_rows))},
        {"metric": "completed_gpt_review_decisions", "value": str(len(output_rows))},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    for decision, count in sorted(decision_counts.items()):
        coverage_rows.append({"metric": f"{decision}_rows", "value": str(count)})
    for grade, count in sorted(evidence_counts.items()):
        coverage_rows.append({"metric": f"{grade}_rows", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote D1/G1 GPT review decisions for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
