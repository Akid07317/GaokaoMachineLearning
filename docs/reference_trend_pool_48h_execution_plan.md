# Reference Trend Pool 48h Execution Plan

日期：2026-05-16

## 本轮结论

本地已从广西考试院投档线种子表生成 `6626` 条 intake preview，其中 `6075` 条可作为严格 2024/2025 院校专业组-year 分数/位次趋势样本。该层仍是 preview，不是 canonical/ML。

## 48 小时优先级

1. 把 `reference_trend_seed_queue.csv` 中 P0/P1 官方考试院来源复核为 source packet backbone。
2. 用联网许可补齐 2025 一分一档物理类正式表的本地结构化缓存，先写 source packet，不直接写 final。
3. 从非 211 todo 中优先处理南京信息工程大学、西南石油大学、成都理工大学、天津工业大学等官方招生网来源，产出 source packet。
4. 对 source packet 逐条生成 intake preview，并按特殊类型、批次、选科、院校专业组代码、最低分/位次进行 QA。
5. 计划数单独建 `plan_count_thickening` 子任务；当前投档线样本可用于 rank/score trend，但不能用于计划变化分析。
6. 若需要 Deep Research，只用于定位官方来源，不直接写入趋势结论。

## 两线程交接

- 资料搜集线程：只写 source packet、raw_file_path、source reachability note。
- 数据整理线程：只读 source packet，生成 intake preview、QA report、exclusion log、eligible flag。
- 两线程都不得写 32 所 decision pool、canonical 或 ML 输入。

## 下一轮建议

优先补 2025 score-rank 正式结构化表，再从非 211 官方招生网中产出 10-20 个高质量 source packet。完成后重跑本脚本，比较 eligible 行数和缺 plan_count 的占比。
