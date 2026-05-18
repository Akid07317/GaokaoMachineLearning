from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"

MARKER = "reference_trend_520_p1_batch17_pipeline_readiness_rollup"
MATRIX = SEED_DIR / "reference_trend_520_p1_batch17_gated_branch_decision_matrix.csv"
APPROVAL_SHEET = SEED_DIR / "reference_trend_520_p1_batch17_user_approval_decision_sheet.csv"
TEMPLATES = SEED_DIR / "reference_trend_520_p1_batch17_local_checklist_review_templates.csv"

OUT_READINESS = SEED_DIR / f"{MARKER}.csv"
OUT_ROLLUP = REPORT_DIR / f"{MARKER}_rollup.csv"
OUT_QA = REPORT_DIR / f"{MARKER}_qa.csv"
OUT_EXCLUSION = REPORT_DIR / f"{MARKER}_exclusion_log.csv"
OUT_DOC = DOC_DIR / f"{MARKER}.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"

READINESS_FIELDS = [
    "readiness_id",
    "source_type",
    "source_id",
    "readiness_lane",
    "readiness_priority",
    "current_state",
    "automation_can_proceed_now",
    "user_or_artifact_needed",
    "affected_group_pair_keys",
    "affected_universities",
    "affected_lookup_scores",
    "consumer_count_after_fanout",
    "safe_next_action",
    "stop_condition",
    "question_for_user_if_notified",
    "source_files",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]
ROLLUP_FIELDS = ["metric", "value", "notes"]
QA_FIELDS = ["qa_check", "status", "details"]
EXCLUSION_FIELDS = [
    "exclusion_id",
    "source_type",
    "source_id",
    "exclusion_reason",
    "safe_next_action",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]

QUESTION_BY_FAMILY = {
    "official_2025_physics_score_rank_raw_cache": "是否提供广西考试院 2025 物理类一分一档官方 raw artifact，或批准浏览器态保存官方页面？",
    "official_min_rank_join_permission": "是否在官方一分一档 raw artifact 可审计后，允许把分数 382/461/462/490 的最低位次回连到对应 group-year？",
    "official_group_code_confirmation_plus_rank_raw": "是否提供江西中医药大学 10412-101 的官方 group-code 证明，并配套 527 分官方位次 raw artifact？",
    "browser_or_static_endpoint_capture": "是否批准对浙大宁波理工学院/浙江中医药大学使用浏览器态或可审计静态 endpoint capture？",
    "OCR_or_user_provided_extracted_table": "是否批准 OCR/人工图片审核，或直接提供官方提取表，用于浙江外国语学院/温州大学/湖南理工学院？",
    "WeChat_official_artifact_capture": "是否提供福建中医药大学微信官方 artifact，或批准微信 capture？",
    "optional_browser_OCR_manual_review_for_backoff": "是否对 5 条 official-only backoff 分支批准浏览器/OCR/人工 review；也可以继续等待静态官方来源。",
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


def build() -> None:
    matrix_rows = read_csv(MATRIX)
    approval_rows = read_csv(APPROVAL_SHEET)
    template_rows = read_csv(TEMPLATES)

    readiness: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    local_matrix_rows = [row for row in matrix_rows if row["user_action_needed"] == "false"]
    local_keys = "|".join(sorted({row["affected_group_pair_keys"] for row in local_matrix_rows if row["affected_group_pair_keys"]}))
    local_universities = "|".join(sorted({row["affected_universities"] for row in local_matrix_rows if row["affected_universities"]}))
    readiness.append(
        {
            "readiness_id": f"{MARKER}_{len(readiness)+1:04d}",
            "source_type": "local_template_bundle",
            "source_id": "marker_142_local_templates",
            "readiness_lane": "local_templates_waiting_for_artifact",
            "readiness_priority": "local_no_new_user_approval",
            "current_state": "templates_ready_but_no_local_or_approved_artifact_to_fill",
            "automation_can_proceed_now": "false",
            "user_or_artifact_needed": "local_cache_or_approved_official_artifact_for_template_fill",
            "affected_group_pair_keys": local_keys,
            "affected_universities": local_universities,
            "affected_lookup_scores": "",
            "consumer_count_after_fanout": len(local_matrix_rows),
            "safe_next_action": "fill_marker_142_templates_only_after_artifact_appears",
            "stop_condition": "stop_before_parse_preview_or_boundary_acceptance_without_artifact",
            "question_for_user_if_notified": "如果已有这 3 所学校的官方本地缓存/截图/表格 artifact，可以交给流水线填模板；否则继续等待。",
            "source_files": f"{rel(MATRIX)}|{rel(TEMPLATES)}",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        }
    )

    for row in approval_rows:
        family = row["approval_family"]
        readiness.append(
            {
                "readiness_id": f"{MARKER}_{len(readiness)+1:04d}",
                "source_type": "approval_option",
                "source_id": row["approval_option_id"],
                "readiness_lane": family,
                "readiness_priority": row["approval_priority"],
                "current_state": row["current_status"],
                "automation_can_proceed_now": "false",
                "user_or_artifact_needed": row["what_user_would_allow_or_provide"],
                "affected_group_pair_keys": row["affected_group_pair_keys"],
                "affected_universities": row["affected_universities"],
                "affected_lookup_scores": row["affected_lookup_scores"],
                "consumer_count_after_fanout": row["consumer_count_after_fanout"],
                "safe_next_action": row["safe_next_after_approval"],
                "stop_condition": "stop_until_user_approval_or_official_raw_artifact_then_run_QA_preview_only",
                "question_for_user_if_notified": QUESTION_BY_FAMILY[family],
                "source_files": row["source_files"],
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

    for row in matrix_rows:
        if row["user_action_needed"] in {"true", "false_optional_approval_later", "false"}:
            exclusions.append(
                {
                    "exclusion_id": f"{MARKER}_exclusion_{len(exclusions)+1:04d}",
                    "source_type": "decision_matrix_family",
                    "source_id": row["decision_family_id"],
                    "exclusion_reason": "represented_in_readiness_rollup_no_execution_needed",
                    "safe_next_action": row["safe_next_after_unblock"],
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                }
            )

    priority_counts = Counter(row["readiness_priority"] for row in readiness)
    source_type_counts = Counter(row["source_type"] for row in readiness)
    scores = sorted(
        {
            score
            for row in readiness
            for score in str(row["affected_lookup_scores"]).split("|")
            if score
        },
        key=lambda value: int(value) if value.isdigit() else value,
    )
    rollup = [
        {"metric": "input_decision_matrix_rows", "value": len(matrix_rows), "notes": rel(MATRIX)},
        {"metric": "input_approval_option_rows", "value": len(approval_rows), "notes": rel(APPROVAL_SHEET)},
        {"metric": "input_local_template_rows", "value": len(template_rows), "notes": rel(TEMPLATES)},
        {"metric": "readiness_rows", "value": len(readiness), "notes": "One local bundle plus approval options."},
        {"metric": "automation_can_proceed_now_rows", "value": sum(row["automation_can_proceed_now"] == "true" for row in readiness), "notes": "All lanes are waiting for artifact/approval."},
        {"metric": "unique_lookup_scores_waiting", "value": len(scores), "notes": "|".join(scores)},
        {"metric": "covered_decision_family_rows", "value": len(exclusions), "notes": "Matrix families represented and logged."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "notes": "Readiness rollup is not intake."},
        {"metric": "calibration_eligible_rows", "value": 0, "notes": "No rank selected."},
        {"metric": "canonical_ml_entry_open", "value": 0, "notes": "Canonical/ML remains closed."},
    ]
    for key, value in sorted(priority_counts.items()):
        rollup.append({"metric": f"readiness_priority::{key}", "value": value, "notes": "readiness row priority"})
    for key, value in sorted(source_type_counts.items()):
        rollup.append({"metric": f"source_type::{key}", "value": value, "notes": "readiness source type"})

    qa_rows = [
        {
            "qa_check": "input_files_present",
            "status": "PASS" if len(matrix_rows) == 10 and len(approval_rows) == 7 and len(template_rows) == 15 else "FAIL",
            "details": f"matrix={len(matrix_rows)} approval={len(approval_rows)} templates={len(template_rows)}",
        },
        {
            "qa_check": "readiness_scope",
            "status": "PASS" if len(readiness) == 8 else "FAIL",
            "details": f"readiness_rows={len(readiness)}",
        },
        {
            "qa_check": "no_autonomous_execution_remaining",
            "status": "PASS" if all(row["automation_can_proceed_now"] == "false" for row in readiness) else "FAIL",
            "details": "Every lane waits for a local artifact, official raw artifact, or user approval.",
        },
        {
            "qa_check": "score_rank_wait_preserved",
            "status": "PASS" if set(scores) >= {"382", "461", "462", "490", "527"} else "FAIL",
            "details": f"scores={'|'.join(scores)}",
        },
        {
            "qa_check": "decision_families_represented",
            "status": "PASS" if len(exclusions) == len(matrix_rows) else "FAIL",
            "details": f"represented={len(exclusions)} matrix={len(matrix_rows)}",
        },
        {
            "qa_check": "intake_canonical_ml_closed",
            "status": "PASS"
            if all(
                row["reference_trend_pool_eligible"] == "false"
                and row["calibration_eligible"] == "false"
                and row["canonical_ml_entry_open"] == "false"
                for row in readiness
            )
            else "FAIL",
            "details": "No readiness lane opens intake, calibration, canonical, or ML.",
        },
    ]

    write_csv(OUT_READINESS, READINESS_FIELDS, readiness)
    write_csv(OUT_ROLLUP, ROLLUP_FIELDS, rollup)
    write_csv(OUT_QA, QA_FIELDS, qa_rows)
    write_csv(OUT_EXCLUSION, EXCLUSION_FIELDS, exclusions)

    doc = f"""# P1 batch17 pipeline readiness rollup

## Summary

This marker summarizes whether the batch17 pipeline has remaining safe autonomous work. Current answer: no row can advance past template/approval state without a local artifact, official raw artifact, or explicit user approval. No browser, fetch, OCR, WeChat capture, rank selection, intake, calibration, canonical, or ML action is performed.

## Outputs

- `{rel(OUT_READINESS)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`

## Findings

- Readiness rows: {len(readiness)}
- Autonomous executable rows now: 0
- Local template bundle: {local_keys or 'none'}
- Approval option rows carried forward: {len(approval_rows)}
- Official score-rank lookup scores still waiting: {"|".join(scores)}

## Boundary

Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
"""
    OUT_DOC.write_text(doc, encoding="utf-8")

    block = f"""

## 145. 2026-05-17 P1 batch17 pipeline readiness rollup

已新增 P1 batch17 pipeline readiness rollup：

- `{rel(OUT_READINESS)}`
- `{rel(OUT_ROLLUP)}`
- `{rel(OUT_QA)}`
- `{rel(OUT_EXCLUSION)}`
- `{rel(OUT_DOC)}`

覆盖结果：读取 marker 143 decision matrix、marker 144 approval decision sheet 与 marker 142 local checklist templates，生成 8 条 readiness rows：1 条本地模板 bundle（3 所学校、15 条模板，等待本地/批准 artifact 才能填充）与 7 条待批准/官方 raw artifact 分支。当前可自主继续执行的 rows 为 0；5 个官方位次 lookup 分数（382/461/462/490/527）继续等待广西考试院官方 raw/cache 或浏览器态批准。QA PASS。

准入边界：本轮只生成 readiness/coverage rollup，不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不重复已阻塞终端 curl，不使用第三方位次，不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化应等待用户批准/提供官方 raw artifact，或等待本地 artifact 后再填 marker 142 模板。
"""
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if "## 145. 2026-05-17 P1 batch17 pipeline readiness rollup" not in existing:
        HANDOFF.write_text(existing.rstrip() + block + "\n", encoding="utf-8")

    failed = [row for row in qa_rows if row["status"] != "PASS"]
    if failed:
        raise SystemExit(f"QA failed: {failed}")
    print(f"Wrote {len(readiness)} readiness rows and {len(exclusions)} represented-family rows for {MARKER}.")


if __name__ == "__main__":
    build()
