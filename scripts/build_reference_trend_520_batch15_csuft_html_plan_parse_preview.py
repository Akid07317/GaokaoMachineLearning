#!/usr/bin/env python3
"""Parse CSUFT 2025 Guangxi official HTML plan pages into source-packet preview.

The exact official page is paginated. This script combines both cached pages,
keeps all official rows visible for audit, and marks ordinary physical
undergraduate rows separately. Outputs stay outside canonical/ML/decision_pool.
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
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

RAW_HTML_PAGE1 = RAW_DIR / "csuft_2025_guangxi_plan_page.html"
RAW_HTML_PAGE2 = RAW_DIR / "csuft_2025_guangxi_plan_page2.html"
RAW_HTMLS = [RAW_HTML_PAGE1, RAW_HTML_PAGE2]

OUT = SEED_DIR / "reference_trend_520_batch15_csuft_html_plan_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_csuft_html_plan_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_csuft_html_plan_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_csuft_html_plan_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_csuft_html_plan_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_ID = "reference_trend_520_p0_batch15_0017"
SOURCE_URL = "https://zs.csuft.edu.cn/f/zsjhinfo?jhnd=2025&ssdm=45"
SOURCE_URL_PAGE2 = "https://zs.csuft.edu.cn/f/zsjhinfo?pageNo=2&pageSize=30&jhnd=2025&ssdm=45"

FIELDS = [
    "record_id",
    "row_scope",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "related_queue_ranks",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_path",
    "source_page_number",
    "source_row_number",
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
    "level",
    "tuition_yuan_per_year",
    "selection_requirement",
    "plan_count",
    "ordinary_physical_candidate",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "special_type_detected",
    "special_type_note",
    "qa_status",
    "collector_confidence",
    "intended_layer",
    "eligible_for_intake_preview",
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


def queue_context() -> tuple[str, str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10538"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10538"]
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "168|169", all_ranks


def special_note(major_name: str, subject_label: str, batch: str, selection: str) -> str:
    text = "|".join([major_name, subject_label, batch, selection])
    tags: list[str] = []
    if any(token in text for token in ["中外合作", "合作办学"]):
        tags.append("cooperative_boundary")
    if "体育" in text:
        tags.append("sport_admission_boundary")
    if any(token in text for token in ["艺术", "音乐", "美术", "舞蹈", "表演", "播音", "编导"]):
        tags.append("art_admission_boundary")
    if "提前批" in batch and "体育" not in batch:
        tags.append("advance_batch_boundary")
    return "|".join(tags) if tags else "none_detected"


def expected_total_rows() -> int | None:
    for path in RAW_HTMLS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"共\s*(\d+)\s*条", text)
        if match:
            return int(match.group(1))
    return None


def extract_table_rows(path: Path) -> list[list[str]]:
    parser = TableParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    for table in parser.tables:
        if not table:
            continue
        header = table[0]
        if {"序号", "专业", "层次", "科类", "批次", "备注", "计划"}.issubset(set(header)):
            return table[1:]
    return []


def parse_rows() -> list[dict[str, object]]:
    queue_ids, batch_rank, all_ranks = queue_context()
    rows: list[dict[str, object]] = []
    for page_number, path in enumerate(RAW_HTMLS, start=1):
        for source_row_number, row in enumerate(extract_table_rows(path), start=1):
            if len(row) < 7:
                continue
            source_no, major_name, level, tuition, subject_label, batch, selection, plan_count = row[:8]
            if not str(plan_count).isdigit():
                continue
            note = special_note(major_name, subject_label, batch, selection)
            ordinary_physical = (
                subject_label == "物理类"
                and level == "本科"
                and batch == "本科普通批"
                and note == "none_detected"
            )
            row_index = len(rows) + 1
            page_url = SOURCE_URL if page_number == 1 else SOURCE_URL_PAGE2
            rows.append(
                {
                    "record_id": f"reference_trend_520_batch15_csuft_html_plan_{row_index:04d}",
                    "row_scope": "official_major_plan_row",
                    "source_id": SOURCE_ID,
                    "queue_record_id": queue_ids,
                    "queue_rank": batch_rank,
                    "related_queue_ranks": all_ranks,
                    "source_url": page_url,
                    "source_owner": "中南林业科技大学本科招生网",
                    "source_title": "2025年中南林业科技大学招生计划（广西）",
                    "raw_file_path": rel(path),
                    "source_page_number": page_number,
                    "source_row_number": source_no or source_row_number,
                    "university_code": "10538",
                    "university_name": "中南林业科技大学",
                    "year": "2025",
                    "province": "广西",
                    "batch": batch,
                    "subject_category": "物理类" if "物理" in subject_label else ("历史类" if "历史" in subject_label else subject_label),
                    "source_subject_label": subject_label,
                    "queue_group_code": "",
                    "source_group_code": "",
                    "major_name": major_name,
                    "level": level,
                    "tuition_yuan_per_year": tuition,
                    "selection_requirement": selection,
                    "plan_count": plan_count,
                    "ordinary_physical_candidate": "1" if ordinary_physical else "0",
                    "source_contains_group_code": "false",
                    "source_contains_plan_count": "true",
                    "source_contains_min_score": "false",
                    "source_contains_min_rank": "false",
                    "special_type_detected": "true" if note != "none_detected" else "false",
                    "special_type_note": note,
                    "qa_status": "parsed_hold_for_group_mapping" if ordinary_physical else "excluded_from_ordinary_physical_candidate",
                    "collector_confidence": "T1_exact_official_guangxi_plan_html_table",
                    "intended_layer": "reference_trend_source_packet_parse_preview_only",
                    "eligible_for_intake_preview": "true",
                    "reference_trend_pool_eligible": "0",
                    "calibration_eligible": "0",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                    "required_resolution": "map_official_group_code_and_join_score_rank_before_calibration",
                    "evidence_note": (
                        f"Official paginated HTML page {page_number} row {source_no}; source prints major, level, tuition, "
                        "subject label, batch, selection requirement and plan count, but no Guangxi professional group, score, or rank."
                    ),
                }
            )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    plan_total = sum(int(row["plan_count"]) for row in rows)
    ordinary_rows = [row for row in rows if row["ordinary_physical_candidate"] == "1"]
    non_ordinary_rows = [row for row in rows if row["ordinary_physical_candidate"] != "1"]
    subject_counts = Counter(str(row["source_subject_label"]) for row in rows)
    batch_counts = Counter(str(row["batch"]) for row in rows)
    special_counts = Counter(str(row["special_type_note"]) for row in rows)
    return [
        {"metric": "official_pages_cached", "value": sum(1 for path in RAW_HTMLS if path.exists()), "note": "|".join(rel(path) for path in RAW_HTMLS if path.exists())},
        {"metric": "expected_total_rows_from_pagination", "value": expected_total_rows() or "", "note": "parsed from official pagination text"},
        {"metric": "parse_preview_rows", "value": len(rows), "note": "all official Guangxi rows extracted from paginated HTML tables"},
        {"metric": "plan_count_sum_all_rows", "value": plan_total, "note": "sum of official Guangxi plan_count values across all visible rows"},
        {"metric": "ordinary_physical_candidate_rows", "value": len(ordinary_rows), "note": "本科普通批 + 物理类 + no detected special boundary"},
        {"metric": "ordinary_physical_candidate_plan_sum", "value": sum(int(row["plan_count"]) for row in ordinary_rows), "note": "candidate plan-side evidence only"},
        {"metric": "non_ordinary_or_special_rows", "value": len(non_ordinary_rows), "note": "history/sport/other boundary rows kept for audit but excluded from ordinary physical candidate"},
        {"metric": "subject_label_distribution", "value": dict(subject_counts), "note": ""},
        {"metric": "batch_distribution", "value": dict(batch_counts), "note": ""},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in special_counts.items() if k != "none_detected"), "note": dict(special_counts)},
        {"metric": "group_code_available_rows", "value": 0, "note": "Official source does not print Guangxi院校专业组 code."},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan source only; no score/rank."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group and score/rank mapping required."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    expected = expected_total_rows()
    ordinary_rows = [row for row in rows if row["ordinary_physical_candidate"] == "1"]
    return [
        {"check": "official_pages_cached", "status": "PASS" if all(path.exists() for path in RAW_HTMLS) else "FAIL", "detail": "|".join(rel(path) for path in RAW_HTMLS if path.exists())},
        {"check": "html_tables_extracted", "status": "PASS" if rows else "FAIL", "detail": f"rows={len(rows)}"},
        {"check": "pagination_row_count_match", "status": "PASS" if expected == len(rows) else "WARN", "detail": f"expected={expected}; parsed={len(rows)}"},
        {
            "check": "plan_count_numeric",
            "status": "PASS" if all(str(row["plan_count"]).isdigit() for row in rows) else "FAIL",
            "detail": f"plan_sum_all={sum(int(row['plan_count']) for row in rows)}; ordinary_physical_sum={sum(int(row['plan_count']) for row in ordinary_rows)}",
        },
        {"check": "ordinary_physical_candidate_identified", "status": "PASS" if ordinary_rows else "FAIL", "detail": f"ordinary_physical_candidate_rows={len(ordinary_rows)}"},
        {"check": "non_target_rows_excluded", "status": "PASS", "detail": "history/sport/non-ordinary rows retained for audit but excluded from ordinary physical candidates"},
        {"check": "subject_group_mapping_hold", "status": "PASS", "detail": "Official page lacks Guangxi professional-group split."},
        {"check": "score_rank_hold", "status": "PASS", "detail": "Official page is plan-only; no score or rank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        if row["ordinary_physical_candidate"] == "1":
            reason = "missing_professional_group_code_and_score_rank"
        elif row["special_type_note"] != "none_detected":
            reason = f"special_or_nonordinary_boundary:{row['special_type_note']}"
        else:
            reason = "non_target_subject_or_batch_for_ordinary_physical_trend"
        out.append(
            {
                "record_id": row["record_id"],
                "university_name": row["university_name"],
                "major_name": row["major_name"],
                "batch": row["batch"],
                "source_subject_label": row["source_subject_label"],
                "plan_count": row["plan_count"],
                "ordinary_physical_candidate": row["ordinary_physical_candidate"],
                "exclusion_reason": reason,
                "special_type_note": row["special_type_note"],
                "next_action": "join with Guangxi official投档线/group context or hold as plan-side evidence only",
            }
        )
    return out


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, object]]) -> None:
    ordinary_rows = [row for row in rows if row["ordinary_physical_candidate"] == "1"]
    special_count = sum(1 for row in rows if row["special_type_note"] != "none_detected")
    DOC_OUT.write_text(
        "\n".join(
            [
                "# reference_trend_520 batch15 CSUFT HTML plan parse preview",
                "",
                f"Generated: {date.today().isoformat()}",
                "",
                "## Scope",
                "",
                "中南林业科技大学官方 2025 广西招生计划页已缓存两页并解析为 source-packet preview。"
                "本产物只用于 reference trend source evidence，不进入 32 所 decision_pool。",
                "",
                "## Result",
                "",
                f"- Official source URL: {SOURCE_URL}",
                f"- Official page 2 URL: {SOURCE_URL_PAGE2}",
                f"- Cached HTML page 1: `{rel(RAW_HTML_PAGE1)}`",
                f"- Cached HTML page 2: `{rel(RAW_HTML_PAGE2)}`",
                f"- Parsed official rows: {len(rows)}",
                f"- Parsed all-row plan count sum: {sum(int(row['plan_count']) for row in rows)}",
                f"- Ordinary physical candidate rows: {len(ordinary_rows)}",
                f"- Ordinary physical candidate plan sum: {sum(int(row['plan_count']) for row in ordinary_rows)}",
                f"- Non-target/special boundary rows: {len(rows) - len(ordinary_rows)}",
                f"- Special boundary rows: {special_count}",
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
    missing = [path for path in RAW_HTMLS if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing cached HTML page(s): {missing}")
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
        [
            "record_id",
            "university_name",
            "major_name",
            "batch",
            "source_subject_label",
            "plan_count",
            "ordinary_physical_candidate",
            "exclusion_reason",
            "special_type_note",
            "next_action",
        ],
    )
    write_doc(rows, rollup, qa)

    ordinary_rows = [row for row in rows if row["ordinary_physical_candidate"] == "1"]
    marker = "## 77. 2026-05-16 batch15 中南林业科技大学 exact Guangxi plan parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增中南林业科技大学 batch15 exact Guangxi plan parse preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方 2025 广西招生计划页两页已缓存并解析，抽出全量 {len(rows)} 行，计划数合计 {sum(int(row["plan_count"]) for row in rows)}；其中本科普通批/物理类/无特殊边界候选 {len(ordinary_rows)} 行，计划数合计 {sum(int(row["plan_count"]) for row in ordinary_rows)}。历史类与体育提前批行保留在审计/排除日志，不进入普通物理候选。

准入边界：本轮只写 source-packet preview/QA；官方页没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。
""",
    )


if __name__ == "__main__":
    main()
