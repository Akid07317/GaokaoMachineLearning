#!/usr/bin/env python3
"""Build a closeout board for reference-trend group mapping review artifacts."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTION_BOARD = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_action_board.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_review_closeout_board.csv"
TODO = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_manual_pending_queue.csv"
ROLLUP = ROOT / "reports/reference_trend_520_group_mapping_review_closeout_rollup.csv"
QA = ROOT / "reports/reference_trend_520_group_mapping_review_closeout_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_group_mapping_review_closeout_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_group_mapping_review_closeout.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


ARTIFACTS = {
    "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_batch3_gxnu_mapping_review_packet.md",
        "next_action": "fill_selected_group_code_selected_decision_reviewer_decision_notes",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_kmust_ujs_group_mapping_qa_workbench.csv": {
        "artifact_type": "mapping_ambiguity_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.csv",
        "doc": "docs/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.md",
        "next_action": "review_mapping_ambiguity_and_select_group_or_hold",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_cugb_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_cugb_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_cugb_mapping_review_packet.md",
        "next_action": "fill_mapping_decision_or_keep_multi_group_hold",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_lzjtu_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_lzjtu_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_lzjtu_mapping_review_packet.md",
        "next_action": "fill_mapping_decision_or_keep_multi_group_hold",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_nanhang_group_boundary_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_nanhang_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_nanhang_mapping_review_packet.md",
        "next_action": "review_boundary_and_rank_missing_holds",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_scuec_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_scuec_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_scuec_mapping_review_packet.md",
        "next_action": "assign_2025_plan_rows_to_group_or_hold_unassigned",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_hrbmu_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_hrbmu_mapping_review_packet.md",
        "next_action": "review_physics_plan_group_missing_and_boundary_holds",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_unnc_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_unnc_mapping_review_packet.md",
        "next_action": "accept_or_hold_pdf_label_group303_mapping",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_gxust_group_line_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_gxust_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_gxust_mapping_review_packet.md",
        "next_action": "review_plan_missing_and_group_line_evidence",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_520_batch7_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_batch7_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_batch7_mapping_review_packet.md",
        "next_action": "review_shzu_fjut_group_mapping_or_keep_school_level_only",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_group_line_mapping_workbench.csv": {
        "artifact_type": "acceptance_decision_sheet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.csv",
        "doc": "docs/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.md",
        "next_action": "accept_hold_request_fix_or_reject_jmu_group_mapping",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_ncut_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_ncut_mapping_review_packet.md",
        "next_action": "review_ncut_group_subject_mapping_or_keep_school_level_only",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_hpu_group_line_workbench.csv": {
        "artifact_type": "intake_enrichment_preview",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_hpu_group_line_intake_preview.csv",
        "doc": "docs/reference_trend_hpu_group_line_intake_preview.md",
        "next_action": "batch_accept_hpu_enrichment_or_keep_preview_only",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_520_batch8_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_csuft_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_csuft_mapping_review_packet.md",
        "next_action": "review_csuft_group_mapping_or_keep_selection_summary_only",
    },
    "clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv": {
        "artifact_type": "mapping_review_packet",
        "artifact": "clean_data/engineering_guangxi_seed/reference_trend_520_zucc_mapping_review_packet.csv",
        "doc": "docs/reference_trend_520_zucc_mapping_review_packet.md",
        "next_action": "find_group_split_or_keep_reject_full_80_assignment_hold",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def truthy_text(value: object) -> bool:
    return bool(str(value or "").strip())


def count_manual_decisions(rows: list[dict[str, str]]) -> tuple[int, str]:
    if not rows:
        return 0, ""
    decision_cols = [
        col
        for col in ("selected_decision", "selected_group_code", "reviewer", "decision_notes", "reviewed_at")
        if col in rows[0]
    ]
    if not decision_cols:
        return 0, ""
    return (
        sum(1 for row in rows if any(truthy_text(row.get(col, "")) for col in decision_cols)),
        "|".join(decision_cols),
    )


def int_from_row(row: dict[str, str], key: str) -> int:
    try:
        return int(float(str(row.get(key, "") or "0")))
    except ValueError:
        return 0


def build_rows() -> list[dict[str, object]]:
    actions = read_csv(ACTION_BOARD)
    out: list[dict[str, object]] = []
    for action in actions:
        workbench = action["workbench_file"]
        spec = ARTIFACTS.get(workbench, {})
        artifact_rel = spec.get("artifact", "")
        artifact_path = ROOT / artifact_rel if artifact_rel else Path()
        artifact_exists = bool(artifact_rel) and artifact_path.exists()
        artifact_rows: list[dict[str, str]] = read_csv(artifact_path) if artifact_exists else []
        manual_decision_rows, manual_cols = count_manual_decisions(artifact_rows)
        artifact_row_count = len(artifact_rows)
        pending_human_rows = 0
        if artifact_exists:
            if spec.get("artifact_type") in {"mapping_review_packet", "mapping_ambiguity_packet", "acceptance_decision_sheet"}:
                pending_human_rows = max(artifact_row_count - manual_decision_rows, 0)
            elif spec.get("artifact_type") == "intake_enrichment_preview":
                pending_human_rows = artifact_row_count
        closeout_status = "artifact_ready"
        if not artifact_exists:
            closeout_status = "artifact_missing"
        elif manual_decision_rows:
            closeout_status = "has_manual_decisions_needs_intake_check"
        elif spec.get("artifact_type") == "intake_enrichment_preview":
            closeout_status = "intake_enrichment_preview_ready_batch_acceptance_pending"
        else:
            closeout_status = "human_decision_pending"

        out.append(
            {
                "action_rank": action.get("action_rank", ""),
                "university_names": action.get("university_names", ""),
                "university_codes": action.get("university_codes", ""),
                "workbench_file": workbench,
                "workbench_rows": action.get("workbench_rows", ""),
                "workbench_plan_count_like_sum": action.get("plan_count_like_sum", ""),
                "candidate_group_codes_or_labels": action.get("candidate_group_codes_or_labels", ""),
                "artifact_type": spec.get("artifact_type", "unknown"),
                "artifact_file": artifact_rel,
                "artifact_exists": str(artifact_exists).lower(),
                "artifact_rows": artifact_row_count,
                "manual_decision_columns": manual_cols,
                "manual_decision_rows_present": manual_decision_rows,
                "pending_human_rows": pending_human_rows,
                "closeout_status": closeout_status,
                "recommended_next_action": spec.get("next_action", "create_or_locate_review_artifact"),
                "reference_trend_pool_eligible_rows": action.get("reference_trend_pool_eligible_rows", ""),
                "calibration_eligible_rows": action.get("calibration_eligible_rows", ""),
                "canonical_ml_entry_open_rows": action.get("canonical_ml_entry_open_rows", ""),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "group_mapping_review_closeout_only_not_decision_pool",
            }
        )
    return out


def build_todo(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "todo_rank": idx,
            "action_rank": row["action_rank"],
            "university_names": row["university_names"],
            "artifact_type": row["artifact_type"],
            "artifact_file": row["artifact_file"],
            "pending_human_rows": row["pending_human_rows"],
            "closeout_status": row["closeout_status"],
            "recommended_next_action": row["recommended_next_action"],
            "decision_pool_boundary": row["decision_pool_boundary"],
            "canonical_ml_entry_open": row["canonical_ml_entry_open"],
        }
        for idx, row in enumerate(
            [r for r in rows if int(r["pending_human_rows"]) > 0 or r["closeout_status"] == "artifact_missing"],
            start=1,
        )
    ]


def build_rollup(rows: list[dict[str, object]], todo: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["closeout_status"]) for row in rows)
    artifact_types = Counter(str(row["artifact_type"]) for row in rows)
    return [
        {"metric": "action_rows", "value": len(rows), "note": "Rows from group mapping action board."},
        {"metric": "artifacts_existing_rows", "value": sum(1 for row in rows if row["artifact_exists"] == "true"), "note": "Rows with a derived artifact present."},
        {"metric": "artifact_missing_rows", "value": sum(1 for row in rows if row["artifact_exists"] != "true"), "note": "Should be zero before closing mapping packet phase."},
        {"metric": "artifact_total_rows", "value": sum(int(row["artifact_rows"]) for row in rows), "note": "Rows across review packets/decision sheets/previews."},
        {"metric": "pending_human_rows", "value": sum(int(row["pending_human_rows"]) for row in rows), "note": "Review rows still awaiting human decision or batch acceptance."},
        {"metric": "todo_items", "value": len(todo), "note": "Condensed human/batch acceptance queue."},
        {"metric": "manual_decision_rows_present", "value": sum(int(row["manual_decision_rows_present"]) for row in rows), "note": "Existing human-filled rows detected."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No closeout promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        *[
            {"metric": f"closeout_status::{key}", "value": value, "note": "Closeout status."}
            for key, value in sorted(statuses.items())
        ],
        *[
            {"metric": f"artifact_type::{key}", "value": value, "note": "Derived artifact type."}
            for key, value in sorted(artifact_types.items())
        ],
    ]


def build_qa(rows: list[dict[str, object]], todo: list[dict[str, object]]) -> list[dict[str, str]]:
    return [
        {"check": "action_board_exists", "status": "PASS" if ACTION_BOARD.exists() else "FAIL", "detail": str(ACTION_BOARD.relative_to(ROOT))},
        {"check": "action_rows_expected", "status": "PASS" if len(rows) == 15 else "WARN", "detail": str(len(rows))},
        {"check": "all_artifacts_present", "status": "PASS" if all(row["artifact_exists"] == "true" for row in rows) else "WARN", "detail": f"{sum(1 for row in rows if row['artifact_exists'] == 'true')}/{len(rows)}"},
        {"check": "manual_decision_rows_detected", "status": "PASS" if sum(int(row["manual_decision_rows_present"]) for row in rows) == 0 else "WARN", "detail": str(sum(int(row["manual_decision_rows_present"]) for row in rows))},
        {"check": "todo_queue_nonempty", "status": "PASS" if todo else "WARN", "detail": str(len(todo))},
        {"check": "canonical_ml_still_closed", "status": "PASS" if all(row["canonical_ml_entry_open_rows"] in {"", "0"} and row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL", "detail": "Closeout board only."},
        {"check": "decision_pool_boundary", "status": "PASS", "detail": "No 32-school decision_pool writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "action_rank": row["action_rank"],
            "university_names": row["university_names"],
            "artifact_file": row["artifact_file"],
            "exclusion_reason": "closeout_summary_only_no_reference_trend_intake_or_canonical_ml_promotion",
            "reference_trend_pool_eligible_rows": 0,
            "calibration_eligible_rows": 0,
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], todo: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# Group Mapping Review Closeout",
        "",
        "Scope: closeout board for the 15 reference-trend group mapping action-board items.",
        "",
        f"- Action rows: {len(rows)}",
        f"- Artifacts present: {sum(1 for row in rows if row['artifact_exists'] == 'true')}/{len(rows)}",
        f"- Artifact rows total: {sum(int(row['artifact_rows']) for row in rows)}",
        f"- Pending human or batch-acceptance rows: {sum(int(row['pending_human_rows']) for row in rows)}",
        f"- Human-filled decision rows detected: {sum(int(row['manual_decision_rows_present']) for row in rows)}",
        "",
        "Pending queue:",
    ]
    for row in todo:
        lines.append(
            f"- {row['todo_rank']}. {row['university_names']}: {row['pending_human_rows']} rows, "
            f"{row['recommended_next_action']} ({row['artifact_file']})"
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
    marker = "## 99. 2026-05-16 Group mapping review closeout"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增 reference trend group mapping review closeout：

- `clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_review_closeout_board.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_manual_pending_queue.csv`
- `reports/reference_trend_520_group_mapping_review_closeout_rollup.csv`
- `reports/reference_trend_520_group_mapping_review_closeout_qa.csv`
- `reports/reference_trend_520_group_mapping_review_closeout_exclusion_log.csv`
- `docs/reference_trend_520_group_mapping_review_closeout.md`

覆盖结果：15 个 action-board 项均已对上派生产物；现有 review/decision/intake preview artifact rows 合计 {values.get('artifact_total_rows')} 行；待人工决策或 batch acceptance rows {values.get('pending_human_rows')} 行；已检测到人工填写 rows {values.get('manual_decision_rows_present')} 行。缺失 artifact rows {values.get('artifact_missing_rows')}。

准入边界：本轮只做总 closeout 和人工待判定队列，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    if not rows:
        raise RuntimeError("No group mapping action rows found.")
    todo = build_todo(rows)
    rollup = build_rollup(rows, todo)
    qa = build_qa(rows, todo)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(TODO, todo, list(todo[0].keys()) if todo else ["todo_rank"])
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(
        EXCLUSION,
        build_exclusion(rows),
        [
            "action_rank",
            "university_names",
            "artifact_file",
            "exclusion_reason",
            "reference_trend_pool_eligible_rows",
            "calibration_eligible_rows",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )
    write_doc(rows, todo, qa)
    append_handoff(rollup)
    print(f"wrote group mapping review closeout rows: {len(rows)}")
    print(f"pending queue rows: {len(todo)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
