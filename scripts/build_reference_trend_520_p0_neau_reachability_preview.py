#!/usr/bin/env python3
"""Build NEAU official reachability preview without header/browser replay.

The Northeast Agricultural University admissions pages are reachable through an
official school landing page and a dedicated undergraduate admissions homepage.
The homepage uses public AJAX endpoints for navigation/news content, but a
direct POST to the category endpoint returned 403 during this run. Per project
rules, this script records reachability evidence and keeps the item out of
reference_trend/canonical/ML until an auditable browser/header check is approved.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "p0_official_drilldown"

RAW_LANDING = RAW_DIR / "neau_zsbweb_index_https.html"
RAW_HOME = RAW_DIR / "neau_zsb_home.html"
OUT = SEED_DIR / "reference_trend_520_p0_neau_reachability_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_neau_reachability_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_neau_reachability_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_neau_reachability_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_neau_reachability_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zsb.neau.edu.cn/"
LANDING_URL = "https://zsbweb.neau.edu.cn/index.htm"
AJAX_ENDPOINT = "https://zsb.neau.edu.cn/f/newsCenter/ajax_get_category_and_link_list"
SOURCE_ID = "reference_trend_520_web_candidate_0002"

FIELDS = [
    "record_id",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "group_code",
    "rank_2024",
    "rank_2025",
    "rank_delta_2025_minus_2024",
    "trend_direction",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_paths",
    "official_chain_status",
    "homepage_ajax_endpoint_candidate",
    "homepage_ajax_simple_post_status",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_packet_status",
    "collector_confidence",
    "requires_manual_approval",
    "approval_required_for",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
    "evidence_note",
]

QUEUE_ROWS = [
    {
        "record_id": "reference_trend_520_p0_neau_reachability_group_102",
        "queue_record_id": "reference_trend_520_plan_source_queue_0002",
        "queue_rank": "2",
        "group_code": "102",
        "rank_2024": "31790",
        "rank_2025": "42974",
        "rank_delta_2025_minus_2024": "11184",
    },
    {
        "record_id": "reference_trend_520_p0_neau_reachability_group_103",
        "queue_record_id": "reference_trend_520_plan_source_queue_0045",
        "queue_rank": "45",
        "group_code": "103",
        "rank_2024": "30649",
        "rank_2025": "48973",
        "rank_delta_2025_minus_2024": "18324",
    },
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def build_rows() -> list[dict[str, object]]:
    raw_paths = "|".join(rel(path) for path in [RAW_LANDING, RAW_HOME] if path.exists())
    rows: list[dict[str, object]] = []
    for item in QUEUE_ROWS:
        rows.append(
            {
                **item,
                "source_id": SOURCE_ID,
                "university_code": "10224",
                "university_name": "东北农业大学",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "trend_direction": "cooler_or_lower_selectivity",
                "source_url": SOURCE_URL,
                "source_owner": "东北农业大学本科招生网",
                "source_title": "东北农业大学本科招生官网首页",
                "raw_file_paths": raw_paths,
                "official_chain_status": "official_school_landing_to_undergraduate_admissions_home_cached",
                "homepage_ajax_endpoint_candidate": AJAX_ENDPOINT,
                "homepage_ajax_simple_post_status": "403_for_direct_terminal_post",
                "source_contains_group_code": "unknown_until_approved_ajax_or_browser_state_check",
                "source_contains_plan_count": "unknown_until_approved_ajax_or_browser_state_check",
                "source_contains_min_score": "false_not_a_score_source",
                "source_contains_min_rank": "false_not_a_score_source",
                "source_packet_status": "official_portal_cached_ajax_blocked_hold_for_manual_approval",
                "collector_confidence": "T2_official_portal_cached_public_ajax_403_not_structured",
                "requires_manual_approval": "true",
                "approval_required_for": "header_cookie_or_browser_state_check_for_public_ajax_endpoint",
                "eligible_for_intake_preview": "false_until_structured_plan_rows_cached_and_QA",
                "reference_trend_pool_eligible": "0",
                "calibration_eligible": "0",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "next_action": "ask_user_approval_for_audited_header_or_browser_state_check; otherwise keep as reachability evidence only",
                "evidence_note": "Official landing page redirects the source chain to the undergraduate admissions homepage; homepage exposes CMS AJAX shape, but direct terminal POST to category/link endpoint returned 403, so no structured Guangxi plan rows were fetched.",
            }
        )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    approvals = Counter(str(row["requires_manual_approval"]) for row in rows)
    return [
        {"metric": "official_landing_cached", "value": 1 if RAW_LANDING.exists() else 0, "note": rel(RAW_LANDING)},
        {"metric": "official_undergraduate_home_cached", "value": 1 if RAW_HOME.exists() else 0, "note": rel(RAW_HOME)},
        {"metric": "queue_records_covered", "value": len(rows), "note": "groups 102 and 103"},
        {"metric": "ajax_endpoint_candidates_identified", "value": 1, "note": AJAX_ENDPOINT},
        {"metric": "direct_ajax_terminal_post_status", "value": 403, "note": "no header/cookie/browser replay attempted"},
        {"metric": "manual_approval_required_rows", "value": approvals.get("true", 0), "note": "header/browser state check required before structured rows"},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No structured plan rows fetched."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan source only; no score/rank rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    return [
        {
            "check": "official_landing_cached",
            "status": "PASS" if RAW_LANDING.exists() else "FAIL",
            "detail": rel(RAW_LANDING),
        },
        {
            "check": "official_undergraduate_home_cached",
            "status": "PASS" if RAW_HOME.exists() else "FAIL",
            "detail": rel(RAW_HOME),
        },
        {
            "check": "official_chain_recorded",
            "status": "PASS" if all(row["source_url"] == SOURCE_URL for row in rows) else "FAIL",
            "detail": f"{LANDING_URL} -> {SOURCE_URL}",
        },
        {
            "check": "ajax_block_not_bypassed",
            "status": "PASS",
            "detail": "Direct terminal POST returned 403; no header/cookie/browser replay attempted.",
        },
        {
            "check": "manual_approval_gate",
            "status": "PASS" if all(row["requires_manual_approval"] == "true" for row in rows) else "FAIL",
            "detail": "Rows require approval before AJAX/header/browser check.",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS"
            if all(row["reference_trend_pool_eligible"] == "0" and row["canonical_ml_entry_open"] == "false" for row in rows)
            else "FAIL",
            "detail": "No trend pool/canonical/ML writes.",
        },
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "exclusion_reason": "official_home_cached_but_structured_plan_rows_not_fetched",
            "blocked_by": "direct_ajax_terminal_post_403_requires_manual_header_or_browser_approval",
            "excluded_from": "reference_trend_pool|canonical|ML|decision_pool",
            "evidence": row["evidence_note"],
        }
        for row in rows
    ]


def build_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, str]]) -> str:
    qa_lines = "\n".join(f"- {item['check']}: {item['status']} - {item['detail']}" for item in qa)
    rollup_lines = "\n".join(f"- {row['metric']}: {row['value']} ({row['note']})" for row in rollup)
    groups = ", ".join(f"{row['group_code']}[{row['queue_record_id']}]" for row in rows)
    return f"""# reference_trend_520 P0 NEAU official reachability preview

Generated: {date.today().isoformat()}

## Scope

本轮处理东北农业大学 P0 官方计划来源发现任务。只缓存并审计官方入口链路，不执行 header/cookie/browser 态检查，不绕过 403，不生成 canonical/ML 输入。

## Result

- Official landing URL: {LANDING_URL}
- Undergraduate admissions URL: {SOURCE_URL}
- Cached landing HTML: `{rel(RAW_LANDING)}`
- Cached admissions homepage: `{rel(RAW_HOME)}`
- Queue records covered: {groups}
- Homepage AJAX candidate: `{AJAX_ENDPOINT}`
- Direct terminal POST status: `403`
- Structured Guangxi plan rows: not fetched
- Manual approval required: yes, for audited header/cookie/browser-state check

## Outputs

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是当前只有官方入口链路和 CMS/AJAX 形状，尚无经批准缓存的 2025 广西物理类本科普通批计划结构化行。

## QA

{qa_lines}

## Rollup

{rollup_lines}
"""


def main() -> None:
    rows = build_rows()
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    exclusions = build_exclusions(rows)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, ["record_id", "university_name", "group_code", "exclusion_reason", "blocked_by", "excluded_from", "evidence"])
    DOC_OUT.write_text(build_doc(rows, rollup, qa), encoding="utf-8")

    marker = "## 79. 2026-05-16 P0 东北农业大学 official reachability preview"
    append_handoff_once(
        marker,
        f"""

{marker}

- Cached official chain: `{rel(RAW_LANDING)}` -> `{rel(RAW_HOME)}`.
- Output preview: `{rel(OUT)}`.
- QA: `{rel(QA_OUT)}`; rollup: `{rel(ROLLUP_OUT)}`; exclusion log: `{rel(EXCLUSION_OUT)}`.
- Result: official undergraduate admissions homepage located, but direct terminal POST to `{AJAX_ENDPOINT}` returned 403. Kept both NEAU group queue rows as reachability evidence only.
- Boundary: no structured plan rows, no reference_trend_pool eligibility, no canonical/ML, no decision_pool merge. Further progress requires manual approval for audited header/cookie/browser-state check.
""",
    )


if __name__ == "__main__":
    main()
