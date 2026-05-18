# Reference Trend 2025 Score Rank Reachability

日期：2026-05-16

## 结论

2025 物理类一分一档目前仍停留在 source-packet 可达性层，不能结构化入 reference trend intake。命令行抓取官方细分页时，HTTPS 返回 `SSL_ERROR_SYSCALL`，HTTP 返回 `Empty reply from server`；此前 CHSI 汇总页也有终端反爬记录。

## 本轮边界

- 未写 canonical。
- 未写 ML。
- 未并入 32 所 decision_pool。
- 未用第三方页面替代官方来源。

## 状态

- checked rows: 3
- blocked rows: 3
- can structure now: 0

## 下一步

1. 使用浏览器态或其他可审计方式打开广西招生考试院 2025 一分一档细分页。
2. 保存 raw HTML/PDF/表格缓存，并补 `raw_file_path`。
3. 再生成 `reference_trend_score_rank_2025_preview.csv`。
4. 仍只进入 source packet/preview/QA，不打开 canonical/ML。
