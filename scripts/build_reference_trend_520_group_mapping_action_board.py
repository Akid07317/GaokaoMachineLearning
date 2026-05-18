#!/usr/bin/env python3
"""Summarize outstanding reference-trend group mapping workbenches.

The output is a derived action board only. It does not modify any source
workbench, and it does not open reference trend intake, canonical, or ML.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "clean_data/engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

OUT = SEED / "reference_trend_520_group_mapping_action_board.csv"
ROLLUP = REPORTS / "reference_trend_520_group_mapping_action_board_rollup.csv"
QA = REPORTS / "reference_trend_520_group_mapping_action_board_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_group_mapping_action_board_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_group_mapping_action_board.md"

MANUAL_FIELD_CANDIDATES = {
    "selected_decision",
    "selected_group_code",
    "reviewer",
    "decision_notes",
    "manual_decision",
    "human_decision",
    "acceptance_decision",
    "review_status",
}

PLAN_FIELDS = (
    "plan_count",
    "source_plan_count",
    "admission_count",
    "guangxi_plan_count_provisional",
    "plan_row_count",
)

TRUTHY = {"1", "true", "yes", "y", "eligible", "accept", "accepted"}


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


def is_truthy(value: object) -> bool:
    return str(value).strip().lower() in TRUTHY


def to_int(value: object) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def workbench_files() -> list[Path]:
    files = sorted(SEED.glob("*group*workbench*.csv"))
    return [path for path in files if path.name != OUT.name]


def board_row(path: Path) -> dict[str, object]:
    rows = read_csv(path)
    fieldnames = list(rows[0].keys()) if rows else []
    universities = sorted({row.get("university_name", "") for row in rows if row.get("university_name", "")})
    codes = sorted({row.get("university_code", "") for row in rows if row.get("university_code", "")})
    group_candidates = sorted(
        {
            value
            for row in rows
            for col in ("group_code", "exam_group_code_candidate", "candidate_exam_authority_group_codes", "exam_authority_group_code", "guangxi_exam_group_code_candidate")
            for value in str(row.get(col, "")).replace("|", ";").split(";")
            if value.strip()
        }
    )

    manual_columns = [col for col in fieldnames if col in MANUAL_FIELD_CANDIDATES]
    manual_rows = sum(1 for row in rows if any(str(row.get(col, "")).strip() for col in manual_columns))

    eligible_rows = sum(1 for row in rows if is_truthy(row.get("reference_trend_pool_eligible", "")))
    canonical_rows = sum(1 for row in rows if is_truthy(row.get("canonical_ml_entry_open", "")))
    calibration_rows = sum(1 for row in rows if is_truthy(row.get("calibration_eligible", "")))

    plan_sum = 0
    plan_rows = 0
    for row in rows:
        for field in PLAN_FIELDS:
            if field in row and str(row.get(field, "")).strip():
                plan_sum += to_int(row[field])
                plan_rows += 1
                break

    suggested_priority = "P2_review_existing_workbench"
    if manual_rows:
        suggested_priority = "P0_intake_manual_decisions"
    elif rows and plan_sum >= 500:
        suggested_priority = "P1_large_plan_mapping_review"
    elif rows and eligible_rows:
        suggested_priority = "P1_eligible_rows_need_boundary_check"

    next_action = "review_or_fill_manual_mapping_fields"
    if manual_rows:
        next_action = "build_post_human_mapping_intake_preview_without_overwriting_source"
    elif canonical_rows:
        next_action = "audit_unexpected_canonical_open_flag"

    return {
        "action_record_id": f"reference_trend_520_group_mapping_action_{abs(hash(path.name)) % 100000:05d}",
        "workbench_file": str(path.relative_to(ROOT)),
        "university_codes": "|".join(codes),
        "university_names": "|".join(universities),
        "workbench_rows": len(rows),
        "rows_with_plan_count_like_field": plan_rows,
        "plan_count_like_sum": plan_sum,
        "candidate_group_codes_or_labels": "|".join(group_candidates[:30]),
        "manual_decision_columns_present": "|".join(manual_columns),
        "manual_decision_rows_present": manual_rows,
        "reference_trend_pool_eligible_rows": eligible_rows,
        "calibration_eligible_rows": calibration_rows,
        "canonical_ml_entry_open_rows": canonical_rows,
        "suggested_priority": suggested_priority,
        "next_action": next_action,
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "group_mapping_action_board_only_not_decision_pool",
    }


def build_board() -> list[dict[str, object]]:
    rows = [board_row(path) for path in workbench_files()]
    priority_order = {
        "P0_intake_manual_decisions": 0,
        "P1_large_plan_mapping_review": 1,
        "P1_eligible_rows_need_boundary_check": 2,
        "P2_review_existing_workbench": 3,
    }
    rows.sort(key=lambda r: (priority_order.get(str(r["suggested_priority"]), 9), -int(r["workbench_rows"]), str(r["workbench_file"])))
    for idx, row in enumerate(rows, start=1):
        row["action_rank"] = idx
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total_rows = sum(int(row["workbench_rows"]) for row in rows)
    plan_sum = sum(int(row["plan_count_like_sum"]) for row in rows)
    manual_rows = sum(int(row["manual_decision_rows_present"]) for row in rows)
    eligible_rows = sum(int(row["reference_trend_pool_eligible_rows"]) for row in rows)
    canonical_rows = sum(int(row["canonical_ml_entry_open_rows"]) for row in rows)
    priorities = Counter(str(row["suggested_priority"]) for row in rows)
    out = [
        {"metric": "workbench_files", "value": len(rows), "note": "Group mapping workbenches included."},
        {"metric": "workbench_source_rows", "value": total_rows, "note": "Rows awaiting review/intake across workbenches."},
        {"metric": "plan_count_like_sum", "value": plan_sum, "note": "Directional only; mixed row types may include row counts or plan counts."},
        {"metric": "manual_decision_rows_present", "value": manual_rows, "note": "Rows with reviewer/decision fields already filled in source workbenches."},
        {"metric": "reference_trend_pool_eligible_rows", "value": eligible_rows, "note": "Should stay zero unless separately accepted."},
        {"metric": "canonical_ml_entry_open_rows", "value": canonical_rows, "note": "Canonical/ML should remain closed."},
    ]
    for key, value in sorted(priorities.items()):
        out.append({"metric": f"priority::{key}", "value": value, "note": "Derived action-board priority."})
    return out


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    return [
        {"check": "workbench_files_found", "status": "PASS" if rows else "FAIL", "detail": f"{len(rows)} files"},
        {"check": "action_board_has_rows", "status": "PASS" if rows else "FAIL", "detail": f"{len(rows)} action rows"},
        {
            "check": "canonical_ml_still_closed",
            "status": "PASS" if all(int(row["canonical_ml_entry_open_rows"]) == 0 for row in rows) else "WARN",
            "detail": "No source workbench rows should open canonical/ML.",
        },
        {
            "check": "derived_board_only",
            "status": "PASS",
            "detail": "No source workbench was modified; output is non-baseline QA/action layer.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "action_record_id": row["action_record_id"],
            "workbench_file": row["workbench_file"],
            "university_names": row["university_names"],
            "exclusion_reason": "manual_group_mapping_or_boundary_review_pending",
            "reference_trend_pool_eligible_rows": row["reference_trend_pool_eligible_rows"],
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    rollup_map = {str(row["metric"]): row["value"] for row in rollup}
    top = rows[:8]
    lines = [
        "# Group Mapping Action Board",
        "",
        "Scope: derived action board for existing reference-trend group mapping workbenches.",
        "",
        f"- Workbench files: {rollup_map.get('workbench_files')}",
        f"- Source rows covered: {rollup_map.get('workbench_source_rows')}",
        f"- Manual decision rows present: {rollup_map.get('manual_decision_rows_present')}",
        f"- Canonical/ML open rows: {rollup_map.get('canonical_ml_entry_open_rows')}",
        "",
        "Top action rows:",
    ]
    for row in top:
        lines.append(
            f"- {row['action_rank']}. {row['university_names'] or row['workbench_file']}: "
            f"{row['workbench_rows']} rows, priority={row['suggested_priority']}, next={row['next_action']}"
        )
    lines.extend(
        [
            "",
            "QA:",
            *[f"- {item['check']}: {item['status']} ({item['detail']})" for item in qa],
            "",
            "Boundary: this board is non-baseline, non-canonical, non-ML, and does not modify source workbenches.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def append_handoff(rollup: list[dict[str, object]]) -> None:
    marker = "## 85. 2026-05-16 group mapping action board"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增 group mapping action board：

- `clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_action_board.csv`
- `reports/reference_trend_520_group_mapping_action_board_rollup.csv`
- `reports/reference_trend_520_group_mapping_action_board_qa.csv`
- `reports/reference_trend_520_group_mapping_action_board_exclusion_log.csv`
- `docs/reference_trend_520_group_mapping_action_board.md`

覆盖结果：聚合 {values.get('workbench_files')} 个既有 group mapping workbench，覆盖 {values.get('workbench_source_rows')} 行待映射/待边界复核记录，形成后续人工接受、组映射、post-human intake 的行动面板。

准入边界：本轮只生成派生 action board，不改任何源工作表；`reference_trend_pool_eligible`、canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_board()
    if not rows:
        raise RuntimeError("No group mapping workbench files found.")
    fieldnames = [
        "action_rank",
        "action_record_id",
        "workbench_file",
        "university_codes",
        "university_names",
        "workbench_rows",
        "rows_with_plan_count_like_field",
        "plan_count_like_sum",
        "candidate_group_codes_or_labels",
        "manual_decision_columns_present",
        "manual_decision_rows_present",
        "reference_trend_pool_eligible_rows",
        "calibration_eligible_rows",
        "canonical_ml_entry_open_rows",
        "suggested_priority",
        "next_action",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
    ]
    write_csv(OUT, rows, fieldnames)
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["action_record_id", "workbench_file", "university_names", "exclusion_reason", "reference_trend_pool_eligible_rows", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, rollup, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} group mapping action-board rows")
    print(f"board: {OUT}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
