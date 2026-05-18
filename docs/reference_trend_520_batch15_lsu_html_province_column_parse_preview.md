# reference_trend_520 batch15 LSU Guangxi-column parse preview

Generated: 2026-05-16

## Scope

丽水学院官方 2025 分省分专业招生计划页已缓存，并从跨省表格中抽取广西列。本产物只用于 source-packet preview，不进入 32 所 decision_pool。
## Result

- Official source URL: https://zsw.lsu.edu.cn/2025/0616/c616a356300/page.htm
- Cached HTML: `raw_sources/reference_trend/batch15_official/lsu_2025_province_major_plan_page.html`
- Parsed Guangxi major rows: 32
- Parsed Guangxi plan count sum: 150
- Official Guangxi total row: 150
- Total reconciliation: True
- Subject route available: 0
- Group code available: 0
- Score/rank available: 0

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_lsu_html_province_column_parse_preview.csv`
- `reports/reference_trend_520_batch15_lsu_html_province_column_parse_rollup.csv`
- `reports/reference_trend_520_batch15_lsu_html_province_column_parse_qa.csv`
- `reports/reference_trend_520_batch15_lsu_html_province_column_parse_exclusion_log.csv`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是官方表格没有广西选科/科类路线、院校专业组代码、最低分或最低位次；后续只能作为计划侧证据，或等待可审计 group/subject mapping。

## QA

- official_page_cached: PASS - raw_sources/reference_trend/batch15_official/lsu_2025_province_major_plan_page.html
- guangxi_column_extracted: PASS - rows=32; plan_sum=150
- total_row_reconciliation: PASS - major_sum=150; source_total=150
- subject_route_hold: PASS - Official table lacks subject route/selection requirement.
- group_code_hold: PASS - Official table lacks Guangxi professional group split.
- score_rank_hold: PASS - Official table is plan-only; no score or rank.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_page_cached_rows: 1 (raw_sources/reference_trend/batch15_official/lsu_2025_province_major_plan_page.html)
- parse_preview_rows: 32 (official Guangxi-column major-plan rows)
- plan_count_sum_extracted: 150 (sum of extracted non-total Guangxi major rows)
- official_guangxi_total_row: 150 (total row in source table)
- plan_total_matches_source_total: true ()
- special_boundary_rows: 5 ({'none_detected': 27, 'art_admission_boundary': 4, 'sport_admission_boundary': 1})
- subject_route_available_rows: 0 (Source does not print Guangxi subject route or selection requirement.)
- group_code_available_rows: 0 (Source does not print Guangxi院校专业组 code.)
- score_rank_available_rows: 0 (Plan source only; no score/rank.)
- reference_trend_pool_eligible_rows: 0 (Subject route/group/score-rank mapping required.)
- calibration_eligible_rows: 0 (No group-year calibration opened.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
