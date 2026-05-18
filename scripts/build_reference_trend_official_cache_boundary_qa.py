#!/usr/bin/env python3
"""Build a boundary QA preview for cached official Guangxi source rows.

The rows handled here are source-packet evidence only. They must not be
promoted into the 32-school decision pool, canonical tables, ML inputs, or
the reference trend statistical pool without a later explicit review.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CLEAN = ROOT / "clean_data" / "engineering_guangxi_seed"
DOCS = ROOT / "docs"

OUT_PREVIEW = CLEAN / "reference_trend_official_cache_boundary_qa_preview.csv"
OUT_ROLLUP = REPORTS / "reference_trend_official_cache_boundary_qa_rollup.csv"
OUT_EXCLUSION = REPORTS / "reference_trend_official_cache_boundary_exclusion_log.csv"
OUT_DOC = DOCS / "reference_trend_official_cache_boundary_qa.md"


FALLBACK_SCHOOLS = {
    "bjtu": ("beijing_jiaotong_211", "北京交通大学"),
    "ncepu": ("huabei_dianli_211", "华北电力大学"),
}

SPECIAL_MARKERS = (
    "专项",
    "高校专项",
    "国家专项",
    "地方专项",
    "民族",
    "预科",
    "中外",
    "合作",
    "艺术",
    "体育",
    "提前",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def first(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name, "")
        if value not in (None, ""):
            return str(value).strip()
    return ""


def infer_school(path: Path, row: dict[str, str]) -> tuple[str, str]:
    school_key = first(row, "school_key")
    school_name = first(row, "school_name")
    if school_key and school_name:
        return school_key, school_name
    stem = path.name
    for token, fallback in FALLBACK_SCHOOLS.items():
        if stem.startswith(token):
            return fallback
    return school_key or "unknown", school_name or "unknown"


def infer_role(path: Path) -> str:
    name = path.name
    if "plan_rows" in name:
        return "plan"
    if "score_group_rows" in name or "summary_score_rows" in name:
        return "score_group_or_summary"
    if "major_score_rows" in name:
        return "score_major"
    if "score_rows" in name:
        return "score_major_or_summary"
    return "unknown"


def is_score_role(role: str) -> bool:
    return role.startswith("score")


def is_plan_role(role: str) -> bool:
    return role == "plan"


def normalize_subject(value: str) -> str:
    if value in ("物理", "物理类"):
        return "物理类"
    if value in ("历史", "历史类"):
        return "历史类"
    return value


def has_any_special(*values: str) -> bool:
    text = " ".join(v for v in values if v)
    return any(marker in text for marker in SPECIAL_MARKERS)


def collect_input_files() -> list[Path]:
    files: list[Path] = []
    patterns = [
        "*guangxi*plan_rows.csv",
        "*guangxi*score_rows.csv",
        "*guangxi*score_group_rows.csv",
        "*guangxi*major_score_rows.csv",
        "*guangxi*summary_score_rows.csv",
    ]
    seen = set()
    for pattern in patterns:
        for path in sorted(REPORTS.glob(pattern)):
            if path.name.endswith("_official_guangxi_summary.csv"):
                continue
            if path.name in seen:
                continue
            seen.add(path.name)
            files.append(path)
    return files


def build_rows() -> tuple[list[dict[str, object]], list[dict[str, object]], Counter]:
    preview: list[dict[str, object]] = []
    exclusion: list[dict[str, object]] = []
    counts: Counter = Counter()
    seen_signatures: dict[tuple[str, ...], str] = {}

    for path in collect_input_files():
        role = infer_role(path)
        rows = read_csv(path)
        counts["input_files"] += 1
        counts["input_rows"] += len(rows)

        for idx, row in enumerate(rows, start=1):
            school_key, school_name = infer_school(path, row)
            year = first(row, "year", "nf")
            province = first(row, "province", "ssmc")
            batch = first(row, "type", "zylx", "zslx")
            subject = normalize_subject(first(row, "subject_type", "science_category", "klmc", "kl"))
            major = first(row, "specialty", "major", "zydhmc", "zyzname")
            group_label = first(row, "selection_group", "zyzname", "zyzdm", "xkzybb", "tjfdm")
            plan_count = first(row, "plan_count", "plannedQuantity", "zsjhs")
            min_score = first(row, "minimum_score", "minScore", "lowestScore", "lowest_score")
            min_rank = first(row, "lowest_score_ranking", "minOrder", "minRank")
            source_url = first(row, "source_url")
            source_slug = first(row, "source_slug")
            requirement = first(row, "requirement", "xkkm", "kskmyqmc")
            remarks = first(row, "remarks")

            ordinary_physics_guangxi = (
                province == "广西"
                and subject == "物理类"
                and ("普通" in batch or batch == "本科普通批")
                and not has_any_special(batch, major, group_label, remarks)
            )
            special = has_any_special(batch, major, group_label, remarks)

            signature = (
                role,
                school_key,
                year,
                province,
                batch,
                subject,
                major,
                group_label,
                plan_count,
                min_score,
                min_rank,
                source_url,
            )
            duplicate_of = seen_signatures.get(signature, "")
            if not duplicate_of:
                seen_signatures[signature] = f"{path.name}:{idx}"

            if is_plan_role(role):
                row_kind = "official_plan_row"
            elif is_score_role(role):
                row_kind = "official_score_row"
            else:
                row_kind = "official_unknown_row"

            if ordinary_physics_guangxi and not duplicate_of:
                qa_status = "source_packet_ready_boundary_hold"
                required_resolution = (
                    "keep_as_decision_pool_source_packet_or_explicitly_approve_reference_trend_use"
                )
            elif duplicate_of:
                qa_status = "duplicate_hold"
                required_resolution = "dedupe_before_any_intake"
            elif special:
                qa_status = "special_type_hold"
                required_resolution = "exclude_or_keep_special_type_isolated"
            else:
                qa_status = "not_ordinary_physics_guangxi_hold"
                required_resolution = "exclude_from_strict_reference_trend_pool"

            record = {
                "record_id": f"official_cache_boundary_{len(preview) + 1:04d}",
                "source_file": str(path.relative_to(ROOT)),
                "source_row_number": idx,
                "school_key": school_key,
                "school_name": school_name,
                "row_kind": row_kind,
                "year": year,
                "province": province,
                "batch": batch,
                "subject_category": subject,
                "major_or_group": major,
                "group_label": group_label,
                "plan_count": plan_count,
                "minimum_score": min_score,
                "minimum_rank": min_rank,
                "requirement": requirement,
                "remarks": remarks,
                "source_url": source_url,
                "source_slug": source_slug,
                "ordinary_physics_guangxi": str(ordinary_physics_guangxi).lower(),
                "special_type_detected": str(special).lower(),
                "duplicate_of": duplicate_of,
                "qa_status": qa_status,
                "collector_confidence": "T2_official_structured_cache_row",
                "intended_layer": "source_packet_preview_only",
                "reference_trend_pool_eligible": "false",
                "decision_pool_boundary": "32_school_decision_pool_source_evidence_only",
                "canonical_ml_entry_open": "false",
                "required_resolution": required_resolution,
            }
            preview.append(record)

            counts[f"row_kind:{row_kind}"] += 1
            counts[f"qa_status:{qa_status}"] += 1
            counts[f"school:{school_name}"] += 1
            if ordinary_physics_guangxi:
                counts["ordinary_physics_guangxi_rows"] += 1
            if special:
                counts["special_type_detected_rows"] += 1
            if duplicate_of:
                counts["duplicate_rows"] += 1
            if source_url:
                counts["rows_with_source_url"] += 1
            if min_score:
                counts["rows_with_min_score"] += 1
            if min_rank:
                counts["rows_with_min_rank"] += 1
            if plan_count:
                counts["rows_with_plan_count"] += 1

            if qa_status != "source_packet_ready_boundary_hold":
                exclusion.append(
                    {
                        "record_id": f"official_cache_boundary_exclusion_{len(exclusion) + 1:04d}",
                        "source_record_id": record["record_id"],
                        "school_name": school_name,
                        "source_file": str(path.relative_to(ROOT)),
                        "qa_status": qa_status,
                        "exclusion_or_hold_reason": required_resolution,
                        "canonical_ml_entry_open": "false",
                        "reference_trend_pool_eligible": "false",
                    }
                )

    counts["unique_schools"] = len({str(r["school_name"]) for r in preview})
    counts["reference_trend_pool_eligible_rows"] = 0
    counts["canonical_ml_entry_open"] = 0
    counts["decision_pool_expansion_performed"] = 0
    return preview, exclusion, counts


def write_rollup(counts: Counter) -> None:
    rows = [
        ("input_files", counts["input_files"]),
        ("input_rows", counts["input_rows"]),
        ("unique_schools", counts["unique_schools"]),
        ("official_plan_rows", counts["row_kind:official_plan_row"]),
        ("official_score_rows", counts["row_kind:official_score_row"]),
        ("ordinary_physics_guangxi_rows", counts["ordinary_physics_guangxi_rows"]),
        ("source_packet_ready_boundary_hold_rows", counts["qa_status:source_packet_ready_boundary_hold"]),
        ("duplicate_hold_rows", counts["qa_status:duplicate_hold"]),
        ("special_type_hold_rows", counts["qa_status:special_type_hold"]),
        ("not_ordinary_physics_guangxi_hold_rows", counts["qa_status:not_ordinary_physics_guangxi_hold"]),
        ("rows_with_plan_count", counts["rows_with_plan_count"]),
        ("rows_with_min_score", counts["rows_with_min_score"]),
        ("rows_with_min_rank", counts["rows_with_min_rank"]),
        ("rows_with_source_url", counts["rows_with_source_url"]),
        ("reference_trend_pool_eligible_rows", counts["reference_trend_pool_eligible_rows"]),
        ("canonical_ml_entry_open", "false"),
        ("decision_pool_expansion_performed", "false"),
    ]
    write_csv(
        OUT_ROLLUP,
        [{"metric": metric, "value": value} for metric, value in rows],
        ["metric", "value"],
    )


def write_doc(counts: Counter) -> None:
    top_schools = [
        (key.removeprefix("school:"), value)
        for key, value in counts.items()
        if key.startswith("school:")
    ]
    top_schools.sort(key=lambda item: (-item[1], item[0]))
    school_lines = "\n".join(f"- {name}: {value} rows" for name, value in top_schools[:12])

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        f"""# Official Cache Boundary QA

日期：{date.today().isoformat()}

## 结论

已将 `reports/` 中已落地的官方广西 plan/score 行合并为 source-packet 边界 QA 预览。该批数据来自 32 所高精度 decision_pool 相关官方 API/缓存文件，因此本轮只登记为证据包预览，不进入 `reference_trend_pool` 统计背景，不写 canonical，不打开 ML。

## 覆盖

- input files: {counts['input_files']}
- input rows: {counts['input_rows']}
- unique schools: {counts['unique_schools']}
- official plan rows: {counts['row_kind:official_plan_row']}
- official score rows: {counts['row_kind:official_score_row']}
- ordinary physics Guangxi rows: {counts['ordinary_physics_guangxi_rows']}
- source-packet ready but boundary-hold rows: {counts['qa_status:source_packet_ready_boundary_hold']}
- duplicate hold rows: {counts['qa_status:duplicate_hold']}
- special type hold rows: {counts['qa_status:special_type_hold']}
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 学校覆盖

{school_lines}

## 下一步

1. 若用户明确批准，可把其中普通物理广西行作为 32 所 decision_pool 的 source evidence 继续做人工映射。
2. 若要用于趋势池，必须先单独批准“32 所是否可作为 reference trend calibration 样本”，否则继续保持边界隔离。
3. 下一轮自动化应回到 P0/P1 非主池官方计划来源发现，或解析上一轮云南中医药/南京中医药 PDF 候选。
""",
        encoding="utf-8",
    )


def main() -> None:
    preview, exclusion, counts = build_rows()

    preview_fields = [
        "record_id",
        "source_file",
        "source_row_number",
        "school_key",
        "school_name",
        "row_kind",
        "year",
        "province",
        "batch",
        "subject_category",
        "major_or_group",
        "group_label",
        "plan_count",
        "minimum_score",
        "minimum_rank",
        "requirement",
        "remarks",
        "source_url",
        "source_slug",
        "ordinary_physics_guangxi",
        "special_type_detected",
        "duplicate_of",
        "qa_status",
        "collector_confidence",
        "intended_layer",
        "reference_trend_pool_eligible",
        "decision_pool_boundary",
        "canonical_ml_entry_open",
        "required_resolution",
    ]
    exclusion_fields = [
        "record_id",
        "source_record_id",
        "school_name",
        "source_file",
        "qa_status",
        "exclusion_or_hold_reason",
        "canonical_ml_entry_open",
        "reference_trend_pool_eligible",
    ]
    write_csv(OUT_PREVIEW, preview, preview_fields)
    write_csv(OUT_EXCLUSION, exclusion, exclusion_fields)
    write_rollup(counts)
    write_doc(counts)

    print(f"official_cache_boundary_rows={len(preview)}")
    print(f"source_packet_ready_boundary_hold_rows={counts['qa_status:source_packet_ready_boundary_hold']}")
    print("reference_trend_pool_eligible_rows=0")


if __name__ == "__main__":
    main()
