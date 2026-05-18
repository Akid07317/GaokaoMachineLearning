#!/usr/bin/env python3
"""Parse HNUCM 2025 Guangxi plan rows into a source-packet preview.

The official source prints province-by-major plan counts, but it does not print
Guangxi admission group codes. This script therefore keeps the output as
noncanonical source-packet preview only.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW = ROOT / "raw_sources" / "reference_trend" / "batch12_official" / "hnucm_2025_plan.html"

OUT = SEED_DIR / "reference_trend_520_batch12_hnucm_source_packet_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch12_hnucm_source_packet_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch12_hnucm_source_packet_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch12_hnucm_source_packet_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch12_hnucm_source_packet_parse.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zhaosheng.hnucm.edu.cn/info/1143/6051.htm"
UNIVERSITY = "湖南中医药大学"
UNIVERSITY_CODE = "10541"
QUEUE_RECORD_ID = "reference_trend_520_plan_source_queue_0098"
QUEUE_RANK = "98"
QUEUE_GROUP_CODE = "105"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "university_name",
    "university_code",
    "year",
    "province",
    "batch",
    "subject_category",
    "queue_group_code",
    "source_group_code",
    "major_name",
    "major_code",
    "program_length",
    "source_subject_text",
    "published_total_plan",
    "guangxi_plan_count",
    "source_url",
    "raw_file_path",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "special_type_flag",
    "special_type_note",
    "confidence_tier",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "qa_status",
    "exclusion_reason",
    "next_action",
]


class RowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, object]]] = []
        self._in_tr = False
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._cell_attrs: dict[str, int] = {"rowspan": 1, "colspan": 1}
        self._row: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "tr":
            self._in_tr = True
            self._row = []
        elif tag.lower() in {"td", "th"} and self._in_tr:
            self._in_cell = True
            self._cell_parts = []
            attrs_dict = {key.lower(): value for key, value in attrs}
            self._cell_attrs = {
                "rowspan": int(attrs_dict.get("rowspan") or 1),
                "colspan": int(attrs_dict.get("colspan") or 1),
            }

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self._cell_parts.append(cleaned)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"td", "th"} and self._in_cell:
            self._row.append(
                {
                    "text": " ".join(self._cell_parts).strip(),
                    "rowspan": self._cell_attrs["rowspan"],
                    "colspan": self._cell_attrs["colspan"],
                }
            )
            self._in_cell = False
            self._cell_parts = []
            self._cell_attrs = {"rowspan": 1, "colspan": 1}
        elif tag.lower() == "tr" and self._in_tr:
            if any(cell["text"] for cell in self._row):
                self.rows.append(self._row)
            self._in_tr = False
            self._row = []


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def to_int(value: str) -> int:
    value = value.strip()
    if not value:
        return 0
    digits = re.sub(r"[^\d-]", "", value)
    return int(digits) if digits else 0


def expand_spans(raw_rows: list[list[dict[str, object]]]) -> list[list[str]]:
    expanded_rows: list[list[str]] = []
    active_spans: dict[int, list[object]] = {}

    for raw_row in raw_rows:
        row: list[str] = []
        col = 0

        def fill_active() -> None:
            nonlocal col
            while col in active_spans:
                text, remaining = active_spans[col]
                row.append(str(text))
                remaining = int(remaining) - 1
                if remaining <= 0:
                    del active_spans[col]
                else:
                    active_spans[col] = [text, remaining]
                col += 1

        for cell in raw_row:
            fill_active()
            text = str(cell["text"])
            rowspan = int(cell["rowspan"])
            colspan = int(cell["colspan"])
            for offset in range(colspan):
                row.append(text)
                if rowspan > 1:
                    active_spans[col + offset] = [text, rowspan - 1]
            col += colspan

        fill_active()
        expanded_rows.append(row)

    return expanded_rows


def special_note(major_name: str) -> tuple[str, str]:
    markers = [
        "拔尖",
        "卓越",
        "5+3",
        "5加4",
        "中外合作",
        "国际",
        "定向",
        "免费",
        "地方专项",
        "国家专项",
        "民族",
        "预科",
    ]
    hits = [marker for marker in markers if marker in major_name]
    if hits:
        return "true", ";".join(hits)
    return "false", ""


def parse_source() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    html = RAW.read_text(encoding="utf-8-sig", errors="replace")
    parser = RowParser()
    parser.feed(html)
    rows = expand_spans(parser.rows)

    header_idx = next(i for i, row in enumerate(rows) if "专业名称" in row and "广西" in row)
    header = rows[header_idx]
    gx_idx = header.index("广西")
    total_idx = header.index("公布合计")
    subject_idx = header.index("科类")
    name_idx = header.index("专业名称")
    code_idx = header.index("专业代码")
    length_idx = header.index("学制")

    total_row = rows[header_idx + 1]
    gx_total_published = to_int(total_row[gx_idx])

    parsed: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    all_guangxi_rows = 0
    all_guangxi_plan_sum = 0

    for raw_row in rows[header_idx + 2 :]:
        if len(raw_row) <= gx_idx:
            continue
        major_name = raw_row[name_idx].strip()
        if not major_name or major_name == "合计":
            continue
        guangxi_count = to_int(raw_row[gx_idx])
        if guangxi_count <= 0:
            continue

        all_guangxi_rows += 1
        all_guangxi_plan_sum += guangxi_count
        subject_text = raw_row[subject_idx].strip()
        is_physical = "物理" in subject_text or "理科" in subject_text
        flag, note = special_note(major_name)

        base = {
            "queue_record_id": QUEUE_RECORD_ID,
            "queue_rank": QUEUE_RANK,
            "university_name": UNIVERSITY,
            "university_code": UNIVERSITY_CODE,
            "year": "2025",
            "province": "广西",
            "batch": "本科普通批",
            "subject_category": "物理类" if is_physical else "non_physical_or_mixed",
            "queue_group_code": QUEUE_GROUP_CODE,
            "source_group_code": "",
            "major_name": major_name,
            "major_code": raw_row[code_idx].strip(),
            "program_length": raw_row[length_idx].strip(),
            "source_subject_text": subject_text,
            "published_total_plan": to_int(raw_row[total_idx]),
            "guangxi_plan_count": guangxi_count,
            "source_url": SOURCE_URL,
            "raw_file_path": rel(RAW),
            "source_contains_group_code": "false",
            "source_contains_min_score": "false",
            "source_contains_min_rank": "false",
            "source_contains_plan_count": "true",
            "special_type_flag": flag,
            "special_type_note": note,
            "confidence_tier": "T1_official_html_table_parsed_no_group_code",
            "reference_trend_pool_eligible": "false",
            "calibration_eligible": "false",
            "canonical_ml_entry_open": "false",
            "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            "qa_status": "hold_for_group_mapping_and_special_type_QA",
            "exclusion_reason": "source_does_not_print_guangxi_group_code",
            "next_action": "map official major rows to Guangxi group code 105 only if a reliable official group/profession mapping is found",
        }
        if is_physical:
            parsed.append(base)
        else:
            excluded.append(
                {
                    "record_id": f"reference_trend_520_batch12_hnucm_nonphysical_{len(excluded)+1:04d}",
                    "university_name": UNIVERSITY,
                    "major_name": major_name,
                    "source_subject_text": subject_text,
                    "guangxi_plan_count": guangxi_count,
                    "exclusion_scope": "physical_reference_trend_preview",
                    "exclusion_reason": "non_physical_subject_text",
                    "required_resolution": "keep outside Guangxi physical ordinary trend preview",
                }
            )

    for idx, row in enumerate(parsed, start=1):
        row["record_id"] = f"reference_trend_520_batch12_hnucm_{idx:04d}"

    meta = {
        "html_table_rows_seen": len(rows),
        "header_columns": len(header),
        "guangxi_column_index": gx_idx,
        "published_guangxi_total_all_subjects": gx_total_published,
        "parsed_guangxi_all_subject_rows": all_guangxi_rows,
        "parsed_guangxi_all_subject_plan_sum": all_guangxi_plan_sum,
        "parsed_guangxi_physical_rows": len(parsed),
        "parsed_guangxi_physical_plan_sum": sum(int(row["guangxi_plan_count"]) for row in parsed),
        "excluded_nonphysical_rows": len(excluded),
        "excluded_nonphysical_plan_sum": sum(int(row["guangxi_plan_count"]) for row in excluded),
    }
    return parsed, excluded, meta


def build_rollup(rows: list[dict[str, object]], excluded: list[dict[str, object]], meta: dict[str, object]) -> list[dict[str, object]]:
    specials = Counter(str(row["special_type_note"]) or "ordinary_unmarked" for row in rows)
    rollup = [
        {"metric": "source_file", "value": rel(RAW), "note": ""},
        {"metric": "source_url", "value": SOURCE_URL, "note": ""},
        {"metric": "published_guangxi_total_all_subjects", "value": meta["published_guangxi_total_all_subjects"], "note": "Header total row for Guangxi."},
        {"metric": "parsed_guangxi_all_subject_rows", "value": meta["parsed_guangxi_all_subject_rows"], "note": ""},
        {"metric": "parsed_guangxi_all_subject_plan_sum", "value": meta["parsed_guangxi_all_subject_plan_sum"], "note": ""},
        {"metric": "parsed_guangxi_physical_rows", "value": meta["parsed_guangxi_physical_rows"], "note": ""},
        {"metric": "parsed_guangxi_physical_plan_sum", "value": meta["parsed_guangxi_physical_plan_sum"], "note": "Source subject contains 理科 or 物理."},
        {"metric": "excluded_nonphysical_rows", "value": meta["excluded_nonphysical_rows"], "note": ""},
        {"metric": "excluded_nonphysical_plan_sum", "value": meta["excluded_nonphysical_plan_sum"], "note": ""},
        {"metric": "special_type_flagged_rows", "value": sum(str(row["special_type_flag"]) == "true" for row in rows), "note": "Flagged, not deleted."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No group code printed by source."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Group-year calibration closed pending mapping."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
    ]
    rollup.extend({"metric": f"special::{key}", "value": value, "note": ""} for key, value in sorted(specials.items()))
    return rollup


def build_qa(rows: list[dict[str, object]], meta: dict[str, object]) -> list[dict[str, object]]:
    total_matches = int(meta["published_guangxi_total_all_subjects"]) == int(meta["parsed_guangxi_all_subject_plan_sum"])
    return [
        {
            "check": "raw_file_exists",
            "status": "PASS" if RAW.exists() and RAW.stat().st_size > 0 else "FAIL",
            "detail": f"{rel(RAW)} bytes={RAW.stat().st_size if RAW.exists() else 0}",
        },
        {
            "check": "guangxi_total_matches_parsed_rows",
            "status": "PASS" if total_matches else "WARN",
            "detail": f"published={meta['published_guangxi_total_all_subjects']} parsed_all_subject_sum={meta['parsed_guangxi_all_subject_plan_sum']}",
        },
        {
            "check": "physical_rows_extracted",
            "status": "PASS" if rows else "FAIL",
            "detail": f"physical_rows={len(rows)} physical_plan_sum={meta['parsed_guangxi_physical_plan_sum']}",
        },
        {
            "check": "no_source_group_code",
            "status": "PASS" if all(not row["source_group_code"] for row in rows) else "FAIL",
            "detail": "Official table has province/major plan counts but does not print Guangxi院校专业组代码.",
        },
        {
            "check": "no_reference_trend_pool_intake",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "false" for row in rows) else "FAIL",
            "detail": "No reference trend pool rows opened.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(str(row["canonical_ml_entry_open"]) == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML input opened.",
        },
    ]


def build_exclusion(rows: list[dict[str, object]], excluded: list[dict[str, object]]) -> list[dict[str, object]]:
    group_hold = [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "major_name": row["major_name"],
            "source_subject_text": row["source_subject_text"],
            "guangxi_plan_count": row["guangxi_plan_count"],
            "exclusion_scope": "reference_trend_pool_calibration",
            "exclusion_reason": row["exclusion_reason"],
            "required_resolution": row["next_action"],
        }
        for row in rows
    ]
    return group_hold + excluded


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], meta: dict[str, object]) -> None:
    lines = [
        "# Reference Trend 520 Batch12 HNUCM Source Packet Parse",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Scope: 湖南中医药大学 official 2025 province-by-major plan HTML table.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Result:",
        f"- Guangxi all-subject published total: {meta['published_guangxi_total_all_subjects']}",
        f"- Parsed Guangxi all-subject rows/sum: {meta['parsed_guangxi_all_subject_rows']} / {meta['parsed_guangxi_all_subject_plan_sum']}",
        f"- Parsed Guangxi physical rows/sum: {meta['parsed_guangxi_physical_rows']} / {meta['parsed_guangxi_physical_plan_sum']}",
        f"- Nonphysical excluded rows/sum: {meta['excluded_nonphysical_rows']} / {meta['excluded_nonphysical_plan_sum']}",
        "",
        "Boundary:",
        "- The source table does not print Guangxi院校专业组代码.",
        "- `queue_group_code=105` is retained only as queue context, not accepted as source group mapping.",
        "- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.",
        "",
        "Rollup:",
    ]
    lines.extend(f"- {row['metric']}: {row['value']} {row['note']}".rstrip() for row in rollup)
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, excluded, meta = parse_source()
    rollup = build_rollup(rows, excluded, meta)
    qa = build_qa(rows, meta)
    exclusion = build_exclusion(rows, excluded)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "major_name", "source_subject_text", "guangxi_plan_count", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup, meta)

    marker = "## 48. 2026-05-16 batch12 湖南中医药大学 source-packet parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增湖南中医药大学官方 HTML 表 source-packet parse preview：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：官方 2025 分省分专业招生计划 HTML 已缓存到 `{rel(RAW)}`。广西全科类发布合计 {meta['published_guangxi_total_all_subjects']}，解析出的广西全科类计划合计 {meta['parsed_guangxi_all_subject_plan_sum']}；其中广西物理/理科类专业行 {meta['parsed_guangxi_physical_rows']} 行、计划合计 {meta['parsed_guangxi_physical_plan_sum']}。非物理类行已写入 exclusion，不混入物理趋势预览。

准入边界：来源提供专业-省份计划数，但不打印广西院校专业组代码；`queue_group_code=105` 只保留为队列上下文，不能作为 source_group_code。所有行 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮若要推进，需要寻找可靠的官方组码/专业映射，或继续 batch12 中浙江海洋大学、温州医科大学、重庆中医药学院等候选的缓存解析。
""",
    )


if __name__ == "__main__":
    main()
