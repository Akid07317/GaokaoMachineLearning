# Reference Trend CUGB Group Mapping Workbench

日期：2026-05-16

## 结论

已基于广西考试院 `2024/2025` 中国地质大学（北京）物理类本科普通批投档线，对校方官方缓存的计划/专业分记录生成候选专业组映射工作台。校方记录有计划数、专业最低分/位次和部分选考组标签，但没有直接给广西院校专业组代码，因此本轮不生成正式 `院校专业组-year` 趋势记录。

## 考试院普通组线

- 2024 ordinary group 101: min_score 581, rank 12908
- 2024 ordinary group 102: min_score 579, rank 13622
- 2024 ordinary group 103: min_score 578, rank 13998
- 2025 ordinary group 101: min_score 561, rank 19743
- 2025 ordinary group 102: min_score 566, rank 17582

## 覆盖

- workbench rows: 53
- score-major candidate rows: 9
- plan-major candidate rows: 44
- exact ordinary group floor score rows: 3
- single-candidate rows: 2
- ambiguous candidate rows: 16
- unmapped rows: 35
- special-group collision context rows: 3
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 使用边界

候选规则只用“专业最低分不低于考试院普通组最低投档线”的必要条件，并额外标注专业最低分/位次是否等于某个普通组线。若分数同时高于多个普通组线，仍保留为 ambiguous；若碰到专项/民族班组线同分同位次，只作为 context 标注，不转为普通组映射。

## 下一步

1. 若要让 CUGB 进入正式 reference trend group-year 层，需要找到官方广西招生计划中的院校专业组代码或人工确认专业组结构。
2. 在未确认前，本文件只作为 32 所 decision_pool 的 source evidence / mapping workbench，不进入统计背景、canonical 或 ML。
3. 下一轮可继续处理最新出现的南京航空航天大学官方缓存行，或回到 P0/P1 非主池官方计划来源发现队列。
