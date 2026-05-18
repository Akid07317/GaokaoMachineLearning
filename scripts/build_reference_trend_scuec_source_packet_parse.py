#!/usr/bin/env python3
"""Parse SCUEC official pages into source-packet previews.

This script fetches two official 中南民族大学招生信息网 pages that passed
source-candidate QA, saves raw HTML for audit, and emits non-canonical
source-packet parse previews. It does not create trend records or ML inputs.
"""

from __future__ import annotations

import csv
import re
import sys
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "scuec"

OUT = SEED_DIR / "reference_trend_scuec_source_packet_parse_preview.csv"
QA_OUT = REPORT_DIR / "reference_trend_scuec_source_packet_parse_qa.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_scuec_source_packet_parse_rollup.csv"
DOC_OUT = DOCS_DIR / "reference_trend_scuec_source_packet_parse.md"

PLAN_URL = "https://zsb.scuec.edu.cn/info/1020/2469.htm"
SCORE_URL = "https://zsb.scuec.edu.cn/info/1031/2476.htm"

SOURCE_PAGES = [
    {
        "source_id": "scuec_2025_physics_plan_official",
        "url": PLAN_URL,
        "raw_name": "scuec_2025_physics_plan.html",
        "source_title": "2025年普通理工/物理类招生计划（不含综合改革省份）",
        "year": "2025",
        "source_role": "plan_count_and_major_structure_candidate",
    },
    {
        "source_id": "scuec_2024_312_score_official",
        "url": SCORE_URL,
        "raw_name": "scuec_2024_312_score.html",
        "source_title": "2024年“3+1+2”高考改革省份录取分数统计",
        "year": "2024",
        "source_role": "score_group_reference_candidate",
    },
]

PREVIEW_FIELDS = [
    "record_id",
    "source_id",
    "source_url",
    "raw_file_path",
    "source_owner",
    "source_title",
    "year",
    "province",
    "batch",
    "subject_category",
    "round_type",
    "university_code",
    "university_name",
    "source_role",
    "source_row_label",
    "group_or_selection_label",
    "major_or_category_name",
    "plan_count",
    "min_score",
    "min_rank",
    "batch_line",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "special_type_detected",
    "parse_status",
    "field_gaps",
    "eligible_for_trend_record",
    "calibration_eligible",
    "qa_note",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._current_table = []
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            text = data.replace("\xa0", " ").strip()
            if text:
                self._current_cell.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_row.append(" ".join(self._current_cell).strip())
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            if any(cell for cell in self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            self.tables.append(self._current_table)
            self._current_table = None


def fetch_html(url: str, raw_path: Path) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(data)
    return data.decode("utf-8-sig", errors="replace")


def parse_tables(html: str) -> list[list[list[str]]]:
    parser = TableParser()
    parser.feed(html)
    return parser.tables


def find_table(tables: list[list[list[str]]], required_terms: set[str]) -> list[list[str]]:
    for table in tables:
        flat = {cell for row in table for cell in row}
        if required_terms.issubset(flat):
            return table
    return []


def normalize_number(value: str) -> str:
    value = value.strip()
    if not value or value == "-":
        return ""
    if re.fullmatch(r"\d+(\.0)?", value):
        return str(int(float(value)))
    return value


def detect_special(label: str) -> str:
    if "预科" in label:
        return "preparatory_exclude"
    if "国家专项" in label:
        return "national_special_exclude"
    return "ordinary_candidate"


def plan_rows(page: dict[str, str], table: list[list[str]], raw_path: Path) -> list[dict[str, str]]:
    if not table:
        return []
    header = table[0]
    try:
        gx_index = header.index("广西")
    except ValueError:
        return []

    rows: list[dict[str, str]] = []
    for raw in table[1:]:
        if len(raw) <= gx_index:
            continue
        major = raw[0].strip()
        plan = normalize_number(raw[gx_index])
        if not major or not plan:
            continue
        special = detect_special(major)
        rows.append(
            {
                "source_id": page["source_id"],
                "source_url": page["url"],
                "raw_file_path": str(raw_path),
                "source_owner": "中南民族大学本科招生信息网",
                "source_title": page["source_title"],
                "year": page["year"],
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "round_type": "ordinary_plan",
                "university_code": "10524",
                "university_name": "中南民族大学",
                "source_role": page["source_role"],
                "source_row_label": major,
                "group_or_selection_label": "",
                "major_or_category_name": major,
                "plan_count": plan,
                "min_score": "",
                "min_rank": "",
                "batch_line": "",
                "source_contains_group_code": "false",
                "source_contains_plan_count": "true",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "special_type_detected": special,
                "parse_status": "parsed_plan_row" if special == "ordinary_candidate" else "parsed_excluded_special_type",
                "field_gaps": "explicit_university_group_code|min_score|min_rank",
                "eligible_for_trend_record": "false",
                "calibration_eligible": "false",
                "qa_note": "Official plan row parsed from Guangxi column; no explicit Guangxi院校专业组 code in source.",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_parse_only_not_decision_pool",
            }
        )
    return rows


def score_rows(page: dict[str, str], table: list[list[str]], raw_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current_province = ""
    category_names = {"国家专项", "普通类", "预科"}
    for raw in table[1:]:
        if not raw:
            continue
        if raw[0] in category_names:
            province = current_province
            category = raw[0]
            values = raw[1:]
        else:
            province = raw[0]
            current_province = province
            category = raw[1] if len(raw) > 1 else ""
            values = raw[2:]
        if province != "广西":
            continue
        special = detect_special(category)
        labels = [
            ("历史+不限组 最低分", "历史类"),
            ("历史+政治组 最低分", "历史类"),
            ("历史类批次线", "历史类"),
            ("物理+不限组 最低分", "物理类"),
            ("物理+化学(1组)最低分", "物理类"),
            ("物理+化学(2组)最低分", "物理类"),
            ("物理类批次线", "物理类"),
        ]
        for (label, subject), value in zip(labels, values):
            value = normalize_number(value)
            if not value or subject != "物理类":
                continue
            is_batch_line = label == "物理类批次线"
            is_score = not is_batch_line
            rows.append(
                {
                    "source_id": page["source_id"],
                    "source_url": page["url"],
                    "raw_file_path": str(raw_path),
                    "source_owner": "中南民族大学本科招生信息网",
                    "source_title": page["source_title"],
                    "year": page["year"],
                    "province": "广西",
                    "batch": "本科普通批",
                    "subject_category": subject,
                    "round_type": "ordinary_score_reference",
                    "university_code": "10524",
                    "university_name": "中南民族大学",
                    "source_role": page["source_role"],
                    "source_row_label": category,
                    "group_or_selection_label": label,
                    "major_or_category_name": "",
                    "plan_count": "",
                    "min_score": value if is_score else "",
                    "min_rank": "",
                    "batch_line": value if is_batch_line else "",
                    "source_contains_group_code": "false",
                    "source_contains_plan_count": "false",
                    "source_contains_min_score": "true" if is_score else "false",
                    "source_contains_min_rank": "false",
                    "special_type_detected": special,
                    "parse_status": "parsed_score_reference" if special == "ordinary_candidate" else "parsed_excluded_special_type",
                    "field_gaps": "explicit_university_group_code|plan_count|min_rank",
                    "eligible_for_trend_record": "false",
                    "calibration_eligible": "false",
                    "qa_note": "Official score row parsed; no minimum rank and labels are selection groups rather than Guangxi院校专业组 codes.",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "reference_trend_source_packet_parse_only_not_decision_pool",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> None:
    all_rows: list[dict[str, str]] = []
    table_counts: dict[str, int] = {}
    for page in SOURCE_PAGES:
        raw_path = RAW_DIR / page["raw_name"]
        if raw_path.exists():
            html = raw_path.read_text(encoding="utf-8-sig", errors="replace")
        else:
            html = fetch_html(page["url"], raw_path)
        tables = parse_tables(html)
        table_counts[page["source_id"]] = len(tables)
        if page["source_role"].startswith("plan"):
            table = find_table(tables, {"专业名称", "广西"})
            all_rows.extend(plan_rows(page, table, raw_path))
        else:
            table = find_table(tables, {"省份", "招生类别"})
            all_rows.extend(score_rows(page, table, raw_path))

    for index, row in enumerate(all_rows, start=1):
        row["record_id"] = f"reference_trend_scuec_source_parse_{index:04d}"
    write_csv(OUT, all_rows, PREVIEW_FIELDS)

    qa_rows = []
    for row in all_rows:
        blocking = []
        if row["special_type_detected"] != "ordinary_candidate":
            blocking.append("special_type_excluded")
        if row["source_contains_group_code"] != "true":
            blocking.append("missing_explicit_group_code")
        if row["source_contains_min_rank"] != "true":
            blocking.append("missing_min_rank")
        if not row["plan_count"] and not row["min_score"]:
            blocking.append("no_plan_or_score_value")
        qa_rows.append(
            {
                "record_id": row["record_id"],
                "source_id": row["source_id"],
                "university_name": row["university_name"],
                "source_row_label": row["source_row_label"],
                "group_or_selection_label": row["group_or_selection_label"],
                "qa_status": "source_packet_parse_ok_not_trend_eligible" if row["special_type_detected"] == "ordinary_candidate" else "excluded_special_type",
                "blocking_issues": "|".join(blocking),
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_source_packet_parse_only_not_decision_pool",
            }
        )
    write_csv(
        QA_OUT,
        qa_rows,
        [
            "record_id",
            "source_id",
            "university_name",
            "source_row_label",
            "group_or_selection_label",
            "qa_status",
            "blocking_issues",
            "canonical_ml_entry_open",
            "decision_pool_boundary",
        ],
    )

    by_source = Counter(row["source_id"] for row in all_rows)
    by_status = Counter(row["parse_status"] for row in all_rows)
    rollup = [
        {"metric": "scuec_source_packet_parse_rows", "value": len(all_rows)},
        {"metric": "plan_parse_rows", "value": by_source.get("scuec_2025_physics_plan_official", 0)},
        {"metric": "score_parse_rows", "value": by_source.get("scuec_2024_312_score_official", 0)},
        {"metric": "ordinary_candidate_rows", "value": sum(1 for row in all_rows if row["special_type_detected"] == "ordinary_candidate")},
        {"metric": "excluded_special_type_rows", "value": sum(1 for row in all_rows if row["special_type_detected"] != "ordinary_candidate")},
        {"metric": "trend_record_eligible_rows", "value": 0},
        {"metric": "calibration_eligible_rows", "value": 0},
        {"metric": "source_tables_fetched", "value": sum(table_counts.values())},
        {"metric": "canonical_ml_entry_open", "value": "false"},
        {"metric": "decision_pool_expansion_performed", "value": "false"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value"])

    DOC_OUT.write_text(
        "\n".join(
            [
                "# Reference Trend SCUEC Source Packet Parse",
                "",
                "日期：2026-05-16",
                "",
                "## 结论",
                "",
                "已把中南民族大学两条 T1 官方候选页推进到 source packet 解析预览层。2025 计划页可抽取广西列计划数；2024 分数页可抽取广西普通类物理组分数参考。但两者都缺显式广西院校专业组代码，分数页也缺最低位次，因此本轮仍不生成 trend record，不进入 calibration/canonical/ML。",
                "",
                "## 覆盖",
                "",
                f"- parsed rows: {len(all_rows)}",
                f"- plan rows: {by_source.get('scuec_2025_physics_plan_official', 0)}",
                f"- score/reference rows: {by_source.get('scuec_2024_312_score_official', 0)}",
                f"- ordinary candidate rows: {sum(1 for row in all_rows if row['special_type_detected'] == 'ordinary_candidate')}",
                f"- excluded special-type rows: {sum(1 for row in all_rows if row['special_type_detected'] != 'ordinary_candidate')}",
                f"- parse status counts: {dict(by_status)}",
                "",
                "## 下一步",
                "",
                "- 将普通候选行继续用于 group mapping QA，而不是直接视为院校专业组-year。",
                "- 用广西考试院投档线或一分一档补齐最低位次后，才能评估 calibration_eligible。",
                "- 保持 32 所 decision_pool、canonical 和 ML 入口关闭。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"scuec_source_packet_parse_rows={len(all_rows)}")
    print(f"ordinary_candidate_rows={rollup[3]['value']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
