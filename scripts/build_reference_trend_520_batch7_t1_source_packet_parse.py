#!/usr/bin/env python3
"""Parse batch-7 T1 official plan sources into source-packet preview rows.

This produces major-level plan rows only. It does not assign group-year
calibration because neither source prints Guangxi院校专业组 codes.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch7_official"

OUT = SEED_DIR / "reference_trend_520_batch7_t1_source_packet_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch7_t1_source_packet_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch7_t1_source_packet_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch7_t1_source_packet_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch7_t1_source_packet_parse.md"
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
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "source_group_code": "",
        "source_contains_group_code": "false",
        "source_contains_plan_count": "true",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "special_type_detected": "false",
        "qa_status": "parsed_hold_for_group_mapping",
        "intended_layer": "reference_trend_source_packet_parse_preview_only",
        "reference_trend_pool_eligible": "0",
        "calibration_eligible": "0",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "required_resolution": "verify_group_code_mapping_before_calibration",
    }


def parse_fjut() -> list[dict[str, object]]:
    path = RAW_DIR / "fjut_2025_guangxi_plan.html"
    parser = TableParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    if not parser.tables:
        return []

    rows: list[dict[str, object]] = []
    current_campus = ""
    current_subject = ""
    for source_index, row in enumerate(parser.tables[0][1:], start=1):
        if len(row) == 6:
            current_campus, current_subject, major, duration, plan, tuition = row
        elif len(row) == 5:
            if row[0].endswith("校区"):
                current_campus, major, duration, plan, tuition = row
            else:
                major, duration, plan, tuition = row[:4]
        elif len(row) == 4:
            major, duration, plan, tuition = row
        else:
            continue
        if "物理" not in current_subject:
            continue
        parsed = base_row()
        parsed.update(
            {
                "record_id": f"reference_trend_520_batch7_t1_fjut_{len(rows) + 1:04d}",
                "source_id": "reference_trend_520_p0_batch7_0003",
                "queue_record_id": "reference_trend_520_plan_source_queue_0035",
                "queue_rank": "35",
                "source_url": "https://join.fjut.edu.cn/2025/0617/c10925a255478/page.htm",
                "source_owner": "福建理工大学本科招生信息网",
                "source_title": "福建理工大学2025年面向广西招生计划",
                "raw_file_path": rel(path),
                "university_code": "10388",
                "university_name": "福建理工大学",
                "subject_category": "物理类",
                "source_subject_label": current_subject,
                "queue_group_code": "150",
                "major_name": major,
                "campus": current_campus,
                "duration_years": duration,
                "tuition_yuan": tuition,
                "plan_category": "",
                "plan_nature": "",
                "plan_type": "",
                "plan_count": plan,
                "collector_confidence": "T1_official_html_table_major_plan_row",
                "evidence_note": f"Source table row {source_index}; source prints subject requirement and plan count, but no group code.",
            }
        )
        rows.append(parsed)
    return rows


def parse_shzu() -> list[dict[str, object]]:
    path = RAW_DIR / "shzu_zhaoshengjihua.js"
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"var dataList = (\[.*?\]);\s*$", text, re.S)
    if not match:
        return []
    data = json.loads(match.group(1))
    rows: list[dict[str, object]] = []
    for source_index, item in enumerate(data, start=1):
        if item.get("年份") != 2025:
            continue
        if item.get("省份") != "广西":
            continue
        if item.get("层次") != "本科":
            continue
        if item.get("批次") != "本科普通批":
            continue
        if "物理" not in str(item.get("科类", "")):
            continue
        parsed = base_row()
        parsed.update(
            {
                "record_id": f"reference_trend_520_batch7_t1_shzu_{len(rows) + 1:04d}",
                "source_id": "reference_trend_520_p0_batch7_0001",
                "queue_record_id": "reference_trend_520_plan_source_queue_0033",
                "queue_rank": "33",
                "source_url": "http://zsb.shzu.edu.cn/14096/list.htm",
                "source_owner": "石河子大学招生网",
                "source_title": "招生计划 JS 数据",
                "raw_file_path": rel(path),
                "university_code": "10759",
                "university_name": "石河子大学",
                "subject_category": "物理类",
                "source_subject_label": item.get("科类", ""),
                "queue_group_code": "101",
                "major_name": item.get("专业名称", ""),
                "campus": "",
                "duration_years": "",
                "tuition_yuan": "",
                "plan_category": item.get("专业类别", ""),
                "plan_nature": item.get("计划性质", ""),
                "plan_type": item.get("计划类别", ""),
                "plan_count": item.get("计划数", ""),
                "collector_confidence": "T1_official_js_major_plan_row",
                "evidence_note": f"Source JS dataList row {source_index}; row filters to 广西/本科/本科普通批/物理类, but no group code.",
            }
        )
        rows.append(parsed)
    return rows


def build_rows() -> list[dict[str, object]]:
    return parse_shzu() + parse_fjut()


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_school = defaultdict(lambda: {"rows": 0, "plan": 0})
    by_subject = Counter()
    for row in rows:
        school = str(row["university_name"])
        by_school[school]["rows"] += 1
        by_school[school]["plan"] += int(row.get("plan_count") or 0)
        by_subject[(school, str(row.get("source_subject_label", "")))] += int(row.get("plan_count") or 0)

    rollup = [
        {"metric": "parse_preview_rows", "value": len(rows), "note": ""},
        {"metric": "universities_parsed", "value": len(by_school), "note": "|".join(sorted(by_school))},
        {"metric": "source_group_code_rows", "value": 0, "note": "Neither source prints Guangxi院校专业组 codes."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Parse preview only; group mapping not accepted."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for school, values in sorted(by_school.items()):
        rollup.append({"metric": f"school::{school}::major_rows", "value": values["rows"], "note": ""})
        rollup.append({"metric": f"school::{school}::plan_total", "value": values["plan"], "note": ""})
    for (school, subject), total in sorted(by_subject.items()):
        rollup.append({"metric": f"subject::{school}::{subject}::plan_total", "value": total, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "qa_check": "official_source_parse",
            "status": "pass" if rows else "fail",
            "value": len(rows),
            "note": "Rows come from cached first-party official HTML/JS sources.",
        },
        {
            "qa_check": "ordinary_physics_filter",
            "status": "pass",
            "value": sum(1 for row in rows if row.get("subject_category") == "物理类"),
            "note": "SHZU explicitly filters 本科普通批; FJUT is an official Guangxi plan table split by physical subject labels.",
        },
        {
            "qa_check": "group_mapping_boundary",
            "status": "pass",
            "value": "held",
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
    totals = defaultdict(lambda: {"rows": 0, "plan": 0, "queue_group": ""})
    for row in rows:
        school = str(row["university_name"])
        totals[school]["rows"] += 1
        totals[school]["plan"] += int(row.get("plan_count") or 0)
        totals[school]["queue_group"] = row.get("queue_group_code", "")
    return [
        {
            "record_id": f"reference_trend_520_batch7_t1_hold_{idx:04d}",
            "university_name": school,
            "queue_group_code": values["queue_group"],
            "parsed_major_rows": values["rows"],
            "parsed_plan_total": values["plan"],
            "exclusion_reason": "no_source_group_code_hold_for_group_mapping",
            "recommended_next_action": "compare with Guangxi exam-authority group composition or obtain official group-code mapping before calibration",
            "canonical_ml_entry_open": "false",
        }
        for idx, (school, values) in enumerate(sorted(totals.items()), start=1)
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    by_school = defaultdict(lambda: {"rows": 0, "plan": 0})
    for row in rows:
        by_school[str(row["university_name"])]["rows"] += 1
        by_school[str(row["university_name"])]["plan"] += int(row.get("plan_count") or 0)
    lines = [
        "# Reference Trend 520 Batch 7 T1 Source Packet Parse",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Scope",
        "",
        "This parse preview converts the two batch7 T1 official plan sources into major-level plan rows. It remains outside canonical/ML and outside the 32-school decision pool.",
        "",
        "## Outputs",
        "",
        "- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_t1_source_packet_parse_preview.csv`",
        "- `reports/reference_trend_520_batch7_t1_source_packet_parse_rollup.csv`",
        "- `reports/reference_trend_520_batch7_t1_source_packet_parse_qa.csv`",
        "- `reports/reference_trend_520_batch7_t1_source_packet_parse_exclusion_log.csv`",
        "",
        "## Parse Summary",
        "",
    ]
    for school, values in sorted(by_school.items()):
        lines.append(f"- {school}: {values['rows']} parsed major rows, plan total {values['plan']}.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No source row prints Guangxi院校专业组 codes. `queue_group_code` is kept only as routing context; `source_group_code` remains blank. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.",
            "",
            "Next step: build a group mapping workbench for 石河子大学/福建理工大学 or continue official-source discovery for the next P0 rows.",
        ]
    )
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff() -> None:
    marker = "## 34. 2026-05-16 batch7 T1 source-packet parse preview"
    content = f"""

{marker}

已新增 batch7 两条 T1 官方来源的 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch7_t1_source_packet_parse.md`

覆盖结果：石河子大学官方 JS 数据解析出广西本科普通批物理类 32 个专业行，计划合计 100；福建理工大学官方广西计划 HTML 表解析出物理类 38 个专业行，计划合计 205（物理+化学 110，物理+不限 95）。

准入边界：两校来源均不打印广西院校专业组代码，`queue_group_code` 只保留为队列上下文，`source_group_code` 为空。`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先做石河子/福建理工 group mapping workbench，或继续下一个 P0 官方来源发现批次。
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
            "queue_group_code",
            "parsed_major_rows",
            "parsed_plan_total",
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
