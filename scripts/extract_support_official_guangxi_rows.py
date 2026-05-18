from __future__ import annotations

import argparse
import csv
from pathlib import Path


SCORE_FIELDS = [
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
]

GXU_SCORE_ROWS = [
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "物理类",
        "major": "自动化",
        "requirement": "物理+化学",
        "campus": "",
        "remarks": "招生类别=普通类;专业组=151物理类;平均分=593;来源=广西大学2024年广西区内录取统计表",
        "highest_score": "603",
        "minimum_score": "590",
        "lowest_score_ranking": "",
        "record_id": "gxu-score-2024-automatic-guangxi",
        "source_url": "https://zs.gxu.edu.cn/info/1277/1968.htm",
    },
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "物理类",
        "major": "自动化（与华南理工大学联合培养）",
        "requirement": "物理+化学",
        "campus": "",
        "remarks": "招生类别=普通类;专业组=151物理类;平均分=610;来源=广西大学2024年广西区内录取统计表",
        "highest_score": "612",
        "minimum_score": "608",
        "lowest_score_ranking": "",
        "record_id": "gxu-score-2024-automatic-scut-guangxi",
        "source_url": "https://zs.gxu.edu.cn/info/1277/1968.htm",
    },
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "物理类",
        "major": "电气工程及其自动化",
        "requirement": "物理+化学",
        "campus": "",
        "remarks": "招生类别=高校专项计划;专业组=651物理类;平均分=588;来源=广西大学2024年广西区内录取统计表",
        "highest_score": "601",
        "minimum_score": "581",
        "lowest_score_ranking": "",
        "record_id": "gxu-score-2024-ee-highered-guangxi",
        "source_url": "https://zs.gxu.edu.cn/info/1277/1968.htm",
    },
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "物理类",
        "major": "电子科学与技术",
        "requirement": "物理+化学",
        "campus": "",
        "remarks": "招生类别=高校专项计划;专业组=651物理类;平均分=578;来源=广西大学2024年广西区内录取统计表",
        "highest_score": "583",
        "minimum_score": "576",
        "lowest_score_ranking": "",
        "record_id": "gxu-score-2024-electronics-highered-guangxi",
        "source_url": "https://zs.gxu.edu.cn/info/1277/1968.htm",
    },
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "物理类",
        "major": "计算机科学与技术",
        "requirement": "物理+化学",
        "campus": "",
        "remarks": "招生类别=高校专项计划;专业组=651物理类;平均分=584;来源=广西大学2024年广西区内录取统计表",
        "highest_score": "589",
        "minimum_score": "581",
        "lowest_score_ranking": "",
        "record_id": "gxu-score-2024-cs-highered-guangxi",
        "source_url": "https://zs.gxu.edu.cn/info/1277/1968.htm",
    },
    {
        "school_name": "广西大学",
        "school_key": "guangxi_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "物理类",
        "major": "数学类",
        "requirement": "物理+化学",
        "campus": "",
        "remarks": "招生类别=国家专项计划;专业组=551物理类;平均分=567;来源=广西大学2024年广西区内录取统计表",
        "highest_score": "581",
        "minimum_score": "561",
        "lowest_score_ranking": "",
        "record_id": "gxu-score-2024-math-national-guangxi",
        "source_url": "https://zs.gxu.edu.cn/info/1277/1968.htm",
    },
]

SUDA_SCORE_ROWS = [
    {
        "school_name": "苏州大学",
        "school_key": "suzhou_daxue_211",
        "year": "2021",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "普通类非定向计划(学校级摘要)",
        "requirement": "",
        "campus": "",
        "remarks": "平均分=589;省控线/特殊类型线=487;投档一志愿率=100;来源=2021年苏州大学普通类非定向计划各省录取最高分、最低分、平均分一览表",
        "highest_score": "614",
        "minimum_score": "580",
        "lowest_score_ranking": "",
        "record_id": "suda-summary-2021-guangxi",
        "source_url": "https://zsb.suda.edu.cn/view.aspx?id=2591",
    },
    {
        "school_name": "苏州大学",
        "school_key": "suzhou_daxue_211",
        "year": "2022",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "普通类非定向计划(学校级摘要)",
        "requirement": "",
        "campus": "",
        "remarks": "平均分=589;省控线/特殊类型控制线=475;来源=2022年苏州大学普通类非定向计划各省录取最高分、最低分、平均分一览表",
        "highest_score": "623",
        "minimum_score": "537",
        "lowest_score_ranking": "",
        "record_id": "suda-summary-2022-guangxi",
        "source_url": "https://zsb.suda.edu.cn/view.aspx?id=2692",
    },
    {
        "school_name": "苏州大学",
        "school_key": "suzhou_daxue_211",
        "year": "2024",
        "province": "广西",
        "type": "本科普通批",
        "science_category": "理工类",
        "major": "普通类非定向计划(学校级摘要)",
        "requirement": "",
        "campus": "",
        "remarks": "平均分=594;省控线/特殊类型控制线=506;来源=2024年苏州大学普通类非定向计划各省录取最高分、最低分、平均分一览表",
        "highest_score": "631",
        "minimum_score": "573",
        "lowest_score_ranking": "",
        "record_id": "suda-summary-2024-guangxi",
        "source_url": "https://zsb.suda.edu.cn/view.aspx?id=2779",
    },
]

BUPT_SCORE_ROWS = [
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "电子信息类（元班）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=5;平均分=647;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "653",
        "minimum_score": "640",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-yuan-electronics-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "通信工程（大类招生）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=21;平均分=632;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "637",
        "minimum_score": "630",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-telecom-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "电子信息类",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=19;平均分=630;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "635",
        "minimum_score": "627",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-electronics-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "计算机类",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=20;平均分=637;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "645",
        "minimum_score": "633",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-cs-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "网络空间安全（大类招生）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=13;平均分=628;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "643",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-cyber-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "人工智能（大类招生）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=21;平均分=628;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "631",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-ai-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "自动化类（智能机器人与智慧物流）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=7;平均分=625;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "625",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-automation-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "金融科技",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=4;平均分=627;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "630",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-fintech-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "理科试验班（信息科学）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=5;平均分=626;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "629",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-science-trial-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "智能交互设计",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=4;平均分=626;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "630",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-design-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
    {
        "school_name": "北京邮电大学",
        "school_key": "beijing_you_dian_211",
        "year": "2023",
        "province": "广西",
        "type": "本科第一批",
        "science_category": "理工类",
        "major": "总计（普通理科专业）",
        "requirement": "",
        "campus": "",
        "remarks": "录取人数=119;平均分=631;来源=北京邮电大学2023年各专业录取分数——广西壮族自治区",
        "highest_score": "653",
        "minimum_score": "625",
        "lowest_score_ranking": "",
        "record_id": "bupt-score-2023-total-general-guangxi",
        "source_url": "https://zsb.bupt.edu.cn/info/1088/2198.htm",
    },
]

HEBUT_NOTICE_ROWS = [
    {
        "school_key": "hebei_gongye_211",
        "school_name": "河北工业大学",
        "year": "2024",
        "province": "广西",
        "batch_name": "本科普通批",
        "admit_count": "41",
        "notice_date_text": "7月27日",
        "source_url": "https://zs.hebut.edu.cn/2024-07-12/205.html",
        "record_id": "hebut-notice-205-guangxi",
    },
    {
        "school_key": "hebei_gongye_211",
        "school_name": "河北工业大学",
        "year": "2025",
        "province": "广西",
        "batch_name": "本科普通批",
        "admit_count": "58",
        "notice_date_text": "7月21日",
        "source_url": "https://zs.hebut.edu.cn/2025-07-12/216.html",
        "record_id": "hebut-notice-216-guangxi",
    },
]

TAIYUAN_SCORE_ROW = {
    "school_name": "太原理工大学",
    "school_key": "taiyuan_ligong_211",
    "year": "2021",
    "province": "广西",
    "type": "本科第一批",
    "science_category": "理工类",
    "major": "普通理工类(学校级摘要)",
    "requirement": "",
    "campus": "",
    "remarks": "录取人数=71;省控线=487;来源=太原理工大学2021年本科录取数据统计表官方PDF",
    "highest_score": "586",
    "minimum_score": "553",
    "lowest_score_ranking": "",
    "record_id": "tyut-score-summary-2021-guangxi",
    "source_url": "https://zs.tyut.edu.cn/__local/4/39/2E/BC13AA04709A12EC9E1B3969035_9F7CAEAF_2702F.pdf",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge_rows(
    existing_rows: list[dict[str, str]],
    new_rows: list[dict[str, str]],
    key_fields: list[str],
) -> list[dict[str, str]]:
    merged: dict[tuple[str, ...], dict[str, str]] = {}
    for row in existing_rows + new_rows:
        key = tuple(row.get(field, "") for field in key_fields)
        merged[key] = row
    return list(merged.values())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Land vetted official Guangxi rows for support / partially blocked engineering target schools."
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics score seed CSV.",
    )
    parser.add_argument(
        "--gxu-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "guangxi_daxue_guangxi_score_rows.csv",
        help="Structured GXU Guangxi score rows output CSV.",
    )
    parser.add_argument(
        "--suda-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "suzhou_daxue_guangxi_score_summary_rows.csv",
        help="Structured Suzhou Univ Guangxi score rows output CSV.",
    )
    parser.add_argument(
        "--bupt-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "beijing_you_dian_guangxi_score_rows.csv",
        help="Structured BUPT Guangxi score rows output CSV.",
    )
    parser.add_argument(
        "--tyut-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "taiyuan_ligong_guangxi_score_summary_rows_v2.csv",
        help="Structured Taiyuan Ligong Guangxi score summary output CSV.",
    )
    parser.add_argument(
        "--hebut-output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "hebei_gongye_guangxi_notice_rows.csv",
        help="Structured Hebut Guangxi notice rows output CSV.",
    )
    parser.add_argument(
        "--gxu-summary-output",
        type=Path,
        default=Path("reports") / "guangxi_daxue_official_guangxi_summary.csv",
        help="GXU summary output CSV.",
    )
    parser.add_argument(
        "--suda-summary-output",
        type=Path,
        default=Path("reports") / "suzhou_daxue_official_guangxi_summary.csv",
        help="Suzhou summary output CSV.",
    )
    parser.add_argument(
        "--bupt-summary-output",
        type=Path,
        default=Path("reports") / "beijing_you_dian_official_guangxi_summary.csv",
        help="BUPT summary output CSV.",
    )
    parser.add_argument(
        "--tyut-summary-output",
        type=Path,
        default=Path("reports") / "taiyuan_ligong_official_score_summary.csv",
        help="Taiyuan Ligong score summary output CSV.",
    )
    parser.add_argument(
        "--hebut-summary-output",
        type=Path,
        default=Path("reports") / "hebei_gongye_notice_summary.csv",
        help="Hebut notice summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    score_rows = GXU_SCORE_ROWS + SUDA_SCORE_ROWS + BUPT_SCORE_ROWS + [TAIYUAN_SCORE_ROW]
    write_rows(GXU_SCORE_ROWS, args.gxu_output, SCORE_FIELDS)
    write_rows(SUDA_SCORE_ROWS, args.suda_output, SCORE_FIELDS)
    write_rows(BUPT_SCORE_ROWS, args.bupt_output, SCORE_FIELDS)
    write_rows([TAIYUAN_SCORE_ROW], args.tyut_output, SCORE_FIELDS)

    existing_rows = [
        row
        for row in read_rows(args.score_major_merged)
        if row.get("record_id", "") not in {new_row["record_id"] for new_row in score_rows}
    ]
    merged_rows = merge_rows(
        existing_rows,
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_rows.sort(
        key=lambda row: (
            row.get("school_key", ""),
            row.get("year", ""),
            row.get("major", ""),
            row.get("record_id", ""),
        )
    )
    write_rows(merged_rows, args.score_major_merged, SCORE_FIELDS)

    write_rows(HEBUT_NOTICE_ROWS, args.hebut_output, list(HEBUT_NOTICE_ROWS[0].keys()))

    write_rows(
        [
            {
                "school_key": "guangxi_daxue_211",
                "school_name": "广西大学",
                "score_rows_total": str(len(GXU_SCORE_ROWS)),
                "score_rows_by_year": "2024:6",
                "note": "2024 广西区内录取统计表中的物理类工程向与专项工程向官方行",
            }
        ],
        args.gxu_summary_output,
        ["school_key", "school_name", "score_rows_total", "score_rows_by_year", "note"],
    )
    write_rows(
        [
            {
                "school_key": "suzhou_daxue_211",
                "school_name": "苏州大学",
                "score_rows_total": str(len(SUDA_SCORE_ROWS)),
                "score_rows_by_year": "2021:1|2022:1|2024:1",
                "note": "2021/2022/2024 官方各省录取最高分最低分平均分汇总页中的广西理工摘要",
            }
        ],
        args.suda_summary_output,
        ["school_key", "school_name", "score_rows_total", "score_rows_by_year", "note"],
    )
    write_rows(
        [
            {
                "school_key": "beijing_you_dian_211",
                "school_name": "北京邮电大学",
                "score_rows_total": str(len(BUPT_SCORE_ROWS)),
                "score_rows_by_year": "2023:11",
                "note": "2023 官方广西各专业录取分数页中普通理科专业明细与总计行",
            }
        ],
        args.bupt_summary_output,
        ["school_key", "school_name", "score_rows_total", "score_rows_by_year", "note"],
    )
    write_rows(
        [
            {
                "school_key": "taiyuan_ligong_211",
                "school_name": "太原理工大学",
                "score_rows_total": "1",
                "score_rows_by_year": "2021:1",
                "note": "2021 官方PDF广西理工类学校级录取摘要",
            }
        ],
        args.tyut_summary_output,
        ["school_key", "school_name", "score_rows_total", "score_rows_by_year", "note"],
    )
    write_rows(
        [
            {
                "school_key": "hebei_gongye_211",
                "school_name": "河北工业大学",
                "rows_total": str(len(HEBUT_NOTICE_ROWS)),
                "rows_by_year": "2024:1|2025:1",
                "note": "2024/2025 官方录取完结批次通知中的广西本科普通批招生人数摘要",
            }
        ],
        args.hebut_summary_output,
        ["school_key", "school_name", "rows_total", "rows_by_year", "note"],
    )

    print(
        "Landed official Guangxi rows for 5 schools: "
        "广西大学、苏州大学、北京邮电大学、太原理工大学、河北工业大学。"
    )


if __name__ == "__main__":
    main()
