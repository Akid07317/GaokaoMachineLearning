# New Official Cache Batch QA

日期：2026-05-16

## 结论

已将新增落地的北京工业大学、东华大学、中国地质大学北京官方缓存/官方文章行统一做 source-packet 边界 QA。该批数据仍属于 32 所 decision-pool 证据线或需要 group/rank/batch 复核，因此本轮不进入 `reference_trend_pool`，不写 canonical，不打开 ML。

## 覆盖

- input rows: 122
- preview rows: 122
- official plan rows: 78
- official major score rows: 43
- strict 2024/2025 candidate rows: 104
- group mapping needed rows: 10
- rank missing / batch review rows: 34
- bridge 2023 old science hold rows: 18
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 数据集

- bjut_plan: 34 rows
- bjut_score: 17 rows
- cugb_plan: 44 rows
- cugb_score_major: 9 rows
- cugb_score_summary: 1 rows
- dhu_score: 17 rows

## 下一步

1. 北京工业大学：2025 计划/分数可作证据，但需与考试院专业组线做映射；2023 旧理科只放 bridge 背景。
2. 东华大学：2025 文章有 `物化1/物化2` 组标签但缺最低位次，需用一分一档换算或继续查官方位次/考试院组线。
3. 中国地质大学北京：官方 AJAX 源质量较好，可继续做 group mapping workbench，但仍不自动进入 trend/canonical/ML。
