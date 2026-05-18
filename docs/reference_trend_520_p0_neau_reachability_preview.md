# reference_trend_520 P0 NEAU official reachability preview

Generated: 2026-05-16

## Scope

本轮处理东北农业大学 P0 官方计划来源发现任务。只缓存并审计官方入口链路，不执行 header/cookie/browser 态检查，不绕过 403，不生成 canonical/ML 输入。

## Result

- Official landing URL: https://zsbweb.neau.edu.cn/index.htm
- Undergraduate admissions URL: https://zsb.neau.edu.cn/
- Cached landing HTML: `raw_sources/reference_trend/p0_official_drilldown/neau_zsbweb_index_https.html`
- Cached admissions homepage: `raw_sources/reference_trend/p0_official_drilldown/neau_zsb_home.html`
- Queue records covered: 102[reference_trend_520_plan_source_queue_0002], 103[reference_trend_520_plan_source_queue_0045]
- Homepage AJAX candidate: `https://zsb.neau.edu.cn/f/newsCenter/ajax_get_category_and_link_list`
- Direct terminal POST status: `403`
- Structured Guangxi plan rows: not fetched
- Manual approval required: yes, for audited header/cookie/browser-state check

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_neau_reachability_preview.csv`
- `reports/reference_trend_520_p0_neau_reachability_rollup.csv`
- `reports/reference_trend_520_p0_neau_reachability_qa.csv`
- `reports/reference_trend_520_p0_neau_reachability_exclusion_log.csv`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是当前只有官方入口链路和 CMS/AJAX 形状，尚无经批准缓存的 2025 广西物理类本科普通批计划结构化行。

## QA

- official_landing_cached: PASS - raw_sources/reference_trend/p0_official_drilldown/neau_zsbweb_index_https.html
- official_undergraduate_home_cached: PASS - raw_sources/reference_trend/p0_official_drilldown/neau_zsb_home.html
- official_chain_recorded: PASS - https://zsbweb.neau.edu.cn/index.htm -> https://zsb.neau.edu.cn/
- ajax_block_not_bypassed: PASS - Direct terminal POST returned 403; no header/cookie/browser replay attempted.
- manual_approval_gate: PASS - Rows require approval before AJAX/header/browser check.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_landing_cached: 1 (raw_sources/reference_trend/p0_official_drilldown/neau_zsbweb_index_https.html)
- official_undergraduate_home_cached: 1 (raw_sources/reference_trend/p0_official_drilldown/neau_zsb_home.html)
- queue_records_covered: 2 (groups 102 and 103)
- ajax_endpoint_candidates_identified: 1 (https://zsb.neau.edu.cn/f/newsCenter/ajax_get_category_and_link_list)
- direct_ajax_terminal_post_status: 403 (no header/cookie/browser replay attempted)
- manual_approval_required_rows: 2 (header/browser state check required before structured rows)
- reference_trend_pool_eligible_rows: 0 (No structured plan rows fetched.)
- calibration_eligible_rows: 0 (Plan source only; no score/rank rows.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
