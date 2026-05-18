#!/usr/bin/env python3
"""Parse ZCMU official Guangxi plan API responses for source-packet preview.

浙江中医药大学招生网 embeds the official 招生计划 page, which loads a
public Vue/Jeecg API under zscx.zcmu.edu.cn/API. The API exposes 2024/2025
Guangxi plan rows with plan counts and subject requirements, but no Guangxi
professional-group code, score, or rank. Keep outputs in non-canonical
source-packet preview only.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

PLAN_QUERY_PAGE = RAW_DIR / "zcmu_2025_plan_query_page.html"
PORTAL_HTML = RAW_DIR / "zcmu_portal.html"
ADMISSION_RULES_HTML = RAW_DIR / "zcmu_2025_admission_rules.html"
ZSCX_ROOT_HTML = RAW_DIR / "zcmu_zscx_root.html"
APP_JS = RAW_DIR / "zcmu_zscx_app.8f095deb.js"
SCHOOL_DICT_JSON = RAW_DIR / "zcmu_dict_school_name.json"
PLAN_YEAR_DICT_JSON = RAW_DIR / "zcmu_dict_plan_year.json"
PROVINCE_DICT_JSON = RAW_DIR / "zcmu_recruit_provice_dict_school1.json"
BATCH_DICT_2025_JSON = RAW_DIR / "zcmu_2025_guangxi_batch_dict.json"
PLAN_JSONS = {
    2024: RAW_DIR / "zcmu_2024_guangxi_plan_api.json",
    2025: RAW_DIR / "zcmu_2025_guangxi_plan_api.json",
}

OUT = SEED_DIR / "reference_trend_520_batch15_zcmu_api_plan_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_zcmu_api_plan_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_zcmu_api_plan_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_zcmu_api_plan_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_zcmu_api_plan_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PLAN_PAGE_URL = "https://zscx.zcmu.edu.cn/zsb_zcmu/zsjh.html"
PORTAL_URL = "https://zsb.zcmu.edu.cn/"
RULES_URL = "https://zsb.zcmu.edu.cn/info/1074/4672.htm"
APP_URL = "https://zscx.zcmu.edu.cn/#/index"
API_ENDPOINT = "https://zscx.zcmu.edu.cn/API/yxy/yxyRecruit/noTokenList"

FIELDS = [
    "record_id",
    "queue_record_id",
    "queue_rank",
    "related_queue_ranks",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "school_group_code",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "raw_plan_query_page_path",
    "raw_portal_html_path",
    "raw_admission_rules_html_path",
    "raw_zscx_root_html_path",
    "raw_app_js_path",
    "raw_school_dict_json_path",
    "raw_plan_year_dict_json_path",
    "raw_province_dict_json_path",
    "raw_batch_dict_2025_json_path",
    "raw_plan_json_path",
    "api_endpoint",
    "api_params",
    "source_row_number",
    "major_name",
    "duration",
    "tuition_yuan_per_year",
    "subject_requirement",
    "guangxi_plan_count",
    "remark",
    "special_type_detected",
    "ordinary_physical_candidate",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "year_pair_support_status",
    "collector_confidence",
    "source_packet_status",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "requires_manual_approval",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "evidence_note",
]


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


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def queue_context() -> tuple[str, str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "10344"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "10344"]
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "155", all_ranks


def special_type(row: dict[str, object]) -> str:
    major = str(row.get("majorName", ""))
    category = str(row.get("type", ""))
    remark = str(row.get("remake", "") or "")
    flags: list[str] = []
    if any(token in major + remark for token in ["中外合作", "合作办学"]):
        flags.append("cooperative_boundary")
    if "体育" in category or any(token in major for token in ["体育", "运动"]):
        flags.append("sport_admission_boundary")
    art_tokens = [
        "音乐",
        "美术",
        "表演",
        "舞蹈",
        "播音",
        "编导",
        "视觉传达设计",
        "环境设计",
        "产品设计",
        "服装与服饰设计",
        "数字媒体艺术",
    ]
    if "艺" in category or any(token in major for token in art_tokens):
        flags.append("art_admission_boundary")
    if "地方专项" in category or "地方专项" in remark:
        flags.append("local_special_program_boundary")
    return "|".join(flags) if flags else "none_detected"


def parse_rows() -> list[dict[str, object]]:
    queue_ids, batch_rank, all_ranks = queue_context()
    rows: list[dict[str, object]] = []
    for year, path in PLAN_JSONS.items():
        payload = load_json(path)
        records = ((payload.get("result") or {}).get("records") or [])
        for idx, row in enumerate(records, start=1):
            plan_count = int(row.get("planNum") or 0)
            special = special_type(row)
            ordinary_physics = (
                row.get("subjectType") == "物理类"
                and row.get("batch") == "本科普通批"
                and row.get("type") == "普通类"
                and special == "none_detected"
            )
            rows.append(
                {
                    "record_id": f"reference_trend_520_batch15_zcmu_api_plan_{year}_{idx:04d}",
                    "queue_record_id": queue_ids,
                    "queue_rank": batch_rank,
                    "related_queue_ranks": all_ranks,
                    "university_code": "10344",
                    "university_name": "浙江中医药大学",
                    "year": row.get("year") or year,
                    "province": row.get("provice", "广西壮族自治区"),
                    "batch": row.get("batch", ""),
                    "subject_category": row.get("subjectType", ""),
                    "school_group_code": "",
                    "source_url": f"{PORTAL_URL}|{PLAN_PAGE_URL}|{APP_URL}|{API_ENDPOINT}|{RULES_URL}",
                    "source_owner": "浙江中医药大学招生办官方网站 / 浙江中医药大学招生查询系统",
                    "source_title": "浙江中医药大学招生计划官方查询系统",
                    "published_date": "",
                    "raw_plan_query_page_path": rel(PLAN_QUERY_PAGE),
                    "raw_portal_html_path": rel(PORTAL_HTML),
                    "raw_admission_rules_html_path": rel(ADMISSION_RULES_HTML),
                    "raw_zscx_root_html_path": rel(ZSCX_ROOT_HTML),
                    "raw_app_js_path": rel(APP_JS),
                    "raw_school_dict_json_path": rel(SCHOOL_DICT_JSON),
                    "raw_plan_year_dict_json_path": rel(PLAN_YEAR_DICT_JSON),
                    "raw_province_dict_json_path": rel(PROVINCE_DICT_JSON),
                    "raw_batch_dict_2025_json_path": rel(BATCH_DICT_2025_JSON),
                    "raw_plan_json_path": rel(path),
                    "api_endpoint": API_ENDPOINT,
                    "api_params": f"schoolDict=1&proviceDict=25&yearDict={year}&pageNo=1&pageSize=200",
                    "source_row_number": idx,
                    "major_name": row.get("majorName", ""),
                    "duration": row.get("schoolSystem", ""),
                    "tuition_yuan_per_year": row.get("money", ""),
                    "subject_requirement": row.get("subject", ""),
                    "guangxi_plan_count": plan_count,
                    "remark": row.get("remake", "") or "",
                    "special_type_detected": special,
                    "ordinary_physical_candidate": "true" if ordinary_physics else "false",
                    "source_contains_group_code": "false",
                    "source_contains_plan_count": "true" if plan_count > 0 else "false",
                    "source_contains_min_score": "false",
                    "source_contains_min_rank": "false",
                    "year_pair_support_status": "2024_2025_same_official_api_available",
                    "collector_confidence": "T2_official_api_plan_rows_no_group_score_rank",
                    "source_packet_status": "official_api_plan_parse_preview_only",
                    "eligible_for_intake_preview": "true",
                    "reference_trend_pool_eligible": "false",
                    "calibration_eligible": "false",
                    "requires_manual_approval": "false",
                    "next_action": "join with Guangxi official professional-group line score/rank before calibration; keep medical major rows as ordinary unless official special-type evidence appears.",
                    "canonical_ml_entry_open": "false",
                    "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                    "evidence_note": "Official ZCMU public plan API row. Plan count and subject requirement parsed; no Guangxi professional-group code, score, or rank returned.",
                }
            )
    return rows


def main() -> None:
    parsed = parse_rows()
    write_csv(OUT, parsed, FIELDS)

    by_year_subject: dict[str, int] = defaultdict(int)
    by_year_subject_rows: Counter[str] = Counter()
    special_counter: Counter[str] = Counter()
    ordinary_physics_plan_sum = 0
    for row in parsed:
        key = f"{row['year']}|{row['subject_category']}|{row['batch']}|{row['type'] if 'type' in row else '普通类'}"
        by_year_subject[key] += int(row["guangxi_plan_count"])
        by_year_subject_rows[key] += 1
        special_counter[str(row["special_type_detected"])] += 1
        if row["ordinary_physical_candidate"] == "true":
            ordinary_physics_plan_sum += int(row["guangxi_plan_count"])

    rollup = [
        {"metric": "official_portal_cached_rows", "value": 1, "note": rel(PORTAL_HTML)},
        {"metric": "official_plan_query_page_cached_rows", "value": 1, "note": rel(PLAN_QUERY_PAGE)},
        {"metric": "official_api_js_cached_rows", "value": 1, "note": rel(APP_JS)},
        {"metric": "official_api_response_cached_years", "value": len(PLAN_JSONS), "note": "2024 and 2025 Guangxi plan API responses"},
        {"metric": "parse_preview_rows_all_guangxi", "value": len(parsed), "note": "All Guangxi rows from cached API responses"},
        {"metric": "guangxi_plan_count_sum_all_years", "value": sum(int(row["guangxi_plan_count"]) for row in parsed), "note": "2024+2025 API plan count sum"},
        {"metric": "year_subject_plan_distribution", "value": dict(sorted(by_year_subject.items())), "note": "Plan counts by year/subject/batch"},
        {"metric": "year_subject_row_distribution", "value": dict(sorted(by_year_subject_rows.items())), "note": "Row counts by year/subject/batch"},
        {"metric": "ordinary_physics_candidate_rows", "value": sum(1 for row in parsed if row["ordinary_physical_candidate"] == "true"), "note": "本科普通批/普通类/物理类 excluding detected special boundaries"},
        {"metric": "ordinary_physics_candidate_plan_sum", "value": ordinary_physics_plan_sum, "note": "2024+2025 ordinary physics plan sum"},
        {"metric": "source_group_code_available_rows", "value": 0, "note": "API does not return Guangxi professional-group code"},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan API only; no score/rank"},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in special_counter.items() if k != "none_detected"), "note": dict(special_counter)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Group score/rank join required before calibration"},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened"},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed"},
    ]
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])

    qa_rows = [
        {"check": "required_raw_files_exist", "status": "PASS" if all(path.exists() for path in [PLAN_QUERY_PAGE, PORTAL_HTML, ZSCX_ROOT_HTML, APP_JS, *PLAN_JSONS.values()]) else "FAIL", "detail": "Official page/app/API artifacts cached"},
        {"check": "api_success_true_all_years", "status": "PASS" if all(load_json(path).get("success") is True for path in PLAN_JSONS.values()) else "FAIL", "detail": "Both API responses report success=true"},
        {"check": "parsed_rows_nonzero", "status": "PASS" if parsed else "FAIL", "detail": f"{len(parsed)} rows parsed"},
        {"check": "official_2025_physics_rows_nonzero", "status": "PASS" if any(str(row["year"]) == "2025" and row["ordinary_physical_candidate"] == "true" for row in parsed) else "FAIL", "detail": "2025 ordinary physics rows available"},
        {"check": "no_pool_or_canonical_entry", "status": "PASS", "detail": "All rows remain preview-only; no canonical/ML/decision-pool writes"},
        {"check": "score_rank_absent_marked", "status": "PASS" if all(row["source_contains_min_score"] == "false" and row["source_contains_min_rank"] == "false" for row in parsed) else "FAIL", "detail": "No API score/rank field promoted"},
    ]
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])

    exclusion = [
        {
            "record_id": row["record_id"],
            "university_code": row["university_code"],
            "university_name": row["university_name"],
            "year": row["year"],
            "major_name": row["major_name"],
            "exclusion_scope": "reference_trend_pool|canonical|ml|decision_pool",
            "exclusion_reason": "official API provides plan_count but no professional-group code, min score, or min rank; requires Guangxi group-line join before calibration",
            "safe_next_action": row["next_action"],
        }
        for row in parsed
    ]
    write_csv(
        EXCLUSION_OUT,
        exclusion,
        [
            "record_id",
            "university_code",
            "university_name",
            "year",
            "major_name",
            "exclusion_scope",
            "exclusion_reason",
            "safe_next_action",
        ],
    )

    year_all_rows = Counter(str(row["year"]) for row in parsed)
    year_all_plan = defaultdict(int)
    year_physics_rows = Counter()
    year_physics_plan = defaultdict(int)
    for row in parsed:
        year = str(row["year"])
        plan = int(row["guangxi_plan_count"])
        year_all_plan[year] += plan
        if row["ordinary_physical_candidate"] == "true":
            year_physics_rows[year] += 1
            year_physics_plan[year] += plan

    doc = f"""# ZCMU Batch15 Official API Plan Parse Preview

Generated: {date.today().isoformat()}

## Scope

浙江中医药大学官方招生计划入口已确认：

- 招生办首页: {PORTAL_URL}
- 招生计划页: {PLAN_PAGE_URL}
- 招生查询系统: {APP_URL}
- 公开计划 API: {API_ENDPOINT}
- 2025 招生章程上下文: {RULES_URL}

本轮只生成 source-packet preview/QA，不写入 `reference_trend_pool`、canonical、ML，也不并入 32 所 `decision_pool`。

## Outputs

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`

## Coverage

- 2025 广西官方计划 API: {year_all_rows['2025']} 行，计划数合计 {year_all_plan['2025']}；其中本科普通批/普通类/物理类 {year_physics_rows['2025']} 行，计划数合计 {year_physics_plan['2025']}。
- 2024 广西官方计划 API: {year_all_rows['2024']} 行，计划数合计 {year_all_plan['2024']}；其中本科普通批/普通类/物理类 {year_physics_rows['2024']} 行，计划数合计 {year_physics_plan['2024']}。
- 两年同一官方 API 可形成计划侧趋势旁证，但 API 不含广西院校专业组代码、最低分或最低位次。

## Gate Boundary

所有记录继续：

- `reference_trend_pool_eligible=false`
- `calibration_eligible=false`
- `canonical_ml_entry_open=false`
- `decision_pool_boundary=do_not_merge_with_32_school_decision_pool`

下一步应与广西考试院院校专业组投档线/专业组上下文做 join workbench，再判断是否进入 calibration preview。
"""
    DOC_OUT.write_text(doc, encoding="utf-8")

    marker = "## 76. 2026-05-16 batch15 浙江中医药大学 API plan parse preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增浙江中医药大学 batch15 API plan parse preview：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：官方招生计划页嵌入官方招生查询系统，JS 暴露公开 `/yxy/yxyRecruit/noTokenList` API；已缓存 2024/2025 广西计划响应。2025 广西 {year_all_rows['2025']} 行、计划数 {year_all_plan['2025']}，其中本科普通批/普通类/物理类 {year_physics_rows['2025']} 行、计划数 {year_physics_plan['2025']}；2024 广西 {year_all_rows['2024']} 行、计划数 {year_all_plan['2024']}，其中本科普通批/普通类/物理类 {year_physics_rows['2024']} 行、计划数 {year_physics_plan['2024']}。

准入边界：本轮只写 source-packet preview/QA；官方 API 没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。
""",
    )

    print(f"Wrote {OUT}")
    print(f"Wrote {ROLLUP_OUT}")
    print(f"Wrote {QA_OUT}")
    print(f"Wrote {EXCLUSION_OUT}")
    print(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
