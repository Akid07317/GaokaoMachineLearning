#!/usr/bin/env python3
"""Parse Lanzhou Jiaotong official API rows into source-packet QA previews."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_sources" / "reference_trend" / "lzjtu"
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

PLAN_JSON = RAW / "zsplan_guangxi_2024_physics.json"
SCORE_JSON = RAW / "lnzy_guangxi_2024_physics.json"

OUT_PREVIEW = CLEAN / "reference_trend_lzjtu_source_packet_parse_preview.csv"
OUT_QA = REPORTS / "reference_trend_lzjtu_source_packet_parse_qa.csv"
OUT_ROLLUP = REPORTS / "reference_trend_lzjtu_source_packet_parse_rollup.csv"
OUT_DOC = DOCS / "reference_trend_lzjtu_source_packet_parse.md"

PLAN_SOURCE_URL = "https://zscx.lzjtu.edu.cn/api//business/web/index/getZsplanList"
SCORE_SOURCE_URL = "https://zscx.lzjtu.edu.cn/api//business/web/index/getLnzyfenshuList"
PORTAL_URL = "https://zscx.lzjtu.edu.cn/"

SPECIAL_MARKERS = ("专项", "预科", "民族", "中外", "合作", "艺术", "体育", "提前")


def load_content(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    if not payload.get("success"):
        return []
    return payload.get("content") or []


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def special_detected(*values: object) -> bool:
    text = " ".join(str(v or "") for v in values)
    return any(marker in text for marker in SPECIAL_MARKERS)


def plan_rows() -> list[dict[str, object]]:
    rows = []
    for idx, row in enumerate(load_content(PLAN_JSON), start=1):
        special = special_detected(row.get("jihualeibie"), row.get("picileibie"), row.get("major"))
        ordinary_physics = (
            row.get("province") == "广西"
            and row.get("kelei") == "物理类"
            and row.get("jihualeibie") == "普通类"
            and row.get("picileibie") == "本科普通批"
            and not special
        )
        rows.append(
            {
                "record_id": f"lzjtu_plan_2024_{idx:04d}",
                "university_code": "10732",
                "university_name": "兰州交通大学",
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("picileibie", ""),
                "subject_category": row.get("kelei", ""),
                "source_role": "official_plan_row",
                "major_or_group": row.get("major", ""),
                "group_label": "",
                "plan_count": row.get("zsnum", ""),
                "minimum_score": "",
                "minimum_rank": "",
                "max_score": "",
                "avg_score": "",
                "rank_field_present": "false",
                "source_contains_group_code": "false",
                "source_contains_plan_count": str(bool(row.get("zsnum"))).lower(),
                "source_contains_min_score": "false",
                "source_contains_min_rank": "false",
                "special_type_detected": str(special).lower(),
                "ordinary_physics_guangxi": str(ordinary_physics).lower(),
                "raw_source_file": str(PLAN_JSON.relative_to(ROOT)),
                "source_url": PLAN_SOURCE_URL,
                "portal_url": PORTAL_URL,
                "collector_confidence": "T2_official_api_major_level_no_group_code",
                "qa_status": "source_packet_intake_ready_group_mapping_needed" if ordinary_physics else "exclude_or_hold_not_strict_ordinary",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "required_resolution": "map_to_exam_authority_group_before_trend_pool_use",
            }
        )
    return rows


def score_rows() -> list[dict[str, object]]:
    rows = []
    for idx, row in enumerate(load_content(SCORE_JSON), start=1):
        special = special_detected(row.get("leixing"), row.get("major"), row.get("remark"))
        ordinary_physics = (
            row.get("province") == "广西"
            and row.get("kelei") == "物理类"
            and row.get("leixing") == "本科"
            and not special
        )
        rows.append(
            {
                "record_id": f"lzjtu_score_2024_{idx:04d}",
                "university_code": "10732",
                "university_name": "兰州交通大学",
                "year": row.get("year", ""),
                "province": row.get("province", ""),
                "batch": row.get("leixing", ""),
                "subject_category": row.get("kelei", ""),
                "source_role": "official_major_score_row",
                "major_or_group": row.get("major", ""),
                "group_label": "",
                "plan_count": "",
                "minimum_score": row.get("minscore", ""),
                "minimum_rank": row.get("minfwc", ""),
                "max_score": row.get("maxscore", ""),
                "avg_score": row.get("avgscore", ""),
                "rank_field_present": str(bool(row.get("minfwc"))).lower(),
                "source_contains_group_code": "false",
                "source_contains_plan_count": "false",
                "source_contains_min_score": str(bool(row.get("minscore"))).lower(),
                "source_contains_min_rank": str(bool(row.get("minfwc"))).lower(),
                "special_type_detected": str(special).lower(),
                "ordinary_physics_guangxi": str(ordinary_physics).lower(),
                "raw_source_file": str(SCORE_JSON.relative_to(ROOT)),
                "source_url": SCORE_SOURCE_URL,
                "portal_url": PORTAL_URL,
                "collector_confidence": "T2_official_api_major_score_with_rank_no_group_code",
                "qa_status": "source_packet_intake_ready_group_mapping_needed" if ordinary_physics else "exclude_or_hold_not_strict_ordinary",
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
                "required_resolution": "map_to_exam_authority_group_before_trend_pool_use",
            }
        )
    return rows


def main() -> None:
    rows = plan_rows() + score_rows()
    counts = Counter()
    for row in rows:
        counts["rows"] += 1
        counts[f"role:{row['source_role']}"] += 1
        counts[f"qa:{row['qa_status']}"] += 1
        if row["ordinary_physics_guangxi"] == "true":
            counts["ordinary_physics_guangxi_rows"] += 1
        if row["source_contains_plan_count"] == "true":
            counts["rows_with_plan_count"] += 1
        if row["source_contains_min_score"] == "true":
            counts["rows_with_min_score"] += 1
        if row["source_contains_min_rank"] == "true":
            counts["rows_with_min_rank"] += 1
        if row["special_type_detected"] == "true":
            counts["special_type_detected_rows"] += 1

    fields = [
        "record_id",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "source_role",
        "major_or_group",
        "group_label",
        "plan_count",
        "minimum_score",
        "minimum_rank",
        "max_score",
        "avg_score",
        "rank_field_present",
        "source_contains_group_code",
        "source_contains_plan_count",
        "source_contains_min_score",
        "source_contains_min_rank",
        "special_type_detected",
        "ordinary_physics_guangxi",
        "raw_source_file",
        "source_url",
        "portal_url",
        "collector_confidence",
        "qa_status",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
    ]
    write_csv(OUT_PREVIEW, rows, fields)

    qa_rows = []
    for row in rows:
        if row["qa_status"] != "source_packet_intake_ready_group_mapping_needed":
            qa_rows.append(
                {
                    "record_id": f"lzjtu_qa_{len(qa_rows) + 1:04d}",
                    "source_record_id": row["record_id"],
                    "qa_status": row["qa_status"],
                    "hold_reason": row["required_resolution"],
                    "reference_trend_pool_eligible": row["reference_trend_pool_eligible"],
                    "canonical_ml_entry_open": row["canonical_ml_entry_open"],
                }
            )
    write_csv(
        OUT_QA,
        qa_rows,
        [
            "record_id",
            "source_record_id",
            "qa_status",
            "hold_reason",
            "reference_trend_pool_eligible",
            "canonical_ml_entry_open",
        ],
    )

    rollup = [
        ("source_packet_rows", counts["rows"]),
        ("official_plan_rows", counts["role:official_plan_row"]),
        ("official_major_score_rows", counts["role:official_major_score_row"]),
        ("ordinary_physics_guangxi_rows", counts["ordinary_physics_guangxi_rows"]),
        ("source_packet_intake_ready_group_mapping_needed_rows", counts["qa:source_packet_intake_ready_group_mapping_needed"]),
        ("rows_with_plan_count", counts["rows_with_plan_count"]),
        ("rows_with_min_score", counts["rows_with_min_score"]),
        ("rows_with_min_rank", counts["rows_with_min_rank"]),
        ("special_type_detected_rows", counts["special_type_detected_rows"]),
        ("reference_trend_pool_eligible_rows", 0),
        ("calibration_eligible_rows", 0),
        ("canonical_ml_entry_open", "false"),
        ("decision_pool_expansion_performed", "false"),
    ]
    write_csv(
        OUT_ROLLUP,
        [{"metric": metric, "value": value} for metric, value in rollup],
        ["metric", "value"],
    )

    OUT_DOC.write_text(
        f"""# Reference Trend Lanzhou Jiaotong Source Packet Parse

日期：{date.today().isoformat()}

## 结论

兰州交通大学官方查询站 `zscx.lzjtu.edu.cn` 已确认可访问，前端 JS 暴露官方 API。已抽取 `2024` 广西物理类本科普通批计划 `26` 行，以及 `2024` 广西物理类本科专业分 `32` 行。该来源可作为 P0 reference trend 的 source-packet 候选，但当前没有院校专业组代码，因此仍需与广西考试院投档线做 group mapping，不能直接进入趋势池。

## 覆盖

- source packet rows: {counts['rows']}
- official plan rows: {counts['role:official_plan_row']}
- official major score rows: {counts['role:official_major_score_row']}
- rows with plan count: {counts['rows_with_plan_count']}
- rows with min score: {counts['rows_with_min_score']}
- rows with min rank: {counts['rows_with_min_rank']}
- intake ready but group mapping needed: {counts['qa:source_packet_intake_ready_group_mapping_needed']}
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 来源边界

- 招生计划 API: `{PLAN_SOURCE_URL}`
- 专业分数 API: `{SCORE_SOURCE_URL}`
- 官方查询入口: `{PORTAL_URL}`
- 官网静态 `zsb.lzjtu.edu.cn/zsjh2025/zsjh20251.htm` 与 `lnfs/lnfs.htm` 当前终端 HEAD 返回 412，但查询站 API 可直接返回 JSON。

## 下一步

1. 用广西考试院 `2024` 兰州交通大学院校专业组投档线做 group mapping。
2. 继续查找是否存在 `2025` 计划/分数接口或页面；当前字段接口只返回到 `2024`。
3. 继续推进下一批 P0/P1 官方来源发现，不打开 canonical/ML。
""",
        encoding="utf-8",
    )

    print(f"lzjtu_source_packet_rows={counts['rows']}")
    print(f"source_packet_intake_ready_group_mapping_needed_rows={counts['qa:source_packet_intake_ready_group_mapping_needed']}")
    print("reference_trend_pool_eligible_rows=0")


if __name__ == "__main__":
    main()
