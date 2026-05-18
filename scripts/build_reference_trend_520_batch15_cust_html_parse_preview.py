#!/usr/bin/env python3
"""Parse CUST 2025 Guangxi official HTML plan page into source-packet preview.

This stays in the non-canonical source-packet layer. The official page has
major-level plan rows and selection requirements, but no Guangxi professional
group code, score, or rank.
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

RAW_HTML = RAW_DIR / "cust_2025_guangxi_plan_mobile_page.html"
OUT = SEED_DIR / "reference_trend_520_batch15_cust_html_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_cust_html_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_cust_html_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_cust_html_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_cust_html_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zsb.cust.edu.cn/gszsjhcx/gx_1/2025/index_mobile.htm"
SOURCE_ID = "reference_trend_520_p0_batch15_0011"
QUEUE_RECORD_ID = "reference_trend_520_plan_source_queue_0161"

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
    "selection_requirement",
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


def special_note(major_name: str) -> str:
    tags: list[str] = []
    if "中外合作" in major_name:
        tags.append("cooperative")
    if "艺术" in major_name:
        tags.append("art_admission_boundary")
    if "体育" in major_name:
        tags.append("sport_admission_boundary")
    return "|".join(tags) if tags else "none_detected"


def parse_rows() -> list[dict[str, object]]:
    parser = TableParser()
    parser.feed(RAW_HTML.read_text(encoding="utf-8", errors="replace"))

    rows: list[dict[str, object]] = []
    for table_idx, table in enumerate(parser.tables, start=1):
        if not table:
            continue
        header = table[0]
        if "专业（类）" not in header or "招生计划" not in header:
            continue
        for source_row_number, row in enumerate(table[1:], start=2):
            if len(row) < 4:
                continue
            major_name, subject_label, selection_requirement, plan_count = row[:4]
            if not plan_count.isdigit():
                continue
            note = special_note(major_name)
            row_index = len(rows) + 1
            rows.append(
                {
                    "record_id": f"reference_trend_520_batch15_cust_html_{row_index:04d}",
                    "row_scope": "official_major_plan_row",
                    "source_id": SOURCE_ID,
                    "queue_record_id": QUEUE_RECORD_ID,
                    "queue_rank": "161",
                    "source_url": SOURCE_URL,
                    "source_owner": "长春理工大学本科招生网",
                    "source_title": "2025年广西招生计划",
                    "raw_file_path": rel(RAW_HTML),
                    "university_code": "10186",
                    "university_name": "长春理工大学",
                    "year": "2025",
                    "province": "广西",
                    "batch": "本科普通批",
                    "subject_category": "物理类" if "物理" in subject_label else "unknown_subject_route",
                    "source_subject_label": subject_label,
                    "queue_group_code": "",
                    "source_group_code": "",
                    "major_name": major_name,
                    "selection_requirement": selection_requirement,
                    "plan_count": plan_count,
                    "source_contains_group_code": "false",
                    "source_contains_plan_count": "true",
                    "source_contains_min_score": "false",
                    "source_contains_min_rank": "false",
                    "special_type_detected": "true" if note != "none_detected" else "false",
                    "special_type_note": note,
                    "qa_status": "parsed_hold_for_group_mapping",
                    "collector_confidence": "T1_official_html_table_major_plan_row",
                    "intended_layer": "reference_trend_source_packet_parse_preview_only",
                    "reference_trend_pool_eligible": "0",
                    "calibration_eligible": "0",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                    "required_resolution": "verify_group_code_mapping_and_score_rank_before_calibration",
                    "evidence_note": (
                        f"Official HTML table {table_idx} row {source_row_number}; source prints major, "
                        "subject label, selection requirement and plan count, but no Guangxi professional group, score, or rank."
                    ),
                }
            )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    plan_total = sum(int(row["plan_count"]) for row in rows)
    special_counts = Counter(str(row["special_type_note"]) for row in rows)
    subject_counts = Counter(str(row["source_subject_label"]) for row in rows)
    return [
        {"metric": "official_page_cached_rows", "value": 1 if RAW_HTML.exists() else 0, "note": rel(RAW_HTML)},
        {"metric": "parse_preview_rows", "value": len(rows), "note": "official major-plan rows extracted from static HTML table"},
        {"metric": "plan_count_sum_extracted", "value": plan_total, "note": "sum of official Guangxi plan_count values"},
        {"metric": "subject_label_distribution", "value": dict(subject_counts), "note": ""},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in special_counts.items() if k != "none_detected"), "note": dict(special_counts)},
        {"metric": "group_code_available_rows", "value": 0, "note": "Source does not print Guangxi院校专业组 code."},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group and score/rank mapping required."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    all_physics = all(row["subject_category"] == "物理类" for row in rows)
    return [
        {"check": "official_page_cached", "status": "PASS" if RAW_HTML.exists() else "FAIL", "detail": rel(RAW_HTML)},
        {"check": "html_table_extracted", "status": "PASS" if rows else "FAIL", "detail": f"rows={len(rows)}"},
        {
            "check": "plan_count_numeric",
            "status": "PASS" if all(str(row["plan_count"]).isdigit() for row in rows) else "FAIL",
            "detail": f"plan_sum={sum(int(row['plan_count']) for row in rows)}" if rows else "",
        },
        {"check": "subject_label_physics", "status": "PASS" if all_physics else "WARN", "detail": "all rows source_subject_label=物理类" if all_physics else "non-physics labels found"},
        {"check": "subject_group_mapping_hold", "status": "PASS", "detail": "Official page lacks Guangxi professional-group split."},
        {"check": "score_rank_hold", "status": "PASS", "detail": "Official page is plan-only; no score or rank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "major_name": row["major_name"],
            "plan_count": row["plan_count"],
            "exclusion_reason": "missing_professional_group_code_and_score_rank",
            "special_type_note": row["special_type_note"],
            "next_action": "join with Guangxi official投档线/group context or hold as plan-side evidence only",
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, object]]) -> None:
    plan_sum = sum(int(row["plan_count"]) for row in rows)
    special_count = sum(1 for row in rows if row["special_type_note"] != "none_detected")
    DOC_OUT.write_text(
        "\n".join(
            [
                "# reference_trend_520 batch15 CUST HTML parse preview",
                "",
                f"Generated: {date.today().isoformat()}",
                "",
                "## Scope",
                "",
                "长春理工大学官方 2025 广西招生计划页已缓存并解析为 source-packet preview。"
                "本产物只用于 reference trend source evidence，不进入 32 所 decision_pool。"
                "",
                "## Result",
                "",
                f"- Official source URL: {SOURCE_URL}",
                f"- Cached HTML: `{rel(RAW_HTML)}`",
                f"- Parsed major plan rows: {len(rows)}",
                f"- Parsed plan count sum: {plan_sum}",
                f"- Special/cooperative boundary rows: {special_count}",
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
                "`canonical_ml_entry_open=false`。原因是官方计划页没有广西院校专业组代码、最低分或最低位次；"
                "后续必须与广西考试院投档线/专业组上下文或官方组拆分证据做可审计映射。",
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
    rows = parse_rows()
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    exclusion = build_exclusion(rows)

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "major_name", "plan_count", "exclusion_reason", "special_type_note", "next_action"])
    write_doc(rows, rollup, qa)

    marker = "## 70. 2026-05-16 batch15 长春理工大学 HTML parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增长春理工大学 batch15 HTML parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 广西招生计划静态 HTML 表格已缓存并解析，抽出 {len(rows)} 个物理类专业计划行，计划数合计 {sum(int(row["plan_count"]) for row in rows)}；其中 {sum(1 for row in rows if row["special_type_note"] != "none_detected")} 行带中外合作/特殊边界标记。

准入边界：本轮只写 source-packet preview/QA；官方页没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可用广西考试院投档线/专业组上下文做 group mapping workbench，或保持计划侧 evidence。
""",
    )


if __name__ == "__main__":
    main()
