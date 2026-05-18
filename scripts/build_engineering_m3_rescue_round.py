from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

READINESS_PATH = CLEAN_DIR / "guangxi_pre_ml_model_readiness_merged.csv"
SOURCE_PACK_PATH = CLEAN_DIR / "guangxi_official_source_pack_merged.csv"
OUTPUT_PATH = CLEAN_DIR / "guangxi_m3_rescue_round_merged.csv"
SUMMARY_PATH = REPORT_DIR / "engineering_m3_rescue_round_school_summary.csv"
ROLLUP_PATH = REPORT_DIR / "engineering_m3_rescue_round_coverage_rollup.csv"

TARGET_KEYS = [
    "beijing_you_dian_211",
    "hebei_gongye_211",
    "taiyuan_ligong_211",
    "donghua_211",
    "suzhou_daxue_211",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def classify(row: dict[str, str]) -> tuple[str, str]:
    key = row["school_key"]
    band = row.get("readiness_band", "")
    latest_year = row.get("latest_year", "")
    minimum_score = row.get("minimum_score", "")
    minimum_rank = row.get("minimum_rank", "")

    if key == "donghua_211" and band == "M2_comparable_ready_with_note":
        return (
            "R1_rescued_by_rank_inference",
            "保留2025物化组，继续补趋势或计划补充说明",
        )
    if key == "suzhou_daxue_211" and band == "M2_comparable_ready_with_note":
        return (
            "R1_rescued_by_rank_inference",
            "保留2024可比摘要，后续若拿到2025官方分数再前推",
        )
    if key == "beijing_you_dian_211":
        return (
            "R2_old_legacy_score_only",
            "当前仅有2023理工类分数，等待更新官方物理类或近年广西分数来源",
        )
    if key == "hebei_gongye_211":
        return (
            "R3_plan_only_wait_score",
            "已有2024/2025计划与录取通知，但缺最低分和位次，优先补学校级分数来源",
        )
    if key == "taiyuan_ligong_211":
        return (
            "R3_plan_only_wait_score",
            "已有2025计划与早年摘要，但缺近年最低分和位次，优先补学校级分数来源",
        )
    if not minimum_score and not minimum_rank and latest_year:
        return ("R4_manual_followup", "保留现状，人工复核下一步来源")
    return ("R0_stable", "当前状态稳定")


def main() -> None:
    readiness_rows = read_csv(READINESS_PATH)
    source_rows = {row["school_key"]: row for row in read_csv(SOURCE_PACK_PATH)}

    merged_rows: list[dict[str, str]] = []
    for row in readiness_rows:
        key = row["school_key"]
        if key not in TARGET_KEYS:
            continue
        source_row = source_rows.get(key, {})
        rescue_band, next_action = classify(row)
        merged_rows.append(
            {
                "school_key": key,
                "school_name": row.get("school_name", ""),
                "latest_year": row.get("latest_year", ""),
                "reference_year": row.get("reference_year", ""),
                "minimum_score": row.get("minimum_score", ""),
                "minimum_rank": row.get("minimum_rank", ""),
                "trend_signal": row.get("trend_signal", ""),
                "readiness_band": row.get("readiness_band", ""),
                "rescue_band": rescue_band,
                "next_action": next_action,
                "plan_source_url": source_row.get("plan_source_url", ""),
                "score_source_url": source_row.get("score_source_url", ""),
                "notes": (
                    "本轮M3修复跟踪: "
                    + ("已补可比位次" if rescue_band == "R1_rescued_by_rank_inference" else "仍待补关键字段")
                ),
            }
        )

    fieldnames = [
        "school_key",
        "school_name",
        "latest_year",
        "reference_year",
        "minimum_score",
        "minimum_rank",
        "trend_signal",
        "readiness_band",
        "rescue_band",
        "next_action",
        "plan_source_url",
        "score_source_url",
        "notes",
    ]
    write_csv(OUTPUT_PATH, merged_rows, fieldnames)

    summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "m3_rescue_round_rows": "1",
            "rescue_band": row["rescue_band"],
            "readiness_band": row["readiness_band"],
            "minimum_score": row["minimum_score"],
            "minimum_rank": row["minimum_rank"],
            "reference_year": row["reference_year"],
            "next_action": row["next_action"],
        }
        for row in merged_rows
    ]
    write_csv(
        SUMMARY_PATH,
        summary_rows,
        [
            "school_key",
            "school_name",
            "m3_rescue_round_rows",
            "rescue_band",
            "readiness_band",
            "minimum_score",
            "minimum_rank",
            "reference_year",
            "next_action",
        ],
    )

    rescue_counts: dict[str, int] = {}
    for row in merged_rows:
        rescue_counts[row["rescue_band"]] = rescue_counts.get(row["rescue_band"], 0) + 1

    rollup_rows = [
        {
            "metric": "m3_rescue_round_schools",
            "value": str(len(merged_rows)),
        },
        {
            "metric": "rescued_to_m2_count",
            "value": str(sum(1 for row in merged_rows if row["rescue_band"] == "R1_rescued_by_rank_inference")),
        },
        {
            "metric": "still_missing_score_count",
            "value": str(sum(1 for row in merged_rows if row["rescue_band"] == "R3_plan_only_wait_score")),
        },
        {
            "metric": "legacy_score_only_count",
            "value": str(sum(1 for row in merged_rows if row["rescue_band"] == "R2_old_legacy_score_only")),
        },
    ]
    for band, count in sorted(rescue_counts.items()):
        rollup_rows.append({"metric": f"count_{band}", "value": str(count)})
    write_csv(ROLLUP_PATH, rollup_rows, ["metric", "value"])

    print(
        "Wrote M3 rescue round for "
        f"{len(merged_rows)} schools "
        f"({sum(1 for row in merged_rows if row['rescue_band'] == 'R1_rescued_by_rank_inference')} rescued to M2)."
    )


if __name__ == "__main__":
    main()
