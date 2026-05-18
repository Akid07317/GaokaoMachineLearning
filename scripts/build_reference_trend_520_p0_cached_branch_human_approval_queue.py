#!/usr/bin/env python3
"""Build a human approval queue for P0 cached-branch blockers.

This queue consolidates local-only blockers that need explicit human approval
or manual QA before any source_packet preview can be attempted. It does not
fetch remote assets, replay forms, OCR images, parse source packets, or write
reference_trend/canonical/ML rows.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

ENDPOINT_AUDIT = CLEAN / "reference_trend_520_p0_endpoint_form_metadata_audit.csv"
PARSE_ACTION = CLEAN / "reference_trend_520_p0_cached_parse_action_queue.csv"
PDF_TABLE_QA = CLEAN / "reference_trend_520_p0_pdf_manual_table_qa_queue.csv"

OUT = CLEAN / "reference_trend_520_p0_cached_branch_human_approval_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_cached_branch_human_approval_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_cached_branch_human_approval_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_cached_branch_human_approval_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_cached_branch_human_approval_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "approval_record_id",
    "source_artifact",
    "source_record_id",
    "source_queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "approval_lane",
    "approval_priority",
    "approval_required",
    "approval_prompt",
    "candidate_kind",
    "candidate_value",
    "candidate_local_path",
    "source_url",
    "cache_path",
    "raw_source_row_count",
    "duplicate_or_collapsed_count",
    "blocked_reason",
    "safe_next_action",
    "expected_output_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
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


def boundary_row(source: dict[str, str]) -> dict[str, object]:
    return {
        "source_queue_record_id": source.get("queue_record_id", ""),
        "queue_rank": source.get("queue_rank", ""),
        "university_code": source.get("university_code", ""),
        "university_name": source.get("university_name", ""),
        "group_pair_key": source.get("group_pair_key", ""),
        "group_code": source.get("group_code", ""),
        "source_url": source.get("source_url", ""),
        "cache_path": source.get("cache_path", ""),
        "expected_output_layer": "human_approval_queue_only_not_source_packet_not_canonical",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "p0_cached_branch_human_approval_only_not_32_school_decision_pool",
    }


def asset_key(row: dict[str, str]) -> str:
    return "|".join(
        [
            row.get("university_code", ""),
            row.get("group_code", ""),
            row.get("candidate_kind", ""),
            row.get("candidate_value", "").split("?", 1)[0].split("#", 1)[0],
        ]
    )


def add_endpoint_approvals(rows: list[dict[str, object]], endpoint_rows: list[dict[str, str]]) -> None:
    targets = [
        row
        for row in endpoint_rows
        if row.get("requires_browser_or_form_approval", "").lower() == "true"
        and row.get("local_endpoint_shape_status", "").startswith("commonquery")
    ]
    for source in targets:
        row = boundary_row(source)
        row.update(
            {
                "source_artifact": str(ENDPOINT_AUDIT.relative_to(ROOT)),
                "source_record_id": source.get("endpoint_audit_id", ""),
                "approval_lane": "browser_form_replay_approval",
                "approval_priority": "P0_approve_commonquery_plan_response_capture",
                "approval_required": "true",
                "approval_prompt": "Approve browser/form replay for the cached commonquery iframe only; write any response only to source_packet/preview/QA layers.",
                "candidate_kind": source.get("endpoint_kind", ""),
                "candidate_value": source.get("endpoint_value", ""),
                "candidate_local_path": "",
                "raw_source_row_count": 1,
                "duplicate_or_collapsed_count": 0,
                "blocked_reason": source.get("local_endpoint_shape_status", ""),
                "safe_next_action": "Wait for explicit browser/form replay approval before capturing endpoint response; do not repeat terminal curl hard grabs.",
                "evidence_note": "Local cached HTML found a commonquery iframe likely tied to招生计划 query surface; no replay or network was used.",
            }
        )
        rows.append(row)


def add_asset_approvals(
    rows: list[dict[str, object]],
    exclusions: list[dict[str, object]],
    parse_rows: list[dict[str, str]],
) -> None:
    targets = [
        row
        for row in parse_rows
        if row.get("parse_action_route") == "asset_link_needs_cached_capture_or_approval"
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in targets:
        grouped[asset_key(source)].append(source)

    for key, members in sorted(grouped.items(), key=lambda item: (item[1][0].get("queue_rank", ""), item[0])):
        source = members[0]
        row = boundary_row(source)
        row.update(
            {
                "source_artifact": str(PARSE_ACTION.relative_to(ROOT)),
                "source_record_id": source.get("parse_action_id", ""),
                "approval_lane": "cached_asset_capture_or_manual_upload",
                "approval_priority": "P0_cached_asset_capture_needed",
                "approval_required": "true",
                "approval_prompt": "Provide a local cached copy or approve browser-state capture for this plan asset; do not fetch it by terminal curl.",
                "candidate_kind": source.get("candidate_kind", ""),
                "candidate_value": source.get("candidate_value", ""),
                "candidate_local_path": source.get("candidate_local_path", ""),
                "raw_source_row_count": len(members),
                "duplicate_or_collapsed_count": max(0, len(members) - 1),
                "blocked_reason": "content_asset_not_cached_or_capture_approval_required",
                "safe_next_action": "After approval or local upload, generate an asset/OCR preview and QA before source_packet consideration.",
                "evidence_note": "This is an official-page asset link discovered in cached HTML; asset content is not locally available in a parse-safe form.",
            }
        )
        rows.append(row)

        for duplicate in members[1:]:
            exclusions.append(
                {
                    "record_id": duplicate.get("parse_action_id", ""),
                    "university_name": duplicate.get("university_name", ""),
                    "reason": "duplicate_asset_candidate_collapsed",
                    "detail": key,
                }
            )


def add_pdf_manual_qa(rows: list[dict[str, object]], pdf_rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in pdf_rows:
        key = source.get("pdf_text_record_id") or source.get("queue_record_id") or "unknown_pdf"
        grouped[key].append(source)

    for key, members in sorted(grouped.items(), key=lambda item: (item[1][0].get("queue_rank", ""), item[0])):
        source = members[0]
        row_types = Counter(member.get("row_type", "") for member in members)
        special_status = Counter(member.get("special_type_boundary_status", "") for member in members)
        row = boundary_row(source)
        row.update(
            {
                "source_artifact": str(PDF_TABLE_QA.relative_to(ROOT)),
                "source_record_id": key,
                "approval_lane": "manual_pdf_table_layout_qa",
                "approval_priority": "P0_manual_pdf_table_layout_qa",
                "approval_required": "manual_qa",
                "approval_prompt": "Manually inspect original PDF/table layout to verify the Guangxi column and ordinary/subject/group mapping.",
                "candidate_kind": "local_pdf_table_layout",
                "candidate_value": source.get("pdf_path", ""),
                "candidate_local_path": source.get("text_artifact_path", ""),
                "raw_source_row_count": len(members),
                "duplicate_or_collapsed_count": len(members),
                "blocked_reason": "pdf_text_collapsed_columns_manual_layout_qa_required",
                "safe_next_action": "Use the original PDF/table view to confirm province column alignment before any source_packet preview.",
                "evidence_note": (
                    "Manual table QA rows collapsed into one approval item. "
                    f"row_type={dict(row_types)}; special_type_boundary={dict(special_status)}"
                ),
            }
        )
        rows.append(row)


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    endpoint_rows = read_csv(ENDPOINT_AUDIT)
    parse_rows = read_csv(PARSE_ACTION)
    pdf_rows = read_csv(PDF_TABLE_QA)
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    add_endpoint_approvals(rows, endpoint_rows)
    add_asset_approvals(rows, exclusions, parse_rows)
    add_pdf_manual_qa(rows, pdf_rows)

    rows.sort(key=lambda row: (str(row.get("queue_rank", "")), str(row.get("approval_lane", "")), str(row.get("candidate_value", ""))))
    for index, row in enumerate(rows, start=1):
        row["approval_record_id"] = f"reference_trend_520_p0_cached_branch_approval_{index:04d}"

    lane_counts = Counter(str(row["approval_lane"]) for row in rows)
    priority_counts = Counter(str(row["approval_priority"]) for row in rows)
    raw_asset_rows = sum(1 for row in parse_rows if row.get("parse_action_route") == "asset_link_needs_cached_capture_or_approval")
    unique_asset_rows = sum(1 for row in rows if row.get("approval_lane") == "cached_asset_capture_or_manual_upload")
    pdf_manual_source_rows = len(pdf_rows)

    rollup_rows: list[dict[str, object]] = [
        {"metric": "endpoint_audit_rows_read", "value": len(endpoint_rows), "note": str(ENDPOINT_AUDIT.relative_to(ROOT))},
        {"metric": "cached_parse_action_rows_read", "value": len(parse_rows), "note": str(PARSE_ACTION.relative_to(ROOT))},
        {"metric": "pdf_manual_table_rows_read", "value": len(pdf_rows), "note": str(PDF_TABLE_QA.relative_to(ROOT))},
        {"metric": "approval_queue_rows", "value": len(rows), "note": "Rows requiring human approval or manual QA."},
        {"metric": "asset_candidate_raw_rows", "value": raw_asset_rows, "note": "Raw asset rows before duplicate collapse."},
        {"metric": "asset_candidate_unique_rows", "value": unique_asset_rows, "note": "Unique asset approval rows after duplicate collapse."},
        {"metric": "asset_candidate_duplicate_rows_collapsed", "value": max(0, raw_asset_rows - unique_asset_rows), "note": ""},
        {"metric": "pdf_manual_qa_source_rows_collapsed", "value": pdf_manual_source_rows, "note": "Manual PDF line rows collapsed into PDF-level approval item(s)."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
        {"metric": "network_browser_or_replay_used", "value": "false", "note": "This builder only reads local CSV artifacts."},
    ]
    rollup_rows += [
        {"metric": f"approval_lane::{key}", "value": count, "note": ""}
        for key, count in sorted(lane_counts.items())
    ]
    rollup_rows += [
        {"metric": f"approval_priority::{key}", "value": count, "note": ""}
        for key, count in sorted(priority_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "source_artifacts_exist",
            "status": "pass" if ENDPOINT_AUDIT.exists() and PARSE_ACTION.exists() and PDF_TABLE_QA.exists() else "fail",
            "value": "endpoint|parse_action|pdf_manual_table",
            "note": "",
        },
        {
            "qa_check": "approval_rows_generated",
            "status": "pass" if rows else "warn",
            "value": len(rows),
            "note": "Human-gated queue only.",
        },
        {
            "qa_check": "asset_duplicates_accounted",
            "status": "pass" if raw_asset_rows - unique_asset_rows == len(exclusions) else "fail",
            "value": f"raw={raw_asset_rows}; unique={unique_asset_rows}; exclusions={len(exclusions)}",
            "note": "",
        },
        {
            "qa_check": "no_source_packet_or_intake_rows",
            "status": "pass" if all(row["reference_trend_pool_eligible"] == "false" for row in rows) else "fail",
            "value": "false",
            "note": "The queue is not intake.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "network_browser_or_replay_used",
            "status": "pass",
            "value": "false",
            "note": "No live access was performed.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    lane_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("approval_lane::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 Cached Branch Human Approval Queue

Date: {date.today().isoformat()}

Scope: consolidated human approval/manual QA queue for P0 cached branch blockers. This package merges cached endpoint replay approvals, cached asset capture approvals, and PDF table-layout QA into one operator-facing queue.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_queue.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_exclusion_log.csv`

## Coverage

- Approval/manual QA rows: {len(rows)}
- QA status: {qa_status}

## Approval Lanes

{lane_lines or "- none"}

## Boundary

This queue is not a source_packet, reference trend intake, canonical, ML, or 32-school decision_pool artifact. Browser/form replay, asset capture, OCR, and manual PDF layout decisions remain gated until the user explicitly approves them.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 108. 2026-05-17 P0 cached branch human approval queue"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    lane_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("approval_lane::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 cached branch human approval queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_queue.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_branch_human_approval_queue.md`

覆盖结果：合并本地 cached 分支的人工作业入口，共 {len(rows)} 条 approval/manual QA rows；lane 分布：{lane_summary or 'none'}。QA {qa_status}。其中 asset candidate raw rows 已去重折叠，PDF manual table rows 折叠为 PDF-level QA 项。

准入边界：本轮只生成人工授权/人工 QA 队列，不执行联网、浏览器/form replay、资产捕获、OCR、source_packet parse 或 reference trend intake；canonical/ML、32 所 decision_pool 均继续关闭。
"""
        )


def main() -> None:
    rows, rollup_rows, qa_rows, exclusions = build()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusions, ["record_id", "university_name", "reason", "detail"])
    write_doc(rows, rollup_rows, qa_rows)
    append_handoff(rows, rollup_rows, qa_rows)
    print(f"wrote {len(rows)} cached branch approval rows")


if __name__ == "__main__":
    main()
