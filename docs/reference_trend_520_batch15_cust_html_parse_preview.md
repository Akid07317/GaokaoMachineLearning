# reference_trend_520 batch15 CUST HTML parse preview

Generated: 2026-05-16

## Scope

长春理工大学官方 2025 广西招生计划页已缓存并解析为 source-packet preview。本产物只用于 reference trend source evidence，不进入 32 所 decision_pool。
## Result

- Official source URL: https://zsb.cust.edu.cn/gszsjhcx/gx_1/2025/index_mobile.htm
- Cached HTML: `raw_sources/reference_trend/batch15_official/cust_2025_guangxi_plan_mobile_page.html`
- Parsed major plan rows: 28
- Parsed plan count sum: 127
- Special/cooperative boundary rows: 4
- Group code available: 0
- Score/rank available: 0

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_cust_html_parse_preview.csv`
- `reports/reference_trend_520_batch15_cust_html_parse_rollup.csv`
- `reports/reference_trend_520_batch15_cust_html_parse_qa.csv`
- `reports/reference_trend_520_batch15_cust_html_parse_exclusion_log.csv`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是官方计划页没有广西院校专业组代码、最低分或最低位次；后续必须与广西考试院投档线/专业组上下文或官方组拆分证据做可审计映射。

## QA

- official_page_cached: PASS - raw_sources/reference_trend/batch15_official/cust_2025_guangxi_plan_mobile_page.html
- html_table_extracted: PASS - rows=28
- plan_count_numeric: PASS - plan_sum=127
- subject_label_physics: PASS - all rows source_subject_label=物理类
- subject_group_mapping_hold: PASS - Official page lacks Guangxi professional-group split.
- score_rank_hold: PASS - Official page is plan-only; no score or rank.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_page_cached_rows: 1 (raw_sources/reference_trend/batch15_official/cust_2025_guangxi_plan_mobile_page.html)
- parse_preview_rows: 28 (official major-plan rows extracted from static HTML table)
- plan_count_sum_extracted: 127 (sum of official Guangxi plan_count values)
- subject_label_distribution: {'物理类': 28} ()
- special_boundary_rows: 4 ({'none_detected': 24, 'cooperative': 4})
- group_code_available_rows: 0 (Source does not print Guangxi院校专业组 code.)
- score_rank_available_rows: 0 (Plan source only; no score/rank.)
- reference_trend_pool_eligible_rows: 0 (Group and score/rank mapping required.)
- calibration_eligible_rows: 0 (No group-year calibration opened.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
