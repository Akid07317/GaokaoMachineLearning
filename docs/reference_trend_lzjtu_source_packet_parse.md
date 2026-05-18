# Reference Trend Lanzhou Jiaotong Source Packet Parse

日期：2026-05-16

## 结论

兰州交通大学官方查询站 `zscx.lzjtu.edu.cn` 已确认可访问，前端 JS 暴露官方 API。已抽取 `2024` 广西物理类本科普通批计划 `26` 行，以及 `2024` 广西物理类本科专业分 `32` 行。该来源可作为 P0 reference trend 的 source-packet 候选，但当前没有院校专业组代码，因此仍需与广西考试院投档线做 group mapping，不能直接进入趋势池。

## 覆盖

- source packet rows: 58
- official plan rows: 26
- official major score rows: 32
- rows with plan count: 26
- rows with min score: 32
- rows with min rank: 32
- intake ready but group mapping needed: 52
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 来源边界

- 招生计划 API: `https://zscx.lzjtu.edu.cn/api//business/web/index/getZsplanList`
- 专业分数 API: `https://zscx.lzjtu.edu.cn/api//business/web/index/getLnzyfenshuList`
- 官方查询入口: `https://zscx.lzjtu.edu.cn/`
- 官网静态 `zsb.lzjtu.edu.cn/zsjh2025/zsjh20251.htm` 与 `lnfs/lnfs.htm` 当前终端 HEAD 返回 412，但查询站 API 可直接返回 JSON。

## 下一步

1. 用广西考试院 `2024` 兰州交通大学院校专业组投档线做 group mapping。
2. 继续查找是否存在 `2025` 计划/分数接口或页面；当前字段接口只返回到 `2024`。
3. 继续推进下一批 P0/P1 官方来源发现，不打开 canonical/ML。
