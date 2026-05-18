#!/usr/bin/env python3
"""Parse batch-9 北方工业大学 official plan table into preview rows.

The official source prints a national major-by-province table. It does not
print Guangxi professional-group codes or subject requirements, so parsed rows
remain source-packet preview only.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch9_official"

RAW = RAW_DIR / "ncut_2025_plan.html"
OUT = SEED_DIR / "reference_trend_520_batch9_ncut_source_packet_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch9_ncut_source_packet_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch9_ncut_source_packet_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch9_ncut_source_packet_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch9_ncut_source_packet_parse.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "record_id",
    "row_scope",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_path",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_subject_label",
    "queue_group_code",
    "source_group_code",
    "major_name",
    "campus",
    "duration_years",
    "tuition_yuan",
    "plan_category",
    "plan_nature",
    "plan_type",
    "plan_count",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "special_type_detected",
    "qa_status",
    "collector_confidence",
    "intended_layer",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "required_resolution",
    "evidence_note",
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


def detect_special(major: str) -> str:
    tags: list[str] = []
    if any(token in major for token in ["视觉传达设计", "环境设计"]):
        tags.append("art_design_boundary")
    if "中外合作办学" in major:
        tags.append("sino_foreign_cooperation")
    return "|".join(tags) if tags else "false"


def parse_rows() -> list[dict[str, object]]:
    parser = TableParser()
    parser.feed(RAW.read_text(encoding="utf-8", errors="replace"))
    if not parser.tables:
        return []
    table = parser.tables[0]
    header = table[0]
    gx_idx = header.index("广西")
    rows: list[dict[str, object]] = []
    for source_index, row in enumerate(table[2:], start=3):
        if gx_idx >= len(row):
            continue
        value = row[gx_idx].strip()
        if not value:
            continue
        major = row[0].strip()
        parsed = {
            "record_id": f"reference_trend_520_batch9_ncut_parse_{len(rows) + 1:04d}",
            "row_scope": "official_major_plan_row",
            "source_id": "reference_trend_520_p0_batch9_0007",
            "queue_record_id": "reference_trend_520_plan_source_queue_0058",
            "queue_rank": "58",
            "source_url": "https://bkzs.ncut.edu.cn/info/1013/2661.htm",
            "source_owner": "北方工业大学招生网",
            "source_title": "北方工业大学2025年本科分专业招生计划",
            "raw_file_path": rel(RAW),
            "university_code": "10009",
            "university_name": "北方工业大学",
            "year": "2025",
            "province": "广西",
            "batch": "本科分专业招生计划_广西列",
            "subject_category": "source_not_printed_hold_for_group_mapping",
            "source_subject_label": "not_printed",
            "queue_group_code": "304",
            "source_group_code": "",
            "major_name": major,
            "campus": "",
            "duration_years": "",
            "tuition_yuan": "",
            "plan_category": "guangxi_column_plan_count",
            "plan_nature": "cross_province_major_plan",
            "plan_type": "ordinary_or_special_unseparated_by_source",
            "plan_count": value,
            "source_contains_group_code": "false",
            "source_contains_plan_count": "true",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "special_type_detected": detect_special(major),
            "qa_status": "parsed_hold_for_subject_and_group_mapping",
            "collector_confidence": "T1_official_html_table_major_plan_row",
            "intended_layer": "reference_trend_source_packet_parse_preview_only",
            "reference_trend_pool_eligible": "0",
            "calibration_eligible": "0",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "required_resolution": "verify_subject_group_code_mapping_and_isolate_art_cooperation_rows_before_calibration",
            "evidence_note": f"Official table row {source_index}; Guangxi column count={value}; source does not print subject requirement or Guangxi group code.",
        }
        rows.append(parsed)
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = sum(int(row.get("plan_count") or 0) for row in rows)
    special_totals = Counter()
    for row in rows:
        special_totals[str(row.get("special_type_detected", "false"))] += int(row.get("plan_count") or 0)
    rollup = [
        {"metric": "parse_preview_rows", "value": len(rows), "note": ""},
        {"metric": "universities_parsed", "value": 1 if rows else 0, "note": "北方工业大学" if rows else ""},
        {"metric": "guangxi_column_plan_total", "value": total, "note": "Source table Guangxi column sum before subject/group filtering."},
        {"metric": "source_group_code_rows", "value": 0, "note": "Source does not print Guangxi院校专业组 code."},
        {"metric": "source_subject_label_rows", "value": 0, "note": "Source does not print subject/selection labels in this national table."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Parse preview only; subject/group mapping not accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for special, plan_total in sorted(special_totals.items()):
        rollup.append({"metric": f"special_type::{special}::plan_total", "value": plan_total, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = sum(int(row.get("plan_count") or 0) for row in rows)
    art_rows = [row for row in rows if "art_design_boundary" in str(row.get("special_type_detected", ""))]
    cooperation_rows = [row for row in rows if "sino_foreign_cooperation" in str(row.get("special_type_detected", ""))]
    return [
        {
            "qa_check": "official_source_parse",
            "status": "pass" if rows else "fail",
            "value": len(rows),
            "note": "Rows come from cached first-party official HTML plan table.",
        },
        {
            "qa_check": "guangxi_column_total",
            "status": "pass" if total == 57 else "warn",
            "value": total,
            "note": "The source table header's Guangxi column total row is 57; parsed row sum should match before filtering.",
        },
        {
            "qa_check": "special_type_isolation",
            "status": "pass",
            "value": f"art_rows={len(art_rows)};cooperation_rows={len(cooperation_rows)}",
            "note": "Art/design and Sino-foreign rows are marked for later isolation, not removed from the raw source-packet preview.",
        },
        {
            "qa_check": "group_mapping_boundary",
            "status": "pass",
            "value": 0,
            "note": "queue_group_code=304 is retained as queue context only; source_group_code is blank for all rows.",
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
    total = sum(int(row.get("plan_count") or 0) for row in rows)
    art_total = sum(int(row.get("plan_count") or 0) for row in rows if "art_design_boundary" in str(row.get("special_type_detected", "")))
    cooperation_total = sum(int(row.get("plan_count") or 0) for row in rows if "sino_foreign_cooperation" in str(row.get("special_type_detected", "")))
    return [
        {
            "record_id": "reference_trend_520_batch9_ncut_hold_0001",
            "university_name": "北方工业大学",
            "queue_group_code": "304",
            "parsed_major_rows": len(rows),
            "parsed_plan_total": total,
            "special_plan_total_marked": art_total + cooperation_total,
            "exclusion_reason": "no_source_group_or_subject_code_hold_for_mapping",
            "recommended_next_action": "compare with Guangxi exam-authority group composition or obtain official group-code/selection mapping before calibration",
            "canonical_ml_entry_open": "false",
        }
    ]


def write_doc(rows: list[dict[str, object]]) -> None:
    total = sum(int(row.get("plan_count") or 0) for row in rows)
    art_total = sum(int(row.get("plan_count") or 0) for row in rows if "art_design_boundary" in str(row.get("special_type_detected", "")))
    cooperation_total = sum(int(row.get("plan_count") or 0) for row in rows if "sino_foreign_cooperation" in str(row.get("special_type_detected", "")))
    text = f"""# Reference Trend 520 Batch 9 北方工业大学 Source Packet Parse

Generated: {date.today().isoformat()}

## Scope

This parse preview converts the batch9 T1 official plan source for 北方工业大学 into Guangxi-column major plan rows. It remains outside canonical/ML and outside the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_exclusion_log.csv`

## Parse Summary

- 北方工业大学: {len(rows)} parsed Guangxi-column major rows, plan total {total}.
- Art/design rows marked for isolation: plan total {art_total}.
- Sino-foreign cooperation rows marked for isolation: plan total {cooperation_total}.

## Boundary

The source does not print Guangxi院校专业组 codes or subject/selection requirements. `queue_group_code=304` is kept only as routing context; `source_group_code` remains blank. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: build a group/subject mapping workbench for 北方工业大学 or continue official-source discovery for the next P0 rows.
"""
    DOC_OUT.write_text(text, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]]) -> None:
    total = sum(int(row.get("plan_count") or 0) for row in rows)
    marker = "## 40. 2026-05-16 batch9 北方工业大学 source-packet parse preview"
    content = f"""

{marker}

已新增 batch9 北方工业大学 T1 官方来源的 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch9_ncut_source_packet_parse.md`

覆盖结果：北方工业大学官方 2025 本科分专业招生计划 HTML 表已缓存，广西列解析出 {len(rows)} 个专业行、计划合计 {total}。其中艺术设计类和中外合作办学行已标记为特殊边界，未删除。

准入边界：来源不打印广西院校专业组代码，也不打印选科/物理类标签；`queue_group_code=304` 只保留为队列上下文，`source_group_code` 为空。`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先做北方工业大学 group/subject mapping workbench，或继续下一个 P0 官方来源发现批次。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = parse_rows()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, build_rollup(rows), ["metric", "value", "note"])
    write_csv(QA_OUT, build_qa(rows), ["qa_check", "status", "value", "note"])
    write_csv(
        EXCLUSION_OUT,
        build_exclusions(rows),
        [
            "record_id",
            "university_name",
            "queue_group_code",
            "parsed_major_rows",
            "parsed_plan_total",
            "special_plan_total_marked",
            "exclusion_reason",
            "recommended_next_action",
            "canonical_ml_entry_open",
        ],
    )
    write_doc(rows)
    write_handoff(rows)

    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    print(f"wrote {ROLLUP_OUT.relative_to(ROOT)}")
    print(f"wrote {QA_OUT.relative_to(ROOT)}")
    print(f"wrote {EXCLUSION_OUT.relative_to(ROOT)} rows=1")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
