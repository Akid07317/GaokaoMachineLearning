from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.engineering_focus import read_engineering_schools, write_target_rows
from gaokao_planner.engineering_focus import EngineeringTarget


SUPPLEMENTAL_TARGETS: list[tuple[str, str, str, int]] = [
    ("zhongguo_shiyou_beijing_211", "本科生招生入口", "http://bkzs.cup.edu.cn/f", 30),
    ("zhongguo_shiyou_beijing_211", "学校章程", "https://www.cup.edu.cn/xxgk/xxzc/index.htm", 20),
    ("zhongguo_shiyou_beijing_211", "本科招生标签页", "https://www.cup.edu.cn/dbewm/8cd0dc4a2eec46129adf843b29b6571f.htm", 25),
    ("zhongguo_shiyou_huadong_211", "本科生招生入口", "https://zhaosheng.upc.edu.cn", 30),
    ("zhongguo_shiyou_huadong_211", "招生就业入口", "https://www.upc.edu.cn/", 18),
    ("zhongguo_shiyou_huadong_211", "学校章程", "https://www.upc.edu.cn/xygk/sdzc1.htm", 18),
    ("zhongguo_kuangye_211", "历年分数", "http://zs.cumt.edu.cn/zsw/lnfs.html", 40),
    ("zhongguo_kuangye_211", "招生计划", "http://zs.cumt.edu.cn/zsw/zsjh.html", 40),
    ("zhongguo_kuangye_211", "录取查询", "http://zs.cumt.edu.cn/zsw/lqcx.html", 30),
    ("beijing_huagong_211", "本科生招生入口", "http://goto.buct.edu.cn/", 30),
    ("beijing_huagong_211", "本科招生", "https://www.buct.edu.cn/zsjy_11437/list.htm", 28),
    ("beijing_huagong_211", "本科生教育", "http://jiaowuchu.buct.edu.cn/", 15),
    ("beijing_you_dian_211", "本科生招生入口", "https://zsb.bupt.edu.cn/", 30),
    ("beijing_you_dian_211", "学校主页", "https://www.bupt.edu.cn/", 10),
    ("huabei_dianli_211", "本科生招生", "https://www.ncepu.edu.cn/zsjy/bkszs/index.htm", 30),
    ("huabei_dianli_211", "本科招生信息网", "https://goto.ncepu.edu.cn/", 28),
    ("huabei_dianli_211", "招生办公室", "http://zhaosheng.ncepu.edu.cn/zs", 20),
    ("hefei_gongda_211", "本科招生首页", "http://bkzs.hfut.edu.cn/", 20),
    ("hefei_gongda_211", "历年分数", "http://bkzs.hfut.edu.cn/static/front/hfut/basic/html_web/lnfs.html", 40),
    ("hefei_gongda_211", "招生计划", "http://bkzs.hfut.edu.cn/static/front/hfut/basic/html_web/zsjh.html", 40),
    ("hefei_gongda_211", "录取查询", "http://bkzs.hfut.edu.cn/static/front/hfut/basic/html_web/lqcx.html", 30),
    ("hehai_211", "本科生招生入口", "http://zsw.hhu.edu.cn/", 30),
    ("hehai_211", "招生就业入口", "https://www.hhu.edu.cn/zsjy/list.htm", 20),
    ("fuzhou_daxue_211", "招生考试中心", "https://zsb.fzu.edu.cn/", 30),
    ("fuzhou_daxue_211", "本科招生入口", "https://zsks.fzu.edu.cn/", 28),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build supplemental fetch targets for missing core engineering schools."
    )
    parser.add_argument(
        "--schools",
        type=Path,
        default=Path("configs") / "engineering_focus_211_non985.csv",
        help="Engineering school configuration CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_core_missing_supplemental_targets.csv",
        help="Output CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    schools = read_engineering_schools(args.schools)
    targets: list[EngineeringTarget] = []
    for seed_id, link_text, url, priority in SUPPLEMENTAL_TARGETS:
        school = schools.get(seed_id)
        if school is None:
            continue
        targets.append(
            EngineeringTarget(
                seed_id=seed_id,
                source_name=school.source_name,
                engineering_tier=school.engineering_tier,
                score_floor=school.score_floor,
                target_url=url,
                link_text=link_text,
                source_page_title=school.source_name,
                matched_reason=link_text,
                fetch_priority=priority,
                score_threshold_status="pending_score_extraction",
            )
        )
    write_target_rows(targets, args.output)
    print(f"Built {len(targets)} supplemental targets into {args.output}.")


if __name__ == "__main__":
    main()
