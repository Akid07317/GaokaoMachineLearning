# Reference Trend 520 Next-Batch PDF Parse QA

日期：2026-05-16

## 结论

已对上一轮 P0 官方 PDF 候选做解析/可达性 QA。云南中医药大学官方 PDF URL 当前返回 404，先进入 reachability/backoff；南京中医药大学官方 PDF 下载并解析成功，但 PDF 仅包含广东省行，未发现广西行，因此不能进入广西 reference trend source packet intake。

## 覆盖

- PDF candidates checked: 2
- download 404 hold rows: 1
- parsed PDF rows: 1
- parsed no-Guangxi rejected rows: 1
- source packet intake ready rows: 0
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 下一步

- 云南中医药大学需要重新定位官方招生计划/手册 PDF 或招生计划页。
- 南京中医药大学继续找官方 2025 外省招生计划页或含广西的录取统计页；当前 PDF 只保留为 rejected source clue。
- 继续处理兰州交通大学官方招生计划端点，或推进下一批 P0/P1 官方来源发现。
