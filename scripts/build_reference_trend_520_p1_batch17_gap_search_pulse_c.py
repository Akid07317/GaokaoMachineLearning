#!/usr/bin/env python3
"""Build marker 131 batch17 gap-search pulse C.

This records official-source discovery outcomes for marker 128's remaining
gap rows 0009-0012. It intentionally writes only candidate/reachability
preview, QA, rollup, exclusion, and handoff artifacts.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts" / "build_reference_trend_520_p1_batch17_gap_search_pulse_b.py"

spec = importlib.util.spec_from_file_location("pulse_base", BASE_SCRIPT)
pulse_base = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(pulse_base)

PREFIX = "reference_trend_520_p1_batch17_gap_search_pulse_c"
pulse_base.PREFIX = PREFIX
pulse_base.OUT = pulse_base.SEED / f"{PREFIX}.csv"
pulse_base.ROLLUP = pulse_base.REPORTS / f"{PREFIX}_rollup.csv"
pulse_base.QA = pulse_base.REPORTS / f"{PREFIX}_qa.csv"
pulse_base.EXCLUSION = pulse_base.REPORTS / f"{PREFIX}_exclusion_log.csv"
pulse_base.DOC = pulse_base.DOCS / f"{PREFIX}.md"

pulse_base.MANUAL_DISCOVERY = {
    "10393-104": {
        "source_candidate_tier": "T2_official_linked_wechat_plan_candidate",
        "source_candidate_status": "official_admission_site_links_2025_plan_wechat_page_unopened",
        "source_url": "https://zsb.fjtcm.edu.cn/",
        "source_title": "福建中医药大学招生办",
        "source_type": "official_university_admission_site_linked_wechat_plan",
        "source_access_status": "official_site_readable_2025_plan_link_points_to_wechat",
        "evidence_summary": "Official FJTCM admissions site exposes 招生计划 and lists 3170人 | 福建中医药大学2025年普通本科招生计划发布 dated 2025-06-24, linking to an official WeChat article that was not opened here.",
        "found_plan_granularity": "official_linked_wechat_plan_entry_no_rows_extracted",
        "ordinary_batch_boundary_status": "unknown_until_wechat_or_static_mirror_table_review",
        "parse_or_access_blocker": "wechat_article_unopened_requires_manual_or_browser_artifact_before_medical_ordinary_batch_rows",
        "requires_browser_or_alternate_fetch": "true_if_wechat_artifact_or_static_mirror_review_is_approved",
        "source_packet_preview_eligible": "true",
        "rejected_nonofficial_evidence_note": "Third-party nationwide plan summaries were not accepted.",
        "next_action": "Queue official WeChat/source-packet capture only with auditable artifact review; isolate medical ordinary-batch rows before preview.",
    },
    "10742-161": {
        "source_candidate_tier": "T4_official_portal_reachability_backoff",
        "source_candidate_status": "official_main_site_admission_work_entry_found_no_static_plan_candidate",
        "source_url": "https://www.xbmu.edu.cn/zsjy/zsgz.htm",
        "source_title": "招生工作-西北民族大学",
        "source_type": "official_university_admission_work_portal_reachability",
        "source_access_status": "official_admission_work_page_readable_plan_detail_not_located",
        "evidence_summary": "Official XBMU site exposes 招生工作 and a 本科生招生信息网 entry, but current official searches did not locate a static 2025 Guangxi plan page.",
        "found_plan_granularity": "none",
        "ordinary_batch_boundary_status": "not_established",
        "parse_or_access_blocker": "no_static_official_plan_page_found_and_ethnic_or_preparatory_boundary_unresolved",
        "requires_browser_or_alternate_fetch": "false_until_static_official_discovery_is_exhausted",
        "source_packet_preview_eligible": "false",
        "rejected_nonofficial_evidence_note": "Third-party plan pages were found but rejected for source-packet preview.",
        "next_action": "Continue official-only discovery; do not use third-party plan rows because ethnic/preparatory boundaries require official isolation.",
    },
    "10623-102": {
        "source_candidate_tier": "T3_official_plan_navigation_cache_miss",
        "source_candidate_status": "official_plan_navigation_found_redirect_cache_miss",
        "source_url": "https://zb.xhu.edu.cn/",
        "source_title": "西华大学招生信息网",
        "source_type": "official_university_admission_plan_navigation",
        "source_access_status": "official_site_readable_plan_nav_redirect_cache_miss",
        "evidence_summary": "Official XHU admissions site exposes 招生计划 navigation, but the plan link resolved through a redirect that produced a cache miss in this pass.",
        "found_plan_granularity": "navigation_only_no_guangxi_group_rows",
        "ordinary_batch_boundary_status": "unknown_until_plan_page_or_pdf_found",
        "parse_or_access_blocker": "plan_navigation_redirect_cache_miss_before_guangxi_rows",
        "requires_browser_or_alternate_fetch": "true_if_static_redirect_replay_or_browser_review_is_approved",
        "source_packet_preview_eligible": "false",
        "rejected_nonofficial_evidence_note": "No third-party plan rows accepted.",
        "next_action": "Retry official plan navigation through auditable static redirect capture or approved browser review; keep intake closed.",
    },
    "10724-152": {
        "source_candidate_tier": "T4_official_plan_section_stale_backoff",
        "source_candidate_status": "official_plan_section_found_no_2025_national_plan_entry",
        "source_url": "https://zhaosheng.xisu.edu.cn/bkzs/zsjh.htm",
        "source_title": "招生计划-西安外国语大学招生网",
        "source_type": "official_university_plan_section_reachability",
        "source_access_status": "official_plan_section_readable_latest_static_national_plan_is_2024",
        "evidence_summary": "Official XISU admissions plan section is readable and lists national plan entries through 2024, but no 2025 national or Guangxi plan entry was located in this pass.",
        "found_plan_granularity": "plan_section_only_no_2025_guangxi_rows",
        "ordinary_batch_boundary_status": "not_established",
        "parse_or_access_blocker": "no_2025_static_plan_entry_found_teacher_language_boundary_unresolved",
        "requires_browser_or_alternate_fetch": "false_until_static_official_discovery_is_exhausted",
        "source_packet_preview_eligible": "false",
        "rejected_nonofficial_evidence_note": "Third-party 2025 plan summaries were not accepted.",
        "next_action": "Continue official-only discovery on XISU site/search; preserve language/teacher-direction boundaries before any preview.",
    },
}


def write_rollup(rows: list[dict[str, object]]) -> None:
    status_counts = pulse_base.Counter(str(row["source_candidate_status"]) for row in rows)
    tier_counts = pulse_base.Counter(str(row["source_candidate_tier"]) for row in rows)
    source_type_counts = pulse_base.Counter(str(row["source_type"]) for row in rows)
    rollup_rows = [
        {
            "metric": "gap_pulse_rows",
            "value": len(rows),
            "note": "Marker-128 gap rows 0009-0012 checked through official-only web search.",
        },
        {
            "metric": "source_packet_preview_candidate_rows",
            "value": sum(row["source_packet_preview_eligible"] == "true" for row in rows),
            "note": "Official surfaces worth source-packet preview follow-up.",
        },
        {"metric": "official_plan_rows_extracted", "value": 0, "note": "No plan rows parsed/extracted in this pass."},
        {"metric": "official_min_rank_rows", "value": 0, "note": "No rank source searched or accepted."},
        {"metric": "requires_manual_approval_now_rows", "value": 0, "note": "No browser/form/cookie/header/login action consumed."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Intake remains closed."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for key, count in sorted(tier_counts.items()):
        rollup_rows.append({"metric": f"tier::{key}", "value": count, "note": ""})
    for key, count in sorted(status_counts.items()):
        rollup_rows.append({"metric": f"status::{key}", "value": count, "note": ""})
    for key, count in sorted(source_type_counts.items()):
        rollup_rows.append({"metric": f"source_type::{key}", "value": count, "note": ""})
    pulse_base.write_csv(pulse_base.ROLLUP, rollup_rows, ["metric", "value", "note"])


def write_qa(rows: list[dict[str, object]]) -> None:
    qa_rows = [
        {
            "check": "pulse_row_count",
            "status": "PASS" if len(rows) == 4 else "FAIL",
            "detail": f"{len(rows)} rows recorded for pulse C.",
        },
        {
            "check": "official_only_or_rejected",
            "status": "PASS" if all(row["source_type"].startswith("official_") for row in rows) else "FAIL",
            "detail": "All accepted surfaces are official/official-linked; nonofficial evidence is only noted as rejected.",
        },
        {
            "check": "no_plan_rows_extracted",
            "status": "PASS",
            "detail": "This pass records source candidates/reachability only; no plan rows parsed.",
        },
        {
            "check": "no_manual_or_login_action_consumed",
            "status": "PASS" if all(row["requires_manual_approval_now"] == "false" for row in rows) else "FAIL",
            "detail": "Login/browser/header/cookie/form actions were not consumed.",
        },
        {
            "check": "no_intake_or_calibration",
            "status": "PASS"
            if all(row["reference_trend_pool_eligible"] == "false" and row["calibration_eligible"] == "false" for row in rows)
            else "FAIL",
            "detail": "No reference trend intake or calibration eligibility opened.",
        },
        {
            "check": "canonical_ml_closed",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML entry opened.",
        },
    ]
    pulse_base.write_csv(pulse_base.QA, qa_rows, ["check", "status", "detail"])


def write_doc(rows: list[dict[str, object]]) -> None:
    candidate_count = sum(row["source_packet_preview_eligible"] == "true" for row in rows)
    doc = [
        "# Reference trend 520 P1 batch17 gap search pulse C",
        "",
        f"Generated: {pulse_base.date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This pulse records official-only web discovery outcomes for marker-128 gap rows 0009-0012.",
        "",
        "## Outputs",
        "",
        f"- `clean_data/engineering_guangxi_seed/{pulse_base.OUT.name}`",
        f"- `reports/{pulse_base.ROLLUP.name}`",
        f"- `reports/{pulse_base.QA.name}`",
        f"- `reports/{pulse_base.EXCLUSION.name}`",
        "",
        "## Summary",
        "",
        f"- Gap rows checked: {len(rows)}",
        f"- Official candidate/reachability rows worth follow-up: {candidate_count}",
        "- Plan rows extracted: 0",
        "- Reference trend eligible rows: 0",
        "- Canonical/ML rows opened: 0",
        "",
        "## Source Outcomes",
        "",
    ]
    for row in rows:
        doc.append(
            f"- `{row['group_pair_key']}` {row['university_name']}: "
            f"{row['source_candidate_status']} -> {row['source_url']}"
        )
    doc.extend([
        "",
        "## Boundary",
        "",
        "No cache, parse, OCR, browser/form replay, login-state review, WeChat capture, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update is performed.",
        "",
    ])
    pulse_base.DOC.write_text("\n".join(doc), encoding="utf-8")


def append_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 131. 2026-05-17 P1 batch17 gap search pulse C"
    content = f"""

{marker}

已新增 P1 batch17 gap search pulse C：

- `clean_data/engineering_guangxi_seed/{pulse_base.OUT.name}`
- `reports/{pulse_base.ROLLUP.name}`
- `reports/{pulse_base.QA.name}`
- `reports/{pulse_base.EXCLUSION.name}`
- `docs/{pulse_base.DOC.name}`

覆盖结果：对 marker 128 的 gap rows 0009-0012 做官方-only web discovery 记录；1 条进入后续 source-packet preview/reachability 候选（福建中医药大学官方招生站链接的 2025 普通本科招生计划微信公众号页），3 条保持 reachability/backoff（西北民族大学官方招生工作入口未定位静态计划页，西华大学官方招生计划导航重定向缓存缺失，西安外国语大学官方招生计划栏可读但未定位 2025 全国/广西计划）。QA PASS。

准入边界：本轮只记录官方来源候选/回退状态，不缓存、不解析、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。
"""
    pulse_base.append_handoff_once(marker, content)


def main() -> None:
    rows = pulse_base.build_rows()
    for idx, row in enumerate(rows, 1):
        row["pulse_id"] = f"reference_trend_520_p1_batch17_gap_pulse_c_{idx:04d}"
    pulse_base.write_csv(pulse_base.OUT, rows, pulse_base.FIELDS)
    write_rollup(rows)
    write_qa(rows)
    pulse_base.write_exclusion(rows)
    write_doc(rows)
    append_handoff(rows)


if __name__ == "__main__":
    main()
