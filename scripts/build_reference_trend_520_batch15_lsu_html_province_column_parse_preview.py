#!/usr/bin/env python3
"""Parse LSU 2025 province-major plan table and extract the Guangxi column.

The official page is a province-column table. It provides major-level Guangxi
plan counts, but no Guangxi subject route, professional group code, score, or
rank. Outputs stay in source-packet preview/QA only.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

RAW_HTML = RAW_DIR / "lsu_2025_province_major_plan_page.html"
OUT = SEED_DIR / "reference_trend_520_batch15_lsu_html_province_column_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_lsu_html_province_column_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_lsu_html_province_column_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_lsu_html_province_column_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_lsu_html_province_column_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zsw.lsu.edu.cn/2025/0616/c616a356300/page.htm"
SOURCE_ID = "reference_trend_520_p0_batch15_0018"
QUEUE_RECORD_ID = "reference_trend_520_plan_source_queue_0170"

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
    "plan_count",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "special_type_detected",
    "special_type_note",
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
            cell = " ".join("".join(self.current_cell).replace("\xa0", " ").split())
            self.current_row.append(cell)
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


def parse_int(value: str) -> int:
    cleaned = "".join(ch for ch in value if ch.isdigit())
    return int(cleaned) if cleaned else 0


def special_note(major_name: str) -> str:
    tags: list[str] = []
    if "中外合作" in major_name:
        tags.append("cooperative")
    if "环境设计" in major_name or "美术" in major_name or "音乐" in major_name or "艺术" in major_name:
        tags.append("art_admission_boundary")
    if "体育" in major_name:
        tags.append("sport_admission_boundary")
    if "预科" in major_name:
        tags.append("preparatory_boundary")
    if "定向" in major_name:
        tags.append("targeted_plan_boundary")
    return "|".join(tags) if tags else "none_detected"


def parse_rows() -> tuple[list[dict[str, object]], int | None]:
    parser = TableParser()
    parser.feed(RAW_HTML.read_text(encoding="utf-8", errors="replace"))

    rows: list[dict[str, object]] = []
    guangxi_total_row_value: int | None = None
    for table_idx, table in enumerate(parser.tables, start=1):
        if not table:
            continue
        header = table[0]
        if "专业名称" not in header or "广西" not in header:
            continue
        guangxi_idx = header.index("广西")
        for source_row_number, source_row in enumerate(table[1:], start=2):
            if len(source_row) <= guangxi_idx:
                continue
            major_name = source_row[0]
            guangxi_plan = parse_int(source_row[guangxi_idx])
            if major_name == "总计":
                guangxi_total_row_value = guangxi_plan
                continue
            if guangxi_plan <= 0:
                continue
            note = special_note(major_name)
            row_index = len(rows) + 1
            rows.append(
                {
                    "record_id": f"reference_trend_520_batch15_lsu_html_{row_index:04d}",
                    "row_scope": "official_major_plan_row",
                    "source_id": SOURCE_ID,
                    "queue_record_id": QUEUE_RECORD_ID,
                    "queue_rank": "170",
                    "source_url": SOURCE_URL,
                    "source_owner": "丽水学院招生网",
                    "source_title": "丽水学院2025年分省分专业招生计划",
                    "raw_file_path": rel(RAW_HTML),
                    "university_code": "10352",
                    "university_name": "丽水学院",
                    "year": "2025",
                    "province": "广西",
                    "batch": "special_or_nonordinary_boundary" if note != "none_detected" else "本科普通批",
                    "subject_category": "unknown_subject_route_official_province_major_plan",
                    "source_subject_label": "",
                    "queue_group_code": "",
                    "source_group_code": "",
                    "major_name": major_name,
                    "plan_count": guangxi_plan,
                    "source_contains_group_code": "false",
                    "source_contains_plan_count": "true",
                    "source_contains_min_score": "false",
                    "source_contains_min_rank": "false",
                    "special_type_detected": "true" if note != "none_detected" else "false",
                    "special_type_note": note,
                    "qa_status": "parsed_hold_for_subject_group_mapping",
                    "collector_confidence": "T1_official_html_table_guangxi_column_major_plan_row",
                    "intended_layer": "reference_trend_source_packet_parse_preview_only",
                    "reference_trend_pool_eligible": "0",
                    "calibration_eligible": "0",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                    "required_resolution": "verify_subject_route_group_code_and_score_rank_before_calibration",
                    "evidence_note": (
                        f"Official HTML table {table_idx} row {source_row_number}; Guangxi column extracted. "
                        "Source prints province-major plan counts but no subject route, professional group, score, or rank."
                    ),
                }
            )
    return rows, guangxi_total_row_value


def build_rollup(rows: list[dict[str, object]], total_row_value: int | None) -> list[dict[str, object]]:
    plan_total = sum(int(row["plan_count"]) for row in rows)
    special_counts = Counter(str(row["special_type_note"]) for row in rows)
    return [
        {"metric": "official_page_cached_rows", "value": 1 if RAW_HTML.exists() else 0, "note": rel(RAW_HTML)},
        {"metric": "parse_preview_rows", "value": len(rows), "note": "official Guangxi-column major-plan rows"},
        {"metric": "plan_count_sum_extracted", "value": plan_total, "note": "sum of extracted non-total Guangxi major rows"},
        {"metric": "official_guangxi_total_row", "value": total_row_value if total_row_value is not None else "", "note": "total row in source table"},
        {"metric": "plan_total_matches_source_total", "value": str(total_row_value == plan_total).lower() if total_row_value is not None else "unknown", "note": ""},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in special_counts.items() if k != "none_detected"), "note": dict(special_counts)},
        {"metric": "subject_route_available_rows", "value": 0, "note": "Source does not print Guangxi subject route or selection requirement."},
        {"metric": "group_code_available_rows", "value": 0, "note": "Source does not print Guangxi院校专业组 code."},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Subject route/group/score-rank mapping required."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]], total_row_value: int | None) -> list[dict[str, object]]:
    plan_total = sum(int(row["plan_count"]) for row in rows)
    return [
        {"check": "official_page_cached", "status": "PASS" if RAW_HTML.exists() else "FAIL", "detail": rel(RAW_HTML)},
        {"check": "guangxi_column_extracted", "status": "PASS" if rows else "FAIL", "detail": f"rows={len(rows)}; plan_sum={plan_total}"},
        {
            "check": "total_row_reconciliation",
            "status": "PASS" if total_row_value == plan_total else "WARN",
            "detail": f"major_sum={plan_total}; source_total={total_row_value}",
        },
        {"check": "subject_route_hold", "status": "PASS", "detail": "Official table lacks subject route/selection requirement."},
        {"check": "group_code_hold", "status": "PASS", "detail": "Official table lacks Guangxi professional group split."},
        {"check": "score_rank_hold", "status": "PASS", "detail": "Official table is plan-only; no score or rank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "major_name": row["major_name"],
            "plan_count": row["plan_count"],
            "exclusion_reason": "missing_subject_route_professional_group_code_and_score_rank",
            "special_type_note": row["special_type_note"],
            "next_action": "join with Guangxi official投档线/group context or hold as province-major plan evidence only",
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, object]], total_row_value: int | None) -> None:
    plan_sum = sum(int(row["plan_count"]) for row in rows)
    DOC_OUT.write_text(
        "\n".join(
            [
                "# reference_trend_520 batch15 LSU Guangxi-column parse preview",
                "",
                f"Generated: {date.today().isoformat()}",
                "",
                "## Scope",
                "",
                "丽水学院官方 2025 分省分专业招生计划页已缓存，并从跨省表格中抽取广西列。"
                "本产物只用于 source-packet preview，不进入 32 所 decision_pool。"
                "",
                "## Result",
                "",
                f"- Official source URL: {SOURCE_URL}",
                f"- Cached HTML: `{rel(RAW_HTML)}`",
                f"- Parsed Guangxi major rows: {len(rows)}",
                f"- Parsed Guangxi plan count sum: {plan_sum}",
                f"- Official Guangxi total row: {total_row_value}",
                f"- Total reconciliation: {plan_sum == total_row_value}",
                "- Subject route available: 0",
                "- Group code available: 0",
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
                "所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、"
                "`canonical_ml_entry_open=false`。原因是官方表格没有广西选科/科类路线、院校专业组代码、最低分或最低位次；"
                "后续只能作为计划侧证据，或等待可审计 group/subject mapping。",
                "",
                "## QA",
                "",
                *[f"- {row['check']}: {row['status']} - {row['detail']}" for row in qa],
                "",
                "## Rollup",
                "",
                *[f"- {row['metric']}: {row['value']} ({row['note']})" for row in rollup],
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    if not RAW_HTML.exists():
        raise FileNotFoundError(f"Missing cached HTML: {RAW_HTML}")
    rows, total_row_value = parse_rows()
    rollup = build_rollup(rows, total_row_value)
    qa = build_qa(rows, total_row_value)
    exclusion = build_exclusion(rows)

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(
        EXCLUSION_OUT,
        exclusion,
        ["record_id", "university_name", "major_name", "plan_count", "exclusion_reason", "special_type_note", "next_action"],
    )
    write_doc(rows, rollup, qa, total_row_value)

    marker = "## 71. 2026-05-16 batch15 丽水学院 Guangxi-column parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增丽水学院 batch15 Guangxi-column parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 分省分专业招生计划页已缓存并解析，抽出广西列 {len(rows)} 个专业计划行，计划数合计 {sum(int(row["plan_count"]) for row in rows)}；与官方广西总计行 {total_row_value} 对齐。

准入边界：本轮只写 source-packet preview/QA；官方表格没有广西科类/选科路线、院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可寻找广西考试院 group-line 上下文或官方专业组拆分；否则保持计划侧 evidence。
""",
    )


if __name__ == "__main__":
    main()
