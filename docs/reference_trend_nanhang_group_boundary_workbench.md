# Reference Trend Nanhang Group Boundary Workbench

日期：2026-05-16

## 结论

已把南京航空航天大学官方缓存行整理成 reference-trend 边界工作台。该校属于 32 所 `decision_pool`，本轮只形成 source evidence / QA，不进入 `reference_trend_pool`、canonical 或 ML。

关键边界：

- 2024 广西考试院普通组：101:618/3954
- 2025 广西考试院普通组：101:615/3507
- 2025 未备注分组待判定：303:578/12953
- 2024 专业分 API 行数：19，但最低位次字段缺失
- 2025 计划行数：21，计划数合计 75

## 覆盖

- workbench rows: 44
- 2024 score-major rows: 19
- 2025 plan rows: 21
- 2024 overview rows: 4
- single-candidate rows: 38
- ambiguous candidate rows: 0
- unmapped rows: 6
- rank-missing major score rows: 19
- reference trend eligible rows: 0

## 使用边界

2024 专业分最低分 `618` 与广西考试院 2024 普通组 `101` 最低分一致，可作为强边界证据；但专业分 API 不含最低位次，也不含院校专业组代码。2025 计划侧有 21 行专业计划，但无法直接确认这些专业属于 `101` 还是未备注的 `303` 组，因此全部保持 hold。

## 下一步

1. 若要正式入 reference trend，需要找到南航 2025 广西招生计划中的院校专业组结构，或人工确认 `303` 组性质。
2. 若继续处理 32 所 source evidence，下一轮可审计 `nanhang` 是否有官方 API 参数能返回 group code。
3. 若回到趋势池扩展，优先处理 P0/P1 非主池官方计划来源发现队列。
