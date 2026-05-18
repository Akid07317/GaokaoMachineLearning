# reference_trend_520 P0 SUES form reachability preview

Generated: 2026-05-16

## Scope

上海工程技术大学官方招生系统首页已缓存并解析出招生计划/历年分数表单参数。本轮不提交表单，只记录可审计参数和人工批准边界。

## Result

- Official source URL: https://zsb.sues.edu.cn/webrecruit/index.do
- Cached HTML: `raw_sources/reference_trend/p0_official_drilldown/sues_webrecruit_index.html`
- Forms identified: 2
- Target option set: 2025 / 广西 / 本科 / 物理类
- Result fetch: not executed
- Manual approval required: yes, for form replay or browser state check

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_sues_form_reachability_preview.csv`
- `reports/reference_trend_520_p0_sues_form_reachability_rollup.csv`
- `reports/reference_trend_520_p0_sues_form_reachability_qa.csv`
- `reports/reference_trend_520_p0_sues_form_reachability_exclusion_log.csv`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是目前只有官方表单入口与参数，尚未获得经批准缓存的结果行；提交表单属于 form replay/browser-state 检查，需要人工批准。

## QA

- official_index_cached: PASS - raw_sources/reference_trend/p0_official_drilldown/sues_webrecruit_index.html
- plan_form_identified: PASS - 
- score_form_identified: PASS - 
- target_options_present: PASS - 广西/本科/物理类 option values present
- form_replay_not_executed: PASS - Only index page cached; no POST result fetch performed.
- manual_approval_gate: PASS - Rows require manual approval before form replay/browser check.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_index_cached: 1 (raw_sources/reference_trend/p0_official_drilldown/sues_webrecruit_index.html)
- official_forms_identified: 2 ({'official_plan_form': 1, 'official_score_rank_form': 1})
- manual_approval_required_rows: 2 (form replay/browser state check required before result rows)
- target_year_available_rows: 2 ()
- guangxi_option_available_rows: 2 ()
- physical_option_available_rows: 2 ()
- reference_trend_pool_eligible_rows: 0 (No result rows fetched.)
- calibration_eligible_rows: 0 (No score/rank rows fetched.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
