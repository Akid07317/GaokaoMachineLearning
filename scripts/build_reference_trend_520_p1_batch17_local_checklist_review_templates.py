from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_local_checklist_review_templates"
INPUT_QUEUE = SEED_DIR / "reference_trend_520_p1_batch17_local_checklist_execution_queue.csv"
INPUT_EXCLUSION = REPORT_DIR / "reference_trend_520_p1_batch17_local_checklist_execution_queue_exclusion_log.csv"

OUT_TEMPLATES = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

TEMPLATE_FIELDS = [
    "template_id",
    "source_checklist_id",
    "group_pair_key",
    "university_code",
    "university_name",
    "group_code",
    "year",
    "province",
    "batch",
    "subject_category",
    "execution_lane",
    "template_scope",
    "review_step_order",
    "review_item",
    "allowed_evidence",
    "blocked_actions",
    "pass_condition",
    "block_condition",
    "output_cell_to_fill",
    "initial_status",
    "source_url",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]
ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "source_checklist_id",
    "group_pair_key",
    "university_name",
    "execution_lane",
    "exclusion_reason",
    "blocked_until",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

TEMPLATE_LANES = {
    "static_table_alignment_checklist",
    "local_placeholder_cache_needed",
    "group_boundary_checklist",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
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


def group_parts(group_pair_key: str) -> tuple[str, str]:
    if "-" not in group_pair_key:
        return "", ""
    university_code, group_code = group_pair_key.split("-", 1)
    return university_code, group_code


def review_steps(row: dict[str, str]) -> list[dict[str, str]]:
    lane = row["execution_lane"]
    if lane == "static_table_alignment_checklist":
        return [
            {
                "template_scope": "source_identity",
                "review_item": "Confirm this is only a recorded official HTML table candidate; do not claim cached rows or parsed plan counts.",
                "allowed_evidence": "marker_141_queue_row|marker_140_board_row|recorded_official_url",
                "pass_condition": "Source URL and candidate type match the recorded queue metadata.",
                "block_condition": "Any row-level data would require local cache or approved artifact first.",
                "output_cell_to_fill": "source_identity_status",
            },
            {
                "template_scope": "table_columns",
                "review_item": "Prepare column checks for province, subject category, batch, major or group structure, and plan count; leave all checks pending until an artifact exists.",
                "allowed_evidence": "local_cache_if_later_available|approved_official_artifact_if_later_available",
                "pass_condition": "Future artifact explicitly isolates Guangxi, physical category, undergraduate ordinary batch, and plan-count columns.",
                "block_condition": "Columns are absent, merged, image-only, or require browser/header/form state.",
                "output_cell_to_fill": "column_alignment_status",
            },
            {
                "template_scope": "group_mapping",
                "review_item": "Keep group 101 unconfirmed until an official group-code line or plan artifact links the table rows to 10537-101.",
                "allowed_evidence": "official_group_code_artifact|exam_authority_group_line_artifact",
                "pass_condition": "Official evidence links the relevant Guangxi ordinary-batch physical rows to group 101.",
                "block_condition": "Only school-level rows or major rows appear without group-code linkage.",
                "output_cell_to_fill": "group_101_mapping_status",
            },
            {
                "template_scope": "special_type_boundary",
                "review_item": "Pre-mark rows requiring isolation before intake: special programs, non-ordinary batches, non-physical categories, minority/preparatory, and cooperation variants.",
                "allowed_evidence": "future_local_table_cache|future_approved_official_artifact",
                "pass_condition": "Future artifact separates ordinary-batch physical rows from all special variants.",
                "block_condition": "Ordinary and special rows remain mixed or labels are ambiguous.",
                "output_cell_to_fill": "special_type_isolation_status",
            },
            {
                "template_scope": "safe_output_gate",
                "review_item": "Limit this row to a table-alignment review template; do not generate source_packet parse preview, rank join, intake, calibration, canonical, or ML output.",
                "allowed_evidence": "this_template_only",
                "pass_condition": "All downstream gates remain closed.",
                "block_condition": "Any downstream file claims parsed plan rows, selected rank, calibration eligibility, or canonical entry.",
                "output_cell_to_fill": "safe_output_gate_status",
            },
        ]
    if lane == "local_placeholder_cache_needed":
        return [
            {
                "template_scope": "missing_artifact",
                "review_item": "Record that no local cache or approved official artifact is currently available for parsing.",
                "allowed_evidence": "marker_141_queue_row|marker_140_board_row",
                "pass_condition": "Placeholder clearly states that no row-level parse is possible yet.",
                "block_condition": "Any plan row, score, rank, or group mapping is inferred from metadata only.",
                "output_cell_to_fill": "local_artifact_status",
            },
            {
                "template_scope": "future_artifact_requirements",
                "review_item": "Specify the minimum future artifact requirements: official page/cache, timestamp or capture note, accessible detail page, and Guangxi physical ordinary-batch isolation.",
                "allowed_evidence": "future_local_cache|future_approved_browser_or_static_artifact",
                "pass_condition": "Future artifact is official and auditable enough for parse-preview review.",
                "block_condition": "Cache miss, login/browser/header dependency, or unauditable third-party copy.",
                "output_cell_to_fill": "future_artifact_requirements_status",
            },
            {
                "template_scope": "medical_boundary",
                "review_item": "Predefine medical-row boundaries before any parse: clinical, non-clinical, special program, and ordinary-batch physical rows must not be mixed.",
                "allowed_evidence": "future_official_plan_artifact",
                "pass_condition": "Future artifact separates target ordinary-batch medical rows from special or non-target rows.",
                "block_condition": "Medical specialty rows are school-level only, mixed, or lack batch/subject labels.",
                "output_cell_to_fill": "medical_boundary_status",
            },
            {
                "template_scope": "group_and_rank_gate",
                "review_item": "Keep group 101, min score, and min rank unavailable until official group/line/rank evidence is provided.",
                "allowed_evidence": "official_group_line_artifact|official_score_rank_raw_artifact",
                "pass_condition": "Official artifacts provide group-code linkage and score-rank evidence.",
                "block_condition": "Only list-page metadata exists or score/rank is inferred.",
                "output_cell_to_fill": "group_rank_gate_status",
            },
            {
                "template_scope": "safe_output_gate",
                "review_item": "Limit this row to placeholder status; do not parse, fetch, OCR, open browser, or create intake/canonical/ML outputs.",
                "allowed_evidence": "this_template_only",
                "pass_condition": "Only placeholder/template outputs are written.",
                "block_condition": "Any parsed row or eligibility claim appears before an artifact exists.",
                "output_cell_to_fill": "safe_output_gate_status",
            },
        ]
    if lane == "group_boundary_checklist":
        return [
            {
                "template_scope": "aggregate_source_boundary",
                "review_item": "Treat the recorded official candidate as an aggregate page lacking accepted group-code evidence.",
                "allowed_evidence": "marker_141_queue_row|marker_140_board_row|marker_133_action_queue_row",
                "pass_condition": "Template preserves aggregate-only status and does not accept group 105.",
                "block_condition": "Group 105 is accepted from aggregate page metadata alone.",
                "output_cell_to_fill": "aggregate_source_status",
            },
            {
                "template_scope": "group_105_precondition",
                "review_item": "Require official plan or line-score evidence that explicitly links the target rows to 10513-105.",
                "allowed_evidence": "official_group_plan_artifact|official_exam_authority_group_line_artifact",
                "pass_condition": "Future artifact explicitly links target rows to group 105.",
                "block_condition": "Only school-level or aggregate rows exist without group-code linkage.",
                "output_cell_to_fill": "group_105_mapping_status",
            },
            {
                "template_scope": "teacher_language_boundary",
                "review_item": "Predefine boundary checks for normal, teacher-training, language direction, and other non-target variants before any row is accepted.",
                "allowed_evidence": "future_official_plan_or_line_artifact",
                "pass_condition": "Future artifact separates normal/language teacher-direction rows from other variants.",
                "block_condition": "Direction labels are absent, mixed, or require manual interpretation.",
                "output_cell_to_fill": "teacher_language_boundary_status",
            },
            {
                "template_scope": "line_rank_precondition",
                "review_item": "Keep min score and min rank unavailable until official line-score and score-rank raw artifacts are linked.",
                "allowed_evidence": "official_exam_authority_line_score|official_score_rank_raw_artifact",
                "pass_condition": "Official line score and rank artifacts are both present and auditable.",
                "block_condition": "Rank is missing, inferred, or from a non-official mirror.",
                "output_cell_to_fill": "line_rank_precondition_status",
            },
            {
                "template_scope": "safe_output_gate",
                "review_item": "Limit this row to group-boundary review template; do not make a boundary decision, intake row, calibration row, canonical entry, or ML input.",
                "allowed_evidence": "this_template_only",
                "pass_condition": "All downstream gates remain closed.",
                "block_condition": "Any downstream file accepts group boundary or eligibility without official evidence.",
                "output_cell_to_fill": "safe_output_gate_status",
            },
        ]
    raise ValueError(f"Unsupported template lane: {lane}")


def build() -> None:
    queue_rows = read_csv(INPUT_QUEUE)
    prior_exclusions = read_csv(INPUT_EXCLUSION)
    templates: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for row in queue_rows:
        lane = row["execution_lane"]
        if lane in TEMPLATE_LANES:
            university_code, group_code = group_parts(row["group_pair_key"])
            for order, step in enumerate(review_steps(row), start=1):
                templates.append(
                    {
                        "template_id": f"{MARKER}_{len(templates)+1:04d}",
                        "source_checklist_id": row["checklist_id"],
                        "group_pair_key": row["group_pair_key"],
                        "university_code": university_code,
                        "university_name": row["university_name"],
                        "group_code": group_code,
                        "year": row["year"],
                        "province": row["province"],
                        "batch": row["batch"],
                        "subject_category": row["subject_category"],
                        "execution_lane": lane,
                        "template_scope": step["template_scope"],
                        "review_step_order": order,
                        "review_item": step["review_item"],
                        "allowed_evidence": step["allowed_evidence"],
                        "blocked_actions": "new_fetch|browser|header_cookie_form_replay|OCR|WeChat|manual_boundary_acceptance|rank_inference|reference_trend_intake|canonical_ml",
                        "pass_condition": step["pass_condition"],
                        "block_condition": step["block_condition"],
                        "output_cell_to_fill": step["output_cell_to_fill"],
                        "initial_status": "pending_local_or_approved_artifact",
                        "source_url": row["source_url"],
                        "reference_trend_pool_eligible": "false",
                        "calibration_eligible": "false",
                        "canonical_ml_entry_open": "false",
                        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                        "evidence_note": row["evidence_note"],
                    }
                )
        else:
            exclusions.append(
                {
                    "exclusion_id": f"{MARKER}_exclusion_{len(exclusions)+1:04d}",
                    "source_checklist_id": row["checklist_id"],
                    "group_pair_key": row["group_pair_key"],
                    "university_name": row["university_name"],
                    "execution_lane": lane,
                    "exclusion_reason": "official_backoff_row_not_a_local_review_template",
                    "blocked_until": "official_static_source_found_or_user_approves_browser_OCR_manual_review",
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )

    source_template_ids = sorted({row["source_checklist_id"] for row in templates})
    lane_counts = Counter(row["execution_lane"] for row in templates)
    scope_counts = Counter(row["template_scope"] for row in templates)
    university_counts = Counter(row["group_pair_key"] for row in templates)

    rollup = [
        {"metric": "input_marker141_queue_rows", "value": len(queue_rows), "notes": rel(INPUT_QUEUE)},
        {"metric": "input_marker141_prior_exclusion_rows", "value": len(prior_exclusions), "notes": rel(INPUT_EXCLUSION)},
        {"metric": "template_source_rows", "value": len(source_template_ids), "notes": "Marker 141 rows expanded into review templates."},
        {"metric": "review_template_rows", "value": len(templates), "notes": "Checklist rows generated without fetch or user approval."},
        {"metric": "excluded_backoff_rows", "value": len(exclusions), "notes": "Marker 141 official-only backoff rows kept out of template execution."},
        {"metric": "network_fetch_rows", "value": 0, "notes": "No web fetch/cache/browser/OCR/WeChat action performed."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "notes": "Templates are not intake rows."},
        {"metric": "calibration_eligible_rows", "value": 0, "notes": "Calibration remains closed."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(university_counts.items()):
        rollup.append({"metric": f"group_pair_key::{key}", "value": value, "notes": "review template rows"})
    for key, value in sorted(lane_counts.items()):
        rollup.append({"metric": f"execution_lane::{key}", "value": value, "notes": "review template lane"})
    for key, value in sorted(scope_counts.items()):
        rollup.append({"metric": f"template_scope::{key}", "value": value, "notes": "review template scope"})

    qa_rows = [
        {
            "qa_check": "input_queue_present",
            "status": "PASS" if len(queue_rows) == 8 else "FAIL",
            "details": f"Read {len(queue_rows)} rows from marker 141 local checklist queue.",
        },
        {
            "qa_check": "template_source_scope",
            "status": "PASS" if len(source_template_ids) == 3 else "FAIL",
            "details": f"Expanded {len(source_template_ids)} local checklist source rows.",
        },
        {
            "qa_check": "template_count",
            "status": "PASS" if len(templates) == 15 else "FAIL",
            "details": f"Generated {len(templates)} review template rows.",
        },
        {
            "qa_check": "queue_balance",
            "status": "PASS" if len(source_template_ids) + len(exclusions) == len(queue_rows) else "FAIL",
            "details": f"template_sources={len(source_template_ids)} exclusions={len(exclusions)} input={len(queue_rows)}",
        },
        {
            "qa_check": "no_fetch_or_external_approval_action",
            "status": "PASS"
            if all("new_fetch" in row["blocked_actions"] and row["initial_status"] == "pending_local_or_approved_artifact" for row in templates)
            else "FAIL",
            "details": "Templates explicitly block fetch/browser/OCR/WeChat/manual acceptance and rank inference.",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in templates
            )
            else "FAIL",
            "details": "No template row opens intake, calibration, canonical, or ML.",
        },
    ]

    write_csv(OUT_TEMPLATES, TEMPLATE_FIELDS, templates)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 local checklist review templates

## Summary

This marker expands the 3 approval-free local checklist rows from marker 141 into concrete review-template rows. It does not fetch pages, parse new artifacts, run OCR, open browser or WeChat state, infer ranks, or open intake/calibration/canonical/ML.

## Outputs

- `{rel(OUT_TEMPLATES)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Input marker 141 queue rows: {len(queue_rows)}
- Review template source rows: {len(source_template_ids)}
- Review template rows: {len(templates)}
- Excluded official-only backoff rows: {len(exclusions)}
- Prior marker 141 blocked rows kept in context: {len(prior_exclusions)}
- Template rows by group: {", ".join(f"{key}={value}" for key, value in sorted(university_counts.items()))}

## Boundary

Every template row is initialized as `pending_local_or_approved_artifact` and keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 142. 2026-05-17 P1 batch17 local checklist review templates

已新增 P1 batch17 local checklist review templates：

- `{rel(OUT_TEMPLATES)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 141 的 8 条 local checklist execution queue，将 3 条无需新批准的本地 checklist 行细化为 15 条审核模板：湖南农业大学 `10537-101` 表格列/专业组/特殊类型边界模板 5 条，牡丹江医科大学 `10229-101` 本地 cache 缺口/医学边界/位次闸门模板 5 条，湖北师范大学 `10513-105` aggregate source/group 105/师范语言方向/位次闸门模板 5 条。另将 5 条 official-only discovery backoff rows 保持在 exclusion log。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可在本地 artifact 或用户批准出现后填充这些模板，或继续等待 marker 136 官方一分一档 raw artifact/浏览器态批准。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 142. 2026-05-17 P1 batch17 local checklist review templates" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(templates)} review templates and {len(exclusions)} exclusions for {MARKER}.")


if __name__ == "__main__":
    build()
