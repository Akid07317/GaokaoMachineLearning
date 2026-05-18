# Reference Trend 520 Next-Batch Web Candidates

日期：2026-05-16

## 结论

已处理下一批 P0 工作台前 4 所学校的官方来源发现。云南中医药大学、兰州交通大学、南京中医药大学均找到官方域名候选；佛山大学本轮只发现第三方转载，先记录为 rejected clue，不能进入 source packet intake。

## 覆盖

- candidate rows: 6
- universities covered: 4 (云南中医药大学、佛山大学、兰州交通大学、南京中医药大学)
- official-domain candidate rows: 5
- rejected third-party-only rows: 1
- source packet statuses: {'official_pdf_candidate_not_parsed': 2, 'rejected_third_party_only': 1, 'official_portal_candidate_not_structured': 2, 'official_context_candidate_not_structured': 1}
- confidence counts: {'T2_official_pdf_needs_parse': 1, 'T4_third_party_only_rejected': 1, 'T2_official_portal_plan_endpoint_needed': 1, 'T2_official_trend_narrative_only': 1, 'T2_official_portal_needs_drilldown': 1, 'T2_official_score_pdf_needs_parse': 1}

## 下一步

- PDF 候选先做文本/表格解析，再判断是否存在广西物理类普通批行。
- 兰州交通大学优先 drilldown 官方 zscx 招生计划查询端点。
- 佛山大学继续找一手官方招生域名，第三方转载不入库。
- 不打开 canonical/ML，不进入 32 所 decision_pool。
