#!/usr/bin/env python3
"""Parse Shanghai Normal University batch15 official out-province PDF.

The PDF has a machine-readable province table. This script extracts Guangxi
plan counts into a source-packet preview only. The PDF does not print Guangxi
professional-group codes, subject route, score, or rank, so every extracted row
remains outside reference_trend_pool/canonical/ML until mapping is resolved.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

HTML_PATH = RAW_DIR / "shnu_2025_outprovince_plan_page.html"
PDF_PATH = RAW_DIR / "shnu_2025_outprovince_plan.pdf"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_shnu_pdf_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_shnu_pdf_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_shnu_pdf_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_shnu_pdf_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_shnu_pdf_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PAGE_URL = "https://ssdzsb.shnu.edu.cn/af/83/c26800a831363/page.htm"
PDF_URL = "https://ssdzsb.shnu.edu.cn/_upload/article/files/85/23/f796eb7c46f3884bb92c191a9052/3faafef1-d12a-4496-86cf-2b399dc5de72.pdf"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "related_queue_ranks",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "school_group_code",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "raw_html_path",
    "raw_pdf_path",
    "pdf_pages",
    "pdf_table_page",
    "source_row_number",
    "major_name",
    "guangxi_plan_count",
    "campus",
    "special_type_detected",
    "ordinary_physical_candidate",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "collector_confidence",
    "source_packet_status",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "requires_manual_approval",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def q_context() -> tuple[str, str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10270"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10270"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "166|167", all_ranks


def html_meta() -> tuple[str, str]:
    if not HTML_PATH.exists():
        return "2025年外省市招生计划", "2025-06-11"
    html = HTML_PATH.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r'<h1 class="arti_title">(.+?)</h1>', html)
    date_match = re.search(r"发布时间：([0-9-]+)", html)
    return (
        title_match.group(1).strip() if title_match else "2025年外省市招生计划",
        date_match.group(1).strip() if date_match else "2025-06-11",
    )


def add_pdfplumber_path() -> None:
    tmp_pdfplumber = Path("/private/tmp/codex_pdfplumber")
    if tmp_pdfplumber.exists():
        sys.path.insert(0, str(tmp_pdfplumber))


def cell_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", "").strip()


def cell_int(value: Any) -> int:
    text = cell_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def special_type(major: str) -> str:
    flags: list[str] = []
    if any(token in major for token in ["中美合作", "中法合作", "中德合作", "中英合作", "中俄合作"]):
        flags.append("cooperative")
    if any(token in major for token in ["音乐", "舞蹈", "美术", "设计", "动画", "表演", "播音", "编导", "戏剧", "绘画", "书法", "中国画"]):
        flags.append("art_admission_boundary")
    if any(token in major for token in ["体育", "运动"]):
        flags.append("sport_admission_boundary")
    return "|".join(flags) if flags else "none_detected"


def parse_tables() -> tuple[list[dict[str, object]], dict[str, object]]:
    if not PDF_PATH.exists():
        return [], {"status": "pdf_not_cached", "pdf_pages": 0}
    add_pdfplumber_path()
    try:
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local runtime
        return [], {"status": f"pdfplumber_unavailable:{exc.__class__.__name__}", "pdf_pages": 0}

    queue_ids, batch_rank, all_ranks = q_context()
    title, published = html_meta()
    parsed_rows: list[dict[str, object]] = []
    raw_table_rows = 0
    table_count = 0
    with pdfplumber.open(str(PDF_PATH)) as pdf:
        pdf_pages = len(pdf.pages)
        for page_index, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            table_count += len(tables)
            for table in tables:
                if not table:
                    continue
                header = [cell_text(cell) for cell in table[0]]
                if "广西" not in header or "专业名称" not in header:
                    continue
                gx_idx = header.index("广西")
                campus_idx = header.index("新生就读校区") if "新生就读校区" in header else len(header) - 1
                for source_row_number, row in enumerate(table[1:], start=2):
                    raw_table_rows += 1
                    if not row:
                        continue
                    major = cell_text(row[0]) if len(row) > 0 else ""
                    gx_plan = cell_int(row[gx_idx]) if len(row) > gx_idx else 0
                    if not major or gx_plan <= 0:
                        continue
                    campus = cell_text(row[campus_idx]) if len(row) > campus_idx else ""
                    special = special_type(major)
                    parsed_rows.append(
                        {
                            "record_id": f"reference_trend_520_batch15_shnu_pdf_parse_{len(parsed_rows) + 1:04d}",
                            "queue_record_id": queue_ids,
                            "queue_rank": batch_rank,
                            "related_queue_ranks": all_ranks,
                            "university_code": "10270",
                            "university_name": "上海师范大学",
                            "year": "2025",
                            "province": "广西",
                            "batch": "本科普通批",
                            "subject_category": "subject_route_unknown_pdf_outprovince_plan",
                            "school_group_code": "",
                            "source_url": f"{PAGE_URL}|{PDF_URL}",
                            "source_owner": "上海师范大学招生办公室",
                            "source_title": title,
                            "published_date": published,
                            "raw_html_path": rel(HTML_PATH) if HTML_PATH.exists() else "",
                            "raw_pdf_path": rel(PDF_PATH),
                            "pdf_pages": pdf_pages,
                            "pdf_table_page": page_index,
                            "source_row_number": source_row_number,
                            "major_name": major,
                            "guangxi_plan_count": gx_plan,
                            "campus": campus,
                            "special_type_detected": special,
                            "ordinary_physical_candidate": "false_special_boundary" if special != "none_detected" else "unknown_until_subject_group_mapping",
                            "source_contains_group_code": "false",
                            "source_contains_plan_count": "true",
                            "source_contains_min_score": "false",
                            "source_contains_min_rank": "false",
                            "collector_confidence": "T2_official_pdf_plan_count_extracted_subject_group_mapping_required",
                            "source_packet_status": "official_pdf_extracted_guangxi_major_rows_no_group_or_subject",
                            "eligible_for_intake_preview": "true_source_packet_preview_only",
                            "reference_trend_pool_eligible": "false_until_group_code_and_subject_route_mapping",
                            "calibration_eligible": "false",
                            "requires_manual_approval": "true_for_subject_route_group_mapping_and_special_type_boundary",
                            "next_action": "Map Guangxi PDF major rows to official 2025 Guangxi professional groups/subject routes; exclude art/sport/cooperative boundaries as needed.",
                            "canonical_ml_entry_open": "false",
                            "decision_pool_boundary": "reference_trend_source_packet_preview_only_not_32_school_decision_pool",
                            "evidence_note": f"Parsed by pdfplumber from official PDF; header Guangxi column index={gx_idx}; PDF table lacks group code/subject route.",
                        }
                    )
    return parsed_rows, {"status": "pdfplumber_tables_extracted", "pdf_pages": pdf_pages, "table_count": table_count, "raw_table_rows": raw_table_rows}


def main() -> None:
    out_rows, meta = parse_tables()
    total_plan = sum(int(row["guangxi_plan_count"]) for row in out_rows)
    special_counts = Counter(row["special_type_detected"] for row in out_rows)
    special_rows = sum(1 for row in out_rows if row["special_type_detected"] != "none_detected")
    rollup_rows = [
        {"metric": "shnu_official_page_cached_rows", "value": 1 if HTML_PATH.exists() else 0, "note": rel(HTML_PATH) if HTML_PATH.exists() else ""},
        {"metric": "shnu_official_pdf_cached_rows", "value": 1 if PDF_PATH.exists() else 0, "note": rel(PDF_PATH) if PDF_PATH.exists() else ""},
        {"metric": "pdf_parse_status", "value": meta.get("status", ""), "note": str(meta)},
        {"metric": "raw_table_rows_seen", "value": meta.get("raw_table_rows", 0), "note": "Rows across extracted PDF tables, excluding headers."},
        {"metric": "guangxi_major_rows_extracted", "value": len(out_rows), "note": "Rows with Guangxi plan_count > 0."},
        {"metric": "guangxi_plan_count_sum_extracted", "value": total_plan, "note": "Sum of extracted Guangxi plan counts."},
        {"metric": "special_boundary_rows", "value": special_rows, "note": dict(special_counts)},
        {"metric": "group_code_available_rows", "value": 0, "note": "PDF is province-major table, not Guangxi professional-group split."},
        {"metric": "subject_route_available_rows", "value": 0, "note": "PDF has no Guangxi subject route/group split."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group and subject-route mapping required."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_page_cached",
            "status": "PASS" if HTML_PATH.exists() else "FAIL",
            "detail": rel(HTML_PATH) if HTML_PATH.exists() else "HTML missing.",
        },
        {
            "check": "official_pdf_cached",
            "status": "PASS" if PDF_PATH.exists() else "FAIL",
            "detail": rel(PDF_PATH) if PDF_PATH.exists() else "PDF missing.",
        },
        {
            "check": "pdfplumber_table_extraction",
            "status": "PASS" if meta.get("status") == "pdfplumber_tables_extracted" else "FAIL",
            "detail": str(meta),
        },
        {
            "check": "guangxi_rows_extracted",
            "status": "PASS" if len(out_rows) > 0 and total_plan > 0 else "FAIL",
            "detail": f"rows={len(out_rows)}; plan_sum={total_plan}",
        },
        {
            "check": "subject_group_mapping_hold",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] != "true" for row in out_rows) else "FAIL",
            "detail": "Official PDF lacks Guangxi professional-group and subject-route split.",
        },
        {
            "check": "special_boundary_flagged",
            "status": "PASS",
            "detail": f"special_boundary_rows={special_rows}; counts={dict(special_counts)}",
        },
        {
            "check": "no_reference_trend_pool_or_canonical_ml",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in out_rows) else "FAIL",
            "detail": "No trend pool/canonical/ML writes.",
        },
    ]
    exclusion_rows = [
        {
            **row,
            "source_packet_status": "held_for_special_or_subject_group_mapping",
            "next_action": "Do not use for trend calibration until Guangxi subject route and professional-group mapping are confirmed.",
        }
        for row in out_rows
        if row["special_type_detected"] != "none_detected" or row["subject_category"] == "subject_route_unknown_pdf_outprovince_plan"
    ]
    doc = f"""# Reference Trend 520 Batch15 Shanghai Normal University PDF Parse Preview

Generated: {date.today().isoformat()}

Purpose: cache and parse 上海师范大学 official 2025 out-province plan PDF into
a non-canonical source-packet preview for later Guangxi subject-route and
professional-group mapping.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official page: `{PAGE_URL}`
- Official PDF: `{PDF_URL}`
- Cached PDF: `{PDF_PATH.relative_to(ROOT) if PDF_PATH.exists() else "not cached"}`
- Parse status: `{meta.get("status", "")}`
- Guangxi rows extracted: {len(out_rows)}
- Guangxi plan count sum: {total_plan}
- Special-boundary rows: {special_rows}

The PDF is useful plan-count evidence, but it is not a Guangxi professional-group
or subject-route split. All rows remain outside `reference_trend_pool`,
`canonical`, `ML`, and the 32-school decision_pool until mapping is resolved.
"""
    write_csv(OUT, out_rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion_rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 69. 2026-05-16 batch15 上海师范大学 PDF parse preview"
    handoff_content = f"""

{marker}

已新增上海师范大学 batch15 PDF parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 外省市招生计划页和 PDF 已缓存，PDF 经 pdfplumber 表格解析后抽出广西列 {len(out_rows)} 个专业行，计划数合计 {total_plan}。其中 {special_rows} 行带艺术/体育/中外合作等特殊边界标记。

准入边界：本轮只写 source-packet preview/QA；PDF 没有广西院校专业组代码、科类/选科路线、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=false_until_group_code_and_subject_route_mapping`，不写 canonical/ML，也不进入 32 所 decision_pool。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
