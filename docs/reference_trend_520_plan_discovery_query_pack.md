# Reference Trend 520 Plan Discovery Query Pack

日期：2026-05-16

## 结论

已把 520 位次窗口 P0/P1 计划数补厚队列压缩成按学校去重的官方来源发现 query pack。它只服务资料搜集线程，目标是找到并写 source packet；不能跳过 source packet 直接写 intake/canonical/ML。

## 覆盖

- query rows: 159
- P0 university queries: 90
- P1 university queries: 69
- queries with existing candidate: 2
- queries needing new official discovery: 157

## 使用边界

- 只接受官方招生网、考试院、学校信息公开等可审计来源。
- 不接受第三方汇总页直接入库。
- 不接受无法区分本科普通批、物理类、特殊类型的混合页面。
- 找到网页后先写 source packet，再进入 intake preview 和 QA。
