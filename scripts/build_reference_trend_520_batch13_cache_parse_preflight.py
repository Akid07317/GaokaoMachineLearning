#!/usr/bin/env python3
"""Build batch-13 cache/parse preflight outputs for newly cached official pages.

The script extracts safe row-level previews only where the cached official HTML
contains plain tables. Image-only and aggregate-only sources remain in readiness
or exclusion states. No row is opened to canonical, ML, or the 32-school
decision pool.
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

OUT = SEED_DIR / "reference_trend_520_batch13_cache_parse_preflight_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch13_cache_parse_preflight_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch13_cache_parse_preflight_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch13_cache_parse_preflight_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch13_cache_parse_preflight.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FILES = {
    "haust": RAW_DIR / "haust_2025_guangxi_plan.html",
    "hqu": RAW_DIR / "hqu_2025_plan.html",
    "suse": RAW_DIR / "suse_2025_plan.html",
    "hrbmu_index": RAW_DIR / "hrbmu_zhaosheng_index.html",
    "hrbmu": RAW_DIR / "hrbmu_2025_guangxi_plan.html",
}

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
    "row_type",
    "source_url",
    "raw_file_path",
    "major_name",
    "major_category",
    "program_length",
    "tuition",
    "campus",
    "plan_nature",
    "plan_count",
    "national_special_plan_count",
    "total_plan_count",
    "source_group_code",
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
    if not text:
        return 0
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def base(row: dict[str, object]) -> dict[str, object]:
    common = {
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "source_group_code": "",
        "source_contains_group_code": "false",
        "eligible_for_intake_preview": "false_until_group_code_or_exam_authority_mapping_QA",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "qa_status": "source_packet_parse_preview_only",
    }
    common.update(row)
    return common


def select_table(path: Path, expected_first_cell: str) -> list[list[str]]:
    tables = extract_tables_from_file(path)
    for table in tables:
        if table and table[0] and table[0][0] == expected_first_cell:
            return table
    return []


def parse_haust(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    path = FILES["haust"]
    table = select_table(path, "省份")
    header = table[0] if table else []
    for index, raw in enumerate(table[1:], start=1):
        values = dict(zip(header, raw))
        subject = values.get("科类", "")
        batch = values.get("批次", "")
        if subject != "物理类" or batch != "本科普通批":
            exclusions.append(
                {
                    "record_id": f"reference_trend_520_batch13_haust_excluded_{index:04d}",
                    "university_name": "河南科技大学",
                    "exclusion_scope": "non_physical_or_non_ordinary_batch",
                    "exclusion_reason": f"科类={subject}; 批次={batch}",
                    "required_resolution": "keep excluded from 广西物理类本科普通批 preview",
                }
            )
            continue
        major = values.get("专业名称", "")
        rows.append(
            base(
                {
                    "record_id": f"reference_trend_520_batch13_haust_{len(rows)+1:04d}",
                    "queue_record_id": "reference_trend_520_plan_source_queue_0129",
                    "queue_rank": "129",
                    "university_code": "10464",
                    "university_name": "河南科技大学",
                    "subject_category": subject,
                    "row_type": "official_major_plan_preview_no_group_code",
                    "source_url": "https://zjc.haust.edu.cn/info/1142/25594.htm",
                    "raw_file_path": rel(path),
                    "major_name": major,
                    "major_category": values.get("专业类别", ""),
                    "program_length": values.get("学制", ""),
                    "tuition": values.get("收费标准", ""),
                    "campus": values.get("办学地点", ""),
                    "plan_nature": values.get("计划性质", ""),
                    "plan_count": int_or_zero(values.get("招生计划数", "")),
                    "national_special_plan_count": 0,
                    "total_plan_count": "",
                    "special_type_flag": "cooperation" if "合作" in major else "",
                    "source_packet_status": "parsed_official_html_table_preview_hold_for_group_code_mapping",
                    "evidence_note": "Official HTML table has major-level Guangxi physical ordinary plan rows but no printed院校专业组 code.",
                }
            )
        )


def parse_hrbmu(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    path = FILES["hrbmu"]
    table = select_table(path, "专业名称")
    header = table[0] if table else []
    for index, raw in enumerate(table[1:], start=1):
        values = dict(zip(header, raw))
        major = values.get("专业名称", "")
        subject = values.get("科类", "")
        if major == "计划总数":
            exclusions.append(
                {
                    "record_id": "reference_trend_520_batch13_hrbmu_excluded_total",
                    "university_name": "哈尔滨医科大学",
                    "exclusion_scope": "summary_row",
                    "exclusion_reason": "计划总数 summary row, not a major row",
                    "required_resolution": "use only for QA total comparison, not as program-year record",
                }
            )
            continue
        if subject != "理":
            exclusions.append(
                {
                    "record_id": f"reference_trend_520_batch13_hrbmu_excluded_{index:04d}",
                    "university_name": "哈尔滨医科大学",
                    "exclusion_scope": "non_physical_proxy_subject",
                    "exclusion_reason": f"科类={subject}",
                    "required_resolution": "keep excluded from 广西物理/理科 preview",
                }
            )
            continue
        plan_count = int_or_zero(values.get("广西", ""))
        national_special = int_or_zero(values.get("国家专项", ""))
        if plan_count == 0 and national_special == 0:
            continue
        note = values.get("备 注", "")
        flags: list[str] = []
        if national_special:
            flags.append("national_special_column_separate_do_not_mix")
        for token in ["5+3", "7+X", "联合学士学位"]:
            if token in major or token in note:
                flags.append(token)
        rows.append(
            base(
                {
                    "record_id": f"reference_trend_520_batch13_hrbmu_{len(rows)+1:04d}",
                    "queue_record_id": "reference_trend_520_plan_source_queue_0122",
                    "queue_rank": "122",
                    "university_code": "10226",
                    "university_name": "哈尔滨医科大学",
                    "subject_category": "理科/物理类_proxy_from_source",
                    "row_type": "official_major_plan_preview_no_group_code",
                    "source_url": "https://www.hrbmu.edu.cn/zhaosheng/info/1202/2625.htm",
                    "raw_file_path": rel(path),
                    "major_name": major,
                    "program_length": values.get("学制", ""),
                    "tuition": values.get("学费", ""),
                    "plan_count": plan_count,
                    "national_special_plan_count": national_special,
                    "total_plan_count": int_or_zero(values.get("合计", "")),
                    "special_type_flag": ";".join(flags),
                    "source_packet_status": "parsed_official_html_table_preview_hold_for_group_code_mapping",
                    "evidence_note": "Official table uses 科类=理 and separate 广西/国家专项 columns; group code is not printed.",
                }
            )
        )


def parse_hqu_aggregate(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    path = FILES["hqu"]
    table = select_table(path, "省份（●有国家专项计划）")
    header = table[0] if table else []
    for raw in table[1:]:
        values = dict(zip(header, raw))
        province = values.get("省份（●有国家专项计划）", "")
        if "广西" not in province:
            continue
        rows.append(
            base(
                {
                    "record_id": "reference_trend_520_batch13_hqu_aggregate_0001",
                    "queue_record_id": "reference_trend_520_plan_source_queue_0119",
                    "queue_rank": "119",
                    "university_code": "10385",
                    "university_name": "华侨大学",
                    "subject_category": "理工/物理_aggregate",
                    "row_type": "official_province_subject_aggregate_not_major_level",
                    "source_url": "https://zsc.hqu.edu.cn/info/1024/7692.htm",
                    "raw_file_path": rel(path),
                    "major_name": "province_subject_aggregate",
                    "plan_count": int_or_zero(values.get("理工/物理", "")),
                    "total_plan_count": int_or_zero(values.get("合计", "")),
                    "special_type_flag": "province_has_national_special_marker;aggregate_only",
                    "source_packet_status": "official_aggregate_preview_not_major_or_group_level",
                    "eligible_for_intake_preview": "false_aggregate_only",
                    "evidence_note": "Official page gives province/subject aggregate for 广西●, not major/group rows.",
                }
            )
        )
        exclusions.append(
            {
                "record_id": "reference_trend_520_batch13_hqu_excluded_aggregate",
                "university_name": "华侨大学",
                "exclusion_scope": "reference_trend_program_group_level",
                "exclusion_reason": "official page exposes aggregate province/subject counts only",
                "required_resolution": "find attachment/detail table before program/group-year preview",
            }
        )


def add_suse_readiness(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> None:
    path = FILES["suse"]
    rows.append(
        base(
            {
                "record_id": "reference_trend_520_batch13_suse_image_ready_0001",
                "queue_record_id": "reference_trend_520_plan_source_queue_0123",
                "queue_rank": "123",
                "university_code": "10622",
                "university_name": "四川轻化工大学",
                "subject_category": "物理类_unknown_until_image_parse",
                "row_type": "official_plan_image_assets_not_parsed",
                "source_url": "https://zjc.suse.edu.cn/2025/0613/c3262a196527/page.htm",
                "raw_file_path": rel(path),
                "major_name": "",
                "plan_count": "",
                "special_type_flag": "image_assets_include_non_3plus3_3plus3_special_preparatory",
                "source_packet_status": "official_image_assets_cached_ocr_or_manual_parse_needed",
                "eligible_for_intake_preview": "false_until_image_parse_QA",
                "evidence_note": "Official page is cached but plan is embedded as images, including separate ordinary/special/preparatory assets.",
            }
        )
    )
    exclusions.append(
        {
            "record_id": "reference_trend_520_batch13_suse_excluded_image_pending",
            "university_name": "四川轻化工大学",
            "exclusion_scope": "row_level_preview",
            "exclusion_reason": "official plan is embedded in images; no OCR/manual transcription performed",
            "required_resolution": "approved image download/OCR or manual transcription route",
        }
    )


def build_rows_and_exclusions() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    parse_haust(rows, exclusions)
    parse_hrbmu(rows, exclusions)
    parse_hqu_aggregate(rows, exclusions)
    add_suse_readiness(rows, exclusions)
    return rows, exclusions


def build_rollup(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> list[dict[str, object]]:
    by_uni = Counter(str(row["university_name"]) for row in rows)
    by_status = Counter(str(row["source_packet_status"]) for row in rows)
    parsed_rows = [row for row in rows if row["row_type"] == "official_major_plan_preview_no_group_code"]
    return [
        {"metric": "preview_rows", "value": len(rows), "note": "Parsed rows plus aggregate/readiness rows."},
        {"metric": "parsed_major_plan_preview_rows", "value": len(parsed_rows), "note": "Major-level rows extracted from cached official HTML tables."},
        {"metric": "parsed_major_plan_sum", "value": sum(int_or_zero(row["plan_count"]) for row in parsed_rows), "note": "Normal Guangxi/physical-proxy plan count only; special columns not mixed."},
        {"metric": "exclusion_rows", "value": len(exclusions), "note": "Non-physical, summary, aggregate, or image-pending rows."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No group code / aggregate/image limitations keep pool closed."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No score/rank and no group-year mapping opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": "ML/canonical remains closed."},
        *({"metric": f"university::{key}", "value": value, "note": ""} for key, value in sorted(by_uni.items())),
        *({"metric": f"status::{key}", "value": value, "note": ""} for key, value in sorted(by_status.items())),
    ]


def build_qa(rows: list[dict[str, object]], exclusions: list[dict[str, object]]) -> list[dict[str, object]]:
    def exists(key: str) -> bool:
        return FILES[key].exists() and FILES[key].stat().st_size > 1000

    return [
        {
            "check": "cached_official_files_exist",
            "status": "PASS" if all(exists(key) for key in ["haust", "hqu", "suse", "hrbmu_index", "hrbmu"]) else "FAIL",
            "detail": "Newly cached batch13 official files are present.",
        },
        {
            "check": "haust_physical_ordinary_rows_extracted",
            "status": "PASS" if any(row["university_name"] == "河南科技大学" for row in rows) else "FAIL",
            "detail": "河南科技大学 rows extracted from official HTML table.",
        },
        {
            "check": "hrbmu_physical_proxy_rows_extracted",
            "status": "PASS" if any(row["university_name"] == "哈尔滨医科大学" for row in rows) else "FAIL",
            "detail": "哈尔滨医科大学 理科/广西 rows extracted from official HTML table.",
        },
        {
            "check": "non_physical_or_summary_excluded",
            "status": "PASS" if exclusions else "WARN",
            "detail": "Non-physical/history/sports/summary/image-pending rows are excluded.",
        },
        {
            "check": "no_reference_trend_pool_entry",
            "status": "PASS" if all(str(row["reference_trend_pool_eligible"]) == "false" for row in rows) else "FAIL",
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
        "# Reference Trend 520 Batch13 Cache Parse Preflight",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Purpose: record the first cache/parse pass for selected batch13 official candidates.",
        "",
        "Outputs:",
        f"- `{rel(OUT)}`",
        f"- `{rel(ROLLUP_OUT)}`",
        f"- `{rel(QA_OUT)}`",
        f"- `{rel(EXCLUSION_OUT)}`",
        "",
        "Key findings:",
        "- 河南科技大学 and 哈尔滨医科大学 have official HTML tables that yield major-level Guangxi physical/proxy rows.",
        "- 华侨大学 currently yields only province/subject aggregate counts for 广西, not major/group rows.",
        "- 四川轻化工大学 is image-asset based and needs approved OCR/manual transcription.",
        "",
        "Boundary:",
        "- All rows remain source-packet parse preview or readiness only.",
        "- No group code is printed in the parsed major rows, so `reference_trend_pool_eligible=false` and `calibration_eligible=false` remain closed.",
        "- No canonical/ML output and no 32-school decision_pool merge.",
        "",
        "Rollup:",
    ]
    lines.extend(f"- {row['metric']}: {row['value']} {row['note']}".rstrip() for row in rollup)
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, exclusions = build_rows_and_exclusions()
    rollup = build_rollup(rows, exclusions)
    qa = build_qa(rows, exclusions)
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusions, ["record_id", "university_name", "exclusion_scope", "exclusion_reason", "required_resolution"])
    write_doc(rows, rollup)

    marker = "## 51. 2026-05-16 batch13 cache parse preflight"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增 batch13 cache/parse preflight：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：已缓存河南科技大学、华侨大学、四川轻化工大学、哈尔滨医科大学官方候选页，并进一步缓存哈尔滨医科大学广西计划明细页。河南科技大学与哈尔滨医科大学可从官方 HTML 表抽取专业级广西物理/理科计划预览；华侨大学本轮只得到广西省份/科类汇总，不是专业/组级记录；四川轻化工大学计划为图片资产，需 OCR 或人工转录审批。

准入边界：本轮只做 source-packet parse preview/preflight。已解析的专业行仍未打印院校专业组代码，也没有分数/位次映射，因此 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`；不进入 32 所 decision_pool。下一轮可继续缓存/解析集美大学官方计划明细，或准备青海大学/安徽工业大学图片 OCR/人工转录审批。
""",
    )


if __name__ == "__main__":
    main()
