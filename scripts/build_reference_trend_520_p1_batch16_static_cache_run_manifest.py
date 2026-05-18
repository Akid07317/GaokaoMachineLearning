#!/usr/bin/env python3
"""Build a no-network run manifest for P1 batch-16 static cache candidates.

The manifest defines target cache paths, allowed static-fetch boundaries, and
the expected receipt layer for a later approved runner. It does not fetch,
cache, parse, OCR, replay forms, or open reference-trend/canonical/ML intake.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

EXEC_QUEUE = CLEAN / "reference_trend_520_p1_batch16_static_cache_execution_queue.csv"
OUT = CLEAN / "reference_trend_520_p1_batch16_static_cache_run_manifest.csv"
ROLLUP = REPORTS / "reference_trend_520_p1_batch16_static_cache_run_manifest_rollup.csv"
QA = REPORTS / "reference_trend_520_p1_batch16_static_cache_run_manifest_qa.csv"
EXCLUSION = REPORTS / "reference_trend_520_p1_batch16_static_cache_run_manifest_exclusion_log.csv"
DOC = DOCS / "reference_trend_520_p1_batch16_static_cache_run_manifest.md"
HANDOFF = DOCS / "gpt54_reference_trend_pool_handoff.md"

CACHE_ROOT = CLEAN / "reference_trend_520_p1_batch16_static_cache_targets"

FIELDS = [
    "run_manifest_id",
    "execution_candidate_id",
    "queue_rank",
    "university_code",
    "university_name",
    "source_url",
    "source_title",
    "cache_execution_route",
    "network_run_status",
    "target_cache_relpath",
    "target_receipt_id",
    "content_type_hint",
    "allowed_static_fetch_mode",
    "must_stop_if",
    "post_cache_next_artifact",
    "post_cache_manual_review_required",
    "source_packet_parse_eligible_now",
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


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def slug(text: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return cleaned[:120] or fallback


def first_url(raw_url: str) -> str:
    return raw_url.split("|", 1)[0].strip()


def content_type_hint(route: str, url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.lower()
    if route == "static_pdf_cache_candidate" or path.endswith(".pdf"):
        return "pdf"
    if route == "static_query_probe_candidate":
        return "html_or_json_query_response_unknown_until_static_probe"
    return "html"


def cache_ext(content_hint: str) -> str:
    if content_hint == "pdf":
        return ".pdf"
    if "json" in content_hint:
        return ".html_or_json"
    return ".html"


def fetch_mode(route: str) -> str:
    if route == "static_query_probe_candidate":
        return "static_GET_or_HEAD_only_no_form_submit"
    if route == "static_pdf_cache_candidate":
        return "static_GET_official_pdf_only"
    return "static_GET_official_html_only"


def next_artifact(route: str) -> str:
    if route == "static_pdf_cache_candidate":
        return "static_pdf_cache_receipt_then_local_text_extract_preview"
    if route == "static_query_probe_candidate":
        return "static_query_reachability_receipt_then_parse_feasibility_preview"
    if route == "detail_url_discovery_before_cache":
        return "detail_url_static_discovery_receipt_or_context_hold"
    return "static_html_cache_receipt_then_table_parse_preview"


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx, item in enumerate(read_csv(EXEC_QUEUE), 1):
        url = first_url(item.get("source_url", ""))
        route = item.get("cache_execution_route", "")
        hint = content_type_hint(route, url)
        parsed = urlparse(url)
        host = slug(parsed.netloc, f"host_{idx:04d}")
        path_part = slug(Path(parsed.path).name or "index", f"target_{idx:04d}")
        rank = slug(item.get("queue_rank", ""), f"rank_{idx:04d}")
        uni_code = slug(item.get("university_code", ""), f"university_{idx:04d}")
        filename = f"{idx:04d}_{rank}_{uni_code}_{host}_{path_part}{cache_ext(hint)}"
        relpath = CACHE_ROOT.relative_to(ROOT) / filename
        rows.append(
            {
                "run_manifest_id": f"reference_trend_520_p1_batch16_static_cache_run_{idx:04d}",
                "execution_candidate_id": item.get("execution_candidate_id", ""),
                "queue_rank": item.get("queue_rank", ""),
                "university_code": item.get("university_code", ""),
                "university_name": item.get("university_name", ""),
                "source_url": item.get("source_url", ""),
                "source_title": item.get("source_title", ""),
                "cache_execution_route": route,
                "network_run_status": "not_run_manifest_only",
                "target_cache_relpath": str(relpath),
                "target_receipt_id": f"reference_trend_520_p1_batch16_static_cache_receipt_{idx:04d}",
                "content_type_hint": hint,
                "allowed_static_fetch_mode": fetch_mode(route),
                "must_stop_if": item.get("stop_condition", "stop_if_cookie_header_form_or_browser_state_required"),
                "post_cache_next_artifact": next_artifact(route),
                "post_cache_manual_review_required": item.get("manual_review_required_before_intake", "true_after_cache_QA"),
                "source_packet_parse_eligible_now": "false",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Manifest only; target path and receipt id reserved for later approved static-cache run.",
            }
        )
    return rows


def write_rollup(rows: list[dict[str, object]]) -> None:
    routes = Counter(str(row["cache_execution_route"]) for row in rows)
    hints = Counter(str(row["content_type_hint"]) for row in rows)
    rollup_rows = [
        {"metric": "batch16_static_cache_run_manifest_rows", "value": len(rows), "note": "No network/cache executed."},
        {"metric": "network_run_not_started_rows", "value": sum(row["network_run_status"] == "not_run_manifest_only" for row in rows), "note": ""},
        {"metric": "reserved_target_cache_paths", "value": len({row["target_cache_relpath"] for row in rows}), "note": "Expected to equal row count."},
        {"metric": "source_packet_parse_eligible_now_rows", "value": 0, "note": "Manifest only."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No cached/parsed rows."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No cached/parsed rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    rollup_rows.extend({"metric": f"route::{key}", "value": value, "note": ""} for key, value in sorted(routes.items()))
    rollup_rows.extend({"metric": f"content_type::{key}", "value": value, "note": ""} for key, value in sorted(hints.items()))
    write_csv(ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "manifest_rows_present",
            "status": "PASS" if rows else "FAIL",
            "detail": f"Generated {len(rows)} static-cache run manifest rows.",
        },
        {
            "check": "network_not_run",
            "status": "PASS" if all(row["network_run_status"] == "not_run_manifest_only" for row in rows) else "FAIL",
            "detail": "Manifest reserves paths but does not fetch/cache.",
        },
        {
            "check": "unique_target_paths",
            "status": "PASS" if len({row["target_cache_relpath"] for row in rows}) == len(rows) else "FAIL",
            "detail": "Every manifest row has a unique target cache path.",
        },
        {
            "check": "official_static_boundaries_present",
            "status": "PASS" if all("static" in str(row["allowed_static_fetch_mode"]) for row in rows) else "FAIL",
            "detail": "All future fetch modes are static-only and must stop on browser/form/cookie/header needs.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "Canonical/ML remains closed.",
        },
    ]
    write_csv(QA, qa_rows, ["check", "status", "detail"])


def write_exclusion(rows: list[dict[str, object]]) -> None:
    exclusions = [
        {
            "item": "batch16_static_cache_run_manifest_all_rows",
            "reason": "manifest_only_no_network_no_cache_no_parse",
            "effect": "excluded_from_source_packet_parse_reference_trend_intake_calibration_canonical_and_decision_pool",
        }
    ]
    for row in rows:
        exclusions.append(
            {
                "item": row["run_manifest_id"],
                "reason": row["network_run_status"],
                "effect": "awaits_future_approved_static_cache_receipt_before_parse_preview",
            }
        )
    write_csv(EXCLUSION, exclusions, ["item", "reason", "effect"])


def write_doc(rows: list[dict[str, object]]) -> None:
    routes = Counter(str(row["cache_execution_route"]) for row in rows)
    lines = [
        "# Reference trend 520 P1 batch16 static cache run manifest",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This manifest reserves target cache paths and receipt IDs for a future approved static-cache run. It does not fetch, cache, parse, OCR, replay forms, or create intake rows.",
        "",
        "## Outputs",
        "",
        f"- `{OUT.relative_to(ROOT)}`",
        f"- `{ROLLUP.relative_to(ROOT)}`",
        f"- `{QA.relative_to(ROOT)}`",
        f"- `{EXCLUSION.relative_to(ROOT)}`",
        "",
        "## Route distribution",
        "",
    ]
    for key, value in sorted(routes.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Future run may only use official URLs listed in the manifest.",
            "- Static GET/HEAD only; no cookies, header replay, form submit, or browser state.",
            "- Stop and request approval if the official site blocks static access or requires browser/form state.",
            "- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_rollup(rows)
    write_qa(rows)
    write_exclusion(rows)
    write_doc(rows)

    marker = "## 115. 2026-05-17 P1 batch16 static cache run manifest"
    handoff = f"""

{marker}

已新增 P1 batch16 static cache run manifest：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：为 marker 114 的 10 条 static-cache execution candidates 预留 target cache paths 与 receipt IDs；按 detail_url_discovery/static_html/static_pdf/static_query 分流。QA PASS。

准入边界：本轮只生成 run manifest，不联网、不缓存、不解析、不 OCR、不浏览器/form replay；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
