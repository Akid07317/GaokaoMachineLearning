#!/usr/bin/env python3
"""Build G4 source reachability closeout and human approval queue.

This merges the P1/P2/P3 local preview layers into one non-canonical closeout.
It does not fetch remote data, replay headers/forms, or open the ML/canonical
entry.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

G4_QUEUE = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_queue_merged.csv"
P1_PREVIEW = SEED_DIR / "guangxi_pre_ml_g4_p1_source_reachability_preview_merged.csv"
P2_PREVIEW = SEED_DIR / "guangxi_pre_ml_g4_p2_cached_entry_header_audit_preview_merged.csv"
P3_PREVIEW = SEED_DIR / "guangxi_pre_ml_g4_p3_manual_source_review_preview_merged.csv"

CLOSEOUT_OUT = SEED_DIR / "guangxi_pre_ml_g4_source_reachability_closeout_merged.csv"
APPROVAL_OUT = SEED_DIR / "guangxi_pre_ml_g4_human_approval_queue_merged.csv"
CLOSEOUT_ROLLUP = REPORT_DIR / "engineering_pre_ml_g4_source_reachability_closeout_coverage_rollup.csv"
APPROVAL_ROLLUP = REPORT_DIR / "engineering_pre_ml_g4_human_approval_queue_coverage_rollup.csv"
DOC_OUT = DOCS_DIR / "pre_ml_g4_source_reachability_closeout.md"


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


def by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("school_key", ""): row for row in rows if row.get("school_key", "")}


def compact(value: object, max_len: int = 260) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 16] + "...[truncated]"


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def stage_from_lane(lane: str) -> str:
    if lane.startswith("P1_"):
        return "P1_local_route_shape_confirmed"
    if lane.startswith("P2_"):
        return "P2_cached_entry_header_route_confirmed"
    return "P3_manual_official_source_review"


def preview_for(
    school_key: str,
    lane: str,
    p1: dict[str, dict[str, str]],
    p2: dict[str, dict[str, str]],
    p3: dict[str, dict[str, str]],
) -> dict[str, str]:
    if lane.startswith("P1_"):
        return p1.get(school_key, {})
    if lane.startswith("P2_"):
        return p2.get(school_key, {})
    return p3.get(school_key, {})


def route_status(lane: str, row: dict[str, str]) -> str:
    if lane.startswith("P1_"):
        return row.get("p1_preview_status", "")
    if lane.startswith("P2_"):
        return row.get("p2_preview_status", "")
    return row.get("p3_review_status", "")


def route_family(lane: str, row: dict[str, str]) -> str:
    if lane.startswith("P1_"):
        return row.get("candidate_extraction_route", "")
    if lane.startswith("P2_"):
        return row.get("candidate_header_route", "")
    return row.get("manual_route", "")


def source_evidence_summary(lane: str, row: dict[str, str]) -> str:
    if lane.startswith("P1_"):
        parts = [
            f"cached_pages={row.get('cached_page_count', '0')}",
            f"js_endpoints={row.get('js_endpoint_count', '0')}",
            f"probe={row.get('probe_status_counts', '')}",
            f"errors={row.get('probe_error_summary', '')}",
        ]
    elif lane.startswith("P2_"):
        parts = [
            f"cached_pages={row.get('cached_existing_page_count', '0')}",
            f"html_endpoints={bool(row.get('cached_endpoints_from_html', ''))}",
            f"static_inventory_rows={row.get('static_inventory_rows', '0')}",
            f"probe={row.get('probe_status_counts', '')}",
            f"errors={row.get('probe_error_summary', '')}",
        ]
    else:
        parts = [
            f"cached_pages={row.get('cached_existing_page_count', '0')}",
            f"discovery_candidates={row.get('discovery_candidate_count', '0')}",
            f"registry={row.get('registry_evidence_kind', '')}/{row.get('registry_block_type', '')}",
        ]
    return "; ".join(part for part in parts if part and not part.endswith("="))


def blocker_summary(lane: str, base: dict[str, str], row: dict[str, str]) -> str:
    text = "|".join(
        [
            base.get("blocker_class", ""),
            row.get("probe_error_summary", ""),
            row.get("registry_block_type", ""),
            row.get("p3_review_status", ""),
        ]
    )
    lowered = text.lower()
    if "fineui" in lowered or "viewstate" in lowered or "form" in lowered:
        return "form_replay_or_state_token_blocked"
    if "483" in lowered or "tls" in lowered or "ssl" in lowered:
        return "remote_probe_483_or_tls_blocked"
    if "403" in lowered or "cookie" in lowered or "header" in lowered:
        return "ajax_header_cookie_403_blocked"
    if "weak_official" in lowered or "disambiguation" in lowered:
        return "weak_official_or_undergraduate_source_disambiguation"
    if "source_gap" in lowered or "needs_discovery" in lowered:
        return "official_source_gap_or_discovery_needed"
    return base.get("blocker_class", "manual_route_blocked")


def flags(lane: str, base: dict[str, str], row: dict[str, str]) -> dict[str, str]:
    blocker = blocker_summary(lane, base, row)
    is_p1_static = lane == "P1_static_family_ready"
    is_header = "403" in blocker or "header" in blocker or "cookie" in blocker
    is_form = "form" in blocker or base.get("blocker_class") == "form_replay_blocked"
    is_browser = "tls" in blocker or "483" in blocker or is_header or is_form
    needs_dr = (
        lane == "P3_manual_review"
        and base.get("blocker_class") == "source_gap"
        and not is_form
    )
    local_possible = is_p1_static
    if lane == "P2_cached_entry_waiting_headers":
        local_possible = False
    if lane == "P1_js_endpoint_exposed":
        local_possible = False
    if lane == "P3_manual_review":
        local_possible = False
    return {
        "requires_live_network_approval": "true",
        "requires_deep_research_approval": bool_text(needs_dr),
        "requires_header_cookie_approval": bool_text(is_header),
        "requires_form_replay_approval": bool_text(is_form),
        "requires_browser_state_approval": bool_text(is_browser),
        "can_continue_local_only": bool_text(local_possible),
        "local_only_next_step": (
            "optional_cached_static_parser_preview_only"
            if local_possible
            else "none_without_live_source_or_human_disambiguation"
        ),
    }


def approval_type(lane: str, base: dict[str, str], row: dict[str, str]) -> str:
    blocker = blocker_summary(lane, base, row)
    if "form" in blocker:
        return "form_replay_or_state_token_approval"
    if "tls" in blocker or "483" in blocker:
        return "browser_or_tls_api_probe_approval"
    if "403" in blocker or "header" in blocker or "cookie" in blocker:
        return "header_cookie_or_browser_state_approval"
    if lane == "P3_manual_review" and base.get("blocker_class") == "source_gap":
        return "official_source_discovery_or_deep_research_approval"
    return "manual_official_source_validation_approval"


def approval_scope(row: dict[str, str], flags_row: dict[str, str]) -> str:
    scopes: list[str] = []
    if flags_row["requires_deep_research_approval"] == "true":
        scopes.append("Deep Research limited to official source reachability")
    if flags_row["requires_header_cookie_approval"] == "true":
        scopes.append("header/cookie replay against listed official endpoints")
    if flags_row["requires_form_replay_approval"] == "true":
        scopes.append("form/state-token replay audit only")
    if flags_row["requires_browser_state_approval"] == "true":
        scopes.append("browser-state/TLS verification")
    if not scopes:
        scopes.append("manual official source validation")
    return "; ".join(scopes)


def priority(lane: str, base: dict[str, str], row: dict[str, str]) -> str:
    approval = approval_type(lane, base, row)
    if approval == "form_replay_or_state_token_approval":
        return "A2_form_high_risk"
    if lane == "P1_static_family_ready":
        return "A1_static_family_lowest_live_scope"
    if approval == "header_cookie_or_browser_state_approval":
        return "A2_header_cookie"
    if approval == "browser_or_tls_api_probe_approval":
        return "A2_browser_tls"
    if approval == "official_source_discovery_or_deep_research_approval":
        return "A3_deep_research_or_manual_source"
    return "A4_manual_validation"


def main() -> None:
    _, queue_rows = read_csv(G4_QUEUE)
    _, p1_rows = read_csv(P1_PREVIEW)
    _, p2_rows = read_csv(P2_PREVIEW)
    _, p3_rows = read_csv(P3_PREVIEW)
    p1 = by_key(p1_rows)
    p2 = by_key(p2_rows)
    p3 = by_key(p3_rows)

    closeout_rows: list[dict[str, object]] = []
    approval_rows: list[dict[str, object]] = []

    for base in queue_rows:
        school_key = base.get("school_key", "")
        lane = base.get("operating_lane", "")
        preview = preview_for(school_key, lane, p1, p2, p3)
        stage = stage_from_lane(lane)
        status = route_status(lane, preview)
        route = route_family(lane, preview)
        blocker = blocker_summary(lane, base, preview)
        flag_row = flags(lane, base, preview)
        evidence_summary = source_evidence_summary(lane, preview)
        closeout_decision = "hold_in_g4_source_reachability_no_canonical_ml"
        ml_closed_reason = (
            "official_source_route_not_live_verified_or_human_accepted; "
            "missing canonical-ready plan/score/rank/trend layer"
        )
        closeout_row = {
            "queue_rank": base.get("queue_rank", ""),
            "school_key": school_key,
            "school_name": base.get("school_name", ""),
            "engineering_tier": base.get("engineering_tier", ""),
            "operating_lane": lane,
            "closeout_stage": stage,
            "official_entry_status": status,
            "route_family": route,
            "blocker_summary": blocker,
            "plan_source_url": base.get("plan_source_url", ""),
            "score_source_url": base.get("score_source_url", ""),
            "source_evidence_summary": evidence_summary,
            "source_reachability_decision": closeout_decision,
            "canonical_ml_action": "do_not_merge_to_canonical_or_ml",
            "canonical_ml_closed_reason": ml_closed_reason,
            "deep_research_boundary": base.get("deep_research_boundary", ""),
            **flag_row,
            "approval_request_type": approval_type(lane, base, preview),
            "approval_priority": priority(lane, base, preview),
            "next_action": preview.get("next_action", base.get("next_action", "")),
            "source_preview_record_id": preview.get("record_id", ""),
            "source_queue_record_id": base.get("record_id", ""),
            "record_id": f"{school_key}-g4-source-reachability-closeout",
            "source_slug": "pre_ml_g4_source_reachability_closeout",
        }
        closeout_rows.append(closeout_row)

        approval_rows.append(
            {
                "approval_rank": "",
                "school_key": school_key,
                "school_name": base.get("school_name", ""),
                "engineering_tier": base.get("engineering_tier", ""),
                "approval_priority": closeout_row["approval_priority"],
                "approval_request_type": closeout_row["approval_request_type"],
                "approval_scope": approval_scope(preview, flag_row),
                "current_blocker": blocker,
                "plan_source_url": base.get("plan_source_url", ""),
                "score_source_url": base.get("score_source_url", ""),
                "allowed_if_approved": (
                    "official-source reachability verification only; collect "
                    "status, endpoint shape, and blocker notes"
                ),
                "forbidden_even_if_approved": (
                    "pool expansion; non-211 discovery; direct canonical/ML writes; "
                    "model training; unreviewed merged data"
                ),
                "can_continue_local_only": flag_row["can_continue_local_only"],
                "local_only_next_step": flag_row["local_only_next_step"],
                "deep_research_boundary": base.get("deep_research_boundary", ""),
                "canonical_ml_action": closeout_row["canonical_ml_action"],
                "next_action": closeout_row["next_action"],
                "source_closeout_record_id": closeout_row["record_id"],
                "record_id": f"{school_key}-g4-human-approval-queue",
                "source_slug": "pre_ml_g4_human_approval_queue",
            }
        )

    priority_order = {
        "A1_static_family_lowest_live_scope": 1,
        "A2_header_cookie": 2,
        "A2_browser_tls": 3,
        "A2_form_high_risk": 4,
        "A3_deep_research_or_manual_source": 5,
        "A4_manual_validation": 6,
    }
    approval_rows.sort(
        key=lambda row: (
            priority_order.get(str(row.get("approval_priority")), 99),
            int(str(next((r for r in closeout_rows if r["school_key"] == row["school_key"]), {"queue_rank": "999"})["queue_rank"])),
        )
    )
    for index, row in enumerate(approval_rows, start=1):
        row["approval_rank"] = index

    closeout_fields = [
        "queue_rank",
        "school_key",
        "school_name",
        "engineering_tier",
        "operating_lane",
        "closeout_stage",
        "official_entry_status",
        "route_family",
        "blocker_summary",
        "plan_source_url",
        "score_source_url",
        "source_evidence_summary",
        "source_reachability_decision",
        "canonical_ml_action",
        "canonical_ml_closed_reason",
        "deep_research_boundary",
        "requires_live_network_approval",
        "requires_deep_research_approval",
        "requires_header_cookie_approval",
        "requires_form_replay_approval",
        "requires_browser_state_approval",
        "can_continue_local_only",
        "local_only_next_step",
        "approval_request_type",
        "approval_priority",
        "next_action",
        "source_preview_record_id",
        "source_queue_record_id",
        "record_id",
        "source_slug",
    ]
    approval_fields = [
        "approval_rank",
        "school_key",
        "school_name",
        "engineering_tier",
        "approval_priority",
        "approval_request_type",
        "approval_scope",
        "current_blocker",
        "plan_source_url",
        "score_source_url",
        "allowed_if_approved",
        "forbidden_even_if_approved",
        "can_continue_local_only",
        "local_only_next_step",
        "deep_research_boundary",
        "canonical_ml_action",
        "next_action",
        "source_closeout_record_id",
        "record_id",
        "source_slug",
    ]
    write_csv(CLOSEOUT_OUT, closeout_rows, closeout_fields)
    write_csv(APPROVAL_OUT, approval_rows, approval_fields)

    closeout_counters = {
        "g4_closeout_school_count": len(closeout_rows),
        "canonical_ml_entry_open": "false",
        "ready_for_canonical_ml_count": 0,
        "requires_live_network_approval_count": sum(row["requires_live_network_approval"] == "true" for row in closeout_rows),
        "requires_deep_research_approval_count": sum(row["requires_deep_research_approval"] == "true" for row in closeout_rows),
        "requires_header_cookie_approval_count": sum(row["requires_header_cookie_approval"] == "true" for row in closeout_rows),
        "requires_form_replay_approval_count": sum(row["requires_form_replay_approval"] == "true" for row in closeout_rows),
        "requires_browser_state_approval_count": sum(row["requires_browser_state_approval"] == "true" for row in closeout_rows),
        "can_continue_local_only_count": sum(row["can_continue_local_only"] == "true" for row in closeout_rows),
    }
    rollup_rows = [{"metric": key, "value": value} for key, value in closeout_counters.items()]
    for name, counter in [
        ("operating_lane", Counter(row["operating_lane"] for row in closeout_rows)),
        ("blocker_summary", Counter(row["blocker_summary"] for row in closeout_rows)),
        ("approval_request_type", Counter(row["approval_request_type"] for row in closeout_rows)),
        ("approval_priority", Counter(row["approval_priority"] for row in closeout_rows)),
    ]:
        for key, value in sorted(counter.items()):
            rollup_rows.append({"metric": f"{name}::{key}", "value": value})
    write_csv(CLOSEOUT_ROLLUP, rollup_rows, ["metric", "value"])

    approval_counter = Counter(row["approval_request_type"] for row in approval_rows)
    approval_rollup = [
        {"metric": "approval_queue_school_count", "value": len(approval_rows)},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "pool_expansion_allowed", "value": "false"},
        {"metric": "non211_search_allowed", "value": "false"},
        {"metric": "deep_research_mainline_allowed", "value": "false"},
    ]
    for key, value in sorted(approval_counter.items()):
        approval_rollup.append({"metric": f"approval_request_type::{key}", "value": value})
    write_csv(APPROVAL_ROLLUP, approval_rollup, ["metric", "value"])

    lines = [
        "# G4 来源可达性 closeout 与人工批准队列",
        "",
        "本报告合并 P1/P2/P3 本地预览；不联网，不启用 Deep Research，不 replay header/cookie/form，不写入 canonical/ML。",
        "",
        "## Closeout 结论",
        "",
        f"- G4 closeout 学校数：{len(closeout_rows)}。",
        f"- 需要 live source 人工批准：{closeout_counters['requires_live_network_approval_count']} 所。",
        f"- 需要 Deep Research 批准：{closeout_counters['requires_deep_research_approval_count']} 所。",
        f"- 需要 header/cookie 批准：{closeout_counters['requires_header_cookie_approval_count']} 所。",
        f"- 需要 form replay 批准：{closeout_counters['requires_form_replay_approval_count']} 所。",
        f"- 需要 browser/TLS 态批准：{closeout_counters['requires_browser_state_approval_count']} 所。",
        f"- 可仅本地继续做解析预览：{closeout_counters['can_continue_local_only_count']} 所。",
        "- 进入 canonical/ML 的学校数：0。",
        "",
        "## 人工批准队列",
        "",
    ]
    for row in approval_rows:
        lines.extend(
            [
                f"### {row['approval_rank']}. {row['school_name']}",
                "",
                f"- 优先级：`{row['approval_priority']}`。",
                f"- 批准类型：`{row['approval_request_type']}`。",
                f"- 当前阻塞：`{row['current_blocker']}`。",
                f"- 批准范围：{row['approval_scope']}。",
                f"- 禁止事项：{row['forbidden_even_if_approved']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 产物",
            "",
            f"- `{CLOSEOUT_OUT.relative_to(ROOT)}`",
            f"- `{APPROVAL_OUT.relative_to(ROOT)}`",
            f"- `{CLOSEOUT_ROLLUP.relative_to(ROOT)}`",
            f"- `{APPROVAL_ROLLUP.relative_to(ROOT)}`",
            f"- `{Path(__file__).relative_to(ROOT)}`",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {CLOSEOUT_OUT}")
    print(f"Wrote {APPROVAL_OUT}")
    print(f"Wrote {CLOSEOUT_ROLLUP}")
    print(f"Wrote {APPROVAL_ROLLUP}")
    print(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
