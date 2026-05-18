#!/usr/bin/env python3
"""Build DGUT official reachability preview for 2025 plan source.

The Dongguan University of Technology admissions portal is reachable and lists a
2025 undergraduate enrollment plan item. The target for the 2025 item is a
WeChat article, and a school-subdomain announcement exposes a shortlink for the
same plan. This script records that official-source chain and keeps the row out
of reference_trend/canonical/ML until a browser/manual capture of the external
article or a first-party structured page is approved.
"""

from __future__ import annotations

import csv
import html
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "p0_official_drilldown"

RAW_PORTAL = RAW_DIR / "dgut_zsb_plan_portal.html"
RAW_ANNOUNCEMENT = RAW_DIR / "dgut_ee_2025_plan_announcement.html"
OUT = SEED_DIR / "reference_trend_520_p0_dgut_reachability_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_dgut_reachability_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_dgut_reachability_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_dgut_reachability_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_dgut_reachability_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PORTAL_URL = "https://zsb.dgut.edu.cn/bkszs/zsjh/"
ANNOUNCEMENT_URL = "https://ee.dgut.edu.cn/info/1061/25990.htm"
SOURCE_ID = "reference_trend_520_web_candidate_0004"
QUEUE_RECORD_ID = "reference_trend_520_plan_source_queue_0003"

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
    "official_portal_2025_item_title",
    "official_portal_2025_item_url",
    "school_subdomain_announcement_url",
    "school_subdomain_shortlink",
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def clean_text(text: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def extract_2025_item(portal_html: str) -> tuple[str, str]:
    # The portal list contains title and href near each other; keep the regex
    # narrow so we only capture the 2025 plan list item.
    pattern = re.compile(
        r'<a\s+class="text db"\s+href="(?P<href>[^"]+)"[^>]*title="(?P<title>[^"]*2025[^"]*本科招生计划[^"]*)"',
        re.S,
    )
    match = pattern.search(portal_html)
    if not match:
        return "", ""
    return html.unescape(match.group("title")), html.unescape(match.group("href")).replace("&amp;", "&")


def extract_shortlink(announcement_html: str) -> str:
    match = re.search(r'<META\s+Name="description"\s+Content="(https?://[^"]+)"', announcement_html, re.I)
    return html.unescape(match.group(1)) if match else ""


def build_rows() -> list[dict[str, object]]:
    portal_html = read_text(RAW_PORTAL)
    announcement_html = read_text(RAW_ANNOUNCEMENT)
    item_title, item_url = extract_2025_item(portal_html)
    shortlink = extract_shortlink(announcement_html)
    raw_paths = "|".join(rel(path) for path in [RAW_PORTAL, RAW_ANNOUNCEMENT] if path.exists())
    note = (
        "Official admissions portal lists the 2025 undergraduate enrollment plan, "
        "but the item targets a WeChat article; a school-subdomain announcement "
        "also exposes only a shortlink. Structured Guangxi physical plan rows "
        "require manual/browser capture or a first-party structured page."
    )
    return [
        {
            "record_id": "reference_trend_520_p0_dgut_reachability_group_101",
            "source_id": SOURCE_ID,
            "queue_record_id": QUEUE_RECORD_ID,
            "queue_rank": "3",
            "university_code": "11819",
            "university_name": "东莞理工学院",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "group_code": "101",
            "rank_2024": "38700",
            "rank_2025": "27014",
            "rank_delta_2025_minus_2024": "-11686",
            "trend_direction": "hotter_or_higher_selectivity",
            "source_url": PORTAL_URL,
            "source_owner": "东莞理工学院招生信息网",
            "source_title": "招生计划_招生信息网",
            "raw_file_paths": raw_paths,
            "official_portal_2025_item_title": item_title,
            "official_portal_2025_item_url": item_url,
            "school_subdomain_announcement_url": ANNOUNCEMENT_URL,
            "school_subdomain_shortlink": shortlink,
            "source_contains_group_code": "unknown_until_manual_or_browser_capture",
            "source_contains_plan_count": "unknown_until_manual_or_browser_capture",
            "source_contains_min_score": "false_not_a_score_source",
            "source_contains_min_rank": "false_not_a_score_source",
            "source_packet_status": "official_portal_cached_social_article_or_shortlink_hold_for_manual_approval",
            "collector_confidence": "T2_official_portal_lists_2025_plan_external_article_not_structured",
            "requires_manual_approval": "true",
            "approval_required_for": "wechat_or_shortlink_browser_capture_or_first_party_structured_page_discovery",
            "eligible_for_intake_preview": "false_until_structured_plan_rows_cached_and_QA",
            "reference_trend_pool_eligible": "0",
            "calibration_eligible": "0",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "next_action": "ask_user_approval_for_browser_capture_of_official_wechat_or_shortlink; alternatively locate first-party structured html/pdf/xlsx plan page",
            "evidence_note": note,
        }
    ]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    row = rows[0]
    return [
        {"metric": "official_plan_portal_cached", "value": 1 if RAW_PORTAL.exists() else 0, "note": rel(RAW_PORTAL)},
        {"metric": "school_subdomain_announcement_cached", "value": 1 if RAW_ANNOUNCEMENT.exists() else 0, "note": rel(RAW_ANNOUNCEMENT)},
        {"metric": "queue_records_covered", "value": len(rows), "note": "group 101"},
        {"metric": "official_2025_plan_item_found", "value": 1 if row["official_portal_2025_item_url"] else 0, "note": row["official_portal_2025_item_title"]},
        {"metric": "external_wechat_target_found", "value": 1 if "mp.weixin.qq.com" in str(row["official_portal_2025_item_url"]) else 0, "note": "manual/browser capture required"},
        {"metric": "school_shortlink_found", "value": 1 if row["school_subdomain_shortlink"] else 0, "note": row["school_subdomain_shortlink"]},
        {"metric": "manual_approval_required_rows", "value": 1, "note": "external article/shortlink capture required before structured rows"},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No structured plan rows fetched."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan source only; no score/rank rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    row = rows[0]
    return [
        {"check": "official_plan_portal_cached", "status": "PASS" if RAW_PORTAL.exists() else "FAIL", "detail": rel(RAW_PORTAL)},
        {"check": "school_subdomain_announcement_cached", "status": "PASS" if RAW_ANNOUNCEMENT.exists() else "FAIL", "detail": rel(RAW_ANNOUNCEMENT)},
        {"check": "official_2025_plan_item_found", "status": "PASS" if row["official_portal_2025_item_url"] else "FAIL", "detail": str(row["official_portal_2025_item_url"])},
        {"check": "shortlink_or_external_target_not_auto_parsed", "status": "PASS", "detail": "No WeChat/shortlink/browser capture attempted."},
        {"check": "manual_approval_gate", "status": "PASS" if row["requires_manual_approval"] == "true" else "FAIL", "detail": "Rows require approval before external article or shortlink capture."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS" if row["reference_trend_pool_eligible"] == "0" and row["canonical_ml_entry_open"] == "false" else "FAIL", "detail": "No trend pool/canonical/ML writes."},
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    row = rows[0]
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "group_code": row["group_code"],
            "exclusion_reason": "official_portal_item_targets_external_article_or_shortlink_not_structured",
            "blocked_by": "manual_browser_capture_or_first_party_structured_source_required",
            "excluded_from": "reference_trend_pool|canonical|ML|decision_pool",
            "evidence": row["evidence_note"],
        }
    ]


def build_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, str]]) -> str:
    row = rows[0]
    qa_lines = "\n".join(f"- {item['check']}: {item['status']} - {item['detail']}" for item in qa)
    rollup_lines = "\n".join(f"- {item['metric']}: {item['value']} ({item['note']})" for item in rollup)
    return f"""# reference_trend_520 P0 DGUT official reachability preview

Generated: {date.today().isoformat()}

## Scope

本轮处理东莞理工学院 P0 官方计划来源发现任务。只缓存并审计官方招生计划网与校内官方发布页，不抓取微信文章、不打开短链、不生成 canonical/ML 输入。

## Result

- Official plan portal: {PORTAL_URL}
- Cached portal HTML: `{rel(RAW_PORTAL)}`
- 2025 plan item title: {row['official_portal_2025_item_title']}
- 2025 plan item target: `{row['official_portal_2025_item_url']}`
- School-subdomain announcement: {ANNOUNCEMENT_URL}
- Cached announcement HTML: `{rel(RAW_ANNOUNCEMENT)}`
- Shortlink exposed by announcement: `{row['school_subdomain_shortlink']}`
- Structured Guangxi plan rows: not fetched
- Manual approval required: yes, for WeChat/shortlink browser capture or another first-party structured source

## Outputs

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是当前只有官方入口、外部微信文章目标和短链证据，尚无经批准缓存的 2025 广西物理类本科普通批计划结构化行。

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

    marker = "## 80. 2026-05-16 P0 东莞理工学院 official reachability preview"
    append_handoff_once(
        marker,
        f"""

{marker}

- Cached official portal: `{rel(RAW_PORTAL)}`.
- Cached school-subdomain announcement: `{rel(RAW_ANNOUNCEMENT)}`.
- Output preview: `{rel(OUT)}`.
- QA: `{rel(QA_OUT)}`; rollup: `{rel(ROLLUP_OUT)}`; exclusion log: `{rel(EXCLUSION_OUT)}`.
- Result: official admissions portal lists the 2025 undergraduate plan item, but the target is a WeChat article; school-subdomain announcement exposes a shortlink only. Kept queue row 0003 / group 101 as reachability evidence only.
- Boundary: no structured Guangxi plan rows, no reference_trend_pool eligibility, no canonical/ML, no decision_pool merge. Further progress requires manual approval for browser capture of official WeChat/shortlink or locating a first-party structured HTML/PDF/XLSX source.
""",
    )


if __name__ == "__main__":
    main()
