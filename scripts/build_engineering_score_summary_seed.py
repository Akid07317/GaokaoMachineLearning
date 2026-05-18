from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "subject_type",
    "campus",
    "minimum_score",
    "minimum_rank",
    "average_score",
    "maximum_score",
    "remarks",
    "record_id",
    "source_url",
    "source_slug",
]

SCORE_RANK_PATH = Path("clean_data/score_rank_table_seed.csv")

SOURCES = [
    {
        "school_name": "北京交通大学招生与就业工作处",
        "school_key": "beijing_jiaotong_211",
        "path": Path("clean_data/engineering_guangxi_seed/beijing_jiaotong_guangxi_score_summary_physics.csv"),
        "kind": "ajax_summary",
    },
    {
        "school_name": "中国地质大学北京",
        "school_key": "zhongguo_dizhi_beijing_211",
        "path": Path("clean_data/engineering_guangxi_seed/zhongguo_dizhi_beijing_guangxi_score_summary_physics.csv"),
        "kind": "ajax_summary",
    },
    {
        "school_name": "华北电力大学",
        "school_key": "huabei_dianli_211",
        "path": Path("clean_data/engineering_guangxi_seed/huabei_dianli_guangxi_score_summary_physics.csv"),
        "kind": "official_summary",
    },
    {
        "school_name": "华东理工大学本科招生网",
        "school_key": "huadong_ligong_211",
        "path": Path("clean_data/engineering_guangxi_seed/huadong_ligong_guangxi_score_summary_physics.csv"),
        "kind": "official_summary",
    },
    {
        "school_name": "南京航空航天大学",
        "school_key": "nanhang_211",
        "path": Path("clean_data/official_api_structured/nanhang_guangxi_score_overview_rows.csv"),
        "kind": "official_overview",
    },
    {
        "school_name": "河海大学",
        "school_key": "hehai_211",
        "path": Path("clean_data/official_api_structured/hehai_guangxi_score_summary_rows.csv"),
        "kind": "official_summary",
    },
    {
        "school_name": "北京工业大学",
        "school_key": "beijing_gongye_211",
        "path": Path("clean_data/official_html_structured/beijing_gongye_guangxi_score_summary_rows.csv"),
        "kind": "official_summary",
    },
    {
        "school_name": "苏州大学",
        "school_key": "suzhou_daxue_211",
        "path": Path("clean_data/official_html_structured/suzhou_daxue_guangxi_score_summary_rows.csv"),
        "kind": "official_summary",
    },
    {
        "school_name": "太原理工大学",
        "school_key": "taiyuan_ligong_211",
        "path": Path("clean_data/official_html_structured/taiyuan_ligong_guangxi_score_summary_rows_v2.csv"),
        "kind": "official_summary",
    },
    {
        "school_name": "河北工业大学",
        "school_key": "hebei_gongye_211",
        "path": Path("clean_data/official_html_structured/hebei_gongye_guangxi_notice_rows.csv"),
        "kind": "official_notice",
    },
    {
        "school_name": "合肥工业大学",
        "school_key": "hefei_gongda_211",
        "path": Path("clean_data/derived_summary_structured/hefei_gongda_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "长安大学",
        "school_key": "changan_211",
        "path": Path("clean_data/derived_summary_structured/changan_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "福州大学",
        "school_key": "fuzhou_daxue_211",
        "path": Path("clean_data/derived_summary_structured/fuzhou_daxue_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "西南交通大学",
        "school_key": "xinan_jiaoda_211",
        "path": Path("clean_data/derived_summary_structured/xinan_jiaoda_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "武汉理工大学",
        "school_key": "wuhan_ligong_211",
        "path": Path("clean_data/derived_summary_structured/wuhan_ligong_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "南京理工大学",
        "school_key": "nanli_211",
        "path": Path("clean_data/derived_summary_structured/nanli_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "西安电子科技大学",
        "school_key": "xidian_211",
        "path": Path("clean_data/derived_summary_structured/xidian_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "郑州大学",
        "school_key": "zhengzhou_daxue_211",
        "path": Path("clean_data/derived_summary_structured/zhengzhou_daxue_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "东华大学",
        "school_key": "donghua_211",
        "path": Path("clean_data/derived_summary_structured/donghua_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "华北电力大学",
        "school_key": "huabei_dianli_211",
        "path": Path("clean_data/derived_summary_structured/huabei_dianli_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "中国地质大学北京",
        "school_key": "zhongguo_dizhi_beijing_211",
        "path": Path("clean_data/derived_summary_structured/zhongguo_dizhi_beijing_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "path": Path("clean_data/derived_summary_structured/beijing_you_dian_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "path": Path("clean_data/derived_summary_structured/guangxi_daxue_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
    {
        "school_name": "华东理工大学本科招生网",
        "school_key": "huadong_ligong_211",
        "path": Path("clean_data/derived_summary_structured/huadong_ligong_211_derived_score_summary_rows.csv"),
        "kind": "derived_major_summary",
    },
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def load_rank_lookup(path: Path) -> dict[tuple[str, str, str], str]:
    if not path.exists():
        return {}
    lookup: dict[tuple[str, str, str], str] = {}
    with path.open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            year = normalize_text(row.get("year"))
            province = normalize_text(row.get("province"))
            subject_type = normalize_text(row.get("subject_type"))
            score = normalize_text(row.get("score"))
            rank_end = normalize_text(row.get("rank_end"))
            if not (year and province and subject_type and score and rank_end):
                continue
            lookup[(year, province, score)] = rank_end
    return lookup


def normalize_source_row(
    row: dict[str, str],
    source: dict[str, object],
    index: int,
    rank_lookup: dict[tuple[str, str, str], str],
) -> dict[str, str]:
    source_kind = str(source["kind"])
    subject_type = normalize_text(row.get("subject_type") or row.get("science_category") or row.get("discipline"))
    maximum_score = normalize_text(row.get("maximum_score") or row.get("highest_score"))
    record_id = normalize_text(row.get("record_id")) or f"{source['school_key']}-summary-{index}"
    row_type = normalize_text(row.get("type") or row.get("batch_name"))
    campus = normalize_text(row.get("campus") or row.get("group"))
    remarks = normalize_text(row.get("remarks"))
    if source_kind == "official_notice":
        remarks = ";".join(
            part
            for part in [
                f"录取批次={normalize_text(row.get('batch_name'))}" if normalize_text(row.get("batch_name")) else "",
                f"录取人数={normalize_text(row.get('admit_count'))}" if normalize_text(row.get("admit_count")) else "",
                f"公告日期={normalize_text(row.get('notice_date_text'))}" if normalize_text(row.get("notice_date_text")) else "",
                "来源=官方录取完结通知",
            ]
            if part
        )
    elif not remarks and normalize_text(row.get("major")):
        remarks = normalize_text(row.get("major"))
    minimum_score = normalize_text(row.get("minimum_score"))
    minimum_rank = normalize_text(row.get("minimum_rank") or row.get("lowest_score_ranking"))
    year = normalize_text(row.get("year"))
    province = normalize_text(row.get("province"))
    score_subject_is_physics_like = (
        "物理" in subject_type
        or "物化" in subject_type
        or (subject_type == "理工类" and year >= "2024")
    )
    if (
        not minimum_rank
        and minimum_score
        and year
        and province == "广西"
        and score_subject_is_physics_like
    ):
        inferred_rank = rank_lookup.get((year, province, minimum_score), "")
        if inferred_rank:
            minimum_rank = inferred_rank
            inference_note = "最低位次=按同年广西物理类一分一档保守换算(rank_end)"
            if "物化" in subject_type:
                inference_note += f";原始科类标签={subject_type}"
            elif subject_type == "理工类" and year >= "2024":
                inference_note += ";原始科类标签=理工类(按2024+广西物理类保守映射)"
            remarks = f"{remarks};{inference_note}" if remarks else inference_note
    return {
        "school_name": str(source["school_name"]),
        "school_key": str(source["school_key"]),
        "year": year,
        "province": province,
        "type": row_type,
        "subject_type": subject_type,
        "campus": campus,
        "minimum_score": minimum_score,
        "minimum_rank": minimum_rank,
        "average_score": normalize_text(row.get("average_score")),
        "maximum_score": maximum_score,
        "remarks": remarks,
        "record_id": record_id,
        "source_url": normalize_text(row.get("source_url")),
        "source_slug": source_kind,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge official Guangxi school-level score summary rows for engineering target schools."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data/engineering_guangxi_seed/guangxi_physics_score_summary_seed_merged.csv"),
        help="Merged Guangxi score-summary seed CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports/engineering_guangxi_score_summary_school_summary.csv"),
        help="School-level summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports/engineering_guangxi_score_summary_coverage_rollup.csv"),
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rank_lookup = load_rank_lookup(SCORE_RANK_PATH)
    merged: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for source in SOURCES:
        rows = read_rows(Path(source["path"]))
        for index, row in enumerate(rows, start=1):
            normalized = normalize_source_row(row, source, index, rank_lookup)
            key = (normalized["school_key"], normalized["record_id"])
            merged[key] = normalized

    merged_rows = list(merged.values())
    merged_rows.sort(
        key=lambda row: (row["school_key"], row["year"], row["type"], row["subject_type"], row["record_id"])
    )
    write_rows(args.output, merged_rows, FIELDS)

    school_counts = Counter(row["school_key"] for row in merged_rows)
    school_names = {row["school_key"]: row["school_name"] for row in merged_rows}
    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": school_names.get(school_key, ""),
            "score_summary_rows": str(count),
        }
        for school_key, count in sorted(school_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(args.school_summary_output, school_summary_rows, ["school_key", "school_name", "score_summary_rows"])

    coverage_rows = [
        {"metric": "target_pool_schools", "value": "32"},
        {"metric": "structured_score_summary_schools", "value": str(len(school_counts))},
        {
            "metric": "structured_score_summary_coverage_ratio",
            "value": f"{len(school_counts) / 32:.4f}",
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(f"Wrote merged Guangxi score-summary seed rows for {len(school_counts)} schools.")


if __name__ == "__main__":
    main()
