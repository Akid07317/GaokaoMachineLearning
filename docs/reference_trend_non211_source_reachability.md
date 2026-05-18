# Reference Trend Non-211 Source Reachability

日期：2026-05-16

## 结论

非 211 P1 官方计划候选目前不能通过终端稳定落源。南京信息工程大学 4 个官方招生网计划页在本轮终端抓取中均为 0 字节超时；这些候选保留在 source reachability 层，后续需要浏览器态或其他可审计方式。

## 覆盖

- checked P0/P1 candidate rows: 5
- terminal timeout rows: 4
- raw cache available rows: 0
- canonical/ML opened: false
- decision pool expanded: false

## 下一步

1. 不再重复用终端 curl 抓南京信息工程大学同一批 P1 URL。
2. 若用户批准浏览器态，可打开 P1 URL 并保存 raw HTML。
3. 只有 raw cache 可审计且字段确认后，才写正式 source packet。
4. 继续把非 211 用作 reference trend pool 来源候选，不并入 32 所 decision_pool。
