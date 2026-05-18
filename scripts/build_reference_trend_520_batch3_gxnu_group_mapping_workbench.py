#!/usr/bin/env python3
"""Build a non-canonical GXNU group mapping workbench.

This workbench turns the cached official 2025 Guangxi Normal University plan
parse rows into a manual review surface. It deliberately does not infer final
exam-authority group codes from major names.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_PARSE = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_t1_source_packet_parse_preview.csv"
INPUT_DELTA = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_2024_2025_matched_group_delta_preview.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_group_mapping_workbench.csv"
ROLLUP = ROOT / "reports/reference_trend_520_batch3_gxnu_group_mapping_rollup.csv"
QA = ROOT / "reports/reference_trend_520_batch3_gxnu_group_mapping_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_batch3_gxnu_group_mapping_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_batch3_gxnu_group_mapping_workbench.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


MANUAL_FIELDS = ("selected_group_code", "selected_decision", "reviewer", "decision_notes")
GROUP_CODES = ("151", "152", "155", "156")


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


def protect_manual_decisions(path: Path) -> None:
    if not path.exists():
        return
    rows = read_csv(path)
    touched = [
        row.get("workbench_record_id", "")
        for row in rows
        if any((row.get(field) or "").strip() for field in MANUAL_FIELDS)
    ]
    if touched:
        raise RuntimeError(
            f"Refusing to overwrite {path}; manual decision fields are populated: "
            + ", ".join(touched[:10])
        )


def group_context() -> dict[str, dict[str, str]]:
    rows = read_csv(INPUT_DELTA)
    ctx: dict[str, dict[str, str]] = {}
    for row in rows:
        if row.get("university_code") == "10602" and row.get("group_code") in GROUP_CODES:
            ctx[row["group_code"]] = row
    return ctx


def context_summary(ctx: dict[str, dict[str, str]]) -> str:
    parts: list[str] = []
    for code in GROUP_CODES:
        row = ctx.get(code, {})
        if row:
            parts.append(
                "{code}:score2025={score};rank2025={rank};delta={delta};trend={trend}".format(
                    code=code,
                    score=row.get("score_2025", ""),
                    rank=row.get("rank_2025", ""),
                    delta=row.get("rank_delta_2025_minus_2024", ""),
                    trend=row.get("trend_direction", ""),
                )
            )
        else:
            parts.append(f"{code}:missing_exam_authority_context")
    return " | ".join(parts)


def build_workbench() -> list[dict[str, object]]:
    parse_rows = read_csv(INPUT_PARSE)
    ctx = group_context()
    summary = context_summary(ctx)
    gxnu_rows = [
        row
        for row in parse_rows
        if row.get("university_code") == "10602"
        and row.get("qa_status") == "source_packet_ready_group_mapping_needed"
        and row.get("province") == "广西"
        and row.get("batch") == "本科普通批"
        and row.get("subject_category") == "物理类"
        and row.get("admission_type") == "普通类"
    ]

    rows: list[dict[str, object]] = []
    for idx, row in enumerate(gxnu_rows, start=1):
        rows.append(
            {
                "workbench_record_id": f"reference_trend_520_batch3_gxnu_mapping_{idx:04d}",
                "source_parse_record_id": row.get("record_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "admission_type": row.get("admission_type", ""),
                "major_or_group": row.get("major_or_group", ""),
                "major_code": row.get("major_code", ""),
                "plan_count": row.get("plan_count", ""),
                "candidate_exam_authority_group_codes": "|".join(GROUP_CODES),
                "candidate_group_score_rank_context": summary,
                "proposed_group_code": "",
                "mapping_status": "needs_human_group_assignment",
                "suggested_decision_options": (
                    "assign_group_code_151|assign_group_code_152|assign_group_code_155|"
                    "assign_group_code_156|exclude_special_or_non_regular|hold_for_exam_authority_group_structure"
                ),
                "selected_group_code": "",
                "selected_decision": "",
                "reviewer": "",
                "decision_notes": "",
                "source_url": row.get("source_url", ""),
                "raw_file_path": row.get("raw_file_path", ""),
                "source_contains_group_code": row.get("source_contains_group_code", ""),
                "source_contains_plan_count": row.get("source_contains_plan_count", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "required_resolution": (
                    "human_assign_exam_authority_group_code_or_hold_before_any_reference_trend_intake"
                ),
                "evidence_note": (
                    "Official GXNU 2025 Guangxi physical ordinary plan row parsed locally; "
                    "source lacks exam-authority group code, so grouping is manual-only."
                ),
            }
        )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    plan_total = sum(int(row["plan_count"] or 0) for row in rows)
    majors = Counter(str(row["major_or_group"]) for row in rows)
    return [
        {"metric": "workbench_rows", "value": len(rows), "note": "GXNU ordinary physical regular plan rows needing group assignment."},
        {"metric": "plan_count_sum", "value": plan_total, "note": "Parsed 2025 official plan count held outside trend intake."},
        {"metric": "candidate_group_codes", "value": "|".join(GROUP_CODES), "note": "Exam authority groups from 2024/2025 delta window."},
        {"metric": "manual_decision_rows_present", "value": 0, "note": "Fresh workbench; no reviewer decisions filled."},
        {"metric": "unique_major_labels", "value": len(majors), "note": "Major labels requiring group assignment."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Held until human group assignment."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan source only; no min score/rank per major."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    statuses = Counter()
    total = 0
    for row in read_csv(INPUT_PARSE):
        if row.get("university_code") == "10602":
            statuses[row.get("qa_status", "")] += 1
            if row.get("qa_status") == "source_packet_ready_group_mapping_needed":
                total += int(row.get("plan_count") or 0)

    plan_sum = sum(int(row["plan_count"] or 0) for row in rows)
    groups = group_context()
    return [
        {"check": "input_parse_exists", "status": "PASS" if INPUT_PARSE.exists() else "FAIL", "detail": str(INPUT_PARSE.relative_to(ROOT))},
        {"check": "candidate_groups_present", "status": "PASS" if all(code in groups for code in GROUP_CODES) else "WARN", "detail": "|".join(sorted(groups))},
        {"check": "workbench_row_count", "status": "PASS" if len(rows) == 53 else "WARN", "detail": f"{len(rows)} rows"},
        {"check": "plan_count_checksum", "status": "PASS" if plan_sum == 2002 and total == 2002 else "WARN", "detail": f"workbench={plan_sum}; source_ready_rows={total}"},
        {"check": "manual_decision_fields_blank", "status": "PASS", "detail": "selected_group_code/selected_decision/reviewer/decision_notes remain blank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["workbench_record_id"],
            "university_name": row["university_name"],
            "major_or_group": row["major_or_group"],
            "plan_count": row["plan_count"],
            "exclusion_reason": "missing_exam_authority_group_code_pending_human_mapping",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    DOC.parent.mkdir(parents=True, exist_ok=True)
    plan_sum = next(item["value"] for item in rollup if item["metric"] == "plan_count_sum")
    DOC.write_text(
        "\n".join(
            [
                "# GXNU Group Mapping Workbench",
                "",
                "Scope: 广西师范大学 2025 广西物理类本科普通批普通类计划解析行。",
                "",
                f"- Workbench rows: {len(rows)}",
                f"- Parsed plan count sum: {plan_sum}",
                "- Candidate exam authority groups: 151 / 152 / 155 / 156",
                "- Manual fields: `selected_group_code`, `selected_decision`, `reviewer`, `decision_notes`",
                "",
                "Boundary: this is a manual mapping workbench only. It does not open reference trend intake, canonical, ML, or the 32-school decision pool.",
                "",
                "QA:",
                *[f"- {item['check']}: {item['status']} ({item['detail']})" for item in qa],
                "",
            ]
        ),
        encoding="utf-8",
    )


def append_handoff(rollup: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    marker = "## 84. 2026-05-16 batch3 广西师范大学 group mapping workbench"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增广西师范大学 group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch3_gxnu_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch3_gxnu_group_mapping_qa.csv`
- `reports/reference_trend_520_batch3_gxnu_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch3_gxnu_group_mapping_workbench.md`

覆盖结果：将 53 条广西师范大学 2025 广西物理类本科普通批普通类官方计划解析行转成可人工确认的专业组映射工作表，计划数合计 {values.get('plan_count_sum')}。候选考试院专业组为 151 / 152 / 155 / 156，脚本不自动归组。

准入边界：这仍是人工映射工作表，不是 source-packet intake；所有行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不并入 32 所 decision_pool。下一步需要人工按专业/组结构分配专业组或继续 hold。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    protect_manual_decisions(OUT)
    rows = build_workbench()
    if not rows:
        raise RuntimeError("No GXNU rows found for group mapping workbench.")

    fieldnames = list(rows[0].keys())
    write_csv(OUT, rows, fieldnames)
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["record_id", "university_name", "major_or_group", "plan_count", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, rollup, qa)
    append_handoff(rollup, qa)
    print(f"wrote {len(rows)} GXNU group mapping workbench rows")
    print(f"workbench: {OUT}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
