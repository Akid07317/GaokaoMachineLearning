# Reference Trend Rank Band And Delta Preview

日期：2026-05-16

## 结论

已基于 `reference_trend_intake_preview.csv` 中的 strict eligible 记录生成位次带覆盖和 2024-2025 同院校专业组 delta 预览。该结果只用于趋势池诊断，不写 canonical/ML，也不并入 32 所 decision_pool。

## 覆盖

- matched 2024/2025 group pairs: 1435
- hotter/higher selectivity pairs: 482
- cooler/lower selectivity pairs: 779
- mixed pairs: 174

## 2025 位次带样本量

- R00_000001_001000: 26
- R01_001001_003000: 39
- R02_003001_005000: 39
- R03_005001_010000: 90
- R04_010001_020000: 185
- R05_020001_040000: 337
- R06_040001_070000: 549
- R07_070001_100000: 491
- R08_100001_plus: 1252

## 边界

- `rank_delta_2025_minus_2024 > 0` 表示最低位次数字变大，通常代表相对降温或门槛下降。
- 当前 `plan_count_available_rows = 0`，所以本轮不能做计划数变化结论。
- 专业组代码跨年沿用不必然代表专业组内专业构成完全一致，后续需要 plan_count/group structure source packet 补厚。
