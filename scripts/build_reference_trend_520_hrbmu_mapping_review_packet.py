#!/usr/bin/env python3
"""Build a Harbin Medical University group mapping review packet."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv"
OUT = ROOT / "clean_data/engineering_guangxi_seed/reference_trend_520_hrbmu_mapping_review_packet.csv"
STATUS = ROOT / "reports/reference_trend_520_hrbmu_mapping_review_status_rollup.csv"
ROLLUP = ROOT / "reports/reference_trend_520_hrbmu_mapping_review_packet_rollup.csv"
QA = ROOT / "reports/reference_trend_520_hrbmu_mapping_review_packet_qa.csv"
EXCLUSION = ROOT / "reports/reference_trend_520_hrbmu_mapping_review_packet_exclusion_log.csv"
DOC = ROOT / "docs/reference_trend_520_hrbmu_mapping_review_packet.md"
HANDOFF = ROOT / "docs/gpt54_reference_trend_pool_handoff.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: object) -> int:
    try:
        return int(float(str(value or "").strip() or "0"))
    except ValueError:
        return 0


def classify(row: dict[str, str]) -> tuple[str, str]:
    status = row.get("mapping_status", "")
    if status == "ordinary_physics_plan_row_group_code_missing":
        return "ordinary_physics_plan_group_code_missing", "map_major_to_151_152_153_154_156_157_158_159_only_after_official_group_structure"
    if status == "national_special_hold":
        return "national_special_isolated_hold", "keep_outside_regular_physics_trend_pool"
    if status == "non_physics_legacy_wen_hold":
        return "non_physics_legacy_hold", "exclude_from_physics_reference_trend"
    return "hold_unclassified", "manual_review"


def build_packet() -> list[dict[str, object]]:
    rows = read_csv(INPUT)
    packet: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        action_class, next_action = classify(row)
        packet.append(
            {
                "packet_record_id": f"reference_trend_520_hrbmu_review_{idx:04d}",
                "source_workbench_record_id": row.get("record_id", ""),
                "source_record_id": row.get("source_record_id", ""),
                "university_code": row.get("university_code", ""),
                "university_name": row.get("university_name", ""),
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("batch", ""),
                "subject_category": row.get("subject_category", ""),
                "major_or_group": row.get("major_or_group", ""),
                "plan_nature": row.get("plan_nature", ""),
                "admission_type": row.get("admission_type", ""),
                "plan_count": row.get("plan_count", ""),
                "candidate_group_codes": row.get("candidate_group_codes", ""),
                "candidate_group_count": row.get("candidate_group_count", ""),
                "candidate_group_floor_summary_2025": row.get("candidate_group_floor_summary_2025", ""),
                "rank_window_delta_context": row.get("rank_window_delta_context", ""),
                "mapping_status": row.get("mapping_status", ""),
                "confidence_tier": row.get("confidence_tier", ""),
                "source_url": row.get("source_url", ""),
                "raw_file_path": row.get("raw_file_path", ""),
                "action_class": action_class,
                "next_action": next_action,
                "evidence_note": row.get("evidence_note", ""),
                "eligible_for_intake_preview": "false",
                "reference_trend_pool_eligible": 0,
                "calibration_eligible": 0,
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "hrbmu_mapping_review_packet_only_not_decision_pool",
                "required_resolution": row.get("required_resolution", ""),
            }
        )
    return packet


def build_status_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["mapping_status"]), str(row["action_class"]))].append(row)
    out: list[dict[str, object]] = []
    for (status, action), group in sorted(grouped.items()):
        out.append(
            {
                "mapping_status": status,
                "action_class": action,
                "rows": len(group),
                "plan_count_sum": sum(to_int(row["plan_count"]) for row in group),
                "candidate_group_count_max": max([to_int(row["candidate_group_count"]) for row in group], default=0),
                "candidate_group_codes_seen": "|".join(sorted({code for row in group for code in str(row.get("candidate_group_codes", "")).split("|") if code})),
                "canonical_ml_entry_open": "false",
            }
        )
    return out


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    actions = Counter(str(row["action_class"]) for row in rows)
    return [
        {"metric": "packet_rows", "value": len(rows), "note": "All rows from HRBMU group mapping workbench."},
        {"metric": "ordinary_physics_plan_rows", "value": statuses.get("ordinary_physics_plan_row_group_code_missing", 0), "note": "Official 2025 physical ordinary plan rows without row-level group code."},
        {"metric": "ordinary_physics_plan_count_sum", "value": sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "ordinary_physics_plan_row_group_code_missing"), "note": "Physical candidate rows only."},
        {"metric": "national_special_hold_rows", "value": statuses.get("national_special_hold", 0), "note": "Special type isolated from ordinary reference trend."},
        {"metric": "national_special_plan_count_sum", "value": sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "national_special_hold"), "note": "Not ordinary trend material."},
        {"metric": "non_physics_hold_rows", "value": statuses.get("non_physics_legacy_wen_hold", 0), "note": "Legacy liberal arts/history rows isolated."},
        {"metric": "non_physics_plan_count_sum", "value": sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "non_physics_legacy_wen_hold"), "note": "Excluded from physical trend."},
        {"metric": "ordinary_candidate_group_codes", "value": "|".join(sorted({code for row in rows if row["mapping_status"] == "ordinary_physics_plan_row_group_code_missing" for code in str(row.get("candidate_group_codes", "")).split("|") if code})), "note": "Potential ordinary physical groups from exam authority lines."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake promotion."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        *[
            {"metric": f"action_class::{key}", "value": value, "note": "Packet classification."}
            for key, value in sorted(actions.items())
        ],
    ]


def build_qa(rows: list[dict[str, object]], status_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    source = read_csv(INPUT)
    statuses = Counter(str(row["mapping_status"]) for row in rows)
    ordinary_codes = {code for row in rows if row["mapping_status"] == "ordinary_physics_plan_row_group_code_missing" for code in str(row.get("candidate_group_codes", "")).split("|") if code}
    return [
        {"check": "input_workbench_exists", "status": "PASS" if INPUT.exists() else "FAIL", "detail": str(INPUT.relative_to(ROOT))},
        {"check": "packet_rows_match_source", "status": "PASS" if len(rows) == len(source) == 22 else "WARN", "detail": f"packet={len(rows)}; source={len(source)}"},
        {"check": "status_counts_match_source_rollup", "status": "PASS" if statuses.get("ordinary_physics_plan_row_group_code_missing", 0) == 19 and statuses.get("national_special_hold", 0) == 1 and statuses.get("non_physics_legacy_wen_hold", 0) == 2 else "WARN", "detail": f"ordinary={statuses.get('ordinary_physics_plan_row_group_code_missing', 0)}; special={statuses.get('national_special_hold', 0)}; nonphysics={statuses.get('non_physics_legacy_wen_hold', 0)}"},
        {"check": "ordinary_physics_plan_count_sum_carried", "status": "PASS" if sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "ordinary_physics_plan_row_group_code_missing") == 32 else "WARN", "detail": str(sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "ordinary_physics_plan_row_group_code_missing"))},
        {"check": "special_and_nonphysics_isolated", "status": "PASS" if sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "national_special_hold") == 13 and sum(to_int(row["plan_count"]) for row in rows if row["mapping_status"] == "non_physics_legacy_wen_hold") == 5 else "WARN", "detail": f"special={sum(to_int(row['plan_count']) for row in rows if row['mapping_status'] == 'national_special_hold')}; nonphysics={sum(to_int(row['plan_count']) for row in rows if row['mapping_status'] == 'non_physics_legacy_wen_hold')}"},
        {"check": "ordinary_candidate_group_count", "status": "PASS" if len(ordinary_codes) == 8 else "WARN", "detail": "|".join(sorted(ordinary_codes))},
        {"check": "status_rollup_present", "status": "PASS" if status_rows else "FAIL", "detail": f"{len(status_rows)} rows"},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "packet_record_id": row["packet_record_id"],
            "mapping_status": row["mapping_status"],
            "major_or_group": row["major_or_group"],
            "action_class": row["action_class"],
            "exclusion_reason": "official_group_structure_or_special_nonphysics_isolation_pending",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], status_rows: list[dict[str, object]], qa: list[dict[str, str]]) -> None:
    lines = [
        "# HRBMU Mapping Review Packet",
        "",
        "Scope: 哈尔滨医科大学 2025 Guangxi plan rows with physical ordinary group-code gaps, special-type isolation, and legacy non-physics holds.",
        "",
        f"- Packet rows: {len(rows)}",
        f"- Ordinary physical plan rows: {sum(1 for row in rows if row['mapping_status'] == 'ordinary_physics_plan_row_group_code_missing')}",
        f"- Ordinary physical plan count: {sum(to_int(row['plan_count']) for row in rows if row['mapping_status'] == 'ordinary_physics_plan_row_group_code_missing')}",
        f"- National special hold rows: {sum(1 for row in rows if row['mapping_status'] == 'national_special_hold')}",
        f"- Non-physics hold rows: {sum(1 for row in rows if row['mapping_status'] == 'non_physics_legacy_wen_hold')}",
        "",
        "Status rollup:",
    ]
    for row in status_rows:
        lines.append(f"- {row['mapping_status']} {row['action_class']}: {row['rows']} rows, plan_count_sum={row['plan_count_sum']}, groups={row['candidate_group_codes_seen']}")
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
    marker = "## 92. 2026-05-16 HRBMU mapping review packet"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    values = {str(row["metric"]): row["value"] for row in rollup}
    section = f"""

{marker}

已新增哈尔滨医科大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_hrbmu_mapping_review_packet.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_hrbmu_mapping_review_packet.md`

覆盖结果：从既有 HRBMU group mapping workbench 派生 {values.get('packet_rows')} 行审核包，其中 2025 物理普通计划缺组码 rows {values.get('ordinary_physics_plan_rows')} 行、计划数 {values.get('ordinary_physics_plan_count_sum')}；国家专项隔离 {values.get('national_special_hold_rows')} 行/计划数 {values.get('national_special_plan_count_sum')}；非物理旧文科隔离 {values.get('non_physics_hold_rows')} 行/计划数 {values.get('non_physics_plan_count_sum')}。物理普通候选组为 {values.get('ordinary_candidate_group_codes')}。

准入边界：本轮只做物理普通待归组、专项隔离和非物理隔离分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。
"""
    HANDOFF.write_text(text.rstrip() + section + "\n", encoding="utf-8")


def main() -> None:
    rows = build_packet()
    if not rows:
        raise RuntimeError("No HRBMU workbench rows found.")
    status_rows = build_status_rollup(rows)
    rollup = build_rollup(rows)
    qa = build_qa(rows, status_rows)
    write_csv(OUT, rows, list(rows[0].keys()))
    write_csv(STATUS, status_rows, list(status_rows[0].keys()))
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION, build_exclusion(rows), ["packet_record_id", "mapping_status", "major_or_group", "action_class", "exclusion_reason", "canonical_ml_entry_open", "decision_pool_boundary"])
    write_doc(rows, status_rows, qa)
    append_handoff(rollup)
    print(f"wrote {len(rows)} HRBMU mapping review packet rows")
    print(f"status rollup rows: {len(status_rows)}")
    print(f"qa: {QA}")


if __name__ == "__main__":
    main()
