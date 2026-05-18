# reference_trend_520 P0 DGUT official reachability preview

Generated: 2026-05-16

## Scope

本轮处理东莞理工学院 P0 官方计划来源发现任务。只缓存并审计官方招生计划网与校内官方发布页，不抓取微信文章、不打开短链、不生成 canonical/ML 输入。

## Result

- Official plan portal: https://zsb.dgut.edu.cn/bkszs/zsjh/
- Cached portal HTML: `raw_sources/reference_trend/p0_official_drilldown/dgut_zsb_plan_portal.html`
- 2025 plan item title: 权威发布︱东莞理工学院2025年本科招生计划
- 2025 plan item target: `https://mp.weixin.qq.com/s?__biz=MzAwOTM0NDAxNw==&mid=2650299150&idx=1&sn=365cd0e5bed0827f58c6cb2b55caa81e&chksm=82559f4a848ce3228f98ad544bd96b9b9338d3b31af279392d94884e5294b4ef0ad68a986778&scene=126&sessionid=1750304554#rd`
- School-subdomain announcement: https://ee.dgut.edu.cn/info/1061/25990.htm
- Cached announcement HTML: `raw_sources/reference_trend/p0_official_drilldown/dgut_ee_2025_plan_announcement.html`
- Shortlink exposed by announcement: `https://l6j.cn/bUgxUC`
- Structured Guangxi plan rows: not fetched
- Manual approval required: yes, for WeChat/shortlink browser capture or another first-party structured source

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_dgut_reachability_preview.csv`
- `reports/reference_trend_520_p0_dgut_reachability_rollup.csv`
- `reports/reference_trend_520_p0_dgut_reachability_qa.csv`
- `reports/reference_trend_520_p0_dgut_reachability_exclusion_log.csv`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是当前只有官方入口、外部微信文章目标和短链证据，尚无经批准缓存的 2025 广西物理类本科普通批计划结构化行。

## QA

- official_plan_portal_cached: PASS - raw_sources/reference_trend/p0_official_drilldown/dgut_zsb_plan_portal.html
- school_subdomain_announcement_cached: PASS - raw_sources/reference_trend/p0_official_drilldown/dgut_ee_2025_plan_announcement.html
- official_2025_plan_item_found: PASS - https://mp.weixin.qq.com/s?__biz=MzAwOTM0NDAxNw==&mid=2650299150&idx=1&sn=365cd0e5bed0827f58c6cb2b55caa81e&chksm=82559f4a848ce3228f98ad544bd96b9b9338d3b31af279392d94884e5294b4ef0ad68a986778&scene=126&sessionid=1750304554#rd
- shortlink_or_external_target_not_auto_parsed: PASS - No WeChat/shortlink/browser capture attempted.
- manual_approval_gate: PASS - Rows require approval before external article or shortlink capture.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_plan_portal_cached: 1 (raw_sources/reference_trend/p0_official_drilldown/dgut_zsb_plan_portal.html)
- school_subdomain_announcement_cached: 1 (raw_sources/reference_trend/p0_official_drilldown/dgut_ee_2025_plan_announcement.html)
- queue_records_covered: 1 (group 101)
- official_2025_plan_item_found: 1 (权威发布︱东莞理工学院2025年本科招生计划)
- external_wechat_target_found: 1 (manual/browser capture required)
- school_shortlink_found: 1 (https://l6j.cn/bUgxUC)
- manual_approval_required_rows: 1 (external article/shortlink capture required before structured rows)
- reference_trend_pool_eligible_rows: 0 (No structured plan rows fetched.)
- calibration_eligible_rows: 0 (Plan source only; no score/rank rows.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
