# Official Cache Boundary QA

日期：2026-05-16

## 结论

已将 `reports/` 中已落地的官方广西 plan/score 行合并为 source-packet 边界 QA 预览。该批数据来自 32 所高精度 decision_pool 相关官方 API/缓存文件，因此本轮只登记为证据包预览，不进入 `reference_trend_pool` 统计背景，不写 canonical，不打开 ML。

## 覆盖

- input files: 24
- input rows: 720
- unique schools: 10
- official plan rows: 338
- official score rows: 382
- ordinary physics Guangxi rows: 477
- source-packet ready but boundary-hold rows: 464
- duplicate hold rows: 82
- special type hold rows: 57
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 学校覆盖

- 华北电力大学: 192 rows
- 河海大学: 138 rows
- 合肥工业大学: 92 rows
- 武汉理工大学: 82 rows
- 长安大学: 69 rows
- 华东理工大学: 50 rows
- 南京理工大学: 42 rows
- 西安电子科技大学: 28 rows
- 北京交通大学: 17 rows
- 河北工业大学: 10 rows

## 下一步

1. 若用户明确批准，可把其中普通物理广西行作为 32 所 decision_pool 的 source evidence 继续做人工映射。
2. 若要用于趋势池，必须先单独批准“32 所是否可作为 reference trend calibration 样本”，否则继续保持边界隔离。
3. 下一轮自动化应回到 P0/P1 非主池官方计划来源发现，或解析上一轮云南中医药/南京中医药 PDF 候选。
