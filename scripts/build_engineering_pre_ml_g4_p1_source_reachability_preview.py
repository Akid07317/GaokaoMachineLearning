#!/usr/bin/env python3
"""Build G4 P1 official-source reachability preview from cached evidence.

This script does not fetch remote pages and does not write canonical/ML inputs.
It only summarizes cached static-page inventory, JS endpoint evidence, and
existing probe logs for the current P1 G4 reachability branch.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
CONFIG_DIR = ROOT / "configs"
DOCS_DIR = ROOT / "docs"

G4_QUEUE = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_queue_merged.csv"
STATIC_SUMMARY = REPORT_DIR / "static_ajax_school_summary.csv"
STATIC_INVENTORY = REPORT_DIR / "static_ajax_page_inventory.csv"
REGISTRY = CONFIG_DIR / "cold_queue_entry_registry_seed.csv"
API_FETCH = REPORT_DIR / "engineering_api_fetch_a1_a2_newrun.csv"
JIANGNAN_TARGETS = REPORT_DIR / "jiangnan_api_probe_targets.csv"
JIANGNAN_FETCH = REPORT_DIR / "jiangnan_api_probe_fetch.csv"
JIANGNAN_PLAN_JS = ROOT / "raw_data" / "official_followup" / "jiangnan_211" / "chunk_plan.js"
JIANGNAN_SCORE_JS = ROOT / "raw_data" / "official_followup" / "jiangnan_211" / "chunk_score.js"

PREVIEW_OUT = SEED_DIR / "guangxi_pre_ml_g4_p1_source_reachability_preview_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_g4_p1_source_reachability_preview_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_g4_p1_source_reachability_preview.md"

P1_LANES = {"P1_static_family_ready", "P1_js_endpoint_exposed"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def rows_by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key, "")}


def group_rows(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row.get(key, ""), []).append(row)
    return grouped


def compact_unique(values: list[str], limit: int | None = None) -> str:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    if limit is not None and len(ordered) > limit:
        return "|".join(ordered[:limit] + [f"...(+{len(ordered) - limit})"])
    return "|".join(ordered)


def count_statuses(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("status", "") or "missing_status" for row in rows)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts))


def count_errors(rows: list[dict[str, str]]) -> str:
    errors: list[str] = []
    for row in rows:
        message = (row.get("error_message", "") or "").strip()
        if not message:
            continue
        errors.append(message)
    return compact_unique(errors, limit=3)


def js_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def endpoints_from_js(text: str) -> str:
    endpoints = re.findall(r'"(/front/[^"]+)"', text)
    return compact_unique(endpoints)


def props_from_js(text: str) -> str:
    props = re.findall(r'prop:"([^"]+)"', text)
    return compact_unique(props)


def fetch_rows_for_school(rows: list[dict[str, str]], school_key: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("source_id") == school_key]


def api_fetch_summary(rows: list[dict[str, str]], registry_note: str) -> dict[str, object]:
    if not rows:
        return {
            "probe_rows": 0,
            "probe_status_counts": "no_recent_probe_rows",
            "probe_error_summary": registry_note,
            "probe_target_kinds": "",
            "probe_request_bodies": "",
        }
    return {
        "probe_rows": len(rows),
        "probe_status_counts": count_statuses(rows),
        "probe_error_summary": count_errors(rows),
        "probe_target_kinds": compact_unique([row.get("target_kind", "") for row in rows]),
        "probe_request_bodies": compact_unique([row.get("request_body", "") for row in rows], limit=4),
    }


def main() -> None:
    _, queue = read_csv(G4_QUEUE)
    _, static_summary_rows = read_csv(STATIC_SUMMARY)
    _, static_inventory_rows = read_csv(STATIC_INVENTORY)
    _, registry_rows = read_csv(REGISTRY)
    _, api_fetch_rows = read_csv(API_FETCH)
    _, jiangnan_targets = read_csv(JIANGNAN_TARGETS)
    _, jiangnan_fetch = read_csv(JIANGNAN_FETCH)

    static_summary = rows_by_key(static_summary_rows, "school_key")
    static_inventory = group_rows(static_inventory_rows, "school_key")
    registry = rows_by_key(registry_rows, "school_key")

    plan_js = js_text(JIANGNAN_PLAN_JS)
    score_js = js_text(JIANGNAN_SCORE_JS)
    jiangnan_js_endpoints = compact_unique(
        [
            *endpoints_from_js(plan_js).split("|"),
            *endpoints_from_js(score_js).split("|"),
        ]
    )
    jiangnan_js_props = compact_unique(
        [
            *props_from_js(plan_js).split("|"),
            *props_from_js(score_js).split("|"),
        ]
    )

    preview_rows: list[dict[str, object]] = []
    p1_queue = [row for row in queue if row.get("operating_lane") in P1_LANES]
    for row in p1_queue:
        school_key = row.get("school_key", "")
        lane = row.get("operating_lane", "")
        registry_row = registry.get(school_key, {})
        static_row = static_summary.get(school_key, {})
        inventory_rows = static_inventory.get(school_key, [])

        if lane == "P1_static_family_ready":
            fetch_rows = fetch_rows_for_school(api_fetch_rows, school_key)
            fetch_summary = api_fetch_summary(fetch_rows, registry_row.get("notes", ""))
            preview_status = "static_family_structure_confirmed_but_remote_fetch_blocked"
            evidence_layer = "cached_static_ajax_page_inventory"
            candidate_route = "static_ajax_family_parser_or_header_replay_route"
            next_action = (
                "保留为 G4 P1 来源可达性预览；若要继续抽取，先基于缓存页生成本地解析器，"
                "联网 header/cookie replay 需单独批准。"
            )
            js_endpoint_count = 0
            js_endpoints = ""
            js_props = ""
            target_urls = ""
            target_request_bodies = ""
        else:
            fetch_summary = api_fetch_summary(jiangnan_fetch, registry_row.get("notes", ""))
            preview_status = "js_endpoint_shape_confirmed_but_remote_probe_blocked"
            evidence_layer = "cached_frontend_js_and_probe_plan"
            candidate_route = "api_param_route_known_header_or_tls_blocked"
            next_action = (
                "保留为 G4 P1 来源可达性预览；下一步只审 header/TLS/浏览器态路线，"
                "不得直接写入 canonical/ML。"
            )
            js_endpoint_count = len([endpoint for endpoint in jiangnan_js_endpoints.split("|") if endpoint])
            js_endpoints = jiangnan_js_endpoints
            js_props = jiangnan_js_props
            target_urls = compact_unique([target.get("url", "") for target in jiangnan_targets])
            target_request_bodies = compact_unique(
                [target.get("request_body", "") for target in jiangnan_targets], limit=5
            )

        preview_rows.append(
            {
                "queue_rank": row.get("queue_rank", ""),
                "school_key": school_key,
                "school_name": row.get("school_name", ""),
                "engineering_tier": row.get("engineering_tier", ""),
                "operating_lane": lane,
                "p1_preview_status": preview_status,
                "evidence_layer": evidence_layer,
                "candidate_extraction_route": candidate_route,
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "cached_plan_page": registry_row.get("cached_plan_evidence_path", ""),
                "cached_score_page": registry_row.get("cached_score_evidence_path", ""),
                "cached_aux_page": registry_row.get("cached_support_evidence_path", ""),
                "registry_notes": registry_row.get("notes", ""),
                "cached_page_count": static_row.get("page_count", "0") or "0",
                "plan_page_count": static_row.get("plan_page_count", "0") or "0",
                "score_page_count": static_row.get("score_page_count", "0") or "0",
                "source_buckets": static_row.get("source_buckets", ""),
                "cached_param_endpoints": static_row.get("param_endpoints", ""),
                "cached_data_endpoints": static_row.get("data_endpoints", ""),
                "cached_config_signature": static_row.get("config_name_signature", ""),
                "cached_response_keys": static_row.get("response_keys", ""),
                "cached_template_fields": static_row.get("template_fields", ""),
                "cached_inventory_files": compact_unique(
                    [item.get("file_path", "") for item in inventory_rows], limit=4
                ),
                "has_guangxi_literal": static_row.get("has_guangxi_literal_any", ""),
                "has_physics_literal": static_row.get("has_physics_literal_any", ""),
                "has_sex_toggle": static_row.get("has_with_sex_toggle_any", ""),
                "has_campus_toggle": static_row.get("has_with_campus_toggle_any", ""),
                "js_endpoint_count": js_endpoint_count,
                "js_endpoints": js_endpoints,
                "js_table_props": js_props,
                "planned_probe_urls": target_urls,
                "planned_probe_request_bodies": target_request_bodies,
                "probe_rows": fetch_summary["probe_rows"],
                "probe_status_counts": fetch_summary["probe_status_counts"],
                "probe_error_summary": fetch_summary["probe_error_summary"],
                "probe_target_kinds": fetch_summary["probe_target_kinds"],
                "probe_request_bodies": fetch_summary["probe_request_bodies"],
                "source_reachability_decision": "hold_in_g4_source_reachability_branch",
                "canonical_ml_action": "do_not_merge_to_canonical_or_ml",
                "deep_research_boundary": row.get("deep_research_boundary", ""),
                "next_action": next_action,
                "record_id": f"{school_key}-g4-p1-source-reachability-preview",
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_g4_p1_source_reachability_preview",
            }
        )

    fields = [
        "queue_rank",
        "school_key",
        "school_name",
        "engineering_tier",
        "operating_lane",
        "p1_preview_status",
        "evidence_layer",
        "candidate_extraction_route",
        "plan_source_url",
        "score_source_url",
        "cached_plan_page",
        "cached_score_page",
        "cached_aux_page",
        "registry_notes",
        "cached_page_count",
        "plan_page_count",
        "score_page_count",
        "source_buckets",
        "cached_param_endpoints",
        "cached_data_endpoints",
        "cached_config_signature",
        "cached_response_keys",
        "cached_template_fields",
        "cached_inventory_files",
        "has_guangxi_literal",
        "has_physics_literal",
        "has_sex_toggle",
        "has_campus_toggle",
        "js_endpoint_count",
        "js_endpoints",
        "js_table_props",
        "planned_probe_urls",
        "planned_probe_request_bodies",
        "probe_rows",
        "probe_status_counts",
        "probe_error_summary",
        "probe_target_kinds",
        "probe_request_bodies",
        "source_reachability_decision",
        "canonical_ml_action",
        "deep_research_boundary",
        "next_action",
        "record_id",
        "source_record_id",
        "source_slug",
    ]
    write_csv(PREVIEW_OUT, preview_rows, fields)

    lane_counts = Counter(row["operating_lane"] for row in preview_rows)
    status_counts = Counter(row["p1_preview_status"] for row in preview_rows)
    blocked_count = sum(1 for row in preview_rows if "blocked" in str(row["p1_preview_status"]))
    rollup_rows = [
        {"metric": "p1_preview_school_count", "value": len(preview_rows)},
        {"metric": "p1_static_family_ready_count", "value": lane_counts.get("P1_static_family_ready", 0)},
        {"metric": "p1_js_endpoint_exposed_count", "value": lane_counts.get("P1_js_endpoint_exposed", 0)},
        {"metric": "p1_remote_probe_blocked_count", "value": blocked_count},
        {"metric": "p1_ready_for_canonical_ml_count", "value": 0},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
        {"metric": "canonical_ml_entry_open", "value": "false"},
    ]
    for status, count in sorted(status_counts.items()):
        rollup_rows.append({"metric": f"preview_status::{status}", "value": count})
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value"])

    lines = [
        "# G4 P1 官方来源可达性预览",
        "",
        "本报告只汇总已缓存页面、已缓存 JS 和既有 probe 日志；不联网，不扩池，不写入 canonical/ML。",
        "",
        "## 结论",
        "",
        f"- P1 预览学校数：{len(preview_rows)}。",
        f"- 静态同家族页面已确认：{lane_counts.get('P1_static_family_ready', 0)} 所。",
        f"- JS/API endpoint 形状已确认：{lane_counts.get('P1_js_endpoint_exposed', 0)} 所。",
        f"- 远程 probe 仍受 403/483/TLS 或 cookie/header 问题阻塞：{blocked_count} 所。",
        "- 当前结果只证明官方来源路线存在，不证明数据已可进入 canonical/ML。",
        "",
        "## 分校预览",
        "",
    ]
    for item in preview_rows:
        lines.extend(
            [
                f"### {item['school_name']}",
                "",
                f"- 队列路线：`{item['operating_lane']}`。",
                f"- 预览状态：`{item['p1_preview_status']}`。",
                f"- 证据层：`{item['evidence_layer']}`。",
                f"- 候选抽取路线：`{item['candidate_extraction_route']}`。",
                f"- cached/probe 摘要：page_count={item['cached_page_count']}，probe_rows={item['probe_rows']}，probe_status={item['probe_status_counts']}。",
                f"- 字段/接口证据：`{item['cached_param_endpoints'] or item['js_endpoints']}`。",
                f"- 下一步：{item['next_action']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 产物",
            "",
            f"- `{PREVIEW_OUT.relative_to(ROOT)}`",
            f"- `{ROLLUP_OUT.relative_to(ROOT)}`",
            f"- `{Path(__file__).relative_to(ROOT)}`",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {PREVIEW_OUT}")
    print(f"Wrote {ROLLUP_OUT}")
    print(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
