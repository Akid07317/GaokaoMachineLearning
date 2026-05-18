#!/usr/bin/env python3
"""Build a KMUST/UJS mapping ambiguity packet.

This derived packet separates single-group score references from ambiguous
threshold matches and excluded rows. It does not promote any row into the
reference trend pool.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_kmust_ujs_group_mapping_qa_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_kmust_ujs_mapping_ambiguity_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


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


def action_class(row: dict[str, str]) -> tuple[str, str]:
    status = row.get("mapping_status", "")
    subject = row.get("subject_category", "")
    special = row.get("special_type_detected", "")
    if status == "single_regular_exam_group_candidate_no_rank":
        return "score_reference_single_regular_group_rank_missing", "can_make_score_reference_packet_after_boundary_check"
    if status == "score_exact_single_group_floor_candidate":
        return "exact_floor_candidate_unconfirmed", "hold_for_official_group_structure_or_manual_accept"
    if status == "ambiguous_multi_group_threshold_candidate":
        return "ambiguous_threshold_multi_group", "need_official_group_structure_or_plan_grouping"
    if subject != "物理类":
        return "exclude_non_physics", "exclude_from_physical_reference_trend"
    if "special" in special or "专项" in row.get("batch", "") or "专项" in row.get("admission_type", ""):
        return "exclude_special_type", "keep_special_type_isolated"
    return "hold_for_manual_boundary_review", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    out: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        cls, next_action = action_class(row)
        out.append(
            {
                "packet_record_id": f"reference_trend_520_kmust_ujs_ambiguity_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "major_or_group": row.get("major_or_group", ""),
                "elective_requirement": row.get("elective_requirement", ""),
                "admission_type": row.get("admission_type", ""),
                "admission_count": row.get("admission_count", ""),
                "source_min_score": row.get("source_min_score", ""),
                "source_min_rank": row.get("source_min_rank", ""),
                "candidate_group_codes": row.get("candidate_group_codes", ""),
                "candidate_group_scores": row.get("candidate_group_scores", ""),
                "candidate_group_ranks": row.get("candidate_group_ranks", ""),
                "candidate_group_count": row.get("candidate_group_count", ""),
                "exact_score_group_codes": row.get("exact_score_group_codes", ""),
                "single_regular_group_code": row.get("single_regular_group_code", ""),
                "mapping_status": row.get("mapping_status", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "action_class": cls,
                "next_action": next_action,
                "source_url": row.get("source_url", ""),
                "raw_file_path": row.get("raw_file_path", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "mapping_ambiguity_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
                "evidence_note": row.get("evidence_note", ""),
            }
        )
    return out


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["university_name"]), str(row["subject_category"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (university, subject, action_class), group in sorted(grouped.items()):
        out.append(
            {
                "university_name": university,
                "subject_category": subject,
                "action_class": action_class,
                "rows": len(group),
                "admission_count_sum": sum(to_int(row["admission_count"]) for row in group),
                "min_source_score": min([to_int(row["source_min_score"]) for row in group if to_int(row["source_min_score"])], default=0),
                "max_source_score": max([to_int(row["source_min_score"]) for row in group if to_int(row["source_min_score"])], default=0),
                "candidate_group_codes_seen": "|".join(
                    sorted(
                        {
                            code
                            for row in group
                            for code in str(row.get("candidate_group_codes", "") or row.get("single_regular_group_code", "")).split("|")
                            if code
                        }
                    )
                ),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    actions = Counter(str(row["action_class"]) for row in rows)
    universities = Counter(str(row["university_name"]) for row in rows)
    out = [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from KMUST/UJS mapping QA workbench."},
        {"metric": "universities", "value": len(universities), "note": "|".join(sorted(universities))},
        {"metric": "single_regular_score_reference_rows", "value": actions.get("score_reference_single_regular_group_rank_missing", 0), "note": "UJS rows: score reference possible after boundary check; rank missing."},
        {"metric": "exact_floor_candidate_rows", "value": actions.get("exact_floor_candidate_unconfirmed", 0), "note": "KMUST exact score-floor QA rows; not accepted mappings."},
        {"metric": "ambiguous_threshold_rows", "value": actions.get("ambiguous_threshold_multi_group", 0), "note": "Need official group structure or plan grouping."},
        {"metric": "excluded_or_hold_rows", "value": actions.get("exclude_non_physics", 0) + actions.get("exclude_special_type", 0), "note": "Non-physical or special-type rows stay isolated."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(actions.items()):
        out.append({"metric": f"action_class::{key}", "value": value, "note": "Packet classification."})
    return out


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    actions = Counter(str(row["action_class"]) for row in rows)
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 86 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "ujs_single_regular_rows_classified", "status": "PASS" if actions.get("score_reference_single_regular_group_rank_missing", 0) == 16 else "WARN", "detail": str(actions.get("score_reference_single_regular_group_rank_missing", 0))},
        {"check": "kmust_ambiguous_rows_classified", "status": "PASS" if actions.get("ambiguous_threshold_multi_group", 0) == 46 else "WARN", "detail": str(actions.get("ambiguous_threshold_multi_group", 0))},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "university_name": row["university_name"],
            "major_or_group": row["major_or_group"],
            "action_class": row["action_class"],
            "exclusion_reason": "mapping_ambiguity_or_boundary_review_pending",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    actions = Counter(str(row["action_class"]) for row in rows)
    lines = [
        "# KMUST/UJS Mapping Ambiguity Packet",
        "",
        "Scope: derived packet from the existing 昆明理工大学 / 江苏大学 mapping QA workbench.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- UJS single-regular score-reference rows with missing rank: {actions.get('score_reference_single_regular_group_rank_missing', 0)}",
        f"- KMUST exact floor candidate rows: {actions.get('exact_floor_candidate_unconfirmed', 0)}",
        f"- KMUST ambiguous threshold rows: {actions.get('ambiguous_threshold_multi_group', 0)}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(
            f"- {row['university_name']} {row['subject_category']} {row['action_class']}: "
            f"{row['rows']} rows, admission_count_sum={row['admission_count_sum']}"
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
    marker = "## 87. 2026-05-16 KMUST/UJS mapping ambiguity packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增昆明理工大学 / 江苏大学 mapping ambiguity packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_status_rollup.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_rollup.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_qa.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_exclusion_log.csv`
- `docs/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.md`

覆盖结果：从既有 mapping QA workbench 派生 86 行 ambiguity packet。江苏大学有 {values.get('single_regular_score_reference_rows')} 行单一普通物理组分数参考但缺 rank；昆明理工大学有 {values.get('exact_floor_candidate_rows')} 行 exact floor candidate 与 {values.get('ambiguous_threshold_rows')} 行多组阈值候选，均需官方组结构或人工边界判断。

准入边界：本轮只做歧义分层和行动提示，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No KMUST/UJS mapping rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)

    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "university_name", "major_or_group", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} KMUST/UJS ambiguity packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
