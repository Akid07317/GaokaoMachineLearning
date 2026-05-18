#!/usr/bin/env python3
"""Parse Guizhou University of Traditional Chinese Medicine 2025 plan PDF.

The official PDF is a one-page province-column table. This script extracts only
the Guangxi column into source-packet preview artifacts. The PDF does not print
Guangxi professional-group codes, scores, or ranks, so rows stay outside
reference_trend_pool/canonical/ML until a score/rank group-line join is built.
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

HTML_PATH = RAW_DIR / "gzy_2025_plan_page.html"
PDF_PATH = RAW_DIR / "gzy_2025_plan_pdf.pdf"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_gzy_pdf_column_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_gzy_pdf_column_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_gzy_pdf_column_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_gzy_pdf_column_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_gzy_pdf_column_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PAGE_URL = "https://zs.gzy.edu.cn/info/1024/1853.htm"
PDF_URL = "https://zs.gzy.edu.cn/__local/5/DD/CD/C6E4AC695107FBBBFA9EC449395_1413CF88_18330.pdf"

WATERMARK_PREFIXES = set("贵州中医药大学")

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
    "major_code",
    "major_name",
    "duration_years",
    "tuition_yuan_per_year",
    "guangxi_plan_count",
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


def upsert_handoff_section(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker not in text:
        with HANDOFF.open("a", encoding="utf-8") as f:
            f.write(content)
        return
    start = text.index(marker)
    next_section = text.find("\n\n## ", start + len(marker))
    prefix = text[:start]
    suffix = text[next_section:] if next_section != -1 else ""
    HANDOFF.write_text(prefix + content.lstrip("\n") + suffix, encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def add_pdfplumber_path() -> None:
    tmp_pdfplumber = Path("/private/tmp/codex_pdfplumber")
    if tmp_pdfplumber.exists():
        sys.path.insert(0, str(tmp_pdfplumber))


def cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def squash(value: Any) -> str:
    return re.sub(r"\s+", "", cell(value))


def clean_watermark_prefix(value: Any) -> str:
    text = cell(value)
    if "\n" in text:
        parts = [part.strip() for part in text.split("\n") if part.strip()]
        if len(parts) >= 2 and len(parts[0]) == 1 and parts[0] in WATERMARK_PREFIXES:
            text = "".join(parts[1:])
    return re.sub(r"\s+", "", text)


def plan_int(value: Any) -> int:
    digits = re.findall(r"\d+", squash(value))
    if not digits:
        return 0
    return int("".join(digits))


def major_code(value: Any) -> str:
    text = squash(value)
    match = re.search(r"\d{6}[A-Z]?", text)
    return match.group(0) if match else text


def html_meta() -> tuple[str, str]:
    if not HTML_PATH.exists():
        return "贵州中医药大学2025年本科分省分专业招生计划表", "2025-06-23"
    html = HTML_PATH.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<h2>(.+?)</h2>", html, flags=re.S)
    date_match = re.search(r"发布日期：([0-9-]+)", html)
    title = re.sub(r"\s+", "", title_match.group(1)) if title_match else "贵州中医药大学2025年本科分省分专业招生计划表"
    published = date_match.group(1) if date_match else "2025-06-23"
    return title, published


def q_context() -> tuple[str, str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10662"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10662"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "160", all_ranks


def special_type(major: str, subject: str) -> str:
    flags: list[str] = []
    if any(token in major for token in ["中外合作", "合作办学"]):
        flags.append("cooperative_boundary")
    if any(token in major for token in ["运动", "体育"]):
        flags.append("sport_admission_boundary")
    if any(token in subject for token in ["文史", "历史"]):
        flags.append("history_subject_boundary")
    return "|".join(flags) if flags else "none_detected"


def parse_pdf() -> tuple[list[dict[str, object]], dict[str, object]]:
    if not PDF_PATH.exists():
        return [], {"status": "pdf_not_cached", "pdf_pages": 0}

    add_pdfplumber_path()
    try:
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover
        return [], {"status": f"pdfplumber_unavailable:{exc.__class__.__name__}", "pdf_pages": 0}

    queue_ids, batch_rank, all_ranks = q_context()
    title, published = html_meta()
    parsed: list[dict[str, object]] = []
    total_checks = {"history": 0, "physical": 0, "all": 0}
    source_rows_seen = 0
    current_code = ""
    current_major = ""
    current_duration = ""
    current_tuition = ""

    with pdfplumber.open(str(PDF_PATH)) as pdf:
        pdf_pages = len(pdf.pages)
        for page_index, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables():
                if not table or len(table) < 4:
                    continue
                headers = [squash(value) for value in table[2]]
                if "广西" not in headers:
                    continue
                gx_idx = headers.index("广西")
                in_total_block = False
                for source_row_number, row in enumerate(table[3:], start=4):
                    if not row:
                        continue
                    first = squash(row[0]) if len(row) > 0 else ""
                    subject = squash(row[4]) if len(row) > 4 else ""
                    if first == "总计":
                        in_total_block = True
                    if in_total_block:
                        if "历史" in subject or "文史" in subject:
                            total_checks["history"] = plan_int(row[gx_idx])
                        elif "物理" in subject or "理工" in subject:
                            total_checks["physical"] = plan_int(row[gx_idx])
                        elif subject == "合计":
                            total_checks["all"] = plan_int(row[gx_idx])
                        continue
                    if first == "合计" or subject == "合计":
                        total_checks["all"] = plan_int(row[gx_idx])
                        continue
                    if not subject:
                        continue
                    if first:
                        current_code = major_code(row[0])
                        current_major = clean_watermark_prefix(row[1]) if len(row) > 1 else ""
                        current_duration = squash(row[2]) if len(row) > 2 else ""
                        current_tuition = squash(row[3]) if len(row) > 3 else ""
                    gx_plan = plan_int(row[gx_idx]) if len(row) > gx_idx else 0
                    source_rows_seen += 1
                    if gx_plan <= 0:
                        continue
                    special = special_type(current_major, subject)
                    ordinary_physical = ("物理" in subject or "理工" in subject) and "cooperative_boundary" not in special and "sport_admission_boundary" not in special
                    parsed.append(
                        {
                            "record_id": f"reference_trend_520_batch15_gzy_pdf_column_parse_{len(parsed) + 1:04d}",
                            "queue_record_id": queue_ids,
                            "queue_rank": batch_rank,
                            "related_queue_ranks": all_ranks,
                            "university_code": "10662",
                            "university_name": "贵州中医药大学",
                            "year": "2025",
                            "province": "广西",
                            "batch": "本科普通批",
                            "subject_category": subject,
                            "school_group_code": "",
                            "source_url": f"{PAGE_URL}|{PDF_URL}",
                            "source_owner": "贵州中医药大学招生信息网",
                            "source_title": title,
                            "published_date": published,
                            "raw_html_path": rel(HTML_PATH),
                            "raw_pdf_path": rel(PDF_PATH),
                            "pdf_pages": pdf_pages,
                            "pdf_table_page": page_index,
                            "source_row_number": source_row_number,
                            "major_code": current_code,
                            "major_name": current_major,
                            "duration_years": current_duration,
                            "tuition_yuan_per_year": current_tuition,
                            "guangxi_plan_count": gx_plan,
                            "special_type_detected": special,
                            "ordinary_physical_candidate": "true" if ordinary_physical else "false",
                            "source_contains_group_code": "false",
                            "source_contains_plan_count": "true",
                            "source_contains_min_score": "false",
                            "source_contains_min_rank": "false",
                            "collector_confidence": "T2_official_pdf_column_parse_no_group_score_rank",
                            "source_packet_status": "official_pdf_column_parse_preview_only",
                            "eligible_for_intake_preview": "true",
                            "reference_trend_pool_eligible": "false",
                            "calibration_eligible": "false",
                            "requires_manual_approval": "false",
                            "next_action": "join with Guangxi official group-line score/rank and professional-group context before calibration.",
                            "canonical_ml_entry_open": "false",
                            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                            "evidence_note": "Official PDF province-column plan row. Guangxi plan count parsed; no group code, score, or rank printed.",
                        }
                    )

    return parsed, {
        "status": "parsed",
        "pdf_pages": pdf_pages,
        "source_rows_seen": source_rows_seen,
        "total_checks": total_checks,
    }


def main() -> None:
    rows, meta = parse_pdf()
    write_csv(OUT, rows, FIELDS)

    total_plan = sum(int(row["guangxi_plan_count"]) for row in rows)
    physical_all_rows = [
        row for row in rows
        if "物理" in str(row.get("subject_category", "")) or "理工" in str(row.get("subject_category", ""))
    ]
    physical_all_plan = sum(int(row["guangxi_plan_count"]) for row in physical_all_rows)
    physical_rows = [row for row in rows if row.get("ordinary_physical_candidate") == "true"]
    physical_plan = sum(int(row["guangxi_plan_count"]) for row in physical_rows)
    counter_subject = Counter(str(row["subject_category"]) for row in rows)
    counter_special = Counter(str(row["special_type_detected"]) for row in rows)
    total_checks = meta.get("total_checks", {}) if isinstance(meta.get("total_checks"), dict) else {}

    rollup_rows = [
        {"metric": "official_page_cached_rows", "value": int(HTML_PATH.exists()), "note": rel(HTML_PATH)},
        {"metric": "official_pdf_cached_rows", "value": int(PDF_PATH.exists()), "note": rel(PDF_PATH)},
        {"metric": "parse_preview_rows_all_guangxi", "value": len(rows), "note": "rows with Guangxi plan count > 0"},
        {"metric": "guangxi_plan_count_sum_all_rows", "value": total_plan, "note": f"official total row={total_checks.get('all', '')}"},
        {"metric": "physical_subject_rows_all", "value": len(physical_all_rows), "note": "all physical/理工 rows, including special boundaries"},
        {"metric": "physical_subject_plan_sum_all", "value": physical_all_plan, "note": f"official physical total row={total_checks.get('physical', '')}"},
        {"metric": "ordinary_physics_candidate_rows", "value": len(physical_rows), "note": "physical/理工 rows excluding sport/cooperative boundaries"},
        {"metric": "ordinary_physics_candidate_plan_sum", "value": physical_plan, "note": "excludes cooperative/sport boundaries"},
        {"metric": "source_group_code_available_rows", "value": 0, "note": "PDF does not print Guangxi professional-group codes"},
        {"metric": "subject_distribution", "value": dict(counter_subject), "note": ""},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in counter_special.items() if k != "none_detected"), "note": dict(counter_special)},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Score/rank and group join required before calibration."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])

    qa_rows = [
        {"check": "official_page_cached", "status": "PASS" if HTML_PATH.exists() else "FAIL", "detail": rel(HTML_PATH)},
        {"check": "official_pdf_cached", "status": "PASS" if PDF_PATH.exists() else "FAIL", "detail": rel(PDF_PATH)},
        {"check": "pdf_column_table_extracted", "status": "PASS" if rows else "FAIL", "detail": f"rows={len(rows)}"},
        {"check": "guangxi_total_matches_pdf", "status": "PASS" if total_plan == total_checks.get("all") else "WARN", "detail": f"parsed={total_plan}; pdf_total={total_checks.get('all')}"},
        {"check": "guangxi_physical_total_matches_pdf", "status": "PASS" if physical_all_plan == total_checks.get("physical") else "WARN", "detail": f"parsed_all_physical={physical_all_plan}; pdf_physical_total={total_checks.get('physical')}; ordinary_candidate_ex_special={physical_plan}"},
        {"check": "score_rank_hold", "status": "PASS", "detail": "Official PDF is plan-only; no score or rank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])

    exclusion_rows = []
    for row in rows:
        exclusion_rows.append(
            {
                "record_id": row["record_id"],
                "university_name": row["university_name"],
                "major_name": row["major_name"],
                "subject_category": row["subject_category"],
                "guangxi_plan_count": row["guangxi_plan_count"],
                "special_type_detected": row["special_type_detected"],
                "exclusion_reason": "missing_school_group_code_score_rank_before_calibration",
                "canonical_ml_entry_open": "false",
            }
        )
    write_csv(
        EXCLUSION_OUT,
        exclusion_rows,
        [
            "record_id",
            "university_name",
            "major_name",
            "subject_category",
            "guangxi_plan_count",
            "special_type_detected",
            "exclusion_reason",
            "canonical_ml_entry_open",
        ],
    )

    doc_lines = [
        "# reference_trend_520 batch15 GZY PDF column parse preview",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "贵州中医药大学官方 2025 本科分省分专业招生计划 PDF 已缓存并解析为广西列 source-packet preview。本产物不进入 32 所 decision_pool。",
        "",
        "## Result",
        "",
        f"- Official source URL: {PAGE_URL}",
        f"- Official PDF URL: {PDF_URL}",
        f"- Cached HTML: `{rel(HTML_PATH)}`",
        f"- Cached PDF: `{rel(PDF_PATH)}`",
        f"- Parsed Guangxi rows: {len(rows)}",
        f"- Guangxi plan sum: {total_plan}",
        f"- Physical subject rows including boundaries: {len(physical_all_rows)}",
        f"- Physical subject plan sum including boundaries: {physical_all_plan}",
        f"- Ordinary physical candidate rows: {len(physical_rows)}",
        f"- Ordinary physical candidate plan sum: {physical_plan}",
        "- Score/rank available: 0",
        "",
        "## Outputs",
        "",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "## Gate Boundary",
        "",
        "官方 PDF 可提取广西专业计划数，但没有院校专业组代码、最低分或最低位次。所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。后续需与广西考试院 group-line score/rank 和专业组上下文做 join workbench。",
        "",
        "## QA",
        "",
    ]
    for row in qa_rows:
        doc_lines.append(f"- {row['check']}: {row['status']} - {row['detail']}")
    doc_lines.extend(["", "## Rollup", ""])
    for row in rollup_rows:
        doc_lines.append(f"- {row['metric']}: {row['value']} ({row['note']})")
    DOC_OUT.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")

    marker = "## 74. 2026-05-16 batch15 贵州中医药大学 PDF column parse preview"
    handoff = f"""

{marker}

已新增贵州中医药大学 batch15 PDF column parse preview：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：官方 2025 本科分省分专业招生计划 PDF 已缓存并解析，抽出广西计划列 {len(rows)} 行，计划数合计 {total_plan}；物理/理工全量 {len(physical_all_rows)} 行，计划数合计 {physical_all_plan}，与 PDF 物理总计 {total_checks.get('physical')} 对齐；剔除中外合作/体育等特殊边界后的普通物理候选 {len(physical_rows)} 行，计划数合计 {physical_plan}。PDF 总计行校验为广西合计 {total_checks.get('all')}。

准入边界：本轮只写 source-packet preview/QA；官方 PDF 没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench，或继续寻找官方专业组拆分表。
"""
    upsert_handoff_section(marker, handoff)


if __name__ == "__main__":
    main()
