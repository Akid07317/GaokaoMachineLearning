#!/usr/bin/env python3
"""Write batch-8 official source discovery preview for uncovered P0 rows.

Outputs stay in reference_trend source-packet/preview layers only.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch8_official"

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch8_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch8_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch8_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch8_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch8.md"
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


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


def cache_status(path: Path) -> str:
    text = read_text(path)
    if not text:
        return "missing"
    if "404" in text and ("页面" in text or "Page Not Found" in text):
        return "official_domain_404"
    if "验证码" in text:
        return "captcha_gate_html"
    return "cached"


def csuft_physics_summary() -> tuple[int, int, str, str]:
    paths = [
        RAW_DIR / "csuft_2025_guangxi_plan.html",
        RAW_DIR / "csuft_2025_guangxi_plan_page2.html",
    ]
    rows: list[tuple[str, str, str, int]] = []
    for path in paths:
        html = read_text(path)
        if not html:
            continue
        parser = TableParser()
        parser.feed(html)
        for table in parser.tables:
            for row in table:
                if len(row) < 8:
                    continue
                major = row[1]
                subject = row[4]
                batch = row[5]
                selection = row[6]
                try:
                    plan_count = int(row[7])
                except ValueError:
                    continue
                if subject == "物理类" and batch == "本科普通批":
                    rows.append((major, subject, selection, plan_count))
    selection_counts = Counter(selection for _major, _subject, selection, _plan_count in rows)
    selection_summary = ";".join(f"{key}:{value}" for key, value in sorted(selection_counts.items()))
    major_sample = "|".join(major for major, _subject, _selection, _plan_count in rows[:8])
    return len(rows), sum(plan for _major, _subject, _selection, plan in rows), selection_summary, major_sample


def build_rows() -> list[dict[str, object]]:
    csuft_rows, csuft_total, csuft_selection_summary, csuft_major_sample = csuft_physics_summary()
    sit_status = cache_status(RAW_DIR / "sit_2025_charter.html")
    lixin_status = cache_status(RAW_DIR / "lixin_2025_charter.html")
    zuel_status = cache_status(RAW_DIR / "zuel_2025_charter.html")
    cppu_status = cache_status(RAW_DIR / "cppu_2025_charter.html")
    cafa_status = cache_status(RAW_DIR / "cafa_2025_charter.html")

    discovered = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0042",
            "queue_rank": "42",
            "university_code": "10259",
            "university_name": "上海应用技术大学",
            "source_url": "https://adm.sit.edu.cn/info/1041/1611.htm",
            "source_owner": "上海应用技术大学招生办公室",
            "source_title": "上海应用技术大学2025年秋季统一高考招生章程",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_charter_cached_context_only",
            "source_role": "official_charter_context_not_plan_table",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "ordinary/admission-rule context only; no Guangxi plan rows",
            "raw_file_path": rel(RAW_DIR / "sit_2025_charter.html"),
            "collector_note": f"Official charter cached as {sit_status}. It confirms 2025招生计划由省级招办公布 and Guangxi reform province admission rules, but no Guangxi group/major plan rows are exposed.",
            "collector_confidence": "T3_official_charter_context_only_no_plan_rows",
            "source_packet_status": "official_charter_cached_context_only",
            "eligible_for_intake_preview": "false",
            "next_action": "find first-party分省分专业计划表 or rely on exam-authority group line only; do not infer plan count from charter",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0043",
            "queue_rank": "43",
            "university_code": "11047",
            "university_name": "上海立信会计金融学院",
            "source_url": "https://zsb.lixin.edu.cn/webrecruit/getNewsContent.do?id=08e0a5b6-2ac2-4b06-a500-f6b909737550&type=%E6%8B%9B%E7%94%9F%E4%BF%A1%E6%81%AF",
            "source_owner": "上海立信会计金融学院本专科招生网",
            "source_title": "上海立信会计金融学院2025年秋季招生章程",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_charter_cached_context_only",
            "source_role": "official_charter_context_not_plan_table",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "ordinary/admission-rule context only; no Guangxi plan rows",
            "raw_file_path": rel(RAW_DIR / "lixin_2025_charter.html"),
            "collector_note": f"Official charter cached as {lixin_status}. It only says the 2025分省分专业招生计划以各省级招办公布文件为准; no first-party Guangxi rows were found in this pass.",
            "collector_confidence": "T3_official_charter_context_only_no_plan_rows",
            "source_packet_status": "official_charter_cached_context_only",
            "eligible_for_intake_preview": "false",
            "next_action": "target first-party plan endpoint/list; reject third-party plan mirrors for this source-packet layer",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0044",
            "queue_rank": "44",
            "university_code": "12044",
            "university_name": "上海第二工业大学",
            "source_url": "https://zsb.sspu.edu.cn/2025/0507/c3129a161937/page.htm",
            "source_owner": "上海第二工业大学本科招生网",
            "source_title": "2025年秋季招生章程候选页",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_domain_timeout",
            "source_role": "official_charter_candidate_reachability_blocked",
            "source_contains_group_code": "unknown_until_cached",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "unknown_until_cached",
            "special_type_detected": "unknown_until_cached",
            "raw_file_path": "",
            "collector_note": "Official-domain charter/plan candidate timed out in terminal fetch. Kept in reachability/backoff layer; no browser/header replay without approval.",
            "collector_confidence": "T3_official_domain_candidate_timeout_not_cached",
            "source_packet_status": "official_domain_candidate_reachability_timeout",
            "eligible_for_intake_preview": "false",
            "next_action": "retry with approved browser/header route or locate alternate first-party HTML/PDF source",
            "requires_manual_approval": "true_for_browser_or_header_retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0046",
            "queue_rank": "46",
            "university_code": "10538",
            "university_name": "中南林业科技大学",
            "source_url": "https://zs.csuft.edu.cn/f/zsjhinfo?jhnd=2025&ssdm=45",
            "source_owner": "中南林业科技大学招生信息网",
            "source_title": "2025年中南林业科技大学招生计划（广西）",
            "published_date": "",
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
            "special_type_detected": "history, physical, and sports/advance rows share listing; filter by subject and batch before use",
            "raw_file_path": f"{rel(RAW_DIR / 'csuft_2025_guangxi_plan.html')}|{rel(RAW_DIR / 'csuft_2025_guangxi_plan_page2.html')}",
            "collector_note": f"Official Guangxi plan pages cached. Local table parse found 本科普通批物理类 {csuft_rows} major rows, plan total {csuft_total}; selection split {csuft_selection_summary}. Sample majors: {csuft_major_sample}. Group code is not printed.",
            "collector_confidence": "T1_official_html_extractable_plan_table_candidate",
            "source_packet_status": "official_html_plan_table_cached_extractable",
            "eligible_for_intake_preview": "conditional_after_source_packet_parse_and_group_mapping",
            "next_action": "build source-packet parse preview; hold 10538-106 group-year calibration until exam-authority group mapping is verified",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0048",
            "queue_rank": "48",
            "university_code": "10520",
            "university_name": "中南财经政法大学",
            "source_url": "https://bkzs.zuel.edu.cn/2025/0529/c15326a393047/page.htm",
            "source_owner": "中南财经政法大学本科招生网",
            "source_title": "中南财经政法大学2025年普通本科招生章程",
            "published_date": "2025-05-29",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_charter_cached_context_only",
            "source_role": "official_charter_context_not_plan_table",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "charter identifies ordinary本科 plus other special types including公安学类/艺术/专项/预科; source rows must be separated",
            "raw_file_path": rel(RAW_DIR / "zuel_2025_charter.html"),
            "collector_note": f"Official charter cached as {zuel_status}. It defines普通本科批 and special-type boundaries, but does not expose Guangxi group/major plan rows.",
            "collector_confidence": "T3_official_charter_context_only_no_plan_rows",
            "source_packet_status": "official_charter_cached_context_only",
            "eligible_for_intake_preview": "false",
            "next_action": "find first-party分省分专业计划表; keep 10520-301 as score/rank-only until plan source appears",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0049",
            "queue_rank": "49",
            "university_code": "11105",
            "university_name": "中国人民警察大学",
            "source_url": "https://www.cppu.edu.cn/info/1036/5298.htm",
            "source_owner": "中国人民警察大学",
            "source_title": "中国人民警察大学2025年本科招生章程",
            "published_date": "2025-06-13",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_charter_cached_embedded_pdf_image",
            "source_role": "official_charter_pdf_image_context_not_plan_table",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "public_security/police admissions boundary likely; embedded charter PDF images not parsed into ordinary trend rows",
            "raw_file_path": rel(RAW_DIR / "cppu_2025_charter.html"),
            "collector_note": f"Official charter page cached as {cppu_status}; content is rendered from embedded PDF/image assets. It is source context only and not an ordinary Guangxi plan table.",
            "collector_confidence": "T3_official_charter_embedded_pdf_image_context_only",
            "source_packet_status": "official_charter_cached_pdf_image_context_only",
            "eligible_for_intake_preview": "false",
            "next_action": "locate official ordinary本科批 Guangxi plan rows or hold as special-boundary context only",
            "requires_manual_approval": "false_for_cached_page; true_if_pdf_image_ocr_browser_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0050",
            "queue_rank": "50",
            "university_code": "10047",
            "university_name": "中央美术学院",
            "source_url": "https://www.cafa.edu.cn/st/2025/80233082.htm",
            "source_owner": "中央美术学院",
            "source_title": "中央美术学院2025年本科招生章程",
            "published_date": "",
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类",
            "round_type": "official_charter_cached_special_type_boundary",
            "source_role": "official_charter_context_not_plan_table",
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "art school; charter separates校考提前批 and ordinary本科批 but no Guangxi plan rows",
            "raw_file_path": rel(RAW_DIR / "cafa_2025_charter.html"),
            "collector_note": f"Official charter cached as {cafa_status}. It confirms special art/ordinary boundaries but not Guangxi group/major plan data.",
            "collector_confidence": "T3_official_charter_special_boundary_context_only",
            "source_packet_status": "official_charter_cached_special_boundary_context_only",
            "eligible_for_intake_preview": "false",
            "next_action": "use only as special-type boundary clue unless an official Guangxi ordinary plan table is found",
            "requires_manual_approval": "false",
        },
    ]

    rows = []
    for idx, row in enumerate(discovered, start=1):
        enriched = {
            "source_id": f"reference_trend_520_p0_batch8_{idx:04d}",
            "intended_layer": "reference_trend_source_packet_preview_only",
            "requires_network": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "record_id": f"reference_trend_520_p0_batch8_{idx:04d}",
        }
        enriched.update(row)
        rows.append(enriched)
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    universities = sorted({str(row["university_name"]) for row in rows if row.get("university_name")})
    t1_rows = [row for row in rows if str(row.get("collector_confidence", "")).startswith("T1_")]
    manual_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    rollup = [
        {"metric": "batch8_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(universities)},
        {"metric": "t1_high_value_rows", "value": len(t1_rows), "note": "中南林业科技大学官方广西计划表。"},
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
        or row.get("source_packet_status") == "official_domain_candidate_reachability_timeout"
        or "大学" in str(row.get("source_owner", ""))
        or "学院" in str(row.get("source_owner", ""))
        or "招生" in str(row.get("source_owner", ""))
        for row in rows
    )
    manual_count = sum(1 for row in rows if str(row.get("requires_manual_approval", "")).startswith("true"))
    return [
        {
            "qa_check": "official_or_reachability_backoff_rows",
            "status": "pass" if official_or_backoff else "warn",
            "value": len(rows),
            "note": "Rows are first-party official pages/assets or explicit official-domain reachability backoff; third-party mirrors are not accepted.",
        },
        {
            "qa_check": "extractable_plan_candidates",
            "status": "pass",
            "value": sum("true" in str(row.get("source_contains_plan_count", "")) for row in rows),
            "note": "Extractable plan source remains held until parse and group mapping.",
        },
        {
            "qa_check": "manual_approval_boundary",
            "status": "pass",
            "value": manual_count,
            "note": "Timeout/browser-needed cases are held and not parsed into data.",
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
        if any(token in status for token in ["context_only", "timeout", "special_boundary"]):
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


def write_doc(rows: list[dict[str, object]]) -> None:
    t1 = [row for row in rows if str(row.get("collector_confidence", "")).startswith("T1_")]
    blocked = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    text = f"""# Reference Trend 520 P0 Official Source Discovery Batch 8

Generated: {date.today().isoformat()}

## Scope

This batch covers uncovered P0 plan-source queue rows around queue ranks 42-50. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch8_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_exclusion_log.csv`

## Key Findings

- Candidate rows: {len(rows)}
- Universities covered: {len({row['university_name'] for row in rows})}
- T1 extractable official candidates: {len(t1)} ({'、'.join(row['university_name'] for row in t1) if t1 else 'none'})
- Manual approval / browser-replay boundaries: {len(blocked)} ({'、'.join(row['university_name'] for row in blocked) if blocked else 'none'})

High-value row:

1. 中南林业科技大学: official Guangxi plan HTML pages cached. Local table parse found 本科普通批物理类 major rows and plan counts, but no Guangxi professional-group code is printed.

Held/context rows:

- 上海应用技术大学、上海立信会计金融学院、中南财经政法大学: official charter/context pages cached; no first-party Guangxi group/major plan table found in this pass.
- 上海第二工业大学: official-domain candidate timed out in terminal fetch and is kept in reachability/backoff.
- 中国人民警察大学: official charter page is embedded PDF/image context, with public-security boundary concerns; not ordinary trend input.
- 中央美术学院: official charter context confirms art/ordinary boundary but not Guangxi ordinary plan rows.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next step should parse the 中南林业科技大学 T1 source into source-packet parse preview, then keep it held until group mapping/acceptance is explicit.
"""
    DOC_OUT.write_text(text, encoding="utf-8")


def write_handoff() -> None:
    marker = "## 36. 2026-05-16 P0 官方来源发现 batch 8"
    content = f"""

{marker}

已新增 batch8 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch8_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch8.md`

覆盖结果：queue rank 42、43、44、46、48、49、50 共 7 所学校。中南林业科技大学官方广西招生计划两页已缓存，可抽取 2025 本科普通批物理类专业行与计划数，但不打印广西院校专业组代码。上海应用技术大学、上海立信会计金融学院、中南财经政法大学只获得官方章程/规则上下文，未获得结构化广西计划表；上海第二工业大学官方候选页终端访问超时，保留在 reachability/backoff；中国人民警察大学与中央美术学院保留为特殊类型/章程边界上下文。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先把中南林业科技大学 T1 来源解析成 source-packet parse preview，并继续 hold group-year calibration，直到专业组映射被人工接受。
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
    write_doc(rows)
    write_handoff()

    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    print(f"wrote {ROLLUP_OUT.relative_to(ROOT)}")
    print(f"wrote {QA_OUT.relative_to(ROOT)}")
    print(f"wrote {EXCLUSION_OUT.relative_to(ROOT)} rows={len(exclusions)}")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
