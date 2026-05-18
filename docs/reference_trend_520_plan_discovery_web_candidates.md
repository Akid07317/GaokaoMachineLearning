# Reference Trend 520 Plan Discovery Web Candidates

日期：2026-05-16

## 结论

本轮从 P0 query pack 中抽查并记录了 4 所学校的官方来源候选，形成 source packet 预览层。中南民族大学已有可文本抽取的官方计划/分数候选；东莞理工学院、东北农业大学、上海工程技术大学目前只落到官方入口或需浏览器/短链核验的 reachability 层。

## 覆盖

- web candidate rows: 6
- universities covered: 4 (上海工程技术大学、东北农业大学、东莞理工学院、中南民族大学)
- T1 official extractable candidates: 2
- T2 portal/reachability candidates: 4
- structured candidate statuses: {'web_verified_candidate_not_parsed': 2, 'official_reachability_candidate_blocked_by_shortlink_or_embedded_asset': 1, 'official_portal_candidate_not_structured': 3}

## 使用边界

- 这些记录只进入 source_packet/preview/QA 层。
- 未解析院校专业组-year，不打开 canonical/ML。
- 东莞理工学院短链、东北农业大学查询端点、上海工程技术大学计划端点都需要后续可审计核验。
- 中南民族大学计划页可先做广西列解析，但仍需特殊类型隔离和专业组映射 QA。
