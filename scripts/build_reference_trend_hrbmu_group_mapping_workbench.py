#!/usr/bin/env python3
"""Build a HRBMU group-mapping workbench from parsed plan rows."""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

SOURCE_PACKET = CLEAN / "reference_trend_520_batch3_t1_source_packet_parse_preview.csv"
ADMISSION_LINES = ROOT / "clean_data" / "admission_line_table_seed.csv"
DELTA_PREVIEW = CLEAN / "reference_trend_520_rank_window_delta_preview.csv"

OUT_WORKBENCH = CLEAN / "reference_trend_hrbmu_group_mapping_workbench.csv"
OUT_ROLLUP = REPORTS / "reference_trend_hrbmu_group_mapping_rollup.csv"
OUT_QA = REPORTS / "reference_trend_hrbmu_group_mapping_qa.csv"
OUT_EXCLUSION = REPORTS / "reference_trend_hrbmu_group_mapping_exclusion_log.csv"
OUT_DOC = DOCS / "reference_trend_hrbmu_group_mapping.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

UNIVERSITY_CODE = "10226"
UNIVERSITY_NAME = "哈尔滨医科大学"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def to_int(value: object) -> int | None:
    if value in ("", None):
        return None
    try:
        return int(float(str(value)))
    except ValueError:
        return None


def group_category(row: dict[str, str]) -> str:
    code = row.get("group_code", "")
    remark = row.get("remark", "")
    if code.startswith("1"):
        return "ordinary_physics"
    if code.startswith("5") or "专项" in remark:
        return "national_special"
    if code.startswith("7") or "民族" in remark:
        return "ethnic_or_other_special"
    return "review"


def group_summary(groups: list[dict[str, str]]) -> str:
    return "|".join(
        f"{row.get('group_code')}:{row.get('min_score')}/{row.get('min_rank_est')}"
        for row in groups
    )


def load_exam_groups() -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = {
        "ordinary_physics": [],
        "national_special": [],
        "ethnic_or_other_special": [],
        "review": [],
    }
    for row in read_csv(ADMISSION_LINES):
        if (
            row.get("university_code") != UNIVERSITY_CODE
            or row.get("year") != "2025"
            or row.get("batch") != "本科普通批"
            or row.get("subject_type") != "物理类"
            or row.get("is_first_round") != "true"
        ):
            continue
        category = group_category(row)
        groups.setdefault(category, []).append({**row, "group_category": category})
    for rows in groups.values():
        rows.sort(key=lambda r: r.get("group_code", ""))
    return groups


def load_rank_window_pairs() -> list[str]:
    pairs = []
    for row in read_csv(DELTA_PREVIEW):
        if row.get("university_code") == UNIVERSITY_CODE:
            pairs.append(
                f"{row.get('group_pair_key')}:{row.get('rank_2024')}->{row.get('rank_2025')}"
                f"({row.get('rank_delta_2025_minus_2024')})"
            )
    return pairs


def plan_row_status(row: dict[str, str]) -> tuple[str, str, str, str]:
    special = row.get("special_type_detected", "")
    subject = row.get("subject_category", "")
    admission_type = row.get("admission_type", "")

    if "national_special" in special or admission_type == "国家专项":
        return (
            "national_special_hold",
            "T4_special_type_hold",
            "national special row must remain isolated from regular trend pool",
            "exclude_special_type_from_regular_reference_trend",
        )
    if not subject.startswith("物理类"):
        return (
            "non_physics_legacy_wen_hold",
            "T4_non_physics_hold",
            "legacy liberal-arts row is not physical reference-trend material",
            "exclude_non_physics_row",
        )
    return (
        "ordinary_physics_plan_row_group_code_missing",
        "T2_plan_count_source_group_mapping_needed",
        "official plan row has count, but HRBMU source does not expose Guangxi institution-major-group code",
        "need official group structure or manually accepted mapping rule before any intake",
    )


def main() -> None:
    source_rows = [
        row
        for row in read_csv(SOURCE_PACKET)
        if row.get("university_code") == UNIVERSITY_CODE
        and row.get("parser_dataset", "").startswith("hrbmu")
    ]
    exam_groups = load_exam_groups()
    ordinary_groups = exam_groups.get("ordinary_physics", [])
    national_special_groups = exam_groups.get("national_special", [])
    rank_window_pairs = load_rank_window_pairs()

    workbench: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, row in enumerate(source_rows, start=1):
        mapping_status, tier, note, required = plan_row_status(row)
        plan_count = to_int(row.get("plan_count"))
        if mapping_status == "ordinary_physics_plan_row_group_code_missing":
            candidate_groups = [g.get("group_code", "") for g in ordinary_groups]
            candidate_summary = group_summary(ordinary_groups)
        elif mapping_status == "national_special_hold":
            candidate_groups = [g.get("group_code", "") for g in national_special_groups]
            candidate_summary = group_summary(national_special_groups)
        else:
            candidate_groups = []
            candidate_summary = ""

        out_row = {
            "record_id": f"reference_trend_hrbmu_group_mapping_{idx:04d}",
            "source_record_id": row.get("record_id", ""),
            "university_code": UNIVERSITY_CODE,
            "university_name": UNIVERSITY_NAME,
            "year": row.get("year", ""),
            "province": row.get("province", ""),
            "batch": row.get("batch", ""),
            "subject_category": row.get("subject_category", ""),
            "major_or_group": row.get("major_or_group", ""),
            "plan_nature": row.get("plan_nature", ""),
            "admission_type": row.get("admission_type", ""),
            "plan_count": plan_count if plan_count is not None else "",
            "candidate_group_codes": "|".join(candidate_groups),
            "candidate_group_count": len([g for g in candidate_groups if g]),
            "candidate_group_floor_summary_2025": candidate_summary,
            "rank_window_delta_context": "|".join(rank_window_pairs),
            "mapping_status": mapping_status,
            "confidence_tier": tier,
            "source_url": row.get("source_url", ""),
            "raw_file_path": row.get("raw_file_path", ""),
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_mapping_qa_only_not_decision_pool",
            "required_resolution": required,
            "evidence_note": note,
        }
        workbench.append(out_row)
        if mapping_status != "ordinary_physics_plan_row_group_code_missing":
            exclusions.append(out_row)

    counts = Counter()
    ordinary_plan_total = 0
    national_special_total = 0
    non_physics_plan_total = 0
    for row in workbench:
        counts["workbench_rows"] += 1
        counts[f"mapping_status::{row['mapping_status']}"] += 1
        if row["mapping_status"] == "ordinary_physics_plan_row_group_code_missing":
            ordinary_plan_total += int(row.get("plan_count") or 0)
        if row["mapping_status"] == "national_special_hold":
            national_special_total += int(row.get("plan_count") or 0)
        if row["mapping_status"] == "non_physics_legacy_wen_hold":
            non_physics_plan_total += int(row.get("plan_count") or 0)

    rollup_rows = [
        {"metric": "workbench_rows", "value": len(workbench), "note": ""},
        {"metric": "ordinary_physics_plan_rows", "value": counts["mapping_status::ordinary_physics_plan_row_group_code_missing"], "note": ""},
        {"metric": "ordinary_physics_plan_total", "value": ordinary_plan_total, "note": "Physical candidate rows only; all Guangxi ordinary column total also includes legacy non-physics rows."},
        {"metric": "national_special_hold_rows", "value": counts["mapping_status::national_special_hold"], "note": ""},
        {"metric": "national_special_plan_total", "value": national_special_total, "note": "Kept outside regular-batch trend calibration."},
        {"metric": "non_physics_hold_rows", "value": counts["mapping_status::non_physics_legacy_wen_hold"], "note": ""},
        {"metric": "non_physics_hold_plan_total", "value": non_physics_plan_total, "note": "Legacy liberal-arts rows inside the same Guangxi ordinary column."},
        {"metric": "all_guangxi_ordinary_column_total", "value": ordinary_plan_total + non_physics_plan_total, "note": "Reconciles to parsed HRBMU ordinary Guangxi column total."},
        {"metric": "exam_authority_ordinary_group_count_2025", "value": len(ordinary_groups), "note": group_summary(ordinary_groups)},
        {"metric": "exam_authority_national_special_group_count_2025", "value": len(national_special_groups), "note": group_summary(national_special_groups)},
        {"metric": "rank_window_delta_context_pairs", "value": len(rank_window_pairs), "note": "|".join(rank_window_pairs)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group mapping is not accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No calibration promotion."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(counts.items()):
        if key.startswith("mapping_status::"):
            rollup_rows.append({"metric": key, "value": value, "note": ""})

    qa_rows = [
        {
            "qa_check": "hrbmu_ordinary_physics_plan_total",
            "status": "pass" if ordinary_plan_total == 32 else "review",
            "value": ordinary_plan_total,
            "note": "Physical candidate rows total 32; remaining ordinary-column plan count is legacy non-physics hold.",
        },
        {
            "qa_check": "hrbmu_all_guangxi_ordinary_column_total",
            "status": "pass" if ordinary_plan_total + non_physics_plan_total == 37 else "review",
            "value": ordinary_plan_total + non_physics_plan_total,
            "note": "Physical candidate total plus legacy non-physics hold reconciles to the parsed HRBMU ordinary Guangxi column total 37.",
        },
        {
            "qa_check": "hrbmu_national_special_plan_total",
            "status": "pass" if national_special_total == 13 else "review",
            "value": national_special_total,
            "note": "Adjacent Guangxi national-special column remains isolated.",
        },
        {
            "qa_check": "exam_authority_2025_ordinary_groups",
            "status": "pass" if len(ordinary_groups) >= 1 else "review",
            "value": group_summary(ordinary_groups),
            "note": "Candidate groups only; source packet still lacks official row-to-group mapping.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
    ]

    fields = [
        "record_id",
        "source_record_id",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "major_or_group",
        "plan_nature",
        "admission_type",
        "plan_count",
        "candidate_group_codes",
        "candidate_group_count",
        "candidate_group_floor_summary_2025",
        "rank_window_delta_context",
        "mapping_status",
        "confidence_tier",
        "source_url",
        "raw_file_path",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]
    write_csv(OUT_WORKBENCH, workbench, fields)
    write_csv(OUT_ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(OUT_QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(OUT_EXCLUSION, exclusions, fields)

    doc = f"""# HRBMU Group Mapping Workbench

Generated: {date.today().isoformat()}

This is a non-baseline, non-canonical, non-ML workbench for 哈尔滨医科大学 2025 广西 plan rows. It uses the parsed official HRBMU plan table and Guangxi exam-authority 2025 institution-group admission lines to expose the remaining group-code mapping gap.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv`
- `reports/reference_trend_hrbmu_group_mapping_rollup.csv`
- `reports/reference_trend_hrbmu_group_mapping_qa.csv`
- `reports/reference_trend_hrbmu_group_mapping_exclusion_log.csv`

## Coverage

- Workbench rows: {len(workbench)}
- Ordinary physical plan rows: {counts['mapping_status::ordinary_physics_plan_row_group_code_missing']}
- Ordinary physical plan total: {ordinary_plan_total}
- Legacy non-physics hold total: {non_physics_plan_total}
- All Guangxi ordinary column total: {ordinary_plan_total + non_physics_plan_total}
- National-special hold rows: {counts['mapping_status::national_special_hold']}
- National-special plan total: {national_special_total}
- 2025 ordinary physical exam-authority groups: {group_summary(ordinary_groups)}
- 2025 national-special exam-authority groups: {group_summary(national_special_groups)}
- 520-window delta context: {'|'.join(rank_window_pairs)}

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`. The HRBMU source has official plan counts but no Guangxi institution-major-group code, so rows remain in mapping QA until an official group structure or a manually accepted mapping rule is available.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    handoff = f"""

## 24. {date.today().isoformat()} 哈尔滨医科大学 group mapping workbench

已新增 HRBMU group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv`
- `reports/reference_trend_hrbmu_group_mapping_rollup.csv`
- `reports/reference_trend_hrbmu_group_mapping_qa.csv`
- `reports/reference_trend_hrbmu_group_mapping_exclusion_log.csv`
- `docs/reference_trend_hrbmu_group_mapping.md`

覆盖结果：workbench {len(workbench)} 行；普通物理计划行 {counts['mapping_status::ordinary_physics_plan_row_group_code_missing']} 行，计划合计 {ordinary_plan_total}；legacy 非物理 hold 计划合计 {non_physics_plan_total}，两者合计回到 HRBMU 广西普通列总数 {ordinary_plan_total + non_physics_plan_total}；国家专项 hold {counts['mapping_status::national_special_hold']} 行，计划合计 {national_special_total}。2025 广西考试院普通物理组线候选为 {group_summary(ordinary_groups)}；520 窗口重点 delta 为 {'|'.join(rank_window_pairs)}。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。HRBMU 官方表有计划数但无广西院校专业组代码，只能作为 mapping QA，不进入 trend pool/canonical/ML。

下一轮优先级：继续找 HRBMU 官方组结构或可审计的院校专业组映射；若没有安全来源，回到 P0/P1 官方计划来源发现队列。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    existing = re.sub(r"\n\n## 24\. 2026-05-16 哈尔滨医科大学 group mapping workbench.*?(?=\n\n## \d+\. |\Z)", "", existing, flags=re.S)
    HANDOFF.write_text(existing + handoff, encoding="utf-8")

    for path in [OUT_WORKBENCH, OUT_ROLLUP, OUT_QA, OUT_EXCLUSION, OUT_DOC]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
