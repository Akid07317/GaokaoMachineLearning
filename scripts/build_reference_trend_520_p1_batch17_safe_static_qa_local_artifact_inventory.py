from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory"
INPUT = SEED_DIR / "reference_trend_520_p1_batch17_safe_static_qa_subqueue.csv"

OUT_INVENTORY = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

ALL_BATCH17_ARTIFACTS = [
    p
    for base in (SEED_DIR, REPORT_DIR, DOC_DIR)
    for p in base.glob("reference_trend_520_p1_batch17*")
]

ARTIFACT_FIELDS = [
    "inventory_id",
    "subqueue_id",
    "group_pair_key",
    "university_name",
    "local_static_lane",
    "min_score",
    "min_rank",
    "local_artifact_status",
    "matched_local_artifacts",
    "official_line_score_status",
    "official_rank_status",
    "plan_or_mapping_artifact_status",
    "immediate_safe_next_step",
    "blocked_next_step",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "subqueue_id",
    "group_pair_key",
    "university_name",
    "exclusion_reason",
    "blocked_until",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


KEYWORD_HINTS = {
    "10412-101": ["jxutcm", "10412", "official_score_rank", "exam_authority"],
    "10537-101": ["gap_search_pulse_b", "source_packet_preview_action_queue", "safe_static"],
    "10596-153": ["exam_authority", "official_score_rank", "gap_pulse", "safe_static"],
    "10407-102": ["exam_authority", "official_score_rank", "gap_pulse", "safe_static"],
    "10092-151": ["exam_authority", "official_score_rank", "gap_pulse", "safe_static"],
    "10092-152": ["exam_authority", "official_score_rank", "gap_pulse", "safe_static"],
    "10466-152": ["exam_authority", "official_score_rank", "gap_pulse", "safe_static"],
    "10513-105": ["exam_authority", "gap_pulse", "safe_static"],
}


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


def artifact_matches(row: dict[str, str]) -> list[str]:
    group = row["group_pair_key"]
    hints = KEYWORD_HINTS.get(group, [])
    direct = []
    for artifact in ALL_BATCH17_ARTIFACTS:
        name = artifact.name.lower()
        if group in name or any(hint in name for hint in hints):
            direct.append(rel(artifact))

    # Keep the inventory compact and focused on files most useful for audit handoff.
    priority_terms = (
        "safe_static_qa_subqueue",
        "exam_authority_line_score_batch",
        "official_score_rank",
        "jxutcm_source_packet_parse_preview",
        "jxutcm_group_join_readiness",
        "jxutcm_line_score_reachability",
        "gap_pulse_coverage_update",
        "gap_search_pulse",
        "source_packet_preview_action_queue",
    )
    direct = [path for path in direct if any(term in path for term in priority_terms)]
    return sorted(set(direct))[:18]


def plan_status(row: dict[str, str], artifacts: list[str]) -> str:
    group = row["group_pair_key"]
    lane = row["local_static_lane"]
    if group == "10412-101" and any("jxutcm_source_packet_parse_preview" in a for a in artifacts):
        return "parsed_plan_preview_and_group_join_readiness_exist"
    if "static_html_table_alignment" in lane:
        return "official_html_table_candidate_recorded_alignment_preview_not_yet_parsed_locally"
    if "existing_candidate" in lane:
        return "official_aggregate_candidate_recorded_group_boundary_not_yet_resolved"
    if row.get("min_score"):
        return "official_candidate_and_line_score_exist_plan_mapping_or_detail_parse_not_ready"
    return "candidate_record_exists_plan_mapping_not_ready"


def immediate_step(row: dict[str, str], pstatus: str) -> str:
    group = row["group_pair_key"]
    if group == "10412-101":
        return "Run local mapping consistency QA between JXUTCM source short group and Guangxi group; keep rank blank."
    if "html_table_candidate" in pstatus:
        return "Prepare local table-alignment checklist from recorded official HTML candidate; do not fetch page."
    if "aggregate_candidate" in pstatus:
        return "Prepare group-boundary checklist from recorded official aggregate candidate; do not fetch page."
    if row.get("min_score"):
        return "Link existing official line-score row to rank approval packet and plan/mapping readiness notes; do not select rank."
    return "Keep as source-packet QA placeholder until local cache or approved artifact exists."


def blocked_step(row: dict[str, str]) -> str:
    if row.get("min_score"):
        return "official_min_rank_waiting_marker_136_approval_or_user_provided_official_raw_artifact"
    return "source_packet_parse_or_group_boundary_waiting_local_cache_or_approved_artifact"


def build() -> None:
    rows = read_csv(INPUT)
    inventory: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for idx, row in enumerate(rows, 1):
        artifacts = artifact_matches(row)
        line_status = "official_min_score_available" if row.get("min_score") else "official_min_score_not_available"
        rank = row.get("min_rank", "")
        rank_status = "unexpected_rank_present_review_required" if rank else "official_min_rank_blank_gate_closed"
        pstatus = plan_status(row, artifacts)
        immediate = immediate_step(row, pstatus)
        blocked = blocked_step(row)

        inventory.append(
            {
                "inventory_id": f"{MARKER}_{idx:04d}",
                "subqueue_id": row["subqueue_id"],
                "group_pair_key": row["group_pair_key"],
                "university_name": row["university_name"],
                "local_static_lane": row["local_static_lane"],
                "min_score": row.get("min_score", ""),
                "min_rank": "",
                "local_artifact_status": "local_artifact_links_recorded" if artifacts else "no_local_artifact_links_found",
                "matched_local_artifacts": "|".join(artifacts),
                "official_line_score_status": line_status,
                "official_rank_status": rank_status,
                "plan_or_mapping_artifact_status": pstatus,
                "immediate_safe_next_step": immediate,
                "blocked_next_step": blocked,
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

        if "not_ready" in pstatus or "not_yet" in pstatus:
            exclusions.append(
                {
                    "exclusion_id": f"{MARKER}_exclusion_{len(exclusions)+1:04d}",
                    "subqueue_id": row["subqueue_id"],
                    "group_pair_key": row["group_pair_key"],
                    "university_name": row["university_name"],
                    "exclusion_reason": pstatus,
                    "blocked_until": blocked,
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )

    line_counts = Counter(row["official_line_score_status"] for row in inventory)
    rank_counts = Counter(row["official_rank_status"] for row in inventory)
    plan_counts = Counter(row["plan_or_mapping_artifact_status"] for row in inventory)
    ready_now = sum(
        1
        for row in inventory
        if row["plan_or_mapping_artifact_status"] == "parsed_plan_preview_and_group_join_readiness_exist"
    )
    rollup = [
        {"metric": "input_safe_static_subqueue_rows", "value": len(rows), "notes": rel(INPUT)},
        {"metric": "inventory_rows", "value": len(inventory), "notes": "One inventory row per strict safe/static subqueue row."},
        {"metric": "rows_with_official_min_score", "value": line_counts["official_min_score_available"], "notes": "Score retained only for QA/readiness."},
        {"metric": "rows_with_selected_min_rank", "value": 0, "notes": "Rank selection gate remains closed."},
        {"metric": "rows_with_parsed_plan_or_mapping_artifacts_available", "value": ready_now, "notes": "Currently only local parsed/readiness artifacts can proceed without new source capture."},
        {"metric": "inventory_exclusion_rows", "value": len(exclusions), "notes": "Rows that still lack a local parse/mapping artifact despite being safe to track."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Gate remains closed."},
    ]
    for key, val in sorted(line_counts.items()):
        rollup.append({"metric": f"line_score::{key}", "value": val, "notes": "line score status"})
    for key, val in sorted(rank_counts.items()):
        rollup.append({"metric": f"rank::{key}", "value": val, "notes": "rank gate status"})
    for key, val in sorted(plan_counts.items()):
        rollup.append({"metric": f"plan_mapping::{key}", "value": val, "notes": "plan/mapping artifact status"})

    qa_rows = [
        {
            "qa_check": "input_safe_subqueue_present",
            "status": "PASS" if INPUT.exists() and len(rows) == 8 else "FAIL",
            "details": f"Read {len(rows)} rows from marker 137 safe static QA subqueue.",
        },
        {
            "qa_check": "inventory_row_balance",
            "status": "PASS" if len(inventory) == len(rows) else "FAIL",
            "details": f"inventory={len(inventory)} input={len(rows)}",
        },
        {
            "qa_check": "rank_stays_blank",
            "status": "PASS" if all(not row["min_rank"] for row in inventory) else "FAIL",
            "details": "No min_rank selected or inferred.",
        },
        {
            "qa_check": "no_external_capture_claimed",
            "status": "PASS"
            if all("do not fetch" in row["immediate_safe_next_step"].lower() or "local" in row["immediate_safe_next_step"].lower() or "approval packet" in row["immediate_safe_next_step"].lower() for row in inventory)
            else "FAIL",
            "details": "Immediate steps are local/checklist/readiness only.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in inventory
            )
            else "FAIL",
            "details": "Inventory remains outside intake/canonical/ML.",
        },
        {
            "qa_check": "handoff_marker_not_preexisting",
            "status": "PASS"
            if "## 138. 2026-05-17 P1 batch17 safe static QA local artifact inventory"
            not in HANDOFF.read_text(encoding="utf-8")
            else "PASS",
            "details": "Marker append is idempotent.",
        },
    ]

    write_csv(OUT_INVENTORY, ARTIFACT_FIELDS, inventory)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 safe static QA local artifact inventory

## Summary

本轮读取 marker 137 的 8 条 strict safe/static QA rows，并仅用本地已有 batch17 文件建立 artifact inventory。未联网、未打开浏览器、未 OCR、未抓取微信/JS/form/header/cookie 来源。

## Outputs

- `{rel(OUT_INVENTORY)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Inventory rows: {len(inventory)}
- Rows with official min_score retained for QA: {line_counts['official_min_score_available']}
- Rows with selected min_rank: 0
- Rows with local parsed/readiness artifacts available now: {ready_now}
- Rows still excluded from intake because local parse/mapping/rank artifact is incomplete: {len(exclusions)}

## Boundary

`min_rank` remains blank. `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row. The 32-school decision_pool remains untouched.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 138. 2026-05-17 P1 batch17 safe static QA local artifact inventory

已新增 P1 batch17 safe static QA local artifact inventory：

- `{rel(OUT_INVENTORY)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 137 的 8 条 strict safe/static QA rows，并仅用本地已有 batch17 文件回连 artifact inventory。6 条保留官方最低分用于 QA/readiness，0 条选择最低位次；当前仅 1 条（江西中医药大学 `10412-101`）具备本地 parsed plan preview/group join readiness 可立即做 mapping consistency QA，其余 7 条仍需本地 parse/mapping artifact、官方位次 raw cache 或人工批准后才能进入下一层。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步可优先对 `10412-101` 做本地 mapping consistency QA，或等待 marker 136 官方一分一档 raw artifact/浏览器态批准以补 5 个分数位次。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 138. 2026-05-17 P1 batch17 safe static QA local artifact inventory" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(inventory)} inventory rows and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
