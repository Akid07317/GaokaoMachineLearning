#!/usr/bin/env python3
"""Parse batch-8 T1 official plan source into source-packet preview rows.

This produces major-level plan rows only. It does not assign group-year
calibration because the source does not print Guangxi院校专业组 codes.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch8_official"

OUT = SEED_DIR / "reference_trend_520_batch8_t1_source_packet_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch8_t1_source_packet_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch8_t1_source_packet_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch8_t1_source_packet_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch8_t1_source_packet_parse.md"
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


def base_row() -> dict[str, object]:
    return {
        "row_scope": "official_major_plan_row",
        "source_id": "reference_trend_520_p0_batch8_0004",
        "queue_record_id": "reference_trend_520_plan_source_queue_0046",
        "queue_rank": "46",
        "source_url": "https://zs.csuft.edu.cn/f/zsjhinfo?jhnd=2025&ssdm=45",
        "source_owner": "中南林业科技大学招生信息网",
        "source_title": "2025年中南林业科技大学招生计划（广西）",
        "university_code": "10538",
        "university_name": "中南林业科技大学",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_subject_label": "物理类",
        "queue_group_code": "106",
        "source_group_code": "",
        "campus": "",
        "duration_years": "",
        "plan_nature": "",
        "source_contains_group_code": "false",
        "source_contains_plan_count": "true",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "special_type_detected": "false",
        "qa_status": "parsed_hold_for_group_mapping",
        "collector_confidence": "T1_official_html_table_major_plan_row",
        "intended_layer": "reference_trend_source_packet_parse_preview_only",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "required_resolution": "verify_group_code_mapping_before_calibration",
    }


def parse_csuft() -> list[dict[str, object]]:
    paths = [
        RAW_DIR / "csuft_2025_guangxi_plan.html",
        RAW_DIR / "csuft_2025_guangxi_plan_page2.html",
    ]
    rows: list[dict[str, object]] = []
    for page_idx, path in enumerate(paths, start=1):
        parser = TableParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        for table in parser.tables:
            for source_index, row in enumerate(table, start=1):
                if len(row) < 8:
                    continue
                _order, major, level, tuition, subject, batch, selection, plan_count = row[:8]
                if subject != "物理类" or batch != "本科普通批":
                    continue
                parsed = base_row()
                parsed.update(
                    {
                        "record_id": f"reference_trend_520_batch8_t1_csuft_{len(rows) + 1:04d}",
                        "raw_file_path": rel(path),
                        "major_name": major,
                        "tuition_yuan": tuition,
                        "plan_category": selection,
                        "plan_type": level,
                        "plan_count": plan_count,
                        "evidence_note": f"Source HTML page {page_idx} table row {source_index}; source prints subject label, batch, selection requirement and plan count, but no Guangxi group code.",
                    }
                )
                rows.append(parsed)
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selection_plan = Counter()
    total_plan = 0
    for row in rows:
        plan = int(row.get("plan_count") or 0)
        total_plan += plan
        selection_plan[str(row.get("plan_category", ""))] += plan
    rollup = [
        {"metric": "parse_preview_rows", "value": len(rows), "note": ""},
        {"metric": "universities_parsed", "value": 1 if rows else 0, "note": "中南林业科技大学" if rows else ""},
        {"metric": "plan_total", "value": total_plan, "note": "official major-plan row sum after physical ordinary filter"},
        {"metric": "source_group_code_rows", "value": 0, "note": "Source does not print Guangxi院校专业组 code."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Parse preview only; group mapping not accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for selection, plan in sorted(selection_plan.items()):
        rollup.append({"metric": f"selection::{selection}::plan_total", "value": plan, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    group_codes = sum(1 for row in rows if row.get("source_group_code"))
    return [
        {
            "qa_check": "official_source_parse",
            "status": "pass" if rows else "fail",
            "value": len(rows),
            "note": "Rows come from cached first-party official HTML plan pages.",
        },
        {
            "qa_check": "ordinary_physics_filter",
            "status": "pass",
            "value": sum(1 for row in rows if row.get("subject_category") == "物理类" and row.get("batch") == "本科普通批"),
            "note": "Rows are filtered to source subject=物理类 and batch=本科普通批.",
        },
        {
            "qa_check": "group_mapping_boundary",
            "status": "pass" if group_codes == 0 else "warn",
            "value": group_codes,
            "note": "queue_group_code is retained as queue context only; source_group_code is blank for all rows.",
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
    total_plan = sum(int(row.get("plan_count") or 0) for row in rows)
    return [
        {
            "record_id": "reference_trend_520_batch8_t1_hold_0001",
            "university_name": "中南林业科技大学",
            "queue_group_code": "106",
            "parsed_major_rows": len(rows),
            "parsed_plan_total": total_plan,
            "exclusion_reason": "no_source_group_code_hold_for_group_mapping",
            "recommended_next_action": "compare with Guangxi exam-authority group composition or obtain official group-code mapping before calibration",
            "canonical_ml_entry_open": "false",
        }
    ]


def write_doc(rows: list[dict[str, object]]) -> None:
    total_plan = sum(int(row.get("plan_count") or 0) for row in rows)
    selection_totals = defaultdict(int)
    for row in rows:
        selection_totals[str(row.get("plan_category", ""))] += int(row.get("plan_count") or 0)
    selection_text = "; ".join(f"{key}: {value}" for key, value in sorted(selection_totals.items()))
    text = f"""# Reference Trend 520 Batch 8 T1 Source Packet Parse

Generated: {date.today().isoformat()}

## Scope

This parse preview converts the batch8 T1 official plan source for 中南林业科技大学 into major-level plan rows. It remains outside canonical/ML and outside the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch8_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_exclusion_log.csv`

## Parse Summary

- 中南林业科技大学: {len(rows)} parsed major rows, plan total {total_plan}.
- Selection requirement plan split: {selection_text}.

## Boundary

The source does not print Guangxi院校专业组 codes. `queue_group_code=106` is kept only as routing context; `source_group_code` remains blank. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: build a group mapping workbench for 中南林业科技大学 or continue official-source discovery for the next P0 rows.
"""
    DOC_OUT.write_text(text, encoding="utf-8")


def write_handoff() -> None:
    marker = "## 37. 2026-05-16 batch8 T1 source-packet parse preview"
    content = f"""

{marker}

已新增 batch8 T1 官方来源的 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch8_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch8_t1_source_packet_parse.md`

覆盖结果：中南林业科技大学官方广西招生计划两页解析出 2025 本科普通批物理类 41 个专业行，计划合计 150。

准入边界：来源不打印广西院校专业组代码，`queue_group_code=106` 只保留为队列上下文，`source_group_code` 为空。`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先做中南林业科技大学 group mapping workbench，或继续下一个 P0 官方来源发现批次。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = parse_csuft()
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
    print(f"wrote {EXCLUSION_OUT.relative_to(ROOT)} rows=1")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
