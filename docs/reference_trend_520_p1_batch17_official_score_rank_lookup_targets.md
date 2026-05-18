# P1 Batch17 Official Score-Rank Lookup Targets

日期：2026-05-17

## 结果

从 marker 134 的 6 条 official rank join gap rows 去重成 5 个 official score-rank lookup targets。后续只需按分数查一次官方 2025 广西物理类一分一档，再在 QA 通过后回填对应 group-year。

- 527: 1 consumer group-year row(s) -> 10412-101
- 490: 2 consumer group-year row(s) -> 10596-153|10092-151
- 462: 1 consumer group-year row(s) -> 10092-152
- 461: 1 consumer group-year row(s) -> 10407-102
- 382: 1 consumer group-year row(s) -> 10466-152

## 边界

本轮只生成去重后的 lookup target 包、QA、rollup 和 duplicate lookup exclusion log；不抓取官方一分一档细页，不重复终端 curl `qg/qn` 阻塞路径，不采用第三方镜像位次，不选择或推断任何 min_rank。

reference trend intake、calibration、canonical/ML 和 32 所 decision_pool 继续关闭。
