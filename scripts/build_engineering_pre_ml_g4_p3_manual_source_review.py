#!/usr/bin/env python3
"""Build G4 P3 manual official-source review preview.

This is a local-only handoff layer for schools whose official source route is
not yet machine-extractable from cached evidence. It reads existing registry,
discovery, and cached-page files; it does not fetch, replay forms, or write
canonical/ML inputs.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
CONFIG_DIR = ROOT / "configs"
DOCS_DIR = ROOT / "docs"

G4_QUEUE = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_queue_merged.csv"
REGISTRY = CONFIG_DIR / "cold_queue_entry_registry_seed.csv"
FALLBACK_REGISTRY = CONFIG_DIR / "actionable_source_fallback_registry.csv"
DISCOVERY_CANDIDATES = REPORT_DIR / "discovery_211_full_candidates_priority.csv"
DISCOVERY_PAGES = REPORT_DIR / "discovery_engineering_entry_supplemental_pages.csv"

PREVIEW_OUT = SEED_DIR / "guangxi_pre_ml_g4_p3_manual_source_review_preview_merged.csv"
ROLLUP_OUT = REPORT_DIR / "engineering_pre_ml_g4_p3_manual_source_review_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_g4_p3_manual_source_review.md"

P3_LANE = "P3_manual_review"


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


def safe_int(value: str) -> int:
    try:
        return int(float(str(value or "0").strip()))
    except ValueError:
        return 0


def path_exists(path_text: str) -> bool:
    return bool(path_text) and (ROOT / path_text).exists()


def is_cached_page_path(path_text: str) -> bool:
    if not path_exists(path_text):
        return False
    path = ROOT / path_text
    return path_text.startswith("raw_data/") and path.suffix.lower() in {".html", ".htm", ".aspx"}


def read_text(path_text: str) -> str:
    if not path_exists(path_text):
        return ""
    return (ROOT / path_text).read_text(encoding="utf-8", errors="ignore")


def cached_paths(row: dict[str, str]) -> list[str]:
    return [
        row.get("cached_plan_evidence_path", ""),
        row.get("cached_score_evidence_path", ""),
        row.get("cached_support_evidence_path", ""),
    ]


def cached_page_stats(paths: list[str]) -> tuple[int, int]:
    existing = [path for path in paths if is_cached_page_path(path)]
    byte_count = sum((ROOT / path).stat().st_size for path in existing)
    return len(existing), byte_count


def extract_cached_page_evidence(paths: list[str]) -> dict[str, str]:
    texts = [read_text(path) for path in paths if is_cached_page_path(path)]
    all_text = "\n".join(texts)
    titles = re.findall(r"<title>\s*([^<]+?)\s*</title>", all_text, flags=re.I)
    hrefs = re.findall(r"href=['\"]([^'\"]+)['\"]", all_text, flags=re.I)
    scripts = re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", all_text, flags=re.I)
    forms = re.findall(r"<form[^>]+(?:action=['\"]([^'\"]*)['\"])?", all_text, flags=re.I)
    input_names = re.findall(r"<input[^>]+name=['\"]([^'\"]+)['\"]", all_text, flags=re.I)
    endpoint_like = re.findall(r"(?:url|href|action)\s*[:=]\s*['\"]([^'\"]*(?:api|ajax|plans|scores|zsjh|lnfs|lqcx)[^'\"]*)['\"]", all_text, flags=re.I)
    keyword_links = [
        href
        for href in hrefs
        if any(word in href.lower() for word in ("zsjh", "lnfs", "lqcx", "plan", "score", "admit", "enroll"))
        or any(word in href for word in ("招生", "计划", "分数", "录取", "广西"))
    ]
    return {
        "cached_page_titles": compact_unique(titles),
        "cached_keyword_links": compact_unique(keyword_links, limit=8),
        "cached_script_assets": compact_unique(scripts, limit=8),
        "cached_form_actions": compact_unique(forms),
        "cached_input_names": compact_unique(input_names, limit=12),
        "cached_endpoint_like_strings": compact_unique(endpoint_like, limit=12),
        "cached_has_guangxi_literal": str("广西" in all_text).lower(),
        "cached_has_plan_score_words": str(any(word in all_text for word in ("招生计划", "历年分数", "录取", "投档"))).lower(),
        "cached_has_fineui_or_viewstate": str(("FineUI" in all_text) or ("__VIEWSTATE" in all_text)).lower(),
    }


def top_candidate_rows(rows: list[dict[str, str]], limit: int = 8) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: safe_int(row.get("score", "0")), reverse=True)[:limit]


def candidate_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    categories = Counter(row.get("category", "") or "uncategorized" for row in rows)
    domains = Counter(row.get("target_domain", "") or urlparse(row.get("target_url", "")).netloc for row in rows)
    top_rows = top_candidate_rows(rows)
    return {
        "discovery_candidate_count": len(rows),
        "discovery_categories": "|".join(f"{key}:{categories[key]}" for key in sorted(categories)),
        "discovery_top_domains": "|".join(f"{key}:{domains[key]}" for key, _ in domains.most_common(6)),
        "discovery_top_urls": compact_unique([row.get("target_url", "") for row in top_rows], limit=8),
        "discovery_top_titles": compact_unique([row.get("link_text", "") for row in top_rows], limit=8),
        "discovery_top_scores": compact_unique([row.get("score", "") for row in top_rows], limit=8),
    }


def page_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    statuses = Counter(row.get("status", "") or "unknown" for row in rows)
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    error_rows = [row for row in rows if row.get("status") != "ok"]
    return {
        "supplemental_page_count": len(rows),
        "supplemental_status_counts": "|".join(f"{key}:{statuses[key]}" for key in sorted(statuses)),
        "supplemental_ok_titles": compact_unique([row.get("page_title", "") for row in ok_rows], limit=8),
        "supplemental_ok_urls": compact_unique([row.get("page_url", "") for row in ok_rows], limit=8),
        "supplemental_error_summary": compact_unique([row.get("error_message", "") for row in error_rows], limit=4),
    }


def manual_status(row: dict[str, str], registry_row: dict[str, str]) -> tuple[str, str, str]:
    blocker = row.get("blocker_class", "")
    school_key = row.get("school_key", "")
    registry_block = registry_row.get("block_type", "")
    if blocker == "form_replay_blocked" or registry_block == "form_replay_blocked":
        return (
            "manual_form_replay_required_not_approved",
            "form_field_and_state_token_audit",
            "仅整理 FineUI/表单字段和缓存入口；表单 replay、验证码、cookie/header 均需人工批准。",
        )
    if school_key == "zhongguo_kuangye_beijing_211":
        return (
            "weak_official_evidence_needs_undergraduate_source_confirmation",
            "official_undergraduate_entry_disambiguation",
            "当前缓存偏研究生/信息公开弱证据，需人工确认本科招生计划与历年分数官方入口。",
        )
    if school_key == "zhongguo_dizhi_wuhan_211":
        return (
            "official_candidate_routes_need_source_disambiguation",
            "official_subdomain_or_candidate_page_validation",
            "现有候选包含招生就业页、继续教育录取查询和招生子域，需人工确认本科普通批官方入口。",
        )
    if registry_block == "needs_discovery":
        return (
            "official_home_or_column_cached_but_stable_plan_score_entry_missing",
            "official_column_tree_discovery_needed",
            "已有官方主页或栏目缓存，但未定位稳定招生计划/历年分数入口；如继续需人工或批准后外查。",
        )
    return (
        "manual_source_review_required",
        "manual_official_source_validation",
        "需人工复核官方来源可达性和后续抽取方式。",
    )


def main() -> None:
    _, queue = read_csv(G4_QUEUE)
    _, registry_rows = read_csv(REGISTRY)
    _, fallback_rows = read_csv(FALLBACK_REGISTRY)
    _, candidate_rows = read_csv(DISCOVERY_CANDIDATES)
    _, page_rows = read_csv(DISCOVERY_PAGES)

    registry = rows_by_key(registry_rows, "school_key")
    fallback = rows_by_key(fallback_rows, "school_key")
    candidates = group_rows(candidate_rows, "seed_id")
    pages = group_rows(page_rows, "seed_id")

    preview_rows: list[dict[str, object]] = []
    p3_rows = [row for row in queue if row.get("operating_lane") == P3_LANE]
    for row in p3_rows:
        school_key = row.get("school_key", "")
        registry_row = registry.get(school_key, {})
        fallback_row = fallback.get(school_key, {})
        paths = cached_paths(registry_row)
        cached_count, cached_bytes = cached_page_stats(paths)
        cached = extract_cached_page_evidence(paths)
        cand = candidate_summary(candidates.get(school_key, []))
        pagesum = page_summary(pages.get(school_key, []))
        status, route, next_action = manual_status(row, registry_row)
        approval_required = "true"
        preview_rows.append(
            {
                "queue_rank": row.get("queue_rank", ""),
                "school_key": school_key,
                "school_name": row.get("school_name", ""),
                "engineering_tier": row.get("engineering_tier", ""),
                "operating_lane": row.get("operating_lane", ""),
                "source_reachability_task_type": row.get("source_reachability_task_type", ""),
                "blocker_class": row.get("blocker_class", ""),
                "p3_review_status": status,
                "manual_route": route,
                "plan_source_url": row.get("plan_source_url", ""),
                "score_source_url": row.get("score_source_url", ""),
                "score_alt_url": registry_row.get("score_alt_url", ""),
                "registry_evidence_kind": registry_row.get("evidence_kind", ""),
                "registry_block_type": registry_row.get("block_type", ""),
                "registry_notes": registry_row.get("notes", ""),
                "fallback_plan_source_url": fallback_row.get("plan_source_url", ""),
                "fallback_score_source_url": fallback_row.get("score_source_url", ""),
                "fallback_source_basis": fallback_row.get("source_basis", ""),
                "fallback_notes": fallback_row.get("notes", ""),
                "cached_plan_page": registry_row.get("cached_plan_evidence_path", ""),
                "cached_score_page": registry_row.get("cached_score_evidence_path", ""),
                "cached_support_page": registry_row.get("cached_support_evidence_path", ""),
                "cached_existing_page_count": cached_count,
                "cached_existing_bytes": cached_bytes,
                "cached_page_titles": cached["cached_page_titles"],
                "cached_keyword_links": cached["cached_keyword_links"],
                "cached_endpoint_like_strings": cached["cached_endpoint_like_strings"],
                "cached_form_actions": cached["cached_form_actions"],
                "cached_input_names": cached["cached_input_names"],
                "cached_script_assets": cached["cached_script_assets"],
                "cached_has_guangxi_literal": cached["cached_has_guangxi_literal"],
                "cached_has_plan_score_words": cached["cached_has_plan_score_words"],
                "cached_has_fineui_or_viewstate": cached["cached_has_fineui_or_viewstate"],
                **cand,
                **pagesum,
                "source_reachability_decision": "hold_in_g4_p3_manual_review_branch",
                "canonical_ml_action": "do_not_merge_to_canonical_or_ml",
                "approval_required_for_next_live_step": approval_required,
                "approval_boundary": "network_deep_research_header_cookie_form_or_browser_check_requires_human_approval",
                "deep_research_boundary": row.get("deep_research_boundary", ""),
                "next_action": next_action,
                "record_id": f"{school_key}-g4-p3-manual-source-review-preview",
                "source_record_id": row.get("record_id", ""),
                "source_slug": "pre_ml_g4_p3_manual_source_review",
            }
        )

    fields = [
        "queue_rank",
        "school_key",
        "school_name",
        "engineering_tier",
        "operating_lane",
        "source_reachability_task_type",
        "blocker_class",
        "p3_review_status",
        "manual_route",
        "plan_source_url",
        "score_source_url",
        "score_alt_url",
        "registry_evidence_kind",
        "registry_block_type",
        "registry_notes",
        "fallback_plan_source_url",
        "fallback_score_source_url",
        "fallback_source_basis",
        "fallback_notes",
        "cached_plan_page",
        "cached_score_page",
        "cached_support_page",
        "cached_existing_page_count",
        "cached_existing_bytes",
        "cached_page_titles",
        "cached_keyword_links",
        "cached_endpoint_like_strings",
        "cached_form_actions",
        "cached_input_names",
        "cached_script_assets",
        "cached_has_guangxi_literal",
        "cached_has_plan_score_words",
        "cached_has_fineui_or_viewstate",
        "discovery_candidate_count",
        "discovery_categories",
        "discovery_top_domains",
        "discovery_top_urls",
        "discovery_top_titles",
        "discovery_top_scores",
        "supplemental_page_count",
        "supplemental_status_counts",
        "supplemental_ok_titles",
        "supplemental_ok_urls",
        "supplemental_error_summary",
        "source_reachability_decision",
        "canonical_ml_action",
        "approval_required_for_next_live_step",
        "approval_boundary",
        "deep_research_boundary",
        "next_action",
        "record_id",
        "source_record_id",
        "source_slug",
    ]
    write_csv(PREVIEW_OUT, preview_rows, fields)

    status_counts = Counter(row["p3_review_status"] for row in preview_rows)
    route_counts = Counter(row["manual_route"] for row in preview_rows)
    rollup_rows: list[dict[str, object]] = [
        {"metric": "p3_manual_review_school_count", "value": len(preview_rows)},
        {"metric": "p3_cached_evidence_available_count", "value": sum(int(row["cached_existing_page_count"]) > 0 for row in preview_rows)},
        {"metric": "p3_discovery_candidates_available_count", "value": sum(int(row["discovery_candidate_count"]) > 0 for row in preview_rows)},
        {"metric": "p3_requires_human_approval_for_live_next_step_count", "value": len(preview_rows)},
        {"metric": "p3_ready_for_canonical_ml_count", "value": 0},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
        {"metric": "canonical_ml_entry_open", "value": "false"},
    ]
    for status, count in sorted(status_counts.items()):
        rollup_rows.append({"metric": f"review_status::{status}", "value": count})
    for route, count in sorted(route_counts.items()):
        rollup_rows.append({"metric": f"manual_route::{route}", "value": count})
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value"])

    lines = [
        "# G4 P3 官方来源人工路线预览",
        "",
        "本报告只汇总本地 registry、缓存页、discovery candidates 和已有报告；不联网，不启用 Deep Research，不 replay 表单/header/cookie，不写入 canonical/ML。",
        "",
        "## 结论",
        "",
        f"- P3 manual review 学校数：{len(preview_rows)}。",
        f"- 本地已有缓存证据的学校：{sum(int(row['cached_existing_page_count']) > 0 for row in preview_rows)} 所。",
        f"- 本地已有 discovery candidates 的学校：{sum(int(row['discovery_candidate_count']) > 0 for row in preview_rows)} 所。",
        "- 五所下一步都需要人工批准后才能继续 live source 检查。",
        "- 当前 P3 结果只作为来源路线预览，不进入 canonical/ML。",
        "",
        "## 分校预览",
        "",
    ]
    for item in preview_rows:
        lines.extend(
            [
                f"### {item['school_name']}",
                "",
                f"- 预览状态：`{item['p3_review_status']}`。",
                f"- 人工路线：`{item['manual_route']}`。",
                f"- registry：`{item['registry_evidence_kind']}` / `{item['registry_block_type']}`。",
                f"- 缓存证据：{item['cached_existing_page_count']} 个文件，{item['cached_existing_bytes']} bytes，标题 `{item['cached_page_titles']}`。",
                f"- discovery 候选：{item['discovery_candidate_count']} 条，top URLs `{item['discovery_top_urls']}`。",
                f"- fallback：`{item['fallback_source_basis']}`，plan `{item['fallback_plan_source_url']}`，score `{item['fallback_score_source_url']}`。",
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
