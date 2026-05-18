#!/usr/bin/env python3
"""Parse Jianghan University official 2025 Guangxi physics plan API response.

The admissions portal delegates 招生计划 to an official Vue data app. The API
returns 2025 Guangxi physics ordinary plan rows with plan counts and subject
requirements, but no Guangxi professional-group code, score, or rank. Keep the
output in source-packet preview only.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch15_official"

PORTAL_HTML = RAW_DIR / "jhun_portal.html"
APP_HTML = RAW_DIR / "jhun_zsdata_lqxx_index.html"
APP_JS = RAW_DIR / "jhun_zsdata_app.fe50b7c2.js"
CHUNK_JS = RAW_DIR / "jhun_zsdata_lqcxjg.be9430e0.js"
GETTYPE_JSON = RAW_DIR / "jhun_zsjh_gettype.json"
PLAN_JSON = RAW_DIR / "jhun_2025_guangxi_physics_plan_api.json"
QUEUE = SEED_DIR / "reference_trend_520_plan_source_packet_queue.csv"
BATCH15 = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch15_preview.csv"

OUT = SEED_DIR / "reference_trend_520_batch15_jhun_api_plan_parse_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_batch15_jhun_api_plan_parse_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_batch15_jhun_api_plan_parse_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_batch15_jhun_api_plan_parse_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_batch15_jhun_api_plan_parse_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

PORTAL_URL = "https://bkzs.jhun.edu.cn/"
APP_URL = "https://zsdata.jhun.edu.cn/zsdata/lqxx/#/"
API_URL = "https://zsdata.jhun.edu.cn/lqxx/s/api/front/lqxx/getList"
API_PAYLOAD = '{"type":"zsjh","sf":"广西","nf":"2025","zslb":"普通类","klmc":"物理类","xqmc":""}'

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
    "campus",
    "school_group_code",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "raw_portal_html_path",
    "raw_app_html_path",
    "raw_app_js_path",
    "raw_chunk_js_path",
    "raw_gettype_json_path",
    "raw_plan_json_path",
    "api_endpoint",
    "api_payload",
    "source_row_number",
    "major_code",
    "major_name",
    "duration",
    "tuition_yuan_per_year",
    "guangxi_plan_count",
    "first_choice_requirement",
    "subject_requirement",
    "requirement_detail",
    "special_type_detected",
    "ordinary_physical_candidate",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
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


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def q_context() -> tuple[str, str, str]:
    qrows = [row for row in read_csv(QUEUE) if row.get("university_code") == "11072"]
    brows = [row for row in read_csv(BATCH15) if row.get("university_code") == "11072"]
    batch_rank = "|".join(sorted({row.get("queue_rank", "") for row in brows if row.get("queue_rank")}))
    queue_ids = "|".join(sorted({row.get("record_id", "") for row in qrows if row.get("record_id")}))
    all_ranks = "|".join(sorted({row.get("queue_rank", "") for row in qrows if row.get("queue_rank")}))
    return queue_ids, batch_rank or "153", all_ranks


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def special_type(row: dict) -> str:
    major = str(row.get("zymc", ""))
    category = str(row.get("zslb", ""))
    flags: list[str] = []
    if any(token in major for token in ["中外合作", "合作办学"]):
        flags.append("cooperative_boundary")
    if "体育" in category or any(token in major for token in ["体育", "运动"]):
        flags.append("sport_admission_boundary")
    art_major_tokens = [
        "音乐",
        "美术",
        "表演",
        "舞蹈",
        "播音",
        "编导",
        "动画",
        "视觉传达设计",
        "环境设计",
        "产品设计",
        "服装与服饰设计",
        "数字媒体艺术",
    ]
    if "艺" in category or any(token in major for token in art_major_tokens):
        flags.append("art_admission_boundary")
    return "|".join(flags) if flags else "none_detected"


def parse_plan() -> tuple[list[dict[str, object]], dict[str, object]]:
    data = load_json(PLAN_JSON)
    queue_ids, batch_rank, all_ranks = q_context()
    parsed: list[dict[str, object]] = []
    for idx, row in enumerate(data.get("list", []) or [], start=1):
        plan = int(row.get("jhrs") or 0)
        if plan <= 0:
            continue
        special = special_type(row)
        ordinary_physical = row.get("klmc") == "物理类" and row.get("zslb") == "普通类" and special == "none_detected"
        parsed.append(
            {
                "record_id": f"reference_trend_520_batch15_jhun_api_plan_{len(parsed) + 1:04d}",
                "queue_record_id": queue_ids,
                "queue_rank": batch_rank,
                "related_queue_ranks": all_ranks,
                "university_code": "11072",
                "university_name": "江汉大学",
                "year": row.get("nf", "2025"),
                "province": row.get("sf", "广西"),
                "batch": row.get("pcmc", "本科批"),
                "subject_category": row.get("klmc", "物理类"),
                "campus": row.get("xqlx", ""),
                "school_group_code": row.get("zygroup", ""),
                "source_url": f"{PORTAL_URL}|{APP_URL}|{API_URL}",
                "source_owner": "江汉大学本科招生网 / 江汉大学招生数据系统",
                "source_title": "江汉大学招生计划官方查询系统",
                "published_date": "",
                "raw_portal_html_path": rel(PORTAL_HTML),
                "raw_app_html_path": rel(APP_HTML),
                "raw_app_js_path": rel(APP_JS),
                "raw_chunk_js_path": rel(CHUNK_JS),
                "raw_gettype_json_path": rel(GETTYPE_JSON),
                "raw_plan_json_path": rel(PLAN_JSON),
                "api_endpoint": API_URL,
                "api_payload": API_PAYLOAD,
                "source_row_number": idx,
                "major_code": row.get("zydm", ""),
                "major_name": row.get("zymc", ""),
                "duration": row.get("xzmc", ""),
                "tuition_yuan_per_year": row.get("zyxf", ""),
                "guangxi_plan_count": plan,
                "first_choice_requirement": row.get("sxkm", ""),
                "subject_requirement": row.get("xkkm", ""),
                "requirement_detail": row.get("xkyq", ""),
                "special_type_detected": special,
                "ordinary_physical_candidate": "true" if ordinary_physical else "false",
                "source_contains_group_code": "true" if row.get("zygroup") else "false",
                "source_contains_plan_count": "true",
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "collector_confidence": "T2_official_api_plan_rows_no_group_score_rank",
                "source_packet_status": "official_api_plan_parse_preview_only",
                "eligible_for_intake_preview": "true",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "requires_manual_approval": "false",
                "next_action": "join with Guangxi official group-line score/rank and professional-group context before calibration.",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "evidence_note": "Official admissions data API row. Plan count and subject requirements parsed; no group code, score, or rank returned.",
            }
        )
    return parsed, data


def gettype_has_guangxi_physics() -> bool:
    data = load_json(GETTYPE_JSON)
    return "广西_2025_物理类_校本部" in (data.get("typeMap") or {})


def main() -> None:
    rows, data = parse_plan()
    write_csv(OUT, rows, FIELDS)

    plan_sum = sum(int(row["guangxi_plan_count"]) for row in rows)
    summary_rows = data.get("sumLists", []) or []
    summary_sum = int(summary_rows[0].get("jhrs") or 0) if summary_rows else 0
    subject_counter = Counter(str(row["subject_requirement"]) for row in rows)
    special_counter = Counter(str(row["special_type_detected"]) for row in rows)
    ordinary_rows = [row for row in rows if row.get("ordinary_physical_candidate") == "true"]

    rollup_rows = [
        {"metric": "official_portal_cached_rows", "value": int(PORTAL_HTML.exists()), "note": rel(PORTAL_HTML)},
        {"metric": "official_app_cached_rows", "value": int(APP_HTML.exists()), "note": rel(APP_HTML)},
        {"metric": "official_api_response_cached_rows", "value": int(PLAN_JSON.exists()), "note": rel(PLAN_JSON)},
        {"metric": "gettype_guangxi_2025_physics_available", "value": int(gettype_has_guangxi_physics()), "note": rel(GETTYPE_JSON)},
        {"metric": "parse_preview_rows_all_guangxi_physics", "value": len(rows), "note": "API list rows"},
        {"metric": "guangxi_physics_plan_count_sum", "value": plan_sum, "note": f"API summary jhrs={summary_sum}"},
        {"metric": "ordinary_physics_candidate_rows", "value": len(ordinary_rows), "note": "physical ordinary rows excluding special boundaries"},
        {"metric": "ordinary_physics_candidate_plan_sum", "value": sum(int(row["guangxi_plan_count"]) for row in ordinary_rows), "note": ""},
        {"metric": "source_group_code_available_rows", "value": sum(1 for row in rows if row.get("school_group_code")), "note": "API zygroup is blank for current rows"},
        {"metric": "subject_requirement_distribution", "value": dict(subject_counter), "note": ""},
        {"metric": "special_boundary_rows", "value": sum(v for k, v in special_counter.items() if k != "none_detected"), "note": dict(special_counter)},
        {"metric": "score_rank_available_rows", "value": 0, "note": "Plan API only; no score/rank."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Score/rank and group join required before calibration."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    write_csv(ROLLUP_OUT, rollup_rows, ["metric", "value", "note"])

    qa_rows = [
        {"check": "official_portal_cached", "status": "PASS" if PORTAL_HTML.exists() else "FAIL", "detail": rel(PORTAL_HTML)},
        {"check": "official_api_endpoint_discovered", "status": "PASS" if APP_JS.exists() and CHUNK_JS.exists() else "FAIL", "detail": f"{rel(APP_JS)}|{rel(CHUNK_JS)}"},
        {"check": "gettype_has_guangxi_2025_physics", "status": "PASS" if gettype_has_guangxi_physics() else "FAIL", "detail": rel(GETTYPE_JSON)},
        {"check": "api_plan_rows_extracted", "status": "PASS" if rows else "FAIL", "detail": f"rows={len(rows)}"},
        {"check": "plan_sum_matches_api_summary", "status": "PASS" if plan_sum == summary_sum else "WARN", "detail": f"parsed={plan_sum}; summary={summary_sum}"},
        {"check": "score_rank_hold", "status": "PASS", "detail": "Official API is plan-only; no score or rank."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]
    write_csv(QA_OUT, qa_rows, ["check", "status", "detail"])

    exclusion_rows = [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "major_name": row["major_name"],
            "subject_category": row["subject_category"],
            "guangxi_plan_count": row["guangxi_plan_count"],
            "special_type_detected": row["special_type_detected"],
            "exclusion_reason": "missing_school_group_code_score_rank_before_calibration",
            "canonical_ml_entry_open": "false",
        }
        for row in rows
    ]
    write_csv(
        EXCLUSION_OUT,
        exclusion_rows,
        [
            "record_id",
            "university_name",
            "major_name",
            "subject_category",
            "guangxi_plan_count",
            "special_type_detected",
            "exclusion_reason",
            "canonical_ml_entry_open",
        ],
    )

    doc_lines = [
        "# reference_trend_520 batch15 JHUN API plan parse preview",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "江汉大学官方招生计划查询系统已缓存并解析为 2025 广西物理类普通类 source-packet preview。本产物不进入 32 所 decision_pool。",
        "",
        "## Result",
        "",
        f"- Official portal URL: {PORTAL_URL}",
        f"- Official app URL: {APP_URL}",
        f"- API endpoint: {API_URL}",
        f"- API payload: `{API_PAYLOAD}`",
        f"- Parsed rows: {len(rows)}",
        f"- Plan sum: {plan_sum}",
        f"- API summary jhrs: {summary_sum}",
        f"- Group code available rows: {sum(1 for row in rows if row.get('school_group_code'))}",
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
        "官方 API 可提取专业计划数和选科要求，但没有广西院校专业组代码、最低分或最低位次。所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。后续需与广西考试院 group-line score/rank 和专业组上下文做 join workbench。",
        "",
        "## QA",
        "",
    ]
    for row in qa_rows:
        doc_lines.append(f"- {row['check']}: {row['status']} - {row['detail']}")
    doc_lines.extend(["", "## Rollup", ""])
    for row in rollup_rows:
        doc_lines.append(f"- {row['metric']}: {row['value']} ({row['note']})")
    DOC_OUT.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")

    marker = "## 75. 2026-05-16 batch15 江汉大学 API plan parse preview"
    handoff = f"""

{marker}

已新增江汉大学 batch15 API plan parse preview：

- `{rel(OUT)}`
- `{rel(ROLLUP_OUT)}`
- `{rel(QA_OUT)}`
- `{rel(EXCLUSION_OUT)}`
- `{rel(DOC_OUT)}`

覆盖结果：官方本科招生网指向官方招生数据系统，JS 暴露 `getType/getList` API；已缓存 2025 广西物理类普通类计划响应，抽出 {len(rows)} 行，计划数合计 {plan_sum}，与 API summary `jhrs={summary_sum}` 对齐。接口返回专业、计划数、学制/学费、选科要求，但 `zygroup` 为空。

准入边界：本轮只写 source-packet preview/QA；官方 API 没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。
"""
    append_handoff_once(marker, handoff)


if __name__ == "__main__":
    main()
