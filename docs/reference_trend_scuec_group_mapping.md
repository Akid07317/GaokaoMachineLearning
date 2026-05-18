# Reference Trend SCUEC Group Mapping Workbench

日期：2026-05-16

## 结论

已将中南民族大学 source packet 解析结果与广西考试院 520 位次窗口数据做组映射 QA。2024 校方分数页的 3 个普通物理组分数可一一匹配考试院 group code 103/104/105；2025 计划页的 32 条普通计划行仍无显式组代码，只能作为计划数/专业结构候选，不能进入院校专业组-year。

## 覆盖

- workbench rows: 35
- score exact single-group matches: 3
- plan rows still unmapped: 32
- mapping status counts: {'plan_row_unmapped_no_group_code': 32, 'score_exact_single_exam_group_match': 3}
- confidence counts: {'T2_official_plan_count_but_group_unmapped': 32, 'T1_school_score_matches_exam_authority_group': 3}
- trend record eligible rows: 0
- calibration eligible rows: 0

## 下一步

- 把 2024 三个分数组映射作为 QA 证据保留，不直接生成趋势样本。
- 继续寻找 2025 官方院校专业组结构或考试院计划来源，解决 2025 计划行无法落到 group code 的问题。
- 继续保持 canonical/ML 和 32 所 decision_pool 入口关闭。
