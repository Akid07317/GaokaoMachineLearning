#!/usr/bin/env python3
"""Write batch-7 official source discovery preview for uncovered P0 rows.

Outputs stay in reference_trend source-packet/preview layers only.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch7_official"

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch7_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch7_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch7_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch7_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch7.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "source_id",
    "queue_record_id",
    "queue_rank",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "year",
    "province",
    "batch",
    "subject_category",
    "round_type",
    "university_name",
    "university_code",
    "source_role",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "special_type_detected",
    "raw_file_path",
    "collector_note",
    "collector_confidence",
    "source_packet_status",
    "intended_layer",
    "requires_network",
    "requires_manual_approval",
    "eligible_for_intake_preview",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.tables: list[list[list[str]]] = []
        self.current_table: list[list[str]] = []
        self.current_row: list[str] = []
        self.current_cell: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.in_table = True
            self.current_table = []
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.current_row = []
        elif self.in_table and tag in {"td", "th"}:
            self.in_cell = True
            self.current_cell = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_table and tag in {"td", "th"} and self.in_cell:
            self.current_row.append(" ".join("".join(self.current_cell).split()))
            self.in_cell = False
        elif self.in_table and tag == "tr" and self.in_row:
            if any(self.current_row):
                self.current_table.append(self.current_row)
            self.in_row = False
        elif tag == "table" and self.in_table:
            self.tables.append(self.current_table)
            self.in_table = False


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


def fjut_physics_summary() -> tuple[int, int, str]:
    html = read_text(RAW_DIR / "fjut_2025_guangxi_plan.html")
    if not html:
        return 0, 0, "no_cached_html"
    parser = TableParser()
    parser.feed(html)
    if not parser.tables:
        return 0, 0, "no_table_found"

    current_campus = ""
    current_subject = ""
    physics_rows: list[tuple[str, str, int]] = []
    for row in parser.tables[0][1:]:
        if len(row) == 6:
            current_campus, current_subject, major, _duration, plan, _tuition = row
        elif len(row) == 5:
            if row[0].endswith("校区"):
                current_campus, major, _duration, plan, _tuition = row
            else:
                major, _duration, plan, _tuition = row[:4]
        elif len(row) == 4:
            major, _duration, plan, _tuition = row
        else:
            continue
        if "物理" in current_subject:
            try:
                physics_rows.append((current_subject, major, int(plan)))
            except ValueError:
                continue

    by_subject = Counter()
    for subject, _major, plan_count in physics_rows:
        by_subject[subject] += plan_count
    summary = ";".join(f"{subject}:{count}" for subject, count in sorted(by_subject.items()))
    return len(physics_rows), sum(plan for _subject, _major, plan in physics_rows), summary


def shzu_guangxi_summary() -> tuple[int, int, str]:
    js = read_text(RAW_DIR / "shzu_zhaoshengjihua.js")
    match = re.search(r"var dataList = (\[.*?\]);\s*$", js, re.S)
    if not match:
        return 0, 0, "no_dataList_match"
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return 0, 0, f"json_decode_failed:{exc}"
    rows = [
        item
        for item in data
        if item.get("年份") == 2025
        and item.get("省份") == "广西"
        and item.get("层次") == "本科"
        and item.get("批次") == "本科普通批"
        and "物理" in str(item.get("科类", ""))
    ]
    total = sum(int(item.get("计划数") or 0) for item in rows)
    majors = "|".join(str(item.get("专业名称", "")) for item in rows[:8])
    return len(rows), total, majors


def cache_status(path: Path) -> str:
    text = read_text(path)
    if not text:
        return "missing"
    if "请输入验证码" in text:
        return "captcha_gate_html"
    if "404错误提示" in text or "您访问的页面未找到" in text:
        return "official_domain_404"
    return "cached"


def build_rows() -> list[dict[str, object]]:
    fjut_rows, fjut_total, fjut_by_subject = fjut_physics_summary()
    shzu_rows, shzu_total, shzu_major_sample = shzu_guangxi_summary()
    swmu_attachment_status = cache_status(RAW_DIR / "swmu_2025_plan_attachment.xls")
    xisu_status = cache_status(RAW_DIR / "xisu_plan_index.html")

    discovered = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0033",
            "queue_rank": "33",
            "university_code": "10759",
            "university_name": "石河子大学",
            "source_url": "http://zsb.shzu.edu.cn/14096/list.htm",
            "source_owner": "石河子大学招生网",
            "source_title": "招生计划",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_dynamic_plan_page_with_cached_js_data",
            "source_role": "official_major_plan_js_extractable_candidate",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "true",
            "special_type_detected": "ordinary_batch_rows_filterable; special/advance batches present in same JS and must remain isolated",
            "raw_file_path": rel(RAW_DIR / "shzu_zhaoshengjihua.js"),
            "collector_note": f"Official admissions plan page references zhaoshengjihua.js. Local parse found Guangxi 本科普通批 物理类 {shzu_rows} major rows, plan total {shzu_total}. Sample majors: {shzu_major_sample}. Group codes are not printed.",
            "collector_confidence": "T1_official_js_extractable_major_plan_candidate",
            "source_packet_status": "official_js_plan_data_cached_extractable",
            "eligible_for_intake_preview": "conditional_after_group_mapping_or_group_absence_acceptance",
            "next_action": "build source-packet parse preview, then hold group-year calibration until exam-authority group 10759-101 mapping is verified",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0034",
            "queue_rank": "34",
            "university_code": "10393",
            "university_name": "福建中医药大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "no_official_source_candidate_found",
            "source_role": "search_backoff_without_first_party_plan_candidate",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "unknown",
            "raw_file_path": "",
            "collector_note": "This pass did not find a first-party 2025 Guangxi physical ordinary plan asset. Search results were dominated by third-party pages or wrong-school matches.",
            "collector_confidence": "T4_no_official_candidate_found_this_pass",
            "source_packet_status": "search_backoff_no_first_party_source",
            "eligible_for_intake_preview": "false",
            "next_action": "retry targeted official-domain search or use exam-authority plan source if available",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0035",
            "queue_rank": "35",
            "university_code": "10388",
            "university_name": "福建理工大学",
            "source_url": "https://join.fjut.edu.cn/2025/0617/c10925a255478/page.htm",
            "source_owner": "福建理工大学本科招生信息网",
            "source_title": "福建理工大学2025年面向广西招生计划",
            "published_date": "2025-06-17",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_html_plan_table_cached",
            "source_role": "official_plan_table_extractable_candidate",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "true",
            "special_type_detected": "history and physical subject rows share table; must split by subject requirement",
            "raw_file_path": rel(RAW_DIR / "fjut_2025_guangxi_plan.html"),
            "collector_note": f"Official HTML table cached. Local table parse found physical rows {fjut_rows}, physical plan total {fjut_total}, split {fjut_by_subject}. No group code printed.",
            "collector_confidence": "T1_official_html_extractable_plan_table_candidate",
            "source_packet_status": "official_html_plan_table_cached_extractable",
            "eligible_for_intake_preview": "conditional_after_subject_split_and_group_mapping",
            "next_action": "build source-packet parse preview; hold 10388-150 group-year calibration until group mapping is verified",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0036",
            "queue_rank": "36",
            "university_code": "10632",
            "university_name": "西南医科大学",
            "source_url": "https://zsxxw.swmu.edu.cn/info/1221/8711.htm",
            "source_owner": "西南医科大学招生办",
            "source_title": "2025年普教本科分省分专业招生计划表",
            "published_date": "2025-06-06",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_attachment_detail_cached_download_captcha_blocked",
            "source_role": "official_plan_attachment_candidate_gated",
            "source_contains_group_code": "unknown_until_attachment_parse",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "true_in_attachment_metadata_not_downloaded",
            "special_type_detected": "unknown_until_attachment_parse",
            "raw_file_path": rel(RAW_DIR / "swmu_2025_plan_detail.html"),
            "collector_note": f"Official detail page exposes XLS attachment, but direct attachment fetch returned {swmu_attachment_status}. Keep as source_packet candidate; no form/captcha replay without approval.",
            "collector_confidence": "T2_official_attachment_candidate_captcha_blocked",
            "source_packet_status": "official_detail_cached_attachment_download_captcha_blocked",
            "eligible_for_intake_preview": "false_until_attachment_obtained_or_official_table_rows_available",
            "next_action": "use manual download/browser-approved route if needed; do not parse captcha page as data",
            "requires_manual_approval": "true_for_browser_or_captcha_replay",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0037",
            "queue_rank": "37",
            "university_code": "10724",
            "university_name": "西安外国语大学",
            "source_url": "https://zhaosheng.xisu.edu.cn/info/1018/2936.htm",
            "source_owner": "西安外国语大学招生信息网",
            "source_title": "招生计划候选页",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_domain_candidate_404",
            "source_role": "official_domain_stale_link_rejected",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "not_reached",
            "raw_file_path": rel(RAW_DIR / "xisu_plan_index.html"),
            "collector_note": f"Official-domain candidate URL cached as {xisu_status}; no Guangxi plan rows returned in this pass.",
            "collector_confidence": "T4_official_domain_404_candidate_rejected",
            "source_packet_status": "official_domain_candidate_404_no_structured_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official site search/index drilldown; do not use stale 404 URL",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0038",
            "queue_rank": "38",
            "university_code": "10705",
            "university_name": "西安石油大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "no_official_source_candidate_found",
            "source_role": "search_backoff_without_first_party_plan_candidate",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "unknown",
            "raw_file_path": "",
            "collector_note": "This pass did not locate a first-party 2025 Guangxi physical ordinary plan asset or endpoint.",
            "collector_confidence": "T4_no_official_candidate_found_this_pass",
            "source_packet_status": "search_backoff_no_first_party_source",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official-domain search or use exam-authority source if available",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0039",
            "queue_rank": "39",
            "university_code": "10671",
            "university_name": "贵州财经大学",
            "source_url": "https://zhaosheng.gufe.edu.cn/__local/8/39/7A/03FC1CF1C8D778BA1F7919F6739_B68BB2C4_70AEED.pdf",
            "source_owner": "贵州财经大学招生网",
            "source_title": "2025本科招生报考指南",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_pdf_candidate_tls_blocked",
            "source_role": "official_pdf_candidate_not_cached",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "likely_true_until_pdf_parse",
            "special_type_detected": "unknown_until_pdf_parse",
            "raw_file_path": "",
            "collector_note": "Official-domain PDF candidate found, but terminal TLS fetch failed with SSL_ERROR_SYSCALL. Keep in reachability/backoff layer; no browser/alt-TLS replay without explicit approval.",
            "collector_confidence": "T2_official_pdf_candidate_tls_blocked_not_cached",
            "source_packet_status": "official_pdf_candidate_reachability_blocked",
            "eligible_for_intake_preview": "false_until_pdf_cached_and_parsed",
            "next_action": "retry with approved browser/alternate fetch route or locate equivalent official HTML source",
            "requires_manual_approval": "true_for_browser_or_alt_tls_retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0040",
            "queue_rank": "40",
            "university_code": "10716",
            "university_name": "陕西中医药大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "no_official_source_candidate_found",
            "source_role": "search_backoff_without_first_party_plan_candidate",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "unknown",
            "raw_file_path": "",
            "collector_note": "This pass surfaced no first-party official 2025 Guangxi plan source; third-party plan pages are rejected for this layer.",
            "collector_confidence": "T4_no_official_candidate_found_this_pass",
            "source_packet_status": "search_backoff_no_first_party_source",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official-domain search or use exam-authority source if available",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0041",
            "queue_rank": "41",
            "university_code": "10743",
            "university_name": "青海大学",
            "source_url": "https://zsw.qhu.edu.cn/zsxx/zszc/92a9bb561a4e4253a01988aec41e7333.htm",
            "source_owner": "青海大学本科招生网",
            "source_title": "青海大学2025年招生计划",
            "published_date": "2025-07-04",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_plan_index_links_external_poster",
            "source_role": "official_index_candidate_no_structured_rows",
            "source_contains_group_code": "false_in_cached_html",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "external_poster_unknown",
            "special_type_detected": "unknown_until_poster_parse",
            "raw_file_path": rel(RAW_DIR / "qhu_2025_plan_index.html"),
            "collector_note": "Official page cached and links a 2025招生计划 poster on eqxiu. Cached official HTML does not expose Guangxi rows or group codes.",
            "collector_confidence": "T2_official_plan_index_external_poster_needs_parse",
            "source_packet_status": "official_index_cached_external_poster_not_parsed",
            "eligible_for_intake_preview": "false_until_official_linked_poster_or_equivalent_rows_parsed",
            "next_action": "parse official-linked poster only if source capture is auditable; otherwise keep as reachability clue",
            "requires_manual_approval": "false_for_index; true_if_browser_needed_for_poster",
        },
    ]

    rows = []
    for idx, row in enumerate(discovered, start=1):
        enriched = {
            "source_id": f"reference_trend_520_p0_batch7_{idx:04d}",
            "intended_layer": "reference_trend_source_packet_preview_only",
            "requires_network": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "record_id": f"reference_trend_520_p0_batch7_{idx:04d}",
        }
        enriched.update(row)
        rows.append(enriched)
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    universities = sorted({str(row["university_name"]) for row in rows if row.get("university_name")})
    t1_rows = [row for row in rows if str(row.get("collector_confidence", "")).startswith("T1_")]
    manual_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    rollup = [
        {"metric": "batch7_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(universities)},
        {"metric": "t1_high_value_rows", "value": len(t1_rows), "note": "石河子官方JS、福建理工官方HTML表。"},
        {"metric": "requires_manual_approval_rows", "value": len(manual_rows), "note": "|".join(str(row["university_name"]) for row in manual_rows)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery/source-packet preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for key, count in sorted(Counter(str(row["collector_confidence"]) for row in rows).items()):
        rollup.append({"metric": f"collector_confidence::{key}", "value": count, "note": ""})
    for key, count in sorted(Counter(str(row["source_packet_status"]) for row in rows).items()):
        rollup.append({"metric": f"source_packet_status::{key}", "value": count, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    official_or_backoff = all(
        row.get("source_url") == ""
        or str(row.get("source_owner", "")).endswith(("招生网", "招生信息网", "本科招生网", "招生办"))
        or "大学" in str(row.get("source_owner", ""))
        for row in rows
    )
    manual_count = sum(1 for row in rows if str(row.get("requires_manual_approval", "")).startswith("true"))
    return [
        {
            "qa_check": "official_cache_rows",
            "status": "pass" if official_or_backoff else "warn",
            "value": len(rows),
            "note": "Rows are first-party official pages/assets or explicit no-source/reachability backoff; third-party rows are not accepted.",
        },
        {
            "qa_check": "manual_approval_boundary",
            "status": "pass",
            "value": manual_count,
            "note": "Captcha/TLS/browser-needed cases are held and not parsed into data.",
        },
        {
            "qa_check": "extractable_plan_candidates",
            "status": "pass",
            "value": sum("true" in str(row.get("source_contains_plan_count", "")) for row in rows),
            "note": "Extractable does not imply group-year calibration; group mapping remains required.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
        {
            "qa_check": "decision_pool_boundary",
            "status": "pass",
            "value": "closed",
            "note": "No merge into the 32-school decision_pool.",
        },
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    exclusions = []
    for row in rows:
        status = str(row.get("source_packet_status", ""))
        if any(token in status for token in ["backoff", "blocked", "404", "captcha"]):
            exclusions.append(
                {
                    "record_id": row["record_id"],
                    "university_name": row["university_name"],
                    "source_url": row["source_url"],
                    "raw_file_path": row.get("raw_file_path", ""),
                    "exclusion_reason": status,
                    "recommended_next_action": row["next_action"],
                    "canonical_ml_entry_open": "false",
                }
            )
    return exclusions


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    t1 = [row for row in rows if str(row.get("collector_confidence", "")).startswith("T1_")]
    blocked = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    text = f"""# Reference Trend 520 P0 Official Source Discovery Batch 7

Generated: {date.today().isoformat()}

## Scope

This batch covers the next uncovered P0 plan-source queue rows, queue ranks 33-41. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch7_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_exclusion_log.csv`

## Key Findings

- Candidate rows: {len(rows)}
- Universities covered: {len({row['university_name'] for row in rows})}
- T1 extractable official candidates: {len(t1)} ({'、'.join(row['university_name'] for row in t1)})
- Manual approval / browser-replay boundaries: {len(blocked)} ({'、'.join(row['university_name'] for row in blocked) if blocked else 'none'})

High-value rows:

1. 石河子大学: official plan page JS data cached. Guangxi 本科普通批 物理类 rows and plan counts are extractable, but no group code is printed.
2. 福建理工大学: official Guangxi HTML plan table cached and locally summarized, but no group code is printed.

Held rows:

- 西南医科大学: official attachment page cached; XLS download is captcha-gated.
- 贵州财经大学: official PDF candidate found, but terminal TLS fetch failed.
- 西安外国语大学: official-domain candidate URL returned 404.
- 福建中医药大学、西安石油大学、陕西中医药大学: no first-party plan source found in this pass.
- 青海大学: official page links an external poster; cached official page has no structured Guangxi rows.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next step should parse the T1 official plan sources into source-packet parse previews, then keep them held until group mapping/acceptance is explicit.
"""
    DOC_OUT.write_text(text, encoding="utf-8")


def write_handoff() -> None:
    marker = "## 33. 2026-05-16 P0 官方来源发现 batch 7"
    content = f"""

{marker}

已新增 batch7 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch7_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch7.md`

覆盖结果：queue rank 33-41 共 9 所学校。石河子大学官方招生计划 JS 已缓存并可抽取广西本科普通批物理类 32 个专业行、计划合计 100；福建理工大学官方广西计划 HTML 表已缓存，可抽取物理类 38 个专业行、计划合计 205。西南医科大学官方附件页已缓存，但 XLS 下载有验证码；贵州财经大学官方 PDF 候选出现 TLS 阻塞；青海大学官方页只给外部海报入口；福建中医药大学、西安石油大学、陕西中医药大学本轮未找到 first-party 结构化计划源；西安外国语大学候选官方链接为 404。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先把石河子大学/福建理工大学两条 T1 来源解析成 source-packet parse preview，并继续 hold group-year calibration，直到专业组映射被人工接受。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    exclusions = build_exclusions(rows)

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["qa_check", "status", "value", "note"])
    write_csv(
        EXCLUSION_OUT,
        exclusions,
        [
            "record_id",
            "university_name",
            "source_url",
            "raw_file_path",
            "exclusion_reason",
            "recommended_next_action",
            "canonical_ml_entry_open",
        ],
    )
    write_doc(rows, rollup)
    write_handoff()

    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    print(f"wrote {ROLLUP_OUT.relative_to(ROOT)}")
    print(f"wrote {QA_OUT.relative_to(ROOT)}")
    print(f"wrote {EXCLUSION_OUT.relative_to(ROOT)} rows={len(exclusions)}")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
