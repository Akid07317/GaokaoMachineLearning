#!/usr/bin/env python3
"""Create a local drilldown queue for P0 rows with existing source candidates.

The queue is derived from the P0 next-action board and the already-collected
candidate preview files. It does not fetch remote content and it does not open
reference_trend_pool, canonical, ML, or the 32-school decision_pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

NEXT_ACTIONS = CLEAN / "reference_trend_520_p0_source_discovery_next_actions.csv"
OUT = CLEAN / "reference_trend_520_p0_local_candidate_drilldown_queue.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_local_candidate_drilldown_queue_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_local_candidate_drilldown_queue_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_local_candidate_drilldown_queue_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_local_candidate_drilldown_queue.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

LOCAL_LANE = "existing_candidate_parse_or_endpoint_drilldown"

FIELDS = [
    "drilldown_record_id",
    "action_record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "candidate_record_id",
    "source_id",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "source_role",
    "source_packet_status",
    "collector_confidence",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "special_type_detected",
    "raw_file_path",
    "candidate_requires_network",
    "candidate_requires_manual_approval",
    "candidate_eligible_for_intake_preview",
    "candidate_next_action",
    "drilldown_lane",
    "drilldown_priority",
    "safe_local_action",
    "approval_or_live_fetch_needed",
    "expected_output_layer",
    "source_artifact_path",
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


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def lower_blob(row: dict[str, str]) -> str:
    fields = [
        "source_packet_status",
        "source_role",
        "collector_confidence",
        "source_title",
        "collector_note",
        "next_action",
        "raw_file_path",
    ]
    return " ".join(str(row.get(field, "")) for field in fields).lower()


def classify(candidate: dict[str, str]) -> dict[str, str]:
    blob = lower_blob(candidate)
    raw_file = candidate.get("raw_file_path", "").strip()
    requires_network = truthy(candidate.get("requires_network", ""))
    requires_manual = truthy(candidate.get("requires_manual_approval", ""))
    has_plan_count = truthy(candidate.get("source_contains_plan_count", "")) or "plan table" in blob

    if "third_party_only_rejected" in blob or "rejected_third_party_only" in blob:
        return {
            "drilldown_lane": "reject_third_party_only_candidate",
            "drilldown_priority": "P0C9_reject_no_local_parse",
            "safe_local_action": "Keep as rejected clue only; do not parse into source_packet or intake.",
            "approval_or_live_fetch_needed": "no_for_rejection_yes_for_new_official_search",
        }
    if "no_official_source_found" in blob:
        return {
            "drilldown_lane": "no_local_candidate_found_in_prior_batch",
            "drilldown_priority": "P0C8_requires_separate_discovery_approval",
            "safe_local_action": "Keep in discovery backoff; do not infer plan fields from absence.",
            "approval_or_live_fetch_needed": "yes_for_new_live_official_search",
        }
    if "no_guangxi_rows" in blob or "no_structured_rows" in blob or "context_only" in blob or "charter" in blob:
        return {
            "drilldown_lane": "context_or_no_rows_hold",
            "drilldown_priority": "P0C7_context_only_not_plan_source",
            "safe_local_action": "Use as source context only; search or exact URL is needed before any plan source_packet.",
            "approval_or_live_fetch_needed": "conditional_if_exact_official_plan_url_missing",
        }
    if "query" in blob or "endpoint" in blob or "parameterized" in blob or "portal" in blob:
        return {
            "drilldown_lane": "endpoint_or_portal_drilldown",
            "drilldown_priority": "P0C4_endpoint_shape_review",
            "safe_local_action": "Inspect cached portal/query metadata and known endpoint shape; request browser/form replay only if local metadata is insufficient.",
            "approval_or_live_fetch_needed": "conditional_for_browser_or_form_replay",
        }
    if "image" in blob or "ocr" in blob or "poster" in blob or "asset" in blob:
        return {
            "drilldown_lane": "image_or_asset_ocr_candidate",
            "drilldown_priority": "P0C3_ocr_or_asset_extract",
            "safe_local_action": "Use cached asset path if present; otherwise request browser/image capture approval before OCR/transcription.",
            "approval_or_live_fetch_needed": "yes_if_asset_not_cached_or_manual_ocr_needed",
        }
    if "pdf" in blob or str(candidate.get("source_url", "")).lower().endswith(".pdf"):
        return {
            "drilldown_lane": "pdf_parse_candidate",
            "drilldown_priority": "P0C2_pdf_parse_or_download",
            "safe_local_action": "Parse cached PDF if raw_file_path exists; otherwise request approval before download/browser retrieval.",
            "approval_or_live_fetch_needed": "no_if_cached_pdf_else_yes_for_download",
        }
    if "extractable" in blob or raw_file or has_plan_count:
        return {
            "drilldown_lane": "cached_html_table_parse_candidate",
            "drilldown_priority": "P0C1_cached_table_parse",
            "safe_local_action": "Parse cached HTML/table into a source_packet parse preview and hold for group mapping QA.",
            "approval_or_live_fetch_needed": "no_for_cached_local_parse",
        }
    return {
        "drilldown_lane": "metadata_drilldown_needed",
        "drilldown_priority": "P0C5_metadata_review",
        "safe_local_action": "Review source candidate metadata before deciding parse, rejection, or approval route.",
        "approval_or_live_fetch_needed": "conditional",
    }


def candidate_rows_for_action(action: dict[str, str]) -> list[tuple[Path, dict[str, str]]]:
    matches: list[tuple[Path, dict[str, str]]] = []
    code = action.get("university_code", "").strip()
    for rel in str(action.get("artifact_paths", "")).split("|"):
        if not rel:
            continue
        path = ROOT / rel
        if not path.exists():
            continue
        for row in read_csv(path):
            if row.get("university_code", "").strip() == code:
                matches.append((path, row))
    return matches


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    actions = read_csv(NEXT_ACTIONS)
    local_actions = [row for row in actions if row.get("action_lane") == LOCAL_LANE]
    rows: list[dict[str, object]] = []
    missing = 0

    for action in local_actions:
        candidates = candidate_rows_for_action(action)
        if not candidates:
            missing += 1
            candidates = [(Path(""), {})]
        for path, candidate in candidates:
            cls = classify(candidate)
            index = len(rows) + 1
            rows.append(
                {
                    "drilldown_record_id": f"reference_trend_520_p0_local_drilldown_{index:04d}",
                    "action_record_id": action.get("action_record_id", ""),
                    "queue_record_id": action.get("queue_record_id", ""),
                    "queue_rank": action.get("queue_rank", ""),
                    "university_code": action.get("university_code", ""),
                    "university_name": action.get("university_name", ""),
                    "group_pair_key": action.get("group_pair_key", ""),
                    "group_code": action.get("group_code", ""),
                    "rank_2024": action.get("rank_2024", ""),
                    "rank_2025": action.get("rank_2025", ""),
                    "rank_delta_2025_minus_2024": action.get("rank_delta_2025_minus_2024", ""),
                    "trend_direction": action.get("trend_direction", ""),
                    "candidate_record_id": candidate.get("record_id", ""),
                    "source_id": candidate.get("source_id", ""),
                    "source_url": candidate.get("source_url", ""),
                    "source_owner": candidate.get("source_owner", ""),
                    "source_title": candidate.get("source_title", ""),
                    "published_date": candidate.get("published_date", ""),
                    "source_role": candidate.get("source_role", ""),
                    "source_packet_status": candidate.get("source_packet_status", ""),
                    "collector_confidence": candidate.get("collector_confidence", ""),
                    "source_contains_group_code": candidate.get("source_contains_group_code", ""),
                    "source_contains_min_score": candidate.get("source_contains_min_score", ""),
                    "source_contains_min_rank": candidate.get("source_contains_min_rank", ""),
                    "source_contains_plan_count": candidate.get("source_contains_plan_count", ""),
                    "special_type_detected": candidate.get("special_type_detected", ""),
                    "raw_file_path": candidate.get("raw_file_path", ""),
                    "candidate_requires_network": candidate.get("requires_network", ""),
                    "candidate_requires_manual_approval": candidate.get("requires_manual_approval", ""),
                    "candidate_eligible_for_intake_preview": candidate.get("eligible_for_intake_preview", ""),
                    "candidate_next_action": candidate.get("next_action", ""),
                    **cls,
                    "expected_output_layer": "source_packet_parse_preview_or_rejection_note_only_not_canonical",
                    "source_artifact_path": str(path.relative_to(ROOT)) if path else "",
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "p0_local_candidate_drilldown_only_not_32_school_decision_pool",
                    "evidence_note": "Joined from P0 next-actions and existing candidate preview files; no web fetch performed.",
                }
            )

    lane_counts = Counter(str(row["drilldown_lane"]) for row in rows)
    priority_counts = Counter(str(row["drilldown_priority"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "local_next_action_rows", "value": len(local_actions), "note": "P0 rows routed to existing-candidate drilldown."},
        {"metric": "candidate_drilldown_rows", "value": len(rows), "note": "Candidate-level rows emitted; multiple candidates per university/group are allowed."},
        {"metric": "candidate_missing_rows", "value": missing, "note": "Actions without matching candidate rows in listed artifact paths."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "Routing/parse queue only."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No intake or calibration rows produced."},
    ]
    rollup_rows += [
        {"metric": f"drilldown_lane::{lane}", "value": count, "note": ""}
        for lane, count in sorted(lane_counts.items())
    ]
    rollup_rows += [
        {"metric": f"drilldown_priority::{priority}", "value": count, "note": ""}
        for priority, count in sorted(priority_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_next_actions_exists",
            "status": "pass" if NEXT_ACTIONS.exists() else "fail",
            "value": str(NEXT_ACTIONS.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "local_lane_rows_detected",
            "status": "pass" if len(local_actions) == 43 else "review",
            "value": len(local_actions),
            "note": "Expected 43 from the current P0 next-action rollup.",
        },
        {
            "qa_check": "candidate_rows_joined",
            "status": "pass" if rows and missing == 0 else "review",
            "value": len(rows),
            "note": f"Missing candidate joins: {missing}.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
    ]

    exclusion_rows: list[dict[str, object]] = [
        {
            "exclusion_record_id": "reference_trend_520_p0_local_drilldown_exclusion_0001",
            "excluded_scope": "reference_trend_intake_canonical_ml",
            "excluded_rows": len(rows),
            "reason": "Local candidate drilldown only; no row is eligible for intake/canonical/ML from this queue.",
        },
        {
            "exclusion_record_id": "reference_trend_520_p0_local_drilldown_exclusion_0002",
            "excluded_scope": "live_network_fetch",
            "excluded_rows": len(rows),
            "reason": "No web fetch, browser, form replay, header/cookie replay, or download was performed in this run.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusion_rows


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]]) -> None:
    lane_counts = Counter(str(row["drilldown_lane"]) for row in rows)
    lines = [
        "# Reference Trend 520 P0 Local Candidate Drilldown Queue",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: convert the P0 `existing_candidate_parse_or_endpoint_drilldown` lane into candidate-level parse/rejection/approval routes without doing any live fetch.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Coverage",
        "",
        f"- Candidate drilldown rows: {len(rows)}",
        "",
        "## Drilldown Lane Rollup",
        "",
    ]
    for lane, count in sorted(lane_counts.items()):
        lines.append(f"- {lane}: {count}")
    lines += [
        "",
        "## Boundary",
        "",
        "This is a non-baseline parse-routing queue. It can only feed future source_packet parse previews, rejection notes, or manual approval queues with QA. It does not open reference_trend_pool, canonical, ML, or the 32-school decision_pool.",
    ]
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 101. 2026-05-16 P0 local candidate drilldown queue"
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    lane_counts = Counter(str(row["drilldown_lane"]) for row in rows)
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            "\n\n"
            f"{marker}\n\n"
            "已新增 P0 local candidate drilldown queue：\n\n"
            f"- `{OUT.relative_to(ROOT)}`\n"
            f"- `{ROLLUP.relative_to(ROOT)}`\n"
            f"- `{QA.relative_to(ROOT)}`\n"
            f"- `{EXCLUSION.relative_to(ROOT)}`\n"
            f"- `{DOC.relative_to(ROOT)}`\n\n"
            f"覆盖结果：从 P0 existing-candidate lane 派生 {len(rows)} 条 candidate-level drilldown rows；"
            + "；".join(f"{lane}={count}" for lane, count in sorted(lane_counts.items()))
            + "。\n\n"
            "准入边界：本轮只做已有候选的本地解析/拒绝/审批路线分流，不执行联网抓取，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。\n"
        )


def main() -> None:
    rows, rollup_rows, qa_rows, exclusion_rows = build()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])
    write_csv(EXCLUSION, exclusion_rows, ["exclusion_record_id", "excluded_scope", "excluded_rows", "reason"])
    write_doc(rows, rollup_rows)
    append_handoff(rows)


if __name__ == "__main__":
    main()
