from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


OUTPUT_FIELDS = [
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
]

SOURCES = [
    {
        "school_key": "hefei_gongda_211",
        "school_name": "合肥工业大学",
        "path": Path("clean_data/direct_page_structured/hfut_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "changan_211",
        "school_name": "长安大学",
        "path": Path("clean_data/official_api_structured/changan_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "fuzhou_daxue_211",
        "school_name": "福州大学",
        "path": Path("clean_data/official_html_structured/fzu_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "xinan_jiaoda_211",
        "school_name": "西南交通大学",
        "path": Path("clean_data/official_html_structured/xinan_jiaoda_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "wuhan_ligong_211",
        "school_name": "武汉理工大学",
        "path": Path("clean_data/official_api_structured/wuhan_ligong_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "nanli_211",
        "school_name": "南京理工大学",
        "path": Path("clean_data/official_api_structured/njust_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "xidian_211",
        "school_name": "西安电子科技大学",
        "path": Path("clean_data/official_api_structured/xidian_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "zhengzhou_daxue_211",
        "school_name": "郑州大学",
        "path": Path("clean_data/official_html_structured/zzu_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "donghua_211",
        "school_name": "东华大学",
        "path": Path("clean_data/article_structured/dhu_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "huabei_dianli_211",
        "school_name": "华北电力大学",
        "path": Path("clean_data/engineering_guangxi_seed/huabei_dianli_guangxi_score_major_physics.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "zhongguo_dizhi_beijing_211",
        "school_name": "中国地质大学北京",
        "path": Path("clean_data/engineering_guangxi_seed/zhongguo_dizhi_beijing_guangxi_score_major_physics.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "beijing_you_dian_211",
        "school_name": "北京邮电大学",
        "path": Path("clean_data/official_html_structured/beijing_you_dian_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "guangxi_daxue_211",
        "school_name": "广西大学",
        "path": Path("clean_data/official_html_structured/guangxi_daxue_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
    },
    {
        "school_key": "huadong_ligong_211",
        "school_name": "华东理工大学",
        "path": Path("clean_data/official_api_structured/huadong_ligong_guangxi_score_rows.csv"),
        "slug": "derived_major_summary",
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


def parse_int(value: str) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def extract_category_from_remarks(remarks: str) -> str:
    text = normalize_text(remarks)
    for prefix in ["招生类别=", "招生类型="]:
        if prefix in text:
            tail = text.split(prefix, 1)[1]
            return tail.split(";", 1)[0].strip()
    return ""


def derive_summary_rows(source: dict[str, object], rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        major_text = normalize_text(row.get("major", ""))
        if any(token in major_text for token in ["本科线", "省控线", "控制线", "特殊类型线", "总计"]):
            continue
        row_type = normalize_text(row.get("type", ""))
        subject_type = normalize_text(row.get("science_category") or row.get("subject_type"))
        remarks = normalize_text(row.get("remarks", ""))
        derived_category = extract_category_from_remarks(remarks)
        if row_type == "本科普通批" and derived_category:
            row_type = derived_category
        groups[
            (
                normalize_text(row.get("year", "")),
                normalize_text(row.get("province", "")),
                row_type,
                subject_type,
            )
        ].append(row)

    output: list[dict[str, str]] = []
    for (year, province, row_type, subject_type), subset in sorted(groups.items()):
        min_candidates: list[tuple[int, int, dict[str, str]]] = []
        max_candidates: list[tuple[int, dict[str, str]]] = []
        for row in subset:
            min_score = parse_int(row.get("minimum_score", ""))
            if min_score is not None:
                rank = parse_int(row.get("lowest_score_ranking", "")) or -1
                min_candidates.append((min_score, rank, row))
            max_score = parse_int(row.get("highest_score", ""))
            if max_score is not None:
                max_candidates.append((max_score, row))

        if not min_candidates and not max_candidates:
            continue

        min_score = ""
        min_rank = ""
        if min_candidates:
            # Lower score means wider threshold; for equal score use larger rank as the more conservative summary.
            min_score_value, min_rank_value, min_row = sorted(min_candidates, key=lambda item: (item[0], -item[1]))[0]
            min_score = str(min_score_value)
            min_rank = "" if min_rank_value < 0 else str(min_rank_value)
        else:
            min_row = subset[0]

        max_score = ""
        if max_candidates:
            max_score = str(max(max_candidates, key=lambda item: item[0])[0])

        source_url = normalize_text(min_row.get("source_url", ""))
        school_name = normalize_text(min_row.get("school_name", "")) or str(source["school_name"])
        school_key = str(source["school_key"])
        major_count = len(subset)
        remarks = (
            f"学校级摘要由官方专业分明细推导;专业条目数={major_count};"
            "最低分取各专业最低分最小值;最高分取各专业最高分最大值"
        )
        output.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": year,
                "province": province,
                "type": row_type,
                "subject_type": subject_type,
                "campus": "",
                "minimum_score": min_score,
                "minimum_rank": min_rank,
                "average_score": "",
                "maximum_score": max_score,
                "remarks": remarks,
                "record_id": f"{school_key}-derived-summary-{year}-{subject_type}-{row_type}",
                "source_url": source_url,
            }
        )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Derive school-level Guangxi score summary rows from official major-level score files."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("clean_data") / "derived_summary_structured",
        help="Output directory for per-school derived summary CSVs.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_major_score_summary_round.csv",
        help="Round summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    round_rows: list[dict[str, str]] = []
    for source in SOURCES:
        source_rows = read_rows(Path(source["path"]))
        derived_rows = derive_summary_rows(source, source_rows)
        output_path = args.output_dir / f"{source['school_key']}_derived_score_summary_rows.csv"
        write_rows(output_path, derived_rows, OUTPUT_FIELDS)
        round_rows.append(
            {
                "school_key": str(source["school_key"]),
                "school_name": str(source["school_name"]),
                "source_path": str(source["path"]),
                "derived_summary_rows": str(len(derived_rows)),
                "output_path": str(output_path),
            }
        )

    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "source_path", "derived_summary_rows", "output_path"],
    )
    print(f"Derived school-level Guangxi score summaries for {len(round_rows)} schools.")


if __name__ == "__main__":
    main()
