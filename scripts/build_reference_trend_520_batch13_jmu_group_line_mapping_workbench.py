#!/usr/bin/env python3
"""Build JMU group-line mapping workbench from parsed source packet and queue.

This keeps Jimei University in a non-baseline QA/workbench layer. The official
plan page prints professional-group codes, and the 520 queue already has
group-year score/rank context. This script joins those two local artifacts as a
candidate mapping preview only; it does not open canonical/ML or promote rows
into the reference trend pool.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

SOURCE_PACKET = SEED_DIR / "reference_trend_520_batch13_jmu_source_packet_parse_preview.csv"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"

OUT = SEED_DIR / "reference_trend_520_batch13_jmu_group_line_mapping_workbench.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_group_line_mapping_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_group_line_mapping_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_group_line_mapping_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch13_jmu_group_line_mapping.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

UNIVERSITY_CODE = "10390"
UNIVERSITY_NAME = "集美大学"

FIELDS = [
    "record_id",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_professional_group_code",
    "guangxi_exam_group_code_candidate",
    "queue_record_id",
    "queue_rank",
    "plan_row_count",
    "plan_count_sum",
    "major_names_preview",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "source_packet_status",
    "mapping_status",
    "confidence_tier",
    "source_url",
    "source_preview_file",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
]

EXCLUSION_FIELDS = [
    "record_id",
    "university_code",
    "university_name",
    "source_professional_group_code",
    "guangxi_exam_group_code_candidate",
    "plan_row_count",
    "plan_count_sum",
    "exclusion_scope",
    "exclusion_reason",
    "required_resolution",
]


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


def append_handoff_once(marker: str, content: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in existing:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def to_int(value: object) -> int:
    if value in ("", None):
        return 0
    try:
        return int(float(str(value)))
    except ValueError:
        return 0


def queue_by_group() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in read_csv(QUEUE):
        if row.get("university_code") != UNIVERSITY_CODE:
            continue
        group = row.get("group_code", "")
        if group:
            out[group] = row
    return out


def source_group_summary() -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = defaultdict(
        lambda: {"rows": [], "plan_sum": 0, "majors": []}
    )
    for row in read_csv(SOURCE_PACKET):
        if row.get("university_code") != UNIVERSITY_CODE:
            continue
        group = row.get("source_professional_group_code", "")
        if not group:
            group = "missing"
        grouped[group]["rows"].append(row)
        grouped[group]["plan_sum"] = int(grouped[group]["plan_sum"]) + to_int(row.get("plan_count"))
        major = row.get("major_name", "")
        if major:
            grouped[group]["majors"].append(major)
    return grouped


def mapping_status(group: str, exam_candidate: str, queue_row: dict[str, str] | None) -> tuple[str, str, str, str]:
    if not queue_row:
        return (
            "hold_no_matching_520_queue_group",
            "T3_group_printed_but_no_score_rank_context",
            "need official exam-authority group-line score/rank before trend calibration",
            "printed source group exists, but no matching queue group-year score/rank context was found",
        )
    if exam_candidate.endswith(queue_row.get("group_code", "")):
        return (
            "candidate_group_line_match_preview_only",
            "T2_candidate_mapping_needs_human_acceptance",
            "human_accept_group_code_mapping_before_any_pool_intake",
            "source prints group code and local queue has same group code with 2024/2025 rank context",
        )
    return (
        "hold_group_code_mismatch",
        "T4_mapping_conflict_hold",
        "resolve source group to Guangxi exam-authority group code",
        "source group candidate and queue group code do not match",
    )


def main() -> None:
    groups = source_group_summary()
    queue_groups = queue_by_group()
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for idx, group in enumerate(sorted(groups), start=1):
        summary = groups[group]
        source_rows = summary["rows"]
        first = source_rows[0] if source_rows else {}
        exam_candidate = str(first.get("guangxi_exam_group_code_candidate", ""))
        queue_group = exam_candidate.split("-")[-1] if "-" in exam_candidate else ""
        queue_row = queue_groups.get(queue_group)
        status, tier, required, note = mapping_status(group, exam_candidate, queue_row)
        row = {
            "record_id": f"reference_trend_520_batch13_jmu_group_mapping_{idx:04d}",
            "university_code": UNIVERSITY_CODE,
            "university_name": UNIVERSITY_NAME,
            "year": "2025",
            "province": "广西",
            "batch": "本科批",
            "subject_category": "物理类",
            "source_professional_group_code": group,
            "guangxi_exam_group_code_candidate": exam_candidate,
            "queue_record_id": queue_row.get("record_id", "") if queue_row else "",
            "queue_rank": queue_row.get("queue_rank", "") if queue_row else "",
            "plan_row_count": len(source_rows),
            "plan_count_sum": summary["plan_sum"],
            "major_names_preview": "|".join(str(x) for x in summary["majors"][:12]),
            "rank_2024": queue_row.get("rank_2024", "") if queue_row else "",
            "rank_2025": queue_row.get("rank_2025", "") if queue_row else "",
            "rank_delta_2025_minus_2024": queue_row.get("rank_delta_2025_minus_2024", "") if queue_row else "",
            "trend_direction": queue_row.get("trend_direction", "") if queue_row else "",
            "source_packet_status": first.get("source_packet_status", ""),
            "mapping_status": status,
            "confidence_tier": tier,
            "source_url": first.get("source_url", ""),
            "source_preview_file": str(SOURCE_PACKET.relative_to(ROOT)),
            "reference_trend_pool_eligible": "false_preview_only",
            "calibration_eligible": "false_pending_human_acceptance_and_score_rank_source_confirmation",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "reference_trend_mapping_workbench_only_not_32_school_decision_pool",
            "required_resolution": required,
            "evidence_note": note,
        }
        rows.append(row)
        if status != "candidate_group_line_match_preview_only":
            exclusions.append(
                {
                    "record_id": f"reference_trend_520_batch13_jmu_group_mapping_excluded_{idx:04d}",
                    "university_code": UNIVERSITY_CODE,
                    "university_name": UNIVERSITY_NAME,
                    "source_professional_group_code": group,
                    "guangxi_exam_group_code_candidate": exam_candidate,
                    "plan_row_count": len(source_rows),
                    "plan_count_sum": summary["plan_sum"],
                    "exclusion_scope": "group_line_mapping_hold",
                    "exclusion_reason": status,
                    "required_resolution": required,
                }
            )

    counts = Counter(row["mapping_status"] for row in rows)
    matched_plan_sum = sum(to_int(row["plan_count_sum"]) for row in rows if row["mapping_status"] == "candidate_group_line_match_preview_only")
    held_plan_sum = sum(to_int(row["plan_count_sum"]) for row in rows if row["mapping_status"] != "candidate_group_line_match_preview_only")
    rollup_rows = [
        {"metric": "workbench_group_rows", "value": len(rows), "note": "One row per source professional group."},
        {"metric": "candidate_group_line_match_rows", "value": counts["candidate_group_line_match_preview_only"], "note": "Preview-only mapping; human acceptance required."},
        {"metric": "candidate_group_line_match_plan_sum", "value": matched_plan_sum, "note": ""},
        {"metric": "hold_rows", "value": len(exclusions), "note": "Rows without local queue score/rank context or with conflicts."},
        {"metric": "hold_plan_sum", "value": held_plan_sum, "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Mapping not promoted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Human acceptance and source confirmation still needed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for status, count in sorted(counts.items()):
        rollup_rows.append({"metric": f"mapping_status::{status}", "value": count, "note": ""})

    qa_rows = [
        {
            "check": "source_group_count",
            "status": "PASS" if len(rows) == 8 else "REVIEW",
            "detail": f"source groups={len(rows)}; expected 8 from JMU official page",
        },
        {
            "check": "source_plan_sum",
            "status": "PASS" if matched_plan_sum + held_plan_sum == 160 else "REVIEW",
            "detail": f"candidate+held plan sum={matched_plan_sum + held_plan_sum}; expected 160",
        },
        {
            "check": "matched_queue_group_count",
            "status": "PASS" if counts["candidate_group_line_match_preview_only"] == 7 else "REVIEW",
            "detail": f"matched rows={counts['candidate_group_line_match_preview_only']}; held rows={len(exclusions)}",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS",
            "detail": "All rows remain false_preview_only.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS",
            "detail": "canonical_ml_entry_open=false for every workbench row.",
        },
    ]

    doc = f"""# Reference Trend 520 Batch13 JMU Group-Line Mapping Workbench

Generated: {date.today().isoformat()}

Purpose: join the parsed 集美大学 official Guangxi plan source packet to the existing
520 rank-window queue as a candidate group-line mapping workbench. This is not
reference-trend pool intake, not canonical, and not ML input.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official source groups: {len(rows)}
- Candidate matched groups: {counts['candidate_group_line_match_preview_only']}
- Candidate matched plan sum: {matched_plan_sum}
- Held groups: {len(exclusions)}
- Held plan sum: {held_plan_sum}

Group 11 remains held because it is printed by the school source but was not in
the current top-batch 520 queue score/rank context. The other seven groups are
candidate mappings only and need human acceptance/source confirmation before
any reference-trend pool intake.

## Boundary

`reference_trend_pool_eligible=false_preview_only`,
`calibration_eligible=false_pending_human_acceptance_and_score_rank_source_confirmation`,
and `canonical_ml_entry_open=false` for all rows.
"""

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, EXCLUSION_FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 53. 2026-05-16 batch13 集美大学 group-line mapping workbench"
    handoff = f"""

{marker}

已新增集美大学 group-line mapping workbench：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：基于集美大学官方广西计划 source packet 中打印的专业组 04/05/06/07/08/09/10/11，和既有 520 队列中的 2024/2025 位次上下文做本地候选映射。7 个专业组可形成 candidate group-line match preview，合计计划数 {matched_plan_sum}；专业组 11 合计计划数 {held_plan_sum}，因当前 520 队列没有对应分数/位次上下文，继续 hold。

准入边界：本轮只是映射工作台，不是正式 trend pool intake。所有行 `reference_trend_pool_eligible=false_preview_only`、`calibration_eligible=false_pending_human_acceptance_and_score_rank_source_confirmation`、`canonical_ml_entry_open=false`；不进入 32 所 decision_pool。下一轮可对 candidate matched groups 做人工接受表，或继续推进青海大学/安徽工业大学图片 OCR/人工转录审批准备。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
