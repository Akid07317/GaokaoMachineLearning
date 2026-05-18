#!/usr/bin/env python3
"""Parse/cache-readiness preview for Hubei University batch15 official PDF.

This script reads the cached official 2025 province/major plan PDF for 湖北大学,
extracts the Guangxi column from the wide plan table when pypdf is available,
and writes a non-canonical source-packet preview. The school PDF gives province
major plan counts but does not print Guangxi professional-group codes, so all
rows remain outside reference_trend_pool/canonical/ML until group mapping is
resolved.
"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

PDF_PATH = RAW_DIR / "hubu_2025_plan_pdf.pdf"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_hubu_pdf_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_hubu_pdf_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_hubu_pdf_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_hubu_pdf_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_hubu_pdf_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PLAN_COLUMN_URL = "https://zsxx.hubu.edu.cn/zsxx/zsjh.htm"
PDF_URL = "https://xxgk.hubu.edu.cn/__local/0/3E/A6/5144BF67BAF45FED441FDBA3834_1D8D2799_1E3A1.pdf"

PROVINCES = [
    "湖北",
    "北京",
    "天津",
    "河北",
    "山西",
    "辽宁",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "陕西",
    "甘肃",
    "宁夏",
    "新疆",
]
GUANGXI_INDEX = PROVINCES.index("广西")

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
    "raw_file_path",
    "pdf_pages",
    "college_code",
    "college_name",
    "major_name",
    "guangxi_plan_count",
    "province_plan_sum",
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


HEADER_FRAGMENTS = {
    "2025年湖北大学分省分专业招生计划表",
    "学",
    "院",
    "码",
    "学院",
    "专业（类）/省份 湖",
    "湖",
    "北",
    "京",
    "天",
    "津",
    "河",
    "山",
    "西",
    "辽",
    "宁",
    "黑",
    "龙",
    "江",
    "上",
    "海",
    "苏",
    "浙",
    "安",
    "徽",
    "福",
    "建",
    "广",
    "东",
    "南",
    "重",
    "庆",
    "四",
    "川",
    "贵",
    "州",
    "云",
    "陕",
    "甘",
    "肃",
    "夏",
    "新",
    "疆",
}


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
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10512"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10512"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "157", all_ranks


def extract_text() -> tuple[str, int, str]:
    if not PDF_PATH.exists():
        return "", 0, "pdf_not_cached"
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local runtime
        return "", 0, f"pypdf_unavailable:{exc.__class__.__name__}"
    try:
        reader = PdfReader(str(PDF_PATH))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text, len(reader.pages), "pypdf_text_extracted"
    except Exception as exc:  # pragma: no cover - defensive for malformed PDFs
        return "", 0, f"pypdf_extract_failed:{exc.__class__.__name__}"


def parse_plan_rows(text: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    parsed: list[dict[str, object]] = []
    buffer = ""
    leftover = ""
    for line in (part.strip() for part in text.splitlines()):
        if not line or line in HEADER_FRAGMENTS:
            continue
        buffer = f"{buffer} {line}".strip()
        match = re.search(r"((?:\s+\d+){" + str(len(PROVINCES)) + r"})$", buffer)
        if not match:
            continue
        prefix = buffer[: match.start()].strip()
        values = [int(value) for value in match.group(1).split()]
        parsed.append({"prefix": prefix, "values": values})
        buffer = ""
    if buffer:
        leftover = buffer[:500]

    total_row = next((row for row in parsed if "总计" in str(row["prefix"])), {})
    major_rows = [row for row in parsed if "总计" not in str(row["prefix"])]
    meta = {
        "raw_parsed_rows": len(parsed),
        "raw_major_rows": len(major_rows),
        "total_guangxi_plan": total_row.get("values", [0] * len(PROVINCES))[GUANGXI_INDEX] if total_row else "",
        "leftover_fragment": leftover,
    }
    return major_rows, meta


def split_prefix(prefix: str) -> tuple[str, str, str]:
    match = re.match(r"^(?P<code>\d{2})\s+(?P<college>.+?)\s+(?P<major>.+)$", prefix)
    if not match:
        return "", "", prefix
    return match.group("code"), match.group("college"), match.group("major")


def special_type(major: str) -> str:
    flags: list[str] = []
    if "中外合作" in major:
        flags.append("cooperative")
    if "荆楚优师计划" in major or "优师计划" in major:
        flags.append("targeted_teacher_program")
    if any(token in major for token in ["体育", "运动训练", "美术", "设计", "播音", "艺术"]):
        flags.append("art_sport_or_art_admission_boundary")
    return "|".join(flags) if flags else "none_detected"


def main() -> None:
    queue_ids, batch_rank, all_ranks = q_context()
    text, pdf_pages, parse_status = extract_text()
    rows, meta = parse_plan_rows(text) if text else ([], {"raw_parsed_rows": 0, "raw_major_rows": 0, "total_guangxi_plan": "", "leftover_fragment": ""})
    guangxi_rows = [row for row in rows if row["values"][GUANGXI_INDEX] > 0]
    out_rows: list[dict[str, object]] = []
    for idx, row in enumerate(guangxi_rows, start=1):
        college_code, college_name, major_name = split_prefix(str(row["prefix"]))
        gx_plan = row["values"][GUANGXI_INDEX]
        province_sum = sum(row["values"])
        special = special_type(major_name)
        out_rows.append(
            {
                "record_id": f"reference_trend_520_batch15_hubu_pdf_parse_{idx:04d}",
                "queue_record_id": queue_ids,
                "queue_rank": batch_rank,
                "related_queue_ranks": all_ranks,
                "university_code": "10512",
                "university_name": "湖北大学",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类_candidate_unconfirmed_by_school_pdf",
                "school_group_code": "",
                "source_url": PDF_URL,
                "source_owner": "湖北大学本科招生信息网/信息公开网",
                "source_title": "2025年湖北大学分省分专业招生计划表",
                "raw_file_path": rel(PDF_PATH) if PDF_PATH.exists() else "",
                "pdf_pages": pdf_pages,
                "college_code": college_code,
                "college_name": college_name,
                "major_name": major_name,
                "guangxi_plan_count": gx_plan,
                "province_plan_sum": province_sum,
                "special_type_detected": special,
                "ordinary_physical_candidate": "false_special_boundary" if special != "none_detected" else "unknown_until_group_mapping",
                "source_contains_group_code": "false",
                "source_contains_plan_count": "true",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "collector_confidence": "T2_official_pdf_plan_count_extracted_group_mapping_required",
                "source_packet_status": "official_pdf_extracted_guangxi_major_rows_no_group_code",
                "eligible_for_intake_preview": "true_source_packet_preview_only",
                "reference_trend_pool_eligible": "false_until_group_code_and_subject_mapping",
                "calibration_eligible": "false",
                "requires_manual_approval": "true_for_group_mapping_and_subject/special_type_boundary",
                "next_action": "Map extracted Guangxi major rows to 2025 Guangxi professional groups 104/105/106/107/108 or hold if no official group split.",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_preview_only_not_32_school_decision_pool",
                "evidence_note": f"Parsed via pypdf from cached official PDF; Guangxi column index {GUANGXI_INDEX}; no school group code in PDF.",
            }
        )

    total_gx = int(meta.get("total_guangxi_plan") or 0)
    parsed_gx_sum = sum(int(row["guangxi_plan_count"]) for row in out_rows)
    special_rows = sum(1 for row in out_rows if row["special_type_detected"] != "none_detected")
    rollup_rows = [
        {"metric": "hubu_pdf_cached_rows", "value": 1 if PDF_PATH.exists() else 0, "note": rel(PDF_PATH) if PDF_PATH.exists() else ""},
        {"metric": "pdf_pages", "value": pdf_pages, "note": parse_status},
        {"metric": "raw_major_rows_parsed", "value": meta.get("raw_major_rows", 0), "note": "Rows parsed from all province columns."},
        {"metric": "guangxi_major_rows_extracted", "value": len(out_rows), "note": "Rows with Guangxi plan_count > 0."},
        {"metric": "guangxi_plan_count_sum_extracted", "value": parsed_gx_sum, "note": "Sum of extracted Guangxi major rows."},
        {"metric": "guangxi_total_from_pdf_total_row", "value": total_gx, "note": "Total row Guangxi column."},
        {"metric": "special_boundary_rows", "value": special_rows, "note": "Cooperative/art/sport/targeted flags."},
        {"metric": "group_code_available_rows", "value": 0, "note": "PDF is major-by-province, not professional-group split."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group mapping required."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_pdf_cached",
            "status": "PASS" if PDF_PATH.exists() else "FAIL",
            "detail": rel(PDF_PATH) if PDF_PATH.exists() else "PDF missing.",
        },
        {
            "check": "pdf_text_extraction",
            "status": "PASS" if text and parse_status == "pypdf_text_extracted" else "FAIL",
            "detail": parse_status,
        },
        {
            "check": "guangxi_total_reconciles",
            "status": "PASS" if total_gx and parsed_gx_sum == total_gx else "WARN",
            "detail": f"extracted={parsed_gx_sum}; total_row={total_gx}; leftover={meta.get('leftover_fragment','')}",
        },
        {
            "check": "group_mapping_hold",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] != "true" for row in out_rows) else "FAIL",
            "detail": "School PDF does not print Guangxi professional-group codes.",
        },
        {
            "check": "special_boundary_flagged",
            "status": "PASS",
            "detail": f"special_boundary_rows={special_rows}",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(row["canonical_ml_entry_open"] == "false" for row in out_rows) else "FAIL",
            "detail": "Canonical/ML remains closed.",
        },
    ]
    doc = f"""# Reference Trend 520 Batch15 Hubei University PDF Parse Preview

Generated: {date.today().isoformat()}

Purpose: cache and parse 湖北大学 official 2025 province/major plan PDF into a
non-canonical source-packet preview for later professional-group mapping.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official plan column: `{PLAN_COLUMN_URL}`
- Official PDF: `{PDF_URL}`
- Cached PDF: `{PDF_PATH.relative_to(ROOT) if PDF_PATH.exists() else "not cached"}`
- PDF pages: {pdf_pages}; parse status: `{parse_status}`
- Guangxi major rows extracted: {len(out_rows)}
- Extracted Guangxi plan sum: {parsed_gx_sum}
- PDF total-row Guangxi plan count: {total_gx}

The PDF is useful plan-count evidence, but it is not a professional-group split.
All rows remain outside `reference_trend_pool`, `canonical`, `ML`, and the
32-school decision_pool until official group mapping is resolved.

## Boundary

`eligible_for_intake_preview=true_source_packet_preview_only` means the row is
usable as a source-packet preview for human/GPT mapping work. It does not mean
it is calibration-ready. `reference_trend_pool_eligible=false_until_group_code_and_subject_mapping`
for every row.
"""

    write_csv(OUT, out_rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, out_rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 63. 2026-05-16 batch15 湖北大学 PDF parse preview"
    handoff_content = f"""

{marker}

已新增湖北大学 batch15 PDF parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 分省分专业招生计划 PDF 已缓存并用 pypdf 抽取文本；广西列解析出 {len(out_rows)} 个专业行，专业行计划数合计 {parsed_gx_sum}，与 PDF 总计行广西列 {total_gx} {'一致' if total_gx and parsed_gx_sum == total_gx else '需复核'}。该 PDF 提供省份-专业计划数，但不打印广西院校专业组代码。

准入边界：本轮只写 source-packet preview/QA；所有行继续 `reference_trend_pool_eligible=false_until_group_code_and_subject_mapping`，不写 canonical/ML，也不进入 32 所 decision_pool。下一步可做人审/GPT group mapping，把计划行映射到 2025 广西湖北大学 104/105/106/107/108 专业组，或因缺官方 group split 继续 hold。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
