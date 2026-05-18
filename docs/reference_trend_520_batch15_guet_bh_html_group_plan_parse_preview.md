# reference_trend_520 batch15 GUET Beihai group-plan parse preview

Generated: 2026-05-16

## Scope

桂林电子科技大学北海校区官方 2025 广西本科招生计划页已缓存并解析。本产物只用于 source-packet preview / group mapping evidence，不进入 32 所 decision_pool。

## Result

- Official source URL: https://www.guet.edu.cn/bh_zs/2025/1028/c3039a144300/page.htm
- Cached HTML: `raw_sources/reference_trend/batch15_official/guet_bh_2025_guangxi_plan_page.html`
- Parsed Guangxi rows: 15
- Ordinary physics group-plan rows: 8
- Ordinary physics plan sum by group: {'161': 200, '162': 852}
- Score/rank available: 0

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_guet_bh_html_group_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_guet_bh_html_group_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_guet_bh_html_group_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_guet_bh_html_group_plan_parse_exclusion_log.csv`

## Gate Boundary

普通物理行已经有官方专业组代码和计划数，但仍缺最低分/最低位次，因此所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。后续可与广西考试院 group-line score/rank 做 join workbench。

## QA

- official_page_cached: PASS - raw_sources/reference_trend/batch15_official/guet_bh_2025_guangxi_plan_page.html
- html_table_extracted: PASS - rows=15
- ordinary_physics_group_rows: PASS - rows=8; plan_sum=1052
- group_code_present: PASS - ordinary physics rows all have source_group_code
- score_rank_hold: PASS - Official page is plan-only; no score or rank.
- special_boundary_flagged: PASS - Art/historical rows retained as boundary rows in exclusion log.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_page_cached_rows: 1 (raw_sources/reference_trend/batch15_official/guet_bh_2025_guangxi_plan_page.html)
- parse_preview_rows_all_guangxi: 15 (all Guangxi rows from official table)
- ordinary_physics_group_plan_rows: 8 (普通类+物理类/理工类+本科批 rows with group code)
- ordinary_physics_plan_count_sum: 1052 ({'161': 200, '162': 852})
- group_code_available_rows: 15 (source notes print 专业组)
- subject_distribution: {'物理类': 11, '历史类': 4} ()
- special_boundary_rows: 6 ({'none_detected': 9, 'art_admission_boundary': 6})
- score_rank_available_rows: 0 (Plan source only; no score/rank.)
- reference_trend_pool_eligible_rows: 0 (Score/rank join required before calibration.)
- calibration_eligible_rows: 0 (No group-year calibration opened.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
