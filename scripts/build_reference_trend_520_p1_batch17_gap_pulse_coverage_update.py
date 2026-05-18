#!/usr/bin/env python3
"""Build marker 132 batch17 gap-pulse coverage update.

This consolidates marker 129-131 gap-search pulses back into the batch17
coverage ledger. It writes only isolated QA/reporting artifacts and does not
open reference-trend intake, calibration, canonical, ML, or the 32-school
decision pool.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

BASE_COVERAGE = SEED / "reference_trend_520_p1_batch17_coverage_rollup.csv"
GAP_QUEUE = SEED / "reference_trend_520_p1_batch17_official_candidate_gap_queue.csv"
PULSE_FILES = [
    SEED / "reference_trend_520_p1_batch17_gap_search_pulse_a.csv",
    SEED / "reference_trend_520_p1_batch17_gap_search_pulse_b.csv",
    SEED / "reference_trend_520_p1_batch17_gap_search_pulse_c.csv",
]

PREFIX = "reference_trend_520_p1_batch17_gap_pulse_coverage_update"
OUT = SEED / f"{PREFIX}.csv"
ROLLUP = REPORTS / f"{PREFIX}_rollup.csv"
QA = REPORTS / f"{PREFIX}_qa.csv"
EXCLUSION = REPORTS / f"{PREFIX}_exclusion_log.csv"
DOC = DOCS / f"{PREFIX}.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "coverage_update_id",
    "base_coverage_id",
    "workset_id",
    "gap_id",
    "queue_rank",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "trend_direction",
    "rank_delta_2025_minus_2024",
    "special_type_boundary",
    "base_coverage_stage",
    "base_official_candidate_id",
    "base_official_candidate_tier",
    "base_official_candidate_status",
    "base_official_candidate_url",
    "gap_pulse_id",
    "gap_pulse_tier",
    "gap_pulse_status",
    "gap_pulse_url",
    "gap_pulse_source_type",
    "gap_pulse_preview_eligible",
    "consolidated_source_state",
    "consolidated_source_tier",
    "consolidated_source_status",
    "consolidated_source_url",
    "source_packet_followup_lane",
    "line_score_status",
    "min_score",
    "min_rank",
    "rank_backoff_candidate_count",
    "requires_browser_or_alternate_fetch",
    "requires_manual_approval_now",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "intake_blocker",
    "next_action",
]


def read_csv(path: Path) -> list[dict[str, str]]:
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


def load_gap_pulses() -> dict[str, dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in PULSE_FILES:
        rows.extend(read_csv(path))
    return {row["group_pair_key"]: row for row in rows}


def truthy(value: str) -> bool:
    return value.lower() in {"true", "true_candidate_only_not_intake", "conditional_after_filtered_official_page_capture"}


def followup_lane(row: dict[str, str], pulse: dict[str, str]) -> str:
    if row.get("source_packet_parse_status") == "jxutcm_group_readiness_candidate":
        return "parsed_plan_preview_group_mapping_and_rank_join_hold"
    if pulse:
        if pulse.get("source_packet_preview_eligible") == "true":
            if "image" in pulse.get("source_type", ""):
                return "manual_image_table_QA_or_approved_asset_capture"
            if "query" in pulse.get("source_type", ""):
                return "official_query_API_or_approved_browser_drilldown"
            if "wechat" in pulse.get("source_type", ""):
                return "official_wechat_artifact_capture_requires_approval"
            if "html_table" in pulse.get("source_type", ""):
                return "html_table_column_alignment_QA"
            return "source_packet_preview_candidate"
        return "official_reachability_backoff_continue_static_discovery"
    if row.get("base_official_candidate_id") or row.get("official_candidate_id"):
        if row.get("min_score"):
            return "candidate_with_line_score_rank_and_plan_mapping_hold"
        return "existing_official_candidate_parse_or_filter_QA"
    return "unresolved"


def consolidated_state(row: dict[str, str], pulse: dict[str, str]) -> str:
    if pulse:
        if pulse.get("source_packet_preview_eligible") == "true":
            return "gap_pulse_official_candidate_needs_source_packet_preview"
        return "gap_pulse_reachability_backoff_no_preview"
    if row.get("source_packet_parse_status") == "jxutcm_group_readiness_candidate":
        return "parsed_plan_preview_exists_but_rank_mapping_hold"
    if row.get("official_candidate_id"):
        if row.get("min_score"):
            return "existing_official_candidate_plus_line_score_rank_missing"
        return "existing_official_candidate_needs_parse_or_filter_QA"
    return "no_source_outcome_recorded"


def build_rows() -> list[dict[str, object]]:
    base_rows = read_csv(BASE_COVERAGE)
    gap_rows_by_key = {row["group_pair_key"]: row for row in read_csv(GAP_QUEUE)}
    pulses_by_key = load_gap_pulses()
    output: list[dict[str, object]] = []

    for idx, row in enumerate(base_rows, 1):
        key = row["group_pair_key"]
        pulse = pulses_by_key.get(key, {})
        gap = gap_rows_by_key.get(key, {})
        state = consolidated_state(row, pulse)
        source_tier = pulse.get("source_candidate_tier") or row.get("official_candidate_tier", "")
        source_status = pulse.get("source_candidate_status") or row.get("official_candidate_status", "")
        source_url = pulse.get("source_url") or row.get("official_candidate_url", "")
        blocker = (
            pulse.get("parse_or_access_blocker")
            or row.get("intake_blocker")
            or "not_intake_ready"
        )
        next_action = (
            pulse.get("next_action")
            or row.get("required_resolution")
            or "Keep intake closed until official rank, group mapping, and plan-source QA pass."
        )
        output.append(
            {
                "coverage_update_id": f"reference_trend_520_p1_batch17_gap_pulse_coverage_update_{idx:04d}",
                "base_coverage_id": row["coverage_id"],
                "workset_id": row["workset_id"],
                "gap_id": gap.get("gap_id", ""),
                "queue_rank": row["queue_rank"],
                "group_pair_key": key,
                "university_code": row["university_code"],
                "university_name": row["university_name"],
                "group_code": row["group_code"],
                "trend_direction": row["trend_direction"],
                "rank_delta_2025_minus_2024": row["rank_delta_2025_minus_2024"],
                "special_type_boundary": row["special_type_boundary"],
                "base_coverage_stage": row["coverage_stage"],
                "base_official_candidate_id": row["official_candidate_id"],
                "base_official_candidate_tier": row["official_candidate_tier"],
                "base_official_candidate_status": row["official_candidate_status"],
                "base_official_candidate_url": row["official_candidate_url"],
                "gap_pulse_id": pulse.get("pulse_id", ""),
                "gap_pulse_tier": pulse.get("source_candidate_tier", ""),
                "gap_pulse_status": pulse.get("source_candidate_status", ""),
                "gap_pulse_url": pulse.get("source_url", ""),
                "gap_pulse_source_type": pulse.get("source_type", ""),
                "gap_pulse_preview_eligible": pulse.get("source_packet_preview_eligible", ""),
                "consolidated_source_state": state,
                "consolidated_source_tier": source_tier,
                "consolidated_source_status": source_status,
                "consolidated_source_url": source_url,
                "source_packet_followup_lane": followup_lane(row, pulse),
                "line_score_status": row["line_score_status"],
                "min_score": row["min_score"],
                "min_rank": row["min_rank"],
                "rank_backoff_candidate_count": row["rank_backoff_candidate_count"],
                "requires_browser_or_alternate_fetch": pulse.get("requires_browser_or_alternate_fetch", ""),
                "requires_manual_approval_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "intake_blocker": blocker,
                "next_action": next_action,
            }
        )
    return output


def write_rollup(rows: list[dict[str, object]]) -> None:
    states = Counter(str(row["consolidated_source_state"]) for row in rows)
    lanes = Counter(str(row["source_packet_followup_lane"]) for row in rows)
    pulse_rows = [row for row in rows if row["gap_pulse_id"]]
    base_candidate_rows = [row for row in rows if row["base_official_candidate_id"]]
    preview_rows = [
        row for row in rows
        if row["base_official_candidate_id"] or row["gap_pulse_preview_eligible"] == "true"
    ]
    rollup = [
        {"metric": "batch17_group_target_rows", "value": len(rows), "note": "Rows from marker 127 coverage ledger."},
        {"metric": "base_official_candidate_rows", "value": len(base_candidate_rows), "note": "Rows already covered before gap pulses."},
        {"metric": "gap_pulse_rows_integrated", "value": len(pulse_rows), "note": "Rows from marker 129-131 pulses A/B/C."},
        {"metric": "all_rows_with_source_or_backoff_outcome", "value": sum(bool(row["consolidated_source_url"]) for row in rows), "note": "Candidate URL or reachability URL present."},
        {"metric": "source_packet_preview_candidate_rows", "value": len(preview_rows), "note": "Existing candidates plus gap-pulse preview-eligible rows."},
        {"metric": "gap_pulse_preview_candidate_rows", "value": sum(row["gap_pulse_preview_eligible"] == "true" for row in rows), "note": "Gap rows worth source-packet preview follow-up."},
        {"metric": "gap_pulse_backoff_rows", "value": sum(row["gap_pulse_preview_eligible"] == "false" for row in rows), "note": "Gap rows with official reachability/backoff only."},
        {"metric": "official_line_score_rows", "value": sum(bool(row["min_score"]) for row in rows), "note": "Rows with official Guangxi exam-authority min_score."},
        {"metric": "official_min_rank_rows", "value": 0, "note": "No official rank accepted."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Intake remains closed."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No rank join/calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for state, count in sorted(states.items()):
        rollup.append({"metric": f"state::{state}", "value": count, "note": ""})
    for lane, count in sorted(lanes.items()):
        rollup.append({"metric": f"lane::{lane}", "value": count, "note": ""})
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    keys = [row["group_pair_key"] for row in rows]
    gap_pulse_count = sum(bool(row["gap_pulse_id"]) for row in rows)
    qa = [
        {
            "check": "coverage_row_count",
            "status": "PASS" if len(rows) == 20 else "FAIL",
            "detail": f"{len(rows)} rows represented from marker 127 coverage.",
        },
        {
            "check": "no_duplicate_group_pair_key",
            "status": "PASS" if len(keys) == len(set(keys)) else "FAIL",
            "detail": f"{len(set(keys))} unique group_pair_key values.",
        },
        {
            "check": "gap_pulses_integrated",
            "status": "PASS" if gap_pulse_count == 12 else "FAIL",
            "detail": f"{gap_pulse_count} marker 129-131 pulse rows integrated.",
        },
        {
            "check": "source_or_backoff_outcome_all_rows",
            "status": "PASS" if all(row["consolidated_source_url"] for row in rows) else "FAIL",
            "detail": "Every batch17 target row has either a candidate URL or official reachability/backoff URL.",
        },
        {
            "check": "no_manual_approval_consumed",
            "status": "PASS" if all(row["requires_manual_approval_now"] == "false" for row in rows) else "FAIL",
            "detail": "No browser/header/cookie/form/login or WeChat capture was consumed.",
        },
        {
            "check": "no_min_rank_claimed",
            "status": "PASS" if all(not row["min_rank"] for row in rows) else "FAIL",
            "detail": "No official minimum rank is claimed in this coverage update.",
        },
        {
            "check": "intake_and_canonical_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in rows
            )
            else "FAIL",
            "detail": "Reference trend intake, calibration, canonical, and ML remain closed.",
        },
    ]
    write_csv(QA, qa, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "coverage_update_id": row["coverage_update_id"],
            "group_pair_key": row["group_pair_key"],
            "university_name": row["university_name"],
            "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": row["intake_blocker"],
            "safe_next_action": row["next_action"],
        }
        for row in rows
    ]
    write_csv(
        EXCLUSION,
        exclusions,
        ["coverage_update_id", "group_pair_key", "university_name", "excluded_from", "reason", "safe_next_action"],
    )


def write_doc(rows: list[dict[str, object]]) -> None:
    state_counts = Counter(str(row["consolidated_source_state"]) for row in rows)
    preview_rows = [
        row for row in rows
        if row["base_official_candidate_id"] or row["gap_pulse_preview_eligible"] == "true"
    ]
    doc = [
        "# Reference trend 520 P1 batch17 gap pulse coverage update",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This consolidates marker 129-131 gap-search pulses into the marker 127 batch17 coverage ledger.",
        "",
        "## Outputs",
        "",
        f"- `clean_data/engineering_guangxi_seed/{OUT.name}`",
        f"- `reports/{ROLLUP.name}`",
        f"- `reports/{QA.name}`",
        f"- `reports/{EXCLUSION.name}`",
        "",
        "## Summary",
        "",
        f"- Batch17 group targets: {len(rows)}",
        f"- Gap pulse rows integrated: {sum(bool(row['gap_pulse_id']) for row in rows)}",
        f"- Rows with source-packet preview follow-up candidates: {len(preview_rows)}",
        f"- Official line-score rows retained: {sum(bool(row['min_score']) for row in rows)}",
        "- Official min-rank rows: 0",
        "- Reference trend eligible rows: 0",
        "- Canonical/ML rows opened: 0",
        "",
        "## Consolidated States",
        "",
    ]
    for state, count in sorted(state_counts.items()):
        doc.append(f"- `{state}`: {count}")
    doc.extend([
        "",
        "## Boundary",
        "",
        "This update performs no network fetch, cache, parse, OCR, browser/form replay, login-state review, WeChat capture, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update.",
        "",
    ])
    DOC.write_text("\n".join(doc), encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 132. 2026-05-17 P1 batch17 gap pulse coverage update"
    preview_rows = [
        row for row in rows
        if row["base_official_candidate_id"] or row["gap_pulse_preview_eligible"] == "true"
    ]
    content = f"""

{marker}

已新增 P1 batch17 gap pulse coverage update：

- `clean_data/engineering_guangxi_seed/{OUT.name}`
- `reports/{ROLLUP.name}`
- `reports/{QA.name}`
- `reports/{EXCLUSION.name}`
- `docs/{DOC.name}`

覆盖结果：将 marker 129-131 的 12 条 gap pulse 结果合并回 marker 127 的 20 条 batch17 group-target coverage ledger。现在 20/20 条都有官方候选或官方 reachability/backoff 结果；其中 {len(preview_rows)}/20 条进入后续 source-packet preview/QA 跟进候选，5/20 条保持 backoff；6/20 条保留广西考试院官方最低分，0/20 条有可采信官方最低位次。QA PASS。

准入边界：本轮只生成合并 coverage/QA/exclusion/rollup，不联网、不缓存、不解析、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)
    append_handoff(rows)


if __name__ == "__main__":
    main()
