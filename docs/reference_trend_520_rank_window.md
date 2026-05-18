# Reference Trend 520 Rank Window Preview

日期：2026-05-16

## 结论

已按项目既有 520 分数线口径，从 reference trend pool 中抽取目标位次上下 20,000 位的趋势窗口。该结果只用于趋势背景和抽样优先级，不写 canonical/ML，也不并入 32 所 decision_pool。

## 位次锚点

- 2024 score 520 rank anchor: 42944
- 2025 score 520 rank anchor: 42339

## 覆盖

- window group-year rows: 1475
- 2024 rows: 784
- 2025 rows: 691
- matched delta rows in window: 457
- hotter/higher selectivity rows: 204
- cooler/lower selectivity rows: 246

## 窗口分层

- near anchor 0-5,000: 378
- adjacent 5,001-10,000: 352
- outer 10,001-20,000: 745

## 边界

- 这是趋势参考窗口，不是报考推荐清单。
- 当前计划数字段仍缺失，不能解释计划数变化。
- 后续应优先对窗口内 hotter/cooler 且接近目标位次的组补 plan/source packet。
