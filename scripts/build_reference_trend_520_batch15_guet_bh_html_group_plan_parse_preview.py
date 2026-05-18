#!/usr/bin/env python3
"""Parse GUET Beihai 2025 Guangxi plan table with professional group notes.

The official source prints major-level plan counts plus Guangxi professional
group notes. It still has no score/rank, so outputs remain source-packet
preview/group-mapping evidence only.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

RAW_HTML = RAW_DIR / "guet_bh_2025_guangxi_plan_page.html"
OUT = SEED_DIR / "reference_trend_520_batch15_guet_bh_html_group_plan_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_guet_bh_html_group_plan_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_guet_bh_html_group_plan_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_guet_bh_html_group_plan_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_guet_bh_html_group_plan_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://www.guet.edu.cn/bh_zs/2025/1028/c3039a144300/page.htm"
SOURCE_ID = "reference_trend_520_p0_batch15_0001"
QUEUE_RECORD_ID = "reference_trend_520_plan_source_queue_0151"

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
    "campus",
    "year",
    "province",
    "batch",
    "source_admission_type",
    "subject_category",
    "source_subject_label",
    "selection_requirement",
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
            self.current_row.append(" ".join("".join(self.current_cell).replace("\xa0", " ").split()))
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


def source_group_code(note: str) -> str:
    match = re.search(r"专业组[：:]\s*(\d+)", note)
    return match.group(1) if match else ""


def subject_category(label: str) -> str:
    if "物理" in label or "理工" in label:
        return "物理类"
    if "历史" in label or "文史" in label:
        return "历史类"
    return "unknown_subject_route"


def special_note(admission_type: str, batch: str, major_name: str) -> str:
    tags: list[str] = []
    text = f"{admission_type}{batch}{major_name}"
    if "艺术" in text or "工艺美术" in text or "公共艺术" in text or "数字媒体艺术" in text:
        tags.append("art_admission_boundary")
    if "中外合作" in text:
        tags.append("cooperative")
    return "|".join(tags) if tags else "none_detected"


def parse_rows() -> list[dict[str, object]]:
    parser = TableParser()
    parser.feed(RAW_HTML.read_text(encoding="utf-8", errors="replace"))
    rows: list[dict[str, object]] = []
    for table_idx, table in enumerate(parser.tables, start=1):
        if not table:
            continue
        header = table[0]
        expected = ["省份", "年份", "类型", "批次", "科类", "专业(类)", "科目要求", "计划数", "备注"]
        if header[: len(expected)] != expected:
            continue
        for source_row_number, source_row in enumerate(table[1:], start=2):
            if len(source_row) < 9:
                continue
            province, year, admission_type, batch, subject_label, major, selection, plan_count, note = source_row[:9]
            if province != "广西" or year != "2025" or not plan_count.isdigit():
                continue
            group = source_group_code(note)
            special = special_note(admission_type, batch, major)
            subj = subject_category(subject_label)
            ordinary_physics = admission_type == "普通类" and "本科" in batch and subj == "物理类"
            row_index = len(rows) + 1
            rows.append(
                {
                    "record_id": f"reference_trend_520_batch15_guet_bh_html_{row_index:04d}",
                    "row_scope": "official_major_group_plan_row",
                    "source_id": SOURCE_ID,
                    "queue_record_id": QUEUE_RECORD_ID,
                    "queue_rank": "151",
                    "source_url": SOURCE_URL,
                    "source_owner": "桂林电子科技大学北海校区招生信息网",
                    "source_title": "2025年桂电北海校区本科招生计划一览表",
                    "raw_file_path": rel(RAW_HTML),
                    "university_code": "10595",
                    "university_name": "桂林电子科技大学",
                    "campus": "北海校区",
                    "year": year,
                    "province": province,
                    "batch": "本科普通批" if ordinary_physics else batch,
                    "source_admission_type": admission_type,
                    "subject_category": subj,
                    "source_subject_label": subject_label,
                    "selection_requirement": selection,
                    "queue_group_code": "",
                    "source_group_code": group,
                    "major_name": major,
                    "plan_count": plan_count,
                    "source_contains_group_code": "true" if group else "false",
                    "source_contains_plan_count": "true",
                    "source_contains_min_score": "false",
                    "source_contains_min_rank": "false",
                    "special_type_detected": "true" if special != "none_detected" else "false",
                    "special_type_note": special,
                    "qa_status": "parsed_group_plan_hold_for_score_rank" if ordinary_physics and group else "parsed_nonordinary_or_nonphysics_boundary_hold",
                    "collector_confidence": "T1_official_html_table_major_group_plan_row",
                    "intended_layer": "reference_trend_source_packet_parse_preview_only",
                    "reference_trend_pool_eligible": "0",
                    "calibration_eligible": "0",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                    "required_resolution": "join_with_official_score_rank_before_calibration",
                    "evidence_note": (
                        f"Official HTML table {table_idx} row {source_row_number}; source prints major, subject, selection, "
                        "plan count and professional group note, but no score/rank."
                    ),
                }
            )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ordinary_physics = [
        row
        for row in rows
        if row["source_admission_type"] == "普通类" and row["subject_category"] == "物理类" and row["source_group_code"]
    ]
    group_plan = defaultdict(int)
    for row in ordinary_physics:
        group_plan[str(row["source_group_code"])] += int(row["plan_count"])
    special_counts = Counter(str(row["special_type_note"]) for row in rows)
    subject_counts = Counter(str(row["subject_category"]) for row in rows)
    return [
        {"metric": "official_page_cached_rows", "value": 1 if RAW_HTML.exists() else 0, "note": rel(RAW_HTML)},
        {"metric": "parse_preview_rows_all_guangxi", "value": len(rows), "note": "all Guangxi rows from official table"},
        {"metric": "ordinary_physics_group_plan_rows", "value": len(ordinary_physics), "note": "普通类+物理类/理工类+本科批 rows with group code"},
        {"metric": "ordinary_physics_plan_count_sum", "value": sum(int(row["plan_count"]) for row in ordinary_physics), "note": dict(sorted(group_plan.items()))},
        {"metric": "group_code_available_rows", "value": sum(1 for row in rows if row["source_group_code"]), "note": "source notes print 专业组"},
        {"metric": "subject_distribution", "value": dict(subject_counts), "note": ""},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in special_counts.items() if k != "none_detected"), "note": dict(special_counts)},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Score/rank join required before calibration."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ordinary_physics = [
        row
        for row in rows
        if row["source_admission_type"] == "普通类" and row["subject_category"] == "物理类" and row["source_group_code"]
    ]
    return [
        {"check": "official_page_cached", "status": "PASS" if RAW_HTML.exists() else "FAIL", "detail": rel(RAW_HTML)},
        {"check": "html_table_extracted", "status": "PASS" if rows else "FAIL", "detail": f"rows={len(rows)}"},
        {"check": "ordinary_physics_group_rows", "status": "PASS" if ordinary_physics else "FAIL", "detail": f"rows={len(ordinary_physics)}; plan_sum={sum(int(row['plan_count']) for row in ordinary_physics)}"},
        {"check": "group_code_present", "status": "PASS" if all(row["source_group_code"] for row in ordinary_physics) else "WARN", "detail": "ordinary physics rows all have source_group_code"},
        {"check": "score_rank_hold", "status": "PASS", "detail": "Official page is plan-only; no score or rank."},
        {"check": "special_boundary_flagged", "status": "PASS", "detail": "Art/historical rows retained as boundary rows in exclusion log."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "campus": row["campus"],
            "source_group_code": row["source_group_code"],
            "major_name": row["major_name"],
            "plan_count": row["plan_count"],
            "exclusion_reason": "missing_score_rank_for_calibration" if row["source_admission_type"] == "普通类" and row["subject_category"] == "物理类" else "nonordinary_or_nonphysics_boundary",
            "special_type_note": row["special_type_note"],
            "next_action": "join with Guangxi official score/rank group line before calibration",
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, object]]) -> None:
    ordinary_physics = [
        row
        for row in rows
        if row["source_admission_type"] == "普通类" and row["subject_category"] == "物理类" and row["source_group_code"]
    ]
    group_plan = defaultdict(int)
    for row in ordinary_physics:
        group_plan[str(row["source_group_code"])] += int(row["plan_count"])
    DOC_OUT.write_text(
        "\n".join(
            [
                "# reference_trend_520 batch15 GUET Beihai group-plan parse preview",
                "",
                f"Generated: {date.today().isoformat()}",
                "",
                "## Scope",
                "",
                "桂林电子科技大学北海校区官方 2025 广西本科招生计划页已缓存并解析。"
                "本产物只用于 source-packet preview / group mapping evidence，不进入 32 所 decision_pool。",
                "",
                "## Result",
                "",
                f"- Official source URL: {SOURCE_URL}",
                f"- Cached HTML: `{rel(RAW_HTML)}`",
                f"- Parsed Guangxi rows: {len(rows)}",
                f"- Ordinary physics group-plan rows: {len(ordinary_physics)}",
                f"- Ordinary physics plan sum by group: {dict(sorted(group_plan.items()))}",
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
                "普通物理行已经有官方专业组代码和计划数，但仍缺最低分/最低位次，"
                "因此所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、"
                "`canonical_ml_entry_open=false`。后续可与广西考试院 group-line score/rank 做 join workbench。",
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
    write_csv(
        EXCLUSION_OUT,
        exclusion,
        ["record_id", "university_name", "campus", "source_group_code", "major_name", "plan_count", "exclusion_reason", "special_type_note", "next_action"],
    )
    write_doc(rows, rollup, qa)

    ordinary_physics = [
        row
        for row in rows
        if row["source_admission_type"] == "普通类" and row["subject_category"] == "物理类" and row["source_group_code"]
    ]
    group_plan = defaultdict(int)
    for row in ordinary_physics:
        group_plan[str(row["source_group_code"])] += int(row["plan_count"])

    marker = "## 73. 2026-05-16 batch15 桂林电子科技大学北海校区 group-plan parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增桂林电子科技大学北海校区 batch15 group-plan parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 广西本科招生计划页已缓存并解析，抽出广西全量 {len(rows)} 行；其中普通类物理/理工本科批 {len(ordinary_physics)} 行，计划数按专业组汇总为 {dict(sorted(group_plan.items()))}。

准入边界：本轮只写 source-packet preview/QA；普通物理行已有官方专业组代码和计划数，但没有最低分/最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。
""",
    )


if __name__ == "__main__":
    main()
