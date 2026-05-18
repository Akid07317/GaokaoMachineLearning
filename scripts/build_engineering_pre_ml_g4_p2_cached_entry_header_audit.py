#!/usr/bin/env python3
"""Build G4 P2 cached-entry/header route audit preview.

This pass is intentionally local-only: it summarizes cached entry pages, known
ajax-family endpoints, and existing 403 probe logs. It does not replay headers,
fetch remote pages, or write canonical/ML inputs.
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
REGISTRY = CONFIG_DIR / "cold_queue_entry_registry_seed.csv"
STATIC_SUMMARY = REPORT_DIR / "static_ajax_school_summary.csv"
STATIC_INVENTORY = REPORT_DIR / "static_ajax_page_inventory.csv"
AJAX_FETCH = REPORT_DIR / "engineering_api_fetch_ajax_family.csv"

PREVIEW_OUT = SEED_DIR / "guangxi_pre_ml_g4_p2_cached_entry_header_audit_preview_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_g4_p2_cached_entry_header_audit_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_g4_p2_cached_entry_header_audit.md"

P2_LANE = "P2_cached_entry_waiting_headers"


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


def path_exists(path_text: str) -> bool:
    return bool(path_text) and (ROOT / path_text).exists()


def read_cached_text(path_text: str) -> str:
    if not path_text:
        return ""
    path = ROOT / path_text
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def cached_paths(row: dict[str, str]) -> list[str]:
    return [
        row.get("cached_plan_evidence_path", ""),
        row.get("cached_score_evidence_path", ""),
        row.get("cached_support_evidence_path", ""),
    ]


def cached_page_stats(paths: list[str]) -> tuple[int, int]:
    existing = [path for path in paths if path_exists(path)]
    byte_count = sum((ROOT / path).stat().st_size for path in existing)
    return len(existing), byte_count


def extract_from_cached_pages(paths: list[str]) -> dict[str, str]:
    texts = [read_cached_text(path) for path in paths if path_exists(path)]
    all_text = "\n".join(texts)
    endpoints = re.findall(r"\$\.url\(['\"]([^'\"]+)['\"]\)", all_text)
    scripts = re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", all_text)
    css = re.findall(r"<link[^>]+href=['\"]([^'\"]+)['\"]", all_text)
    template_fields = re.findall(r"out\(\$value,\s*['\"]([^'\"]+)['\"]", all_text)
    template_fields.extend(re.findall(r'"fieldName"\s*:\s*"([^"]+)"', all_text))
    config_names = re.findall(r"name\s*:\s*['\"]([^'\"]+)['\"]", all_text)
    config_names.extend(re.findall(r'"fieldName"\s*:\s*"([^"]+)"', all_text))
    response_keys = re.findall(r"res\.data\.([A-Za-z0-9_]+)", all_text)
    response_keys.extend(re.findall(r"\$\.out\(res,\s*['\"]data\.([^'\"]+)['\"]", all_text))
    response_keys.extend(re.findall(r"\$\.out\(res,\s*['\"]data\.([^'\"]+)['\"]", all_text))
    page_titles = re.findall(r"<title>\s*([^<]+?)\s*</title>", all_text, flags=re.I)
    has_guangxi = "广西" in all_text
    has_physics = "物理" in all_text
    has_header_dynamic = any("newsCenter/ajax_get_category_and_link_list" in value for value in endpoints)
    return {
        "cached_endpoints_from_html": compact_unique(endpoints),
        "cached_script_assets": compact_unique(scripts, limit=8),
        "cached_css_assets": compact_unique(css, limit=6),
        "cached_template_fields_from_html": compact_unique(template_fields),
        "cached_config_fields_from_html": compact_unique(config_names),
        "cached_response_keys_from_html": compact_unique(response_keys),
        "cached_page_titles": compact_unique(page_titles),
        "cached_has_guangxi_literal": str(has_guangxi).lower(),
        "cached_has_physics_literal": str(has_physics).lower(),
        "cached_has_dynamic_header_endpoint": str(has_header_dynamic).lower(),
    }


def count_statuses(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("status", "") or "missing_status" for row in rows)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts))


def ajax_probe_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    if not rows:
        return {
            "probe_rows": 0,
            "probe_status_counts": "no_probe_rows",
            "probe_error_summary": "",
            "probe_target_kinds": "",
            "probe_urls": "",
            "probe_request_bodies": "",
        }
    errors = [row.get("error_message", "") for row in rows if row.get("error_message", "")]
    return {
        "probe_rows": len(rows),
        "probe_status_counts": count_statuses(rows),
        "probe_error_summary": compact_unique(errors, limit=4),
        "probe_target_kinds": compact_unique([row.get("target_kind", "") for row in rows]),
        "probe_urls": compact_unique([row.get("url", "") for row in rows], limit=8),
        "probe_request_bodies": compact_unique([row.get("request_body", "") for row in rows], limit=5),
    }


def main() -> None:
    _, queue = read_csv(G4_QUEUE)
    _, registry_rows = read_csv(REGISTRY)
    _, static_summary_rows = read_csv(STATIC_SUMMARY)
    _, static_inventory_rows = read_csv(STATIC_INVENTORY)
    _, ajax_fetch_rows = read_csv(AJAX_FETCH)

    registry = rows_by_key(registry_rows, "school_key")
    static_summary = rows_by_key(static_summary_rows, "school_key")
    static_inventory = group_rows(static_inventory_rows, "school_key")
    ajax_fetch = group_rows(ajax_fetch_rows, "source_id")

    preview_rows: list[dict[str, object]] = []
    p2_queue = [row for row in queue if row.get("operating_lane") == P2_LANE]
    for row in p2_queue:
        school_key = row.get("school_key", "")
        registry_row = registry.get(school_key, {})
        static_row = static_summary.get(school_key, {})
        inventory_rows = static_inventory.get(school_key, [])
        paths = cached_paths(registry_row)
        cached_count, cached_bytes = cached_page_stats(paths)
        cached_extract = extract_from_cached_pages(paths)
        probe = ajax_probe_summary(ajax_fetch.get(school_key, []))
        html_endpoint_count = len(
            [endpoint for endpoint in str(cached_extract["cached_endpoints_from_html"]).split("|") if endpoint]
        )
        static_inventory_count = len(inventory_rows)
        if static_inventory_count:
            preview_status = "static_inventory_and_cached_entry_confirmed_but_ajax_probe_403"
            evidence_layer = "cached_entry_pages_static_inventory_and_ajax_probe_logs"
            route = "static_ajax_inventory_header_replay_candidate"
        elif html_endpoint_count:
            preview_status = "cached_entry_html_endpoint_shape_confirmed_but_ajax_probe_403"
            evidence_layer = "cached_entry_pages_and_ajax_probe_logs"
            route = "cached_html_endpoint_header_replay_candidate"
        else:
            preview_status = "cached_entry_confirmed_but_endpoint_shape_needs_manual_parse"
            evidence_layer = "cached_entry_pages_and_ajax_probe_logs"
            route = "manual_cached_page_parse_before_header_replay"

        preview_rows.append(
            {
                "queue_rank": row.get("queue_rank", ""),
                "school_key": school_key,
                "school_name": row.get("school_name", ""),
                "engineering_tier": row.get("engineering_tier", ""),
                "operating_lane": row.get("operating_lane", ""),
                "p2_preview_status": preview_status,
                "evidence_layer": evidence_layer,
                "candidate_header_route": route,
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "score_alt_url": registry_row.get("score_alt_url", ""),
                "registry_evidence_kind": registry_row.get("evidence_kind", ""),
                "registry_block_type": registry_row.get("block_type", ""),
                "registry_notes": registry_row.get("notes", ""),
                "cached_plan_page": registry_row.get("cached_plan_evidence_path", ""),
                "cached_score_page": registry_row.get("cached_score_evidence_path", ""),
                "cached_support_page": registry_row.get("cached_support_evidence_path", ""),
                "cached_existing_page_count": cached_count,
                "cached_existing_bytes": cached_bytes,
                "cached_page_titles": cached_extract["cached_page_titles"],
                "cached_endpoints_from_html": cached_extract["cached_endpoints_from_html"],
                "cached_template_fields_from_html": cached_extract["cached_template_fields_from_html"],
                "cached_config_fields_from_html": cached_extract["cached_config_fields_from_html"],
                "cached_response_keys_from_html": cached_extract["cached_response_keys_from_html"],
                "cached_script_assets": cached_extract["cached_script_assets"],
                "cached_has_guangxi_literal": cached_extract["cached_has_guangxi_literal"],
                "cached_has_physics_literal": cached_extract["cached_has_physics_literal"],
                "cached_has_dynamic_header_endpoint": cached_extract["cached_has_dynamic_header_endpoint"],
                "static_inventory_rows": static_inventory_count,
                "static_page_count": static_row.get("page_count", "0") or "0",
                "static_param_endpoints": static_row.get("param_endpoints", ""),
                "static_data_endpoints": static_row.get("data_endpoints", ""),
                "static_config_signature": static_row.get("config_name_signature", ""),
                "static_response_keys": static_row.get("response_keys", ""),
                "static_template_fields": static_row.get("template_fields", ""),
                "static_has_zyz_or_group_route": str(
                    "zyz" in static_row.get("config_name_signature", "")
                    or "zyz" in static_row.get("template_fields", "")
                    or "zyz" in str(cached_extract["cached_config_fields_from_html"])
                ).lower(),
                "probe_rows": probe["probe_rows"],
                "probe_status_counts": probe["probe_status_counts"],
                "probe_error_summary": probe["probe_error_summary"],
                "probe_target_kinds": probe["probe_target_kinds"],
                "probe_urls": probe["probe_urls"],
                "probe_request_bodies": probe["probe_request_bodies"],
                "source_reachability_decision": "hold_in_g4_p2_header_audit_branch",
                "canonical_ml_action": "do_not_merge_to_canonical_or_ml",
                "approval_boundary": "network_header_cookie_replay_requires_human_approval",
                "deep_research_boundary": row.get("deep_research_boundary", ""),
                "next_action": (
                    "先完成人工批准前的 header 路线审计；若要继续，只能单独申请联网/"
                    "header/cookie/browser 态验证，不得直接进入 canonical/ML。"
                ),
                "record_id": f"{school_key}-g4-p2-cached-entry-header-audit-preview",
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_g4_p2_cached_entry_header_audit",
            }
        )

    fields = [
        "queue_rank",
        "school_key",
        "school_name",
        "engineering_tier",
        "operating_lane",
        "p2_preview_status",
        "evidence_layer",
        "candidate_header_route",
        "plan_source_url",
        "score_source_url",
        "score_alt_url",
        "registry_evidence_kind",
        "registry_block_type",
        "registry_notes",
        "cached_plan_page",
        "cached_score_page",
        "cached_support_page",
        "cached_existing_page_count",
        "cached_existing_bytes",
        "cached_page_titles",
        "cached_endpoints_from_html",
        "cached_template_fields_from_html",
        "cached_config_fields_from_html",
        "cached_response_keys_from_html",
        "cached_script_assets",
        "cached_has_guangxi_literal",
        "cached_has_physics_literal",
        "cached_has_dynamic_header_endpoint",
        "static_inventory_rows",
        "static_page_count",
        "static_param_endpoints",
        "static_data_endpoints",
        "static_config_signature",
        "static_response_keys",
        "static_template_fields",
        "static_has_zyz_or_group_route",
        "probe_rows",
        "probe_status_counts",
        "probe_error_summary",
        "probe_target_kinds",
        "probe_urls",
        "probe_request_bodies",
        "source_reachability_decision",
        "canonical_ml_action",
        "approval_boundary",
        "deep_research_boundary",
        "next_action",
        "record_id",
        "source_record_id",
        "source_slug",
    ]
    write_csv(PREVIEW_OUT, preview_rows, fields)

    status_counts = Counter(row["p2_preview_status"] for row in preview_rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "p2_preview_school_count", "value": len(preview_rows)},
        {"metric": "p2_probe_403_school_count", "value": sum("403" in str(row["probe_error_summary"]) for row in preview_rows)},
        {"metric": "p2_static_inventory_available_count", "value": sum(int(row["static_inventory_rows"]) > 0 for row in preview_rows)},
        {"metric": "p2_cached_html_endpoint_shape_available_count", "value": sum(bool(row["cached_endpoints_from_html"]) for row in preview_rows)},
        {"metric": "p2_ready_for_canonical_ml_count", "value": 0},
        {"metric": "network_replay_requires_human_approval", "value": "true"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
        {"metric": "canonical_ml_entry_open", "value": "false"},
    ]
    for status, count in sorted(status_counts.items()):
        rollup_rows.append({"metric": f"preview_status::{status}", "value": count})
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value"])

    lines = [
        "# G4 P2 缓存入口与 header 路线审计",
        "",
        "本报告只汇总已缓存入口页、既有 ajax_family probe 日志和 static inventory；不联网、不 replay header/cookie、不写入 canonical/ML。",
        "",
        "## 结论",
        "",
        f"- P2 审计学校数：{len(preview_rows)}。",
        f"- 既有 probe 显示接口层 403 的学校：{sum('403' in str(row['probe_error_summary']) for row in preview_rows)} 所。",
        f"- 已有 static inventory 的学校：{sum(int(row['static_inventory_rows']) > 0 for row in preview_rows)} 所。",
        f"- 可从缓存 HTML 直接确认 endpoint 形状的学校：{sum(bool(row['cached_endpoints_from_html']) for row in preview_rows)} 所。",
        "- 三所均继续留在 G4 P2 source reachability branch；任何联网/header/cookie/browser 态动作都需要单独人工批准。",
        "",
        "## 分校审计",
        "",
    ]
    for item in preview_rows:
        lines.extend(
            [
                f"### {item['school_name']}",
                "",
                f"- 预览状态：`{item['p2_preview_status']}`。",
                f"- 候选 header 路线：`{item['candidate_header_route']}`。",
                f"- 缓存入口：{item['cached_existing_page_count']} 个文件，{item['cached_existing_bytes']} bytes。",
                f"- 缓存 endpoint：`{item['cached_endpoints_from_html'] or item['static_param_endpoints']}`。",
                f"- 字段证据：`{item['cached_template_fields_from_html'] or item['static_template_fields']}`。",
                f"- probe 摘要：rows={item['probe_rows']}，status={item['probe_status_counts']}，error={item['probe_error_summary']}。",
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
