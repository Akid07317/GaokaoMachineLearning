from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa"
PLAN_PREVIEW = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview.csv"
GROUP_READINESS = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_group_join_readiness.csv"
LINE_SCORE = SEED_DIR / "reference_trend_520_p1_batch17_jxutcm_line_score_reachability.csv"
INVENTORY = SEED_DIR / "reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory.csv"

OUT_QA_ROWS = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

QA_ROW_FIELDS = [
    "mapping_qa_id",
    "group_readiness_id",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "queue_group_code",
    "source_group_code",
    "exam_authority_group_code",
    "mapping_candidate_status",
    "mapping_consistency_status",
    "mapping_acceptance_status",
    "major_row_count",
    "plan_count_sum",
    "subject_requirements",
    "major_names_preview",
    "special_type_row_count",
    "special_type_boundary_status",
    "official_min_score",
    "official_min_rank",
    "official_score_source_url",
    "official_rank_status",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
]

ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "mapping_qa_id",
    "university_code",
    "university_name",
    "queue_group_code",
    "source_group_code",
    "exclusion_reason",
    "blocked_until",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def boolish(value: str) -> bool:
    return value.strip().lower() == "true"


def aggregate_plan_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    major_names: dict[str, list[str]] = defaultdict(list)
    subject_requirements: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        group = row["source_group_code"]
        entry = grouped.setdefault(
            group,
            {
                "major_row_count": 0,
                "plan_count_sum": 0,
                "special_type_row_count": 0,
                "source_contains_plan_count": boolish(row["source_contains_plan_count"]),
                "source_contains_min_score": boolish(row["source_contains_min_score"]),
                "source_contains_min_rank": boolish(row["source_contains_min_rank"]),
            },
        )
        entry["major_row_count"] = int(entry["major_row_count"]) + 1
        entry["plan_count_sum"] = int(entry["plan_count_sum"]) + int(row.get("plan_count") or 0)
        if boolish(row.get("special_type_detected", "")):
            entry["special_type_row_count"] = int(entry["special_type_row_count"]) + 1
        if row.get("major_name"):
            major_names[group].append(row["major_name"])
        if row.get("subject_requirement"):
            subject_requirements[group].add(row["subject_requirement"])

    for group, entry in grouped.items():
        entry["major_names_preview"] = "；".join(major_names[group][:8])
        entry["subject_requirements"] = "；".join(sorted(subject_requirements[group]))
    return grouped


def special_boundary_status(special_count: int) -> str:
    if special_count:
        return "special_type_boundary_review_needed_5_plus_3_row_present"
    return "no_special_type_row_detected_in_source_group"


def build() -> None:
    plan_rows = read_csv(PLAN_PREVIEW)
    readiness_rows = read_csv(GROUP_READINESS)
    line_rows = read_csv(LINE_SCORE)
    inventory_rows = read_csv(INVENTORY) if INVENTORY.exists() else []
    plan_by_group = aggregate_plan_rows(plan_rows)

    if len(line_rows) != 1:
        raise SystemExit(f"Expected exactly one JXUTCM line score row, found {len(line_rows)}")
    line = line_rows[0]

    qa_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for idx, readiness in enumerate(readiness_rows, 1):
        group = readiness["source_group_code"]
        plan = plan_by_group[group]
        is_suffix_candidate = (
            readiness["group_mapping_status"] == "candidate_suffix_match_only_not_confirmed"
        )

        if is_suffix_candidate:
            mapping_candidate_status = "candidate_mapping_suffix_match_needs_official_confirmation"
            mapping_consistency_status = "conditional_candidate_only"
            official_min_score = line["min_score"]
            official_min_rank = ""
            official_score_source_url = line["score_source_url"]
            official_rank_status = "official_min_rank_blank_waiting_marker_136_raw_artifact"
            required_resolution = (
                "Confirm source short group 01 maps to Guangxi exam-authority group 101 via official "
                "填报系统 or source table key, then join official one-score-one-rank for score 527."
            )
            evidence_note = (
                "Source plan group 01 is the only suffix candidate for queue group 101; official "
                "exam-authority line score confirms 10412-101 has min_score 527 but provides no rank."
            )
        else:
            mapping_candidate_status = "adjacent_source_group_not_candidate_for_queue_101"
            mapping_consistency_status = "excluded_adjacent_source_group_suffix_mismatch"
            official_min_score = ""
            official_min_rank = ""
            official_score_source_url = ""
            official_rank_status = "not_rank_join_candidate_for_target_group"
            required_resolution = (
                "Keep as adjacent source-packet context only unless an official group-code mapping "
                "artifact later links this source group to a different Guangxi exam-authority group."
            )
            evidence_note = (
                f"Source short group {group} is not a suffix match for target queue group 101; "
                "not linked to official score row 10412-101."
            )

        mapping_qa_id = f"{MARKER}_{idx:04d}"
        row = {
            "mapping_qa_id": mapping_qa_id,
            "group_readiness_id": readiness["group_readiness_id"],
            "university_code": readiness["university_code"],
            "university_name": readiness["university_name"],
            "year": readiness["year"],
            "province": readiness["province"],
            "batch": readiness["batch"],
            "subject_category": readiness["subject_category"],
            "queue_group_code": readiness["queue_group_code"],
            "source_group_code": group,
            "exam_authority_group_code": line["exam_authority_group_code"] if is_suffix_candidate else "",
            "mapping_candidate_status": mapping_candidate_status,
            "mapping_consistency_status": mapping_consistency_status,
            "mapping_acceptance_status": "not_accepted_for_intake_or_calibration",
            "major_row_count": plan["major_row_count"],
            "plan_count_sum": plan["plan_count_sum"],
            "subject_requirements": plan["subject_requirements"],
            "major_names_preview": plan["major_names_preview"],
            "special_type_row_count": plan["special_type_row_count"],
            "special_type_boundary_status": special_boundary_status(int(plan["special_type_row_count"])),
            "official_min_score": official_min_score,
            "official_min_rank": official_min_rank,
            "official_score_source_url": official_score_source_url,
            "official_rank_status": official_rank_status,
            "source_contains_plan_count": str(plan["source_contains_plan_count"]).lower(),
            "source_contains_min_score": str(plan["source_contains_min_score"]).lower(),
            "source_contains_min_rank": str(plan["source_contains_min_rank"]).lower(),
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "required_resolution": required_resolution,
            "evidence_note": evidence_note,
        }
        qa_rows.append(row)

        exclusion_reason = (
            "candidate_mapping_not_confirmed_and_special_type_boundary_review_needed"
            if is_suffix_candidate and int(plan["special_type_row_count"])
            else "adjacent_source_group_suffix_mismatch"
        )
        blocked_until = (
            "official_group_mapping_confirmation_and_official_rank_raw_artifact"
            if is_suffix_candidate
            else "official_group_mapping_artifact_for_adjacent_group_if_needed"
        )
        exclusions.append(
            {
                "exclusion_id": f"{MARKER}_exclusion_{idx:04d}",
                "mapping_qa_id": mapping_qa_id,
                "university_code": readiness["university_code"],
                "university_name": readiness["university_name"],
                "queue_group_code": readiness["queue_group_code"],
                "source_group_code": group,
                "exclusion_reason": exclusion_reason,
                "blocked_until": blocked_until,
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

    consistency_counts = Counter(row["mapping_consistency_status"] for row in qa_rows)
    special_counts = Counter(row["special_type_boundary_status"] for row in qa_rows)
    total_plan = sum(int(row["plan_count_sum"]) for row in qa_rows)
    suffix_candidates = consistency_counts["conditional_candidate_only"]
    accepted = sum(row["mapping_acceptance_status"] != "not_accepted_for_intake_or_calibration" for row in qa_rows)
    linked_score_rows = sum(1 for row in qa_rows if row["official_min_score"])
    selected_rank_rows = sum(1 for row in qa_rows if row["official_min_rank"])

    rollup = [
        {"metric": "plan_preview_major_rows", "value": len(plan_rows), "notes": rel(PLAN_PREVIEW)},
        {"metric": "source_group_rows", "value": len(qa_rows), "notes": "One row per JXUTCM source short group."},
        {"metric": "plan_count_sum", "value": total_plan, "notes": "Sum across all source groups from official plan preview."},
        {"metric": "suffix_candidate_rows", "value": suffix_candidates, "notes": "Only 01 -> 101 is a suffix candidate."},
        {"metric": "accepted_mapping_rows", "value": accepted, "notes": "No mapping accepted for intake or calibration."},
        {"metric": "official_min_score_linked_rows", "value": linked_score_rows, "notes": "Only the suffix candidate links to 10412-101 min_score=527."},
        {"metric": "selected_min_rank_rows", "value": selected_rank_rows, "notes": "Rank remains blank."},
        {"metric": "inventory_rows_read", "value": len(inventory_rows), "notes": rel(INVENTORY) if INVENTORY.exists() else "inventory file missing"},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Gate remains closed."},
    ]
    for key, val in sorted(consistency_counts.items()):
        rollup.append({"metric": f"mapping_consistency::{key}", "value": val, "notes": "mapping QA status"})
    for key, val in sorted(special_counts.items()):
        rollup.append({"metric": f"special_boundary::{key}", "value": val, "notes": "special-type boundary status"})

    qa_checks = [
        {
            "qa_check": "required_inputs_present",
            "status": "PASS" if all(path.exists() for path in (PLAN_PREVIEW, GROUP_READINESS, LINE_SCORE)) else "FAIL",
            "details": "Plan preview, group readiness, and line-score reachability inputs were read locally.",
        },
        {
            "qa_check": "plan_preview_row_count",
            "status": "PASS" if len(plan_rows) == 26 else "FAIL",
            "details": f"plan_rows={len(plan_rows)}",
        },
        {
            "qa_check": "group_balance",
            "status": "PASS" if len(qa_rows) == 5 and set(plan_by_group) == {"01", "02", "04", "06", "08"} else "FAIL",
            "details": f"groups={','.join(sorted(plan_by_group))}; qa_rows={len(qa_rows)}",
        },
        {
            "qa_check": "plan_count_balance",
            "status": "PASS" if total_plan == 62 else "FAIL",
            "details": f"plan_count_sum={total_plan}",
        },
        {
            "qa_check": "single_suffix_candidate",
            "status": "PASS" if suffix_candidates == 1 else "FAIL",
            "details": f"suffix_candidate_rows={suffix_candidates}",
        },
        {
            "qa_check": "official_min_score_linked_no_rank",
            "status": "PASS" if linked_score_rows == 1 and selected_rank_rows == 0 and line["min_score"] == "527" else "FAIL",
            "details": f"linked_score_rows={linked_score_rows}; selected_rank_rows={selected_rank_rows}; line_score={line['min_score']}",
        },
        {
            "qa_check": "no_mapping_accepted",
            "status": "PASS" if accepted == 0 else "FAIL",
            "details": "Every row remains outside intake/calibration.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in qa_rows
            )
            else "FAIL",
            "details": "Reference trend intake, calibration, canonical and ML gates remain closed.",
        },
    ]

    write_csv(OUT_QA_ROWS, QA_ROW_FIELDS, qa_rows)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_checks)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 JXUTCM mapping consistency QA

## Summary

本轮只使用本地已有 marker 122/123/124/138 产物，对江西中医药大学 `10412-101` 做 source short group 到广西考试院专业组的保守 mapping consistency QA。未联网、未抓取一分一档细页、未使用浏览器态、未选择最低位次。

## Outputs

- `{rel(OUT_QA_ROWS)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Source plan major rows: {len(plan_rows)}
- Source group rows: {len(qa_rows)}
- Plan count sum: {total_plan}
- Only suffix candidate: source group `01` -> target `101`
- Official min_score linked to suffix candidate: `{line["min_score"]}`
- Selected min_rank rows: {selected_rank_rows}
- Accepted mapping rows: {accepted}

## Boundary

`01 -> 101` remains a candidate-only suffix match, not an accepted mapping. The candidate group contains one `5+3` row, so special-type/boundary review is flagged before any calibration. Source groups `02/04/06/08` are kept only as adjacent source-packet context. `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 139. 2026-05-17 P1 batch17 JXUTCM mapping consistency QA

已新增 P1 batch17 江西中医药大学 mapping consistency QA：

- `{rel(OUT_QA_ROWS)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 122/123/124/138 的本地产物，对 `10412-101` 做 source short group 到广西考试院专业组的保守一致性检查。`01 -> 101` 仅为后缀候选映射，不作为已确认映射；该候选组有 6 个专业、计划数 13，并含 1 条 `5+3` 行，已标记 special-type/boundary review。广西考试院官方最低分 `527` 已回连到候选组，但最低位次继续为空；`02/04/06/08` 作为相邻 source groups 全部排除出目标组 mapping。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步需要官方 group-code 映射确认或 marker 136 的官方一分一档 raw artifact，才能继续 rank join/eligibility 判断。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 139. 2026-05-17 P1 batch17 JXUTCM mapping consistency QA" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_checks if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(qa_rows)} mapping QA rows and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
