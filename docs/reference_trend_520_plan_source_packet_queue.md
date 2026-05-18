# Reference Trend 520 Plan Source Packet Queue

日期：2026-05-16

## 结论

已从 520 位次窗口的 457 个跨年专业组对生成计划数补厚 source packet 队列。该队列只决定下一步去哪里找官方计划/专业组结构来源，不写 canonical/ML，也不并入 32 所 decision_pool。

## 覆盖

- queue rows: 457
- P0 urgent rows: 117
- P1 high rows: 129
- P2 medium rows: 157
- rows with existing official-source candidates: 9
- rows needing new official-source discovery: 448

## 下一步

优先处理 P0/P1 中已有 `plan_candidate` 的学校；若候选 URL 已知终端阻塞，则不要重复硬抓，改走浏览器态或人工批准路线。只要 source packet 没落地，就不能把计划数写入 intake/canonical。
