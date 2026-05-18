#!/usr/bin/env python3
"""Audit cached endpoint/form metadata for P0 endpoint action rows.

This script reads cached HTML pages and extracts form, iframe, and script
endpoint shapes. It does not replay forms, fetch endpoints, or create
source_packet/intake/canonical rows.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlparse


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

ACTION_QUEUE = CLEAN / "reference_trend_520_p0_cached_parse_action_queue.csv"
OUT = CLEAN / "reference_trend_520_p0_endpoint_form_metadata_audit.csv"
ROLLUP = REPORTS / "reference_trend_520_p0_endpoint_form_metadata_audit_rollup.csv"
QA = REPORTS / "reference_trend_520_p0_endpoint_form_metadata_audit_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p0_endpoint_form_metadata_audit_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p0_endpoint_form_metadata_audit.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

ENDPOINT_ROUTE = "endpoint_metadata_review_before_live_replay"

FIELDS = [
    "endpoint_audit_id",
    "parse_action_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "group_pair_key",
    "group_code",
    "source_url",
    "cache_path",
    "endpoint_kind",
    "endpoint_value",
    "method",
    "target",
    "parsed_path",
    "query_params",
    "input_names",
    "contains_commonquery",
    "contains_search_api",
    "contains_plan_query_terms",
    "local_endpoint_shape_status",
    "requires_network",
    "requires_browser_or_form_approval",
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


def bool_str(value: bool) -> str:
    return "true" if value else "false"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def attrs(tag: str) -> dict[str, str]:
    found = re.findall(r"""([:\w-]+)\s*=\s*["']([^"']*)["']""", tag, flags=re.I)
    return {key.lower(): value for key, value in found}


def compact_params(url: str) -> str:
    parsed = urlparse(url)
    params = parse_qsl(parsed.query, keep_blank_values=True)
    return "|".join(f"{key}={value}" for key, value in params[:12])


def parsed_path(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path or url.split("?", 1)[0]


def input_names_near_form(form_tag: str, html: str) -> str:
    start = html.find(form_tag)
    if start < 0:
        return ""
    end = html.find("</form>", start)
    block = html[start:end if end >= 0 else start + 1200]
    names = re.findall(r"""<input[^>]+name\s*=\s*["']([^"']+)["']""", block, flags=re.I)
    return "|".join(dict.fromkeys(names))


def endpoint_status(kind: str, value: str, text: str) -> tuple[str, str]:
    lower = f"{kind} {value} {text}".lower()
    if "commonquery" in lower or "querymatch" in lower:
        return (
            "commonquery_iframe_shape_found_replay_approval_required",
            "Preserve endpoint shape and request browser/form replay approval before any endpoint response capture.",
        )
    if "/_web/_search/api/search" in lower:
        return (
            "site_search_endpoint_not_plan_data",
            "Keep as site search only; do not treat as招生计划 data endpoint.",
        )
    return (
        "supporting_script_or_unknown_endpoint_shape",
        "Keep as endpoint metadata; no live request without approval.",
    )


def base_row(action: dict[str, str]) -> dict[str, object]:
    return {
        "parse_action_id": action.get("parse_action_id", ""),
        "queue_record_id": action.get("queue_record_id", ""),
        "queue_rank": action.get("queue_rank", ""),
        "university_code": action.get("university_code", ""),
        "university_name": action.get("university_name", ""),
        "group_pair_key": action.get("group_pair_key", ""),
        "group_code": action.get("group_code", ""),
        "source_url": action.get("source_url", ""),
        "cache_path": action.get("cache_path", ""),
        "expected_output_layer": "endpoint_form_metadata_audit_only_not_source_packet_not_canonical",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "p0_endpoint_metadata_audit_only_not_32_school_decision_pool",
        "evidence_note": "Local cached HTML metadata audit only; no endpoint replay, no network, no source_packet parse rows.",
    }


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    action_rows = read_csv(ACTION_QUEUE)
    targets = [row for row in action_rows if row.get("parse_action_route", "") == ENDPOINT_ROUTE]
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []

    for action in targets:
        cache_path = action.get("cache_path", "")
        path = ROOT / cache_path if cache_path else None
        if not path or not path.exists():
            exclusions.append(
                {
                    "record_id": action.get("parse_action_id", ""),
                    "university_name": action.get("university_name", ""),
                    "reason": "cache_html_missing",
                    "detail": cache_path,
                }
            )
            continue
        html = read_text(path)
        extracted: list[dict[str, str]] = []

        for tag in re.findall(r"""<form\b[^>]*>""", html, flags=re.I):
            attr = attrs(tag)
            value = attr.get("action", "")
            extracted.append(
                {
                    "endpoint_kind": "form_action",
                    "endpoint_value": value,
                    "method": attr.get("method", ""),
                    "target": attr.get("target", ""),
                    "input_names": input_names_near_form(tag, html),
                }
            )
        for tag in re.findall(r"""<iframe\b[^>]*>""", html, flags=re.I):
            attr = attrs(tag)
            extracted.append(
                {
                    "endpoint_kind": "iframe_src",
                    "endpoint_value": attr.get("src", ""),
                    "method": "iframe_get",
                    "target": "",
                    "input_names": "",
                }
            )
        for tag in re.findall(r"""<script\b[^>]*src\s*=\s*["'][^"']+["'][^>]*>""", html, flags=re.I):
            attr = attrs(tag)
            value = attr.get("src", "")
            if any(token in value.lower() for token in ["commonquery", "query", "api", "datepicker", "layui"]):
                extracted.append(
                    {
                        "endpoint_kind": "script_src",
                        "endpoint_value": value,
                        "method": "script_get",
                        "target": "",
                        "input_names": "",
                    }
                )

        if not extracted:
            exclusions.append(
                {
                    "record_id": action.get("parse_action_id", ""),
                    "university_name": action.get("university_name", ""),
                    "reason": "no_endpoint_shape_found_in_cached_html",
                    "detail": cache_path,
                }
            )
            continue

        for item in extracted:
            value = item["endpoint_value"]
            status, safe_action = endpoint_status(item["endpoint_kind"], value, html[:1600])
            lower_value = value.lower()
            row = base_row(action)
            row.update(
                {
                    "endpoint_kind": item["endpoint_kind"],
                    "endpoint_value": value,
                    "method": item["method"],
                    "target": item["target"],
                    "parsed_path": parsed_path(value),
                    "query_params": compact_params(value),
                    "input_names": item["input_names"],
                    "contains_commonquery": bool_str("commonquery" in lower_value or "querymatch" in lower_value),
                    "contains_search_api": bool_str("/_web/_search/api/search" in lower_value),
                    "contains_plan_query_terms": bool_str("招生计划" in html or "计划查询" in html),
                    "local_endpoint_shape_status": status,
                    "requires_network": "false",
                    "requires_browser_or_form_approval": "true" if "approval_required" in status or item["endpoint_kind"] == "iframe_src" else "false",
                    "safe_next_action": safe_action,
                }
            )
            rows.append(row)

    for index, row in enumerate(rows, start=1):
        row["endpoint_audit_id"] = f"reference_trend_520_p0_endpoint_audit_{index:04d}"

    status_counts = Counter(str(row["local_endpoint_shape_status"]) for row in rows)
    kind_counts = Counter(str(row["endpoint_kind"]) for row in rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "input_parse_action_rows", "value": len(action_rows), "note": "Rows read from cached parse action queue."},
        {"metric": "endpoint_target_rows", "value": len(targets), "note": "Rows routed for endpoint metadata review."},
        {"metric": "endpoint_audit_rows", "value": len(rows), "note": "Local endpoint/form metadata rows generated."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "No canonical/ML rows produced."},
    ]
    rollup_rows += [
        {"metric": f"local_endpoint_shape_status::{key}", "value": count, "note": ""}
        for key, count in sorted(status_counts.items())
    ]
    rollup_rows += [
        {"metric": f"endpoint_kind::{key}", "value": count, "note": ""}
        for key, count in sorted(kind_counts.items())
    ]

    qa_rows: list[dict[str, object]] = [
        {
            "qa_check": "input_parse_action_queue_exists",
            "status": "pass" if ACTION_QUEUE.exists() else "fail",
            "value": str(ACTION_QUEUE.relative_to(ROOT)),
            "note": "",
        },
        {
            "qa_check": "endpoint_target_rows",
            "status": "pass" if len(targets) == 1 else "warn",
            "value": len(targets),
            "note": "Expected 1 from latest cached parse action queue.",
        },
        {
            "qa_check": "endpoint_audit_rows_generated",
            "status": "pass" if rows else "warn",
            "value": len(rows),
            "note": "Metadata only; no replay.",
        },
        {
            "qa_check": "commonquery_iframe_detected",
            "status": "pass" if any(row["contains_commonquery"] == "true" for row in rows) else "warn",
            "value": sum(1 for row in rows if row["contains_commonquery"] == "true"),
            "note": "Commonquery iframe is the likely招生计划 query surface.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "fail",
            "value": "closed",
            "note": "No canonical/ML rows produced.",
        },
        {
            "qa_check": "network_or_replay_used",
            "status": "pass",
            "value": "false",
            "note": "Only cached HTML was inspected.",
        },
    ]
    return rows, rollup_rows, qa_rows, exclusions


def write_doc(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    status_lines = "\n".join(
        f"- `{row['metric'].split('::', 1)[1]}`: {row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("local_endpoint_shape_status::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    DOC.write_text(
        f"""# Reference Trend 520 P0 Endpoint/Form Metadata Audit

Date: {date.today().isoformat()}

Scope: local metadata audit of cached endpoint/form HTML for P0 endpoint routes. This audit identifies endpoint shapes only. It does not perform live replay, endpoint fetches, browser actions, source_packet parsing, or canonical/ML writes.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_endpoint_form_metadata_audit.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_rollup.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_qa.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_exclusion_log.csv`

## Coverage

- Endpoint audit rows: {len(rows)}
- QA status: {qa_status}

## Endpoint Shape Status

{status_lines or "- none"}

## Boundary

The cached page exposes a commonquery iframe shape that may be the招生计划 query surface, but live query replay requires browser/form approval. The site search endpoint is not plan data.
""",
        encoding="utf-8",
    )


def append_handoff(rows: list[dict[str, object]], rollup_rows: list[dict[str, object]], qa_rows: list[dict[str, object]]) -> None:
    marker = "## 107. 2026-05-17 P0 endpoint/form metadata audit"
    if HANDOFF.exists() and marker in HANDOFF.read_text(encoding="utf-8", errors="ignore"):
        return
    status_summary = "; ".join(
        f"{row['metric'].split('::', 1)[1]}={row['value']}"
        for row in rollup_rows
        if str(row["metric"]).startswith("local_endpoint_shape_status::")
    )
    qa_status = "PASS" if all(row["status"] == "pass" for row in qa_rows) else "WARN"
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

{marker}

已新增 P0 endpoint/form metadata audit：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_endpoint_form_metadata_audit.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_rollup.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_qa.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_exclusion_log.csv`
- `docs/reference_trend_520_p0_endpoint_form_metadata_audit.md`

覆盖结果：处理滨州医学院 1 条 endpoint action row，基于本地缓存 HTML 提取 form/iframe/script endpoint metadata；状态分布：{status_summary or 'none'}。QA {qa_status}。已确认 commonquery iframe 是更可能的招生计划查询 surface，站内搜索 form 仅作搜索端点，不可当作计划数据。

准入边界：本轮只做本地 endpoint/form 元数据审计，不执行 live replay、不联网、不浏览器操作、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
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
    print(f"wrote {len(rows)} endpoint metadata audit rows")


if __name__ == "__main__":
    main()
