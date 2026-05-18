# P1 Batch17 Official Rank Join Gap Queue

日期：2026-05-17

## 结果

从 marker 133 的 source-packet preview action queue 中抽取 6 条已有广西考试院官方最低分、但仍缺官方最低位次的 group-year rows，生成官方一分一档位次 join gap queue。

- group-year rank gap rows：6
- unique score lookup keys：5
- excluded rows：9
- official rank rows accepted：0

## 分数查找目标

- 527: 1 group row(s)
- 490: 2 group row(s)
- 462: 1 group row(s)
- 461: 1 group row(s)
- 382: 1 group row(s)

## 边界

本轮只生成 rank join gap queue、QA、rollup 和 exclusion log；不抓取广西考试院一分一档细分页，不重复终端 curl `qg/qn` 阻塞路径，不采用第三方镜像位次，不做位次换算，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。

下一步只有在获得官方 2025 物理类一分一档 raw cache，或用户批准浏览器态/可审计替代抓取后，才能把 `min_score` join 到官方 `min_rank`。
