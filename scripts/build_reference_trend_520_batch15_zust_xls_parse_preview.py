#!/usr/bin/env python3
"""Parse Zhejiang University of Science and Technology batch15 official XLS.

The official 2025 plan page links an XLS attachment with province-major plan
counts. This writes a non-canonical source-packet preview for Guangxi rows and
keeps every row outside reference_trend_pool/canonical/ML until professional
group and subject-route mapping are resolved.
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

PAGE_PATH = RAW_DIR / "zust_2025_plan_page.html"
XLS_PATH = RAW_DIR / "zust_2025_plan_attachment.xls"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_zust_xls_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_zust_xls_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_zust_xls_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_zust_xls_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_zust_xls_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PAGE_URL = "https://zsb.zust.edu.cn/wzxq/9163af354da64088986a66b6bc726358"
XLS_URL = "https://job.zust.edu.cn/zjcFiles//ckimgs/1750238175796.xls"

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
    "selection_requirement",
    "school_group_code",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "raw_html_path",
    "raw_attachment_path",
    "sheet_name",
    "source_row_number",
    "college_name",
    "major_name",
    "duration",
    "tuition_yuan_per_year",
    "freshman_campus",
    "guangxi_plan_count",
    "national_plan_count",
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

PROVINCE_HEADERS = [
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "江苏",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "四川",
    "贵州",
    "云南",
    "陕西",
    "甘肃",
    "新疆",
    "预科",
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
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "11057"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "11057"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "156", all_ranks


def html_meta() -> tuple[str, str]:
    if not PAGE_PATH.exists():
        return "浙江科技大学2025年本科招生计划发布", "2025-06-18"
    html = PAGE_PATH.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r'<h1 id="article_title">(.+?)</h1>', html)
    date_match = re.search(r"<h6><span>([0-9-]+)</span>", html)
    return (
        title_match.group(1).strip() if title_match else "浙江科技大学2025年本科招生计划发布",
        date_match.group(1).strip() if date_match else "2025-06-18",
    )


def add_xlrd_path() -> None:
    tmp_xlrd = Path("/private/tmp/codex_xlrd")
    if tmp_xlrd.exists():
        sys.path.insert(0, str(tmp_xlrd))


def load_sheet() -> tuple[str, list[list[Any]], str]:
    if not XLS_PATH.exists():
        return "", [], "xls_not_cached"
    add_xlrd_path()
    try:
        import xlrd  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local runtime
        return "", [], f"xlrd_unavailable:{exc.__class__.__name__}"
    try:
        book = xlrd.open_workbook(str(XLS_PATH))
        sheet = book.sheet_by_index(0)
        rows = [sheet.row_values(idx) for idx in range(sheet.nrows)]
        return sheet.name, rows, "xlrd_sheet_loaded"
    except Exception as exc:  # pragma: no cover - defensive for malformed xls
        return "", [], f"xlrd_read_failed:{exc.__class__.__name__}"


def cell_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def cell_int(value: Any) -> int:
    if value in ("", None):
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def special_type(major: str, selection: str, campus: str) -> str:
    flags: list[str] = []
    if "中外合作" in major:
        flags.append("cooperative")
    if any(token in major for token in ["三位一体", "专升本", "中本一体", "四年制高职本科"]):
        flags.append("non_ordinary_route")
    if campus == "校外" or "联合培养" in major:
        flags.append("joint_training_or_off_campus_boundary")
    if "预科" in selection or "预科" in major:
        flags.append("preparatory_boundary")
    return "|".join(flags) if flags else "none_detected"


def subject_bucket(selection: str) -> tuple[str, str]:
    if "物理" in selection:
        return "物理类_candidate_from_school_selection_requirement", "true_candidate_subject_requires_physics"
    if selection == "不限":
        return "subject_route_ambiguous_unlimited_selection", "hold_subject_route_mapping_required"
    return "subject_route_unknown", "hold_subject_route_mapping_required"


def parse_rows(sheet_name: str, rows: list[list[Any]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    if len(rows) < 3:
        return [], {"status": "no_rows"}

    header = [cell_text(value) for value in rows[1]]
    try:
        province_start = header.index("天津")
        gx_col = header.index("广西")
    except ValueError:
        return [], {"status": "header_missing_province_or_guangxi"}

    queue_ids, batch_rank, all_ranks = q_context()
    title, published = html_meta()
    college = ""
    parsed: list[dict[str, object]] = []
    province_cols = [idx for idx, name in enumerate(header) if name in PROVINCE_HEADERS]
    for row_idx, row in enumerate(rows[2:], start=3):
        if row and cell_text(row[0]):
            college = cell_text(row[0])
        major = cell_text(row[1]) if len(row) > 1 else ""
        if not major:
            continue
        gx_count = cell_int(row[gx_col]) if len(row) > gx_col else 0
        if gx_count <= 0:
            continue
        selection = cell_text(row[3]) if len(row) > 3 else ""
        campus = cell_text(row[5]) if len(row) > 5 else ""
        subject_category, ordinary_candidate = subject_bucket(selection)
        special = special_type(major, selection, campus)
        province_plan_sum = sum(cell_int(row[idx]) for idx in province_cols if len(row) > idx)
        national_plan_count = cell_int(row[7]) if len(row) > 7 else 0
        parsed.append(
            {
                "record_id": f"reference_trend_520_batch15_zust_xls_parse_{len(parsed) + 1:04d}",
                "queue_record_id": queue_ids,
                "queue_rank": batch_rank,
                "related_queue_ranks": all_ranks,
                "university_code": "11057",
                "university_name": "浙江科技大学",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": subject_category,
                "selection_requirement": selection,
                "school_group_code": "",
                "source_url": f"{PAGE_URL}|{XLS_URL}",
                "source_owner": "浙江科技大学招生网/浙江科技大学就业指导中心附件服务",
                "source_title": title,
                "published_date": published,
                "raw_html_path": rel(PAGE_PATH) if PAGE_PATH.exists() else "",
                "raw_attachment_path": rel(XLS_PATH) if XLS_PATH.exists() else "",
                "sheet_name": sheet_name,
                "source_row_number": row_idx,
                "college_name": college,
                "major_name": major,
                "duration": cell_text(row[2]) if len(row) > 2 else "",
                "tuition_yuan_per_year": cell_text(row[4]) if len(row) > 4 else "",
                "freshman_campus": campus,
                "guangxi_plan_count": gx_count,
                "national_plan_count": national_plan_count,
                "province_plan_sum": province_plan_sum,
                "special_type_detected": special,
                "ordinary_physical_candidate": "false_special_boundary" if special != "none_detected" else ordinary_candidate,
                "source_contains_group_code": "false",
                "source_contains_plan_count": "true",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "collector_confidence": "T2_official_xls_plan_count_extracted_group_mapping_required",
                "source_packet_status": "official_xls_extracted_guangxi_major_rows_no_group_code",
                "eligible_for_intake_preview": "true_source_packet_preview_only",
                "reference_trend_pool_eligible": "false_until_group_code_and_subject_route_mapping",
                "calibration_eligible": "false",
                "requires_manual_approval": "true_for_professional_group_mapping_and_unlimited_selection_route",
                "next_action": "Map extracted Guangxi major rows to official 2025 Guangxi professional groups/subject routes, or hold if no official group split is available.",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_preview_only_not_32_school_decision_pool",
                "evidence_note": f"Parsed from official XLS attachment; Guangxi column index={gx_col}; province column start={province_start}; no group code/min score/min rank in attachment.",
            }
        )
    return parsed, {"status": "parsed", "gx_col": gx_col, "province_start": province_start}


def main() -> None:
    sheet_name, sheet_rows, load_status = load_sheet()
    out_rows, meta = parse_rows(sheet_name, sheet_rows) if sheet_rows else ([], {"status": load_status})
    total_plan = sum(int(row["guangxi_plan_count"]) for row in out_rows)
    subject_counts = Counter(row["subject_category"] for row in out_rows)
    ambiguous_rows = [row for row in out_rows if row["subject_category"] != "物理类_candidate_from_school_selection_requirement"]
    special_rows = [row for row in out_rows if row["special_type_detected"] != "none_detected"]

    rollup_rows = [
        {"metric": "zust_official_page_cached_rows", "value": 1 if PAGE_PATH.exists() else 0, "note": rel(PAGE_PATH) if PAGE_PATH.exists() else ""},
        {"metric": "zust_official_xls_cached_rows", "value": 1 if XLS_PATH.exists() else 0, "note": rel(XLS_PATH) if XLS_PATH.exists() else ""},
        {"metric": "xls_load_status", "value": load_status, "note": sheet_name},
        {"metric": "raw_sheet_rows", "value": len(sheet_rows), "note": str(meta)},
        {"metric": "guangxi_major_rows_extracted", "value": len(out_rows), "note": "Rows with Guangxi plan_count > 0."},
        {"metric": "guangxi_plan_count_sum_extracted", "value": total_plan, "note": "Sum of extracted Guangxi plan counts."},
        {"metric": "physics_selection_rows", "value": subject_counts.get("物理类_candidate_from_school_selection_requirement", 0), "note": "Rows whose school selection requirement includes physics."},
        {"metric": "ambiguous_unlimited_selection_rows", "value": len(ambiguous_rows), "note": "Rows with 不限 or unknown selection route; not physical-trend eligible yet."},
        {"metric": "special_boundary_rows", "value": len(special_rows), "note": "Special route/cooperative/joint/off-campus flags."},
        {"metric": "group_code_available_rows", "value": 0, "note": "XLS is major-by-province, not Guangxi professional-group split."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group and subject-route mapping required."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    qa_rows = [
        {
            "check": "official_page_cached",
            "status": "PASS" if PAGE_PATH.exists() else "FAIL",
            "detail": rel(PAGE_PATH) if PAGE_PATH.exists() else "Official page missing.",
        },
        {
            "check": "official_xls_cached",
            "status": "PASS" if XLS_PATH.exists() else "FAIL",
            "detail": rel(XLS_PATH) if XLS_PATH.exists() else "XLS missing.",
        },
        {
            "check": "xls_load_and_header_parse",
            "status": "PASS" if load_status == "xlrd_sheet_loaded" and meta.get("status") == "parsed" else "FAIL",
            "detail": f"load_status={load_status}; meta={meta}",
        },
        {
            "check": "guangxi_rows_extracted",
            "status": "PASS" if len(out_rows) > 0 and total_plan > 0 else "FAIL",
            "detail": f"rows={len(out_rows)}; plan_sum={total_plan}",
        },
        {
            "check": "ambiguous_subject_route_flagged",
            "status": "PASS",
            "detail": f"ambiguous_unlimited_selection_rows={len(ambiguous_rows)}",
        },
        {
            "check": "group_mapping_hold",
            "status": "PASS" if all(row["reference_trend_pool_eligible"] != "true" for row in out_rows) else "FAIL",
            "detail": "Official XLS does not print Guangxi professional-group codes.",
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
            "source_packet_status": "held_for_subject_route_mapping_unlimited_selection",
            "next_action": "Confirm whether this 不限-selection major belongs to Guangxi physical professional group, history group, or both before any trend-pool use.",
        }
        for row in ambiguous_rows
    ]

    doc = f"""# Reference Trend 520 Batch15 Zhejiang University of Science and Technology XLS Parse Preview

Generated: {date.today().isoformat()}

Purpose: cache and parse 浙江科技大学 official 2025 plan page/XLS into a
non-canonical source-packet preview for later professional-group and subject
route mapping.

## Outputs

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`

## Summary

- Official page: `{PAGE_URL}`
- Official XLS attachment: `{XLS_URL}`
- Cached page: `{PAGE_PATH.relative_to(ROOT) if PAGE_PATH.exists() else "not cached"}`
- Cached XLS: `{XLS_PATH.relative_to(ROOT) if XLS_PATH.exists() else "not cached"}`
- XLS load status: `{load_status}`; sheet: `{sheet_name}`
- Guangxi rows extracted: {len(out_rows)}
- Guangxi plan count sum: {total_plan}
- Physics-selection rows: {subject_counts.get("物理类_candidate_from_school_selection_requirement", 0)}
- Ambiguous 不限-selection rows: {len(ambiguous_rows)}

The official XLS is useful plan-count evidence, but it is not a Guangxi
professional-group split and it contains several `不限` rows whose physical/history
route must be confirmed. All rows remain outside `reference_trend_pool`,
`canonical`, `ML`, and the 32-school decision_pool.

## Boundary

`eligible_for_intake_preview=true_source_packet_preview_only` marks a row as a
plan-side source-packet preview, not as calibration-ready data. Every row remains
`reference_trend_pool_eligible=false_until_group_code_and_subject_route_mapping`.
"""

    write_csv(OUT, out_rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion_rows, FIELDS)
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 66. 2026-05-16 batch15 浙江科技大学 XLS parse preview"
    handoff_content = f"""

{marker}

已新增浙江科技大学 batch15 XLS parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方招生计划网页和其引用的 2025 全日制本科招生计划 XLS 已缓存。XLS 广西列解析出 {len(out_rows)} 个专业计划行，计划数合计 {total_plan}；其中 {subject_counts.get("物理类_candidate_from_school_selection_requirement", 0)} 行选考要求含物理，{len(ambiguous_rows)} 行为 `不限`，需后续结合广西投档线/专业组拆分确认物理/历史路线。

准入边界：本轮只写 source-packet preview/QA；附件没有广西院校专业组代码、最低分、最低位次，所有行继续 `reference_trend_pool_eligible=false_until_group_code_and_subject_route_mapping`，不写 canonical/ML，也不进入 32 所 decision_pool。下一步可查找浙江科技大学 2025 广西投档专业组线或官方专业组拆分，用于 group mapping；否则保持计划侧 evidence。
"""
    append_handoff_once(marker, handoff_content)


if __name__ == "__main__":
    main()
