#!/usr/bin/env python3
"""Parse cached Jimei University 2025 Guangxi plan source packet.

The official page includes major-level rows and a printed professional-group
column. This script keeps the result in source-packet preview only, with QA and
exclusions. It does not open canonical/ML or merge into the 32-school decision
pool.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gaokao_planner.html_tables import extract_tables_from_file  # noqa: E402


SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch13_official"

INDEX_FILES = [
    RAW_DIR / "jmu_plan_index.html",
    RAW_DIR / "jmu_plan_index_page2.html",
    RAW_DIR / "jmu_plan_index_page3.html",
]
SOURCE_HTML = RAW_DIR / "jmu_2025_guangxi_plan.html"

OUT = SEED_DIR / "reference_trend_520_batch13_jmu_source_packet_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_source_packet_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_source_packet_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch13_jmu_source_packet_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch13_jmu_source_packet_parse.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_url",
    "raw_file_path",
    "major_name",
    "first_subject",
    "required_subject",
    "program_length",
    "plan_count",
    "tuition",
    "remarks",
    "source_professional_group_code",
    "guangxi_exam_group_code_candidate",
    "source_contains_group_code",
    "special_type_flag",
    "source_packet_status",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "qa_status",
    "evidence_note",
]


GROUP_TO_QUEUE = {
    "04": ("reference_trend_520_plan_source_queue_0112", "112", "10390-104"),
    "05": ("reference_trend_520_plan_source_queue_0113", "113", "10390-105"),
    "09": ("reference_trend_520_plan_source_queue_0114", "114", "10390-109"),
    "10": ("reference_trend_520_plan_source_queue_0115", "115", "10390-110"),
    "06": ("reference_trend_520_plan_source_queue_0137", "137", "10390-106"),
    "08": ("reference_trend_520_plan_source_queue_0163", "163", "10390-108"),
    "07": ("reference_trend_520_plan_source_queue_0246", "246", "10390-107"),
    "11": ("reference_trend_520_plan_source_queue_0112|reference_trend_520_plan_source_queue_0113|reference_trend_520_plan_source_queue_0114|reference_trend_520_plan_source_queue_0115", "112|113|114|115", "10390-111_not_in_current_top_batch_window"),
}


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


def int_or_zero(value: object) -> int:
    text = str(value).strip()
    return int(text) if text.isdigit() else 0


def load_source_table() -> tuple[list[str], list[list[str]]]:
    tables = extract_tables_from_file(SOURCE_HTML)
    if not tables:
        return [], []
    table = tables[0]
    # First row is a red note spanning all columns; second row is the header.
    return table[1], table[2:]


def build_rows_and_exclusions() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    header, raw_rows = load_source_table()
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    source_total = 0
    source_major_rows = 0
    for idx, raw in enumerate(raw_rows, start=1):
        if raw and raw[0] == "合计":
            source_total = int_or_zero(raw[1] if len(raw) > 1 else "")
            exclusions.append(
                {
                    "record_id": "reference_trend_520_batch13_jmu_excluded_total",
                    "university_name": "集美大学",
                    "exclusion_scope": "summary_row",
                    "exclusion_reason": "合计 summary row, not a major row",
                    "required_resolution": "use only for QA total comparison",
                }
            )
            continue
        if len(raw) != len(header):
            exclusions.append(
                {
                    "record_id": f"reference_trend_520_batch13_jmu_excluded_malformed_{idx:04d}",
                    "university_name": "集美大学",
                    "exclusion_scope": "malformed_row",
                    "exclusion_reason": f"expected {len(header)} columns, got {len(raw)}",
                    "required_resolution": "manual source inspection if row is needed",
                }
            )
            continue
        values = dict(zip(header, raw))
        plan_count = int_or_zero(values.get("计划数", ""))
        source_major_rows += 1
        batch = values.get("批次", "")
        first_subject = values.get("科类/首先科目", "")
        group = values.get("专业组", "")
        major = values.get("专业", "")
        if batch != "本科批" or first_subject != "物理类":
            exclusions.append(
                {
                    "record_id": f"reference_trend_520_batch13_jmu_excluded_{idx:04d}",
                    "university_name": "集美大学",
                    "exclusion_scope": "non_ordinary_physical_batch",
                    "exclusion_reason": f"批次={batch}; 科类/首先科目={first_subject}; 专业组={group}",
                    "required_resolution": "keep out of 广西物理类本科普通批 preview",
                }
            )
            continue
        queue_record_id, queue_rank, exam_group_candidate = GROUP_TO_QUEUE.get(
            group,
            ("reference_trend_520_plan_source_queue_0112|reference_trend_520_plan_source_queue_0113|reference_trend_520_plan_source_queue_0114|reference_trend_520_plan_source_queue_0115", "112|113|114|115", f"10390-1{group}"),
        )
        remarks = values.get("备注", "")
        flags = []
        if "软件工程" in major or "13000" in remarks:
            flags.append("tuition_step_note")
        if "航海" in remarks:
            flags.append("navigation_related")
        rows.append(
            {
                "record_id": f"reference_trend_520_batch13_jmu_{len(rows)+1:04d}",
                "queue_record_id": queue_record_id,
                "queue_rank": queue_rank,
                "university_code": "10390",
                "university_name": "集美大学",
                "year": "2025",
                "province": "广西",
                "batch": batch,
                "subject_category": "物理类",
                "source_url": "https://zsb.jmu.edu.cn/info/1623/7855.htm",
                "raw_file_path": rel(SOURCE_HTML),
                "major_name": major,
                "first_subject": first_subject,
                "required_subject": values.get("选考科目/再选科目", ""),
                "program_length": values.get("学制", ""),
                "plan_count": plan_count,
                "tuition": values.get("学费(元/人·年)", ""),
                "remarks": remarks,
                "source_professional_group_code": group,
                "guangxi_exam_group_code_candidate": exam_group_candidate,
                "source_contains_group_code": "true",
                "special_type_flag": ";".join(flags),
                "source_packet_status": "parsed_official_html_table_preview_with_group_code_hold_for_score_rank_mapping",
                "eligible_for_intake_preview": "true_source_packet_preview_only",
                "reference_trend_pool_eligible": "false_until_score_rank_or_exam_authority_group_line_match",
                "calibration_eligible": "false_no_score_rank",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "qa_status": "source_packet_parse_preview_only",
                "evidence_note": "Official page prints professional-group code; mapping to Guangxi exam group remains candidate until score/rank line match.",
            }
        )
    metrics = {"source_total": source_total, "source_major_rows": source_major_rows}
    return rows, exclusions, metrics


def build_rollup(rows: list[dict[str, object]], exclusions: list[dict[str, object]], metrics: dict[str, int]) -> list[dict[str, object]]:
    by_group = Counter(str(row["source_professional_group_code"]) for row in rows)
    group_plan = Counter()
    for row in rows:
        group_plan[str(row["source_professional_group_code"])] += int_or_zero(row["plan_count"])
    preview_plan_sum = sum(int_or_zero(row["plan_count"]) for row in rows)
    excluded_plan_sum = metrics["source_total"] - preview_plan_sum
    return [
        {"metric": "cached_index_pages", "value": sum(path.exists() for path in INDEX_FILES), "note": "JMU plan index pages cached."},
        {"metric": "source_major_rows", "value": metrics["source_major_rows"], "note": "All major rows before exclusions."},
        {"metric": "source_total_plan_count", "value": metrics["source_total"], "note": "Official total row."},
        {"metric": "preview_physical_ordinary_rows", "value": len(rows), "note": "本科批 + 物理类 rows."},
        {"metric": "preview_physical_ordinary_plan_sum", "value": preview_plan_sum, "note": "Sum of preview rows."},
        {"metric": "excluded_plan_sum", "value": excluded_plan_sum, "note": "History/advance/summary plan count by difference."},
        {"metric": "exclusion_rows", "value": len(exclusions), "note": "Non-ordinary physical plus summary rows."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Needs score/rank or exam authority group-line match before pool intake."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No score/rank in source packet."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "ML/canonical remains closed."},
        *({"metric": f"group_row_count::{key}", "value": value, "note": ""} for key, value in sorted(by_group.items())),
        *({"metric": f"group_plan_sum::{key}", "value": value, "note": ""} for key, value in sorted(group_plan.items())),
    ]


def build_qa(rows: list[dict[str, object]], exclusions: list[dict[str, object]], metrics: dict[str, int]) -> list[dict[str, object]]:
    preview_plan_sum = sum(int_or_zero(row["plan_count"]) for row in rows)
    excluded_major_plan_sum = 0
    header, raw_rows = load_source_table()
    for raw in raw_rows:
        if raw and raw[0] == "合计":
            continue
        if len(raw) == len(header):
            values = dict(zip(header, raw))
            if not (values.get("批次") == "本科批" and values.get("科类/首先科目") == "物理类"):
                excluded_major_plan_sum += int_or_zero(values.get("计划数", ""))
    return [
        {
            "check": "cached_jmu_pages_exist",
            "status": "PASS" if SOURCE_HTML.exists() and all(path.exists() for path in INDEX_FILES) else "FAIL",
            "detail": "Plan index pages and Guangxi detail page are cached.",
        },
        {
            "check": "source_total_matches_preview_plus_excluded",
            "status": "PASS" if metrics["source_total"] == preview_plan_sum + excluded_major_plan_sum else "FAIL",
            "detail": f"source_total={metrics['source_total']}; preview={preview_plan_sum}; excluded_major={excluded_major_plan_sum}",
        },
        {
            "check": "physical_ordinary_group_codes_present",
            "status": "PASS" if rows and all(row["source_professional_group_code"] for row in rows) else "FAIL",
            "detail": "Every preview row has a printed professional-group code.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]).startswith("false") for row in rows) else "FAIL",
            "detail": "No row enters reference_trend_pool.",
        },
        {
            "check": "no_canonical_ml_entry",
            "status": "PASS" if all(str(row["canonical_ml_entry_open"]) == "false" for row in rows) else "FAIL",
            "detail": "No canonical/ML input opened.",
        },
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]]) -> None:
    lines = [
        "# Reference Trend 520 Batch13 JMU Source Packet Parse",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: parse 集美大学 official 2025 Guangxi plan detail page into a source-packet preview.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Key findings:",
        "- The official Guangxi detail page prints batch, major, first subject, required subject, plan count, remarks, and professional-group code.",
        "- 本科批 + 物理类 preview rows: 39; plan sum: 160.",
        "- Groups printed in source: 04, 05, 06, 07, 08, 09, 10, 11.",
        "",
        "Boundary:",
        "- This is source-packet parse preview only.",
        "- Group codes are printed, but score/rank group-line matching is not included in this source, so `reference_trend_pool_eligible` remains closed.",
        "- No canonical/ML output and no 32-school decision_pool merge.",
        "",
        "Rollup:",
    ]
    lines.extend(f"- {row['metric']}: {row['value']} {row['note']}".rstrip() for row in rollup)
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, exclusions, metrics = build_rows_and_exclusions()
    rollup = build_rollup(rows, exclusions, metrics)
    qa = build_qa(rows, exclusions, metrics)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, ["record_id", "university_name", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup)

    marker = "## 52. 2026-05-16 batch13 集美大学 source-packet parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增集美大学官方广西计划 source-packet parse preview：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：已缓存集美大学招生计划入口 3 页和 2025 广西招生计划明细页。官方明细页直接打印“专业组”列；本科批 + 物理类共 39 行，计划数合计 160，覆盖源内专业组 04/05/06/07/08/09/10/11。提前批航海类、历史类和合计行已写入 exclusion，不混入物理普通批预览。

准入边界：本轮只做 source-packet parse preview。虽然源页打印专业组代码，但本轮没有同步广西考试院投档分/位次线，也没有做 group-line score/rank mapping，因此 `reference_trend_pool_eligible=false_until_score_rank_or_exam_authority_group_line_match`、`calibration_eligible=false_no_score_rank`、`canonical_ml_entry_open=false`；不进入 32 所 decision_pool。下一轮可继续做 JMU group-line score/rank 匹配预览，或推进青海大学/安徽工业大学图片 OCR 审批准备。
""",
    )


if __name__ == "__main__":
    main()
