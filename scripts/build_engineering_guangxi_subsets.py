from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_guangxi_subset import (
    attach_school,
    filter_guangxi_physics,
    read_rows,
    write_rows,
)


def maybe_read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_rows(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build Guangxi physics seed subsets from normalized engineering API tables."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("clean_data") / "engineering_api_a1_a2",
        help="Directory containing normalized API CSVs.",
    )
    parser.add_argument(
        "--official-dir",
        type=Path,
        default=Path("clean_data") / "engineering_api_official",
        help="Directory containing official normalized API CSVs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed",
        help="Output directory for Guangxi subset CSVs.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("reports") / "engineering_guangxi_subset_summary.csv",
        help="Summary CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    ajax_dir = Path("clean_data") / "engineering_api_ajax_family"
    official_dir = args.official_dir

    huabei_plan = filter_guangxi_physics(
        read_rows(input_dir / "huabei_dianli_plan_rows.csv"),
        province_field="province",
        category_field="science_category",
    )
    huabei_score_summary = filter_guangxi_physics(
        read_rows(input_dir / "huabei_dianli_score_summary_rows.csv"),
        province_field="province",
        category_field="science_category",
    )
    huabei_score_major = filter_guangxi_physics(
        read_rows(input_dir / "huabei_dianli_score_major_rows.csv"),
        province_field="province",
        category_field="science_category",
    )
    nanhang_plan = filter_guangxi_physics(
        read_rows(input_dir / "nanhang_plan_query_rows.csv"),
        province_field="province",
        category_field="subject",
    )
    bjtu_plan = filter_guangxi_physics(
        maybe_read_rows(ajax_dir / "beijing_jiaotong_plan_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    bjtu_score_summary = filter_guangxi_physics(
        maybe_read_rows(ajax_dir / "beijing_jiaotong_score_summary_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    bjtu_score_major = filter_guangxi_physics(
        maybe_read_rows(ajax_dir / "beijing_jiaotong_score_major_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    cugb_plan = filter_guangxi_physics(
        maybe_read_rows(ajax_dir / "zhongguo_dizhi_beijing_plan_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    cugb_score_summary = filter_guangxi_physics(
        maybe_read_rows(ajax_dir / "zhongguo_dizhi_beijing_score_summary_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    cugb_score_major = filter_guangxi_physics(
        maybe_read_rows(ajax_dir / "zhongguo_dizhi_beijing_score_major_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    ecust_plan = filter_guangxi_physics(
        maybe_read_rows(official_dir / "huadong_ligong_plan_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    ecust_score_summary = filter_guangxi_physics(
        maybe_read_rows(official_dir / "huadong_ligong_score_summary_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )
    ecust_score_major = filter_guangxi_physics(
        maybe_read_rows(official_dir / "huadong_ligong_score_major_rows.csv"),
        province_field="province",
        category_field="subject_type",
    )

    write_rows(
        output_dir / "huabei_dianli_guangxi_plan_physics.csv",
        huabei_plan,
        [
            "year",
            "province",
            "type",
            "science_category",
            "major",
            "planned_quantity",
            "requirement",
            "record_id",
            "source_url",
        ],
    )
    write_rows(
        output_dir / "huabei_dianli_guangxi_score_summary_physics.csv",
        huabei_score_summary,
        [
            "year",
            "province",
            "type",
            "science_category",
            "highest_score",
            "minimum_score",
            "lowest_score_ranking",
            "record_id",
            "source_url",
        ],
    )
    write_rows(
        output_dir / "huabei_dianli_guangxi_score_major_physics.csv",
        huabei_score_major,
        [
            "year",
            "province",
            "type",
            "science_category",
            "major",
            "requirement",
            "highest_score",
            "minimum_score",
            "lowest_score_ranking",
            "record_id",
            "source_url",
        ],
    )
    write_rows(
        output_dir / "nanhang_guangxi_plan_physics.csv",
        nanhang_plan,
        [
            "year",
            "province",
            "type",
            "subject",
            "college",
            "specialty",
            "plan_number",
            "weight",
            "record_id",
            "introduction_link",
            "source_slug",
        ],
    )
    write_rows(
        output_dir / "beijing_jiaotong_guangxi_plan_physics.csv",
        bjtu_plan,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "specialty",
            "plan_count",
            "requirement",
            "remarks",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "beijing_jiaotong_guangxi_score_summary_physics.csv",
        bjtu_score_summary,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "campus",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "beijing_jiaotong_guangxi_score_major_physics.csv",
        bjtu_score_major,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "major",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "remarks",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "zhongguo_dizhi_beijing_guangxi_plan_physics.csv",
        cugb_plan,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "specialty",
            "plan_count",
            "requirement",
            "remarks",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "zhongguo_dizhi_beijing_guangxi_score_summary_physics.csv",
        cugb_score_summary,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "campus",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "zhongguo_dizhi_beijing_guangxi_score_major_physics.csv",
        cugb_score_major,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "major",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "remarks",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "huadong_ligong_guangxi_plan_physics.csv",
        ecust_plan,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "specialty",
            "plan_count",
            "requirement",
            "remarks",
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "huadong_ligong_guangxi_score_summary_physics.csv",
        ecust_score_summary,
        [
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
            "source_payload",
        ],
    )
    write_rows(
        output_dir / "huadong_ligong_guangxi_score_major_physics.csv",
        ecust_score_major,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "major",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "remarks",
            "source_payload",
        ],
    )

    merged_plan = attach_school(huabei_plan, "华北电力大学", "huabei_dianli_211")
    for row in merged_plan:
        row["subject_type"] = row.pop("science_category", "")
        row["plan_count"] = row.pop("planned_quantity", "")
        row["specialty"] = row.pop("major", "")
        row["college"] = ""

    nanhang_plan_tagged = attach_school(nanhang_plan, "南京航空航天大学招生网", "nanhang_211")
    for row in nanhang_plan_tagged:
        row["subject_type"] = row.pop("subject", "")
        row["plan_count"] = row.pop("plan_number", "")
        row["requirement"] = ""
        row["specialty"] = row.pop("specialty", "")

    bjtu_plan_tagged = attach_school(bjtu_plan, "北京交通大学招生与就业工作处", "beijing_jiaotong_211")
    for row in bjtu_plan_tagged:
        row["weight"] = ""
        row["record_id"] = ""
        row["source_url"] = ""
        row["introduction_link"] = ""
        row["source_slug"] = row.pop("source_payload", "")
    cugb_plan_tagged = attach_school(cugb_plan, "中国地质大学北京", "zhongguo_dizhi_beijing_211")
    for row in cugb_plan_tagged:
        row["weight"] = ""
        row["record_id"] = ""
        row["source_url"] = ""
        row["introduction_link"] = ""
        row["source_slug"] = row.pop("source_payload", "")
    ecust_plan_tagged = attach_school(ecust_plan, "华东理工大学本科招生网", "huadong_ligong_211")
    for row in ecust_plan_tagged:
        row["weight"] = ""
        row["record_id"] = ""
        row["source_url"] = ""
        row["introduction_link"] = ""
        row["source_slug"] = row.pop("source_payload", "")

    merged_plan_rows = (
        merged_plan
        + nanhang_plan_tagged
        + bjtu_plan_tagged
        + cugb_plan_tagged
        + ecust_plan_tagged
    )
    write_rows(
        output_dir / "guangxi_physics_plan_seed_merged.csv",
        merged_plan_rows,
        [
            "school_name",
            "school_key",
            "year",
            "province",
            "type",
            "subject_type",
            "college",
            "specialty",
            "plan_count",
            "requirement",
            "selection_group",
            "campus",
            "remarks",
            "weight",
            "record_id",
            "source_url",
            "introduction_link",
            "source_slug",
        ],
    )

    merged_score_major = attach_school(huabei_score_major, "华北电力大学", "huabei_dianli_211")
    bjtu_score_major_tagged = attach_school(bjtu_score_major, "北京交通大学招生与就业工作处", "beijing_jiaotong_211")
    for row in bjtu_score_major_tagged:
        row["science_category"] = row.pop("subject_type", "")
        row["requirement"] = row.pop("selection_group", "")
        row["highest_score"] = row.pop("maximum_score", "")
        row["source_url"] = ""
        row["record_id"] = ""
        row["lowest_score_ranking"] = row.pop("minimum_rank", "")
        row.pop("average_score", None)
        row.pop("source_payload", None)
    cugb_score_major_tagged = attach_school(cugb_score_major, "中国地质大学北京", "zhongguo_dizhi_beijing_211")
    for row in cugb_score_major_tagged:
        row["science_category"] = row.pop("subject_type", "")
        row["requirement"] = row.pop("selection_group", "")
        row["highest_score"] = row.pop("maximum_score", "")
        row["source_url"] = ""
        row["record_id"] = ""
        row["lowest_score_ranking"] = row.pop("minimum_rank", "")
        row.pop("average_score", None)
        row.pop("source_payload", None)
    ecust_score_major_tagged = attach_school(ecust_score_major, "华东理工大学本科招生网", "huadong_ligong_211")
    for row in ecust_score_major_tagged:
        row["science_category"] = row.pop("subject_type", "")
        row["requirement"] = row.pop("selection_group", "")
        row["highest_score"] = row.pop("maximum_score", "")
        row["source_url"] = ""
        row["record_id"] = ""
        row["lowest_score_ranking"] = row.pop("minimum_rank", "")
        row.pop("average_score", None)
        row.pop("source_payload", None)
    merged_score_major = (
        merged_score_major
        + bjtu_score_major_tagged
        + cugb_score_major_tagged
        + ecust_score_major_tagged
    )
    write_rows(
        output_dir / "guangxi_physics_score_major_seed_merged.csv",
        merged_score_major,
        [
            "school_name",
            "school_key",
            "year",
            "province",
            "type",
            "science_category",
            "major",
            "requirement",
            "campus",
            "remarks",
            "highest_score",
            "minimum_score",
            "lowest_score_ranking",
            "record_id",
            "source_url",
        ],
    )

    summary_rows = [
        {
            "dataset": "huabei_dianli_guangxi_plan_physics",
            "rows": str(len(huabei_plan)),
            "notes": "Guangxi physics plan rows from Huabei static JSON.",
        },
        {
            "dataset": "huabei_dianli_guangxi_score_summary_physics",
            "rows": str(len(huabei_score_summary)),
            "notes": "Guangxi physics score summary rows from Huabei static JSON.",
        },
        {
            "dataset": "huabei_dianli_guangxi_score_major_physics",
            "rows": str(len(huabei_score_major)),
            "notes": "Guangxi physics major score rows from Huabei static JSON.",
        },
        {
            "dataset": "nanhang_guangxi_plan_physics",
            "rows": str(len(nanhang_plan)),
            "notes": "Guangxi physics plan rows from Nanhang enrollment API.",
        },
        {
            "dataset": "beijing_jiaotong_guangxi_plan_physics",
            "rows": str(len(bjtu_plan)),
            "notes": "Guangxi physics plan rows from Beijing Jiaotong ajax payload.",
        },
        {
            "dataset": "beijing_jiaotong_guangxi_score_summary_physics",
            "rows": str(len(bjtu_score_summary)),
            "notes": "Guangxi physics score-summary rows from Beijing Jiaotong ajax payload.",
        },
        {
            "dataset": "beijing_jiaotong_guangxi_score_major_physics",
            "rows": str(len(bjtu_score_major)),
            "notes": "Guangxi physics major-score rows from Beijing Jiaotong ajax payload.",
        },
        {
            "dataset": "zhongguo_dizhi_beijing_guangxi_plan_physics",
            "rows": str(len(cugb_plan)),
            "notes": "Guangxi physics plan rows from CUGB ajax payload.",
        },
        {
            "dataset": "zhongguo_dizhi_beijing_guangxi_score_summary_physics",
            "rows": str(len(cugb_score_summary)),
            "notes": "Guangxi physics score-summary rows from CUGB ajax payload.",
        },
        {
            "dataset": "zhongguo_dizhi_beijing_guangxi_score_major_physics",
            "rows": str(len(cugb_score_major)),
            "notes": "Guangxi physics major-score rows from CUGB ajax payload.",
        },
        {
            "dataset": "huadong_ligong_guangxi_plan_physics",
            "rows": str(len(ecust_plan)),
            "notes": "Guangxi physics plan rows from ECUST official lqxx2 API.",
        },
        {
            "dataset": "huadong_ligong_guangxi_score_summary_physics",
            "rows": str(len(ecust_score_summary)),
            "notes": "Guangxi physics score-summary rows from ECUST official lqxx2 API.",
        },
        {
            "dataset": "huadong_ligong_guangxi_score_major_physics",
            "rows": str(len(ecust_score_major)),
            "notes": "Guangxi physics major-score rows from ECUST official lqxx2 API.",
        },
        {
            "dataset": "guangxi_physics_plan_seed_merged",
            "rows": str(len(merged_plan_rows)),
            "notes": "Merged Guangxi physics plan rows from currently successful core schools.",
        },
        {
            "dataset": "guangxi_physics_score_major_seed_merged",
            "rows": str(len(merged_score_major)),
            "notes": "Merged Guangxi physics major-score rows from currently successful core schools.",
        },
    ]
    write_rows(args.summary, summary_rows, ["dataset", "rows", "notes"])

    print(
        f"Built Guangxi subset seeds in {output_dir} "
        f"with summary {args.summary}."
    )


if __name__ == "__main__":
    main()
