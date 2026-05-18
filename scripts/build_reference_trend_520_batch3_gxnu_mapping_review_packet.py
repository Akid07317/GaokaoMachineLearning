#!/usr/bin/env python3
"""Build a GXNU group-mapping review packet from the manual workbench.

This is a derived reviewer aid. It clusters majors by discipline code and
keeps group assignment blank.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_group_mapping_workbench.csv"
DELTA = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_2024_2025_matched_group_delta_preview.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_mapping_review_packet.csv"
DISCIPLINE = ROOT / "reports/reference_trend_520_batch3_gxnu_mapping_discipline_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_batch3_gxnu_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_batch3_gxnu_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_batch3_gxnu_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_batch3_gxnu_mapping_review_packet.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"

DISCIPLINE_NAMES = {
    "01": "哲学",
    "02": "经济学",
    "03": "法学",
    "04": "教育学",
    "05": "文学",
    "06": "历史学",
    "07": "理学",
    "08": "工学",
    "09": "农学",
    "10": "医学",
    "11": "军事学",
    "12": "管理学",
    "13": "艺术学",
}


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


def to_int(value: object) -> int:
    try:
        return int(float(str(value or "").strip() or "0"))
    except ValueError:
        return 0


def group_context() -> dict[str, dict[str, str]]:
    rows = read_csv(DELTA)
    return {
        row["group_code"]: row
        for row in rows
        if row.get("university_code") == "10602" and row.get("group_code") in {"151", "152", "155", "156"}
    }


def discipline_code(major_code: str) -> str:
    digits = "".join(ch for ch in str(major_code or "") if ch.isdigit())
    return digits[:2] if len(digits) >= 2 else "unknown"


def reviewer_focus(code: str) -> str:
    if code in {"07", "08"}:
        return "重点核对是否对应理学/工学组，以及选科要求是否分组"
    if code in {"02", "03", "04", "05", "06", "12"}:
        return "重点核对是否对应不限/人文社科/管理教育类组"
    if code == "13":
        return "确认是否已排除艺术类或是否误入普通批普通类"
    return "按招生计划原表和考试院专业组结构人工核对"


def build_rows() -> list[dict[str, object]]:
    rows = read_csv(WORKBENCH)
    ctx = group_context()
    packet_rows: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        code = discipline_code(row.get("major_code", ""))
        packet_rows.append(
            {
                "packet_record_id": f"reference_trend_520_batch3_gxnu_review_{idx:04d}",
                "source_workbench_record_id": row.get("workbench_record_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "major_code": row.get("major_code", ""),
                "major_or_group": row.get("major_or_group", ""),
                "discipline_code": code,
                "discipline_family": DISCIPLINE_NAMES.get(code, "unknown"),
                "plan_count": row.get("plan_count", ""),
                "candidate_group_codes": row.get("candidate_exam_authority_group_codes", ""),
                "group151_2025_score_rank": f"{ctx.get('151', {}).get('score_2025', '')}/{ctx.get('151', {}).get('rank_2025', '')}",
                "group152_2025_score_rank": f"{ctx.get('152', {}).get('score_2025', '')}/{ctx.get('152', {}).get('rank_2025', '')}",
                "group155_2025_score_rank": f"{ctx.get('155', {}).get('score_2025', '')}/{ctx.get('155', {}).get('rank_2025', '')}",
                "group156_2025_score_rank": f"{ctx.get('156', {}).get('score_2025', '')}/{ctx.get('156', {}).get('rank_2025', '')}",
                "reviewer_focus": reviewer_focus(code),
                "proposed_group_code": "",
                "do_not_auto_assign_reason": "source_plan_has_no_exam_authority_group_code",
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )
    return packet_rows


def build_discipline_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    plan_by_code: dict[str, int] = defaultdict(int)
    count_by_code: Counter[str] = Counter()
    labels_by_code: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        code = str(row["discipline_code"])
        plan_by_code[code] += to_int(row["plan_count"])
        count_by_code[code] += 1
        if len(labels_by_code[code]) < 12:
            labels_by_code[code].append(str(row["major_or_group"]))
    out: list[dict[str, object]] = []
    for code in sorted(count_by_code, key=lambda c: (-plan_by_code[c], c)):
        out.append(
            {
                "discipline_code": code,
                "discipline_family": DISCIPLINE_NAMES.get(code, "unknown"),
                "major_rows": count_by_code[code],
                "plan_count_sum": plan_by_code[code],
                "sample_major_labels": "|".join(labels_by_code[code]),
                "mapping_status": "human_group_assignment_needed",
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]], discipline_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "Row-level reviewer packet rows."},
        {"metric": "discipline_families", "value": len(discipline_rows), "note": "Major-code prefix clusters."},
        {"metric": "plan_count_sum", "value": sum(to_int(row["plan_count"]) for row in rows), "note": "Matches GXNU group mapping workbench checksum."},
        {"metric": "candidate_group_codes", "value": "151|152|155|156", "note": "Candidate exam authority groups only; no auto assignment."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Held until human group assignment."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]], discipline_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    plan_sum = sum(to_int(row["plan_count"]) for row in rows)
    wb_rows = read_csv(WORKBENCH)
    wb_plan_sum = sum(to_int(row.get("plan_count", "")) for row in wb_rows)
    ctx = group_context()
    return [
        {"check": "input_workbench_exists", "status": "PASS" if WORKBENCH.exists() else "FAIL", "detail": str(WORKBENCH.relative_to(ROOT))},
        {"check": "packet_rows_match_workbench", "status": "PASS" if len(rows) == len(wb_rows) else "FAIL", "detail": f"packet={len(rows)}; workbench={len(wb_rows)}"},
        {"check": "plan_count_checksum", "status": "PASS" if plan_sum == wb_plan_sum == 2002 else "WARN", "detail": f"packet={plan_sum}; workbench={wb_plan_sum}"},
        {"check": "candidate_group_context_present", "status": "PASS" if all(code in ctx for code in ("151", "152", "155", "156")) else "WARN", "detail": "|".join(sorted(ctx))},
        {"check": "discipline_rollup_present", "status": "PASS" if discipline_rows else "FAIL", "detail": f"{len(discipline_rows)} discipline families"},
        {"check": "no_auto_group_assignment", "status": "PASS", "detail": "proposed_group_code is intentionally blank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "major_or_group": row["major_or_group"],
            "plan_count": row["plan_count"],
            "exclusion_reason": "review_packet_only_pending_manual_group_assignment",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], discipline_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    top = discipline_rows[:8]
    lines = [
        "# GXNU Mapping Review Packet",
        "",
        "Scope: derived reviewer packet for 广西师范大学 2025 广西物理类本科普通批普通类计划 rows.",
        "",
        f"- Row-level packet rows: {len(rows)}",
        f"- Plan count checksum: {sum(to_int(row['plan_count']) for row in rows)}",
        "- Candidate groups: 151 / 152 / 155 / 156",
        "",
        "Discipline rollup:",
    ]
    for row in top:
        lines.append(
            f"- {row['discipline_code']} {row['discipline_family']}: "
            f"{row['major_rows']} rows, plan {row['plan_count_sum']}"
        )
    lines.extend(
        [
            "",
            "QA:",
            *[f"- {item['check']}: {item['status']} ({item['detail']})" for item in qa],
            "",
            "Boundary: this packet helps manual mapping only. It does not assign groups or write reference trend/canonical/ML.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def append_handoff(rollup: list[dict[str, object]]) -> None:
    marker = "## 86. 2026-05-16 广西师范大学 mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增广西师范大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_mapping_review_packet.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_discipline_rollup.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_batch3_gxnu_mapping_review_packet.md`

覆盖结果：将广西师范大学 53 行专业组映射工作表整理为人工审核包，并按专业代码前两位聚合为 {values.get('discipline_families')} 个学科簇，计划数校验仍为 {values.get('plan_count_sum')}。

准入边界：该包只辅助人工分配 151 / 152 / 155 / 156，不自动归组；`reference_trend_pool_eligible`、canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    if not rows:
        raise RuntimeError("No GXNU workbench rows found.")
    discipline_rows = build_discipline_rollup(rows)
    rollup = build_rollup(rows, discipline_rows)
    qa = build_qa(rows, discipline_rows)

    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(DISCIPLINE, discipline_rows, list(discipline_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "major_or_group", "plan_count", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, discipline_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} GXNU mapping review packet rows")
    print(f"discipline rollup rows: {len(discipline_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
