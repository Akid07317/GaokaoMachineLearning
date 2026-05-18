# reference_trend_520 batch15 CSUFT HTML plan parse preview

Generated: 2026-05-16

## Scope

中南林业科技大学官方 2025 广西招生计划页已缓存两页并解析为 source-packet preview。本产物只用于 reference trend source evidence，不进入 32 所 decision_pool。

## Result

- Official source URL: https://zs.csuft.edu.cn/f/zsjhinfo?jhnd=2025&ssdm=45
- Official page 2 URL: https://zs.csuft.edu.cn/f/zsjhinfo?pageNo=2&pageSize=30&jhnd=2025&ssdm=45
- Cached HTML page 1: `raw_sources/reference_trend/batch15_official/csuft_2025_guangxi_plan_page.html`
- Cached HTML page 2: `raw_sources/reference_trend/batch15_official/csuft_2025_guangxi_plan_page2.html`
- Parsed official rows: 50
- Parsed all-row plan count sum: 173
- Ordinary physical candidate rows: 41
- Ordinary physical candidate plan sum: 150
- Non-target/special boundary rows: 9
- Special boundary rows: 1
- Group code available: 0
- Score/rank available: 0

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_csuft_html_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_csuft_html_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_csuft_html_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_csuft_html_plan_parse_exclusion_log.csv`

## Gate Boundary

所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是官方计划页没有广西院校专业组代码、最低分或最低位次；后续必须与广西考试院投档线/专业组上下文或官方组拆分证据做可审计映射。

## QA

- official_pages_cached: PASS - raw_sources/reference_trend/batch15_official/csuft_2025_guangxi_plan_page.html|raw_sources/reference_trend/batch15_official/csuft_2025_guangxi_plan_page2.html
- html_tables_extracted: PASS - rows=50
- pagination_row_count_match: PASS - expected=50; parsed=50
- plan_count_numeric: PASS - plan_sum_all=173; ordinary_physical_sum=150
- ordinary_physical_candidate_identified: PASS - ordinary_physical_candidate_rows=41
- non_target_rows_excluded: PASS - history/sport/non-ordinary rows retained for audit but excluded from ordinary physical candidates
- subject_group_mapping_hold: PASS - Official page lacks Guangxi professional-group split.
- score_rank_hold: PASS - Official page is plan-only; no score or rank.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_pages_cached: 2 (raw_sources/reference_trend/batch15_official/csuft_2025_guangxi_plan_page.html|raw_sources/reference_trend/batch15_official/csuft_2025_guangxi_plan_page2.html)
- expected_total_rows_from_pagination: 50 (parsed from official pagination text)
- parse_preview_rows: 50 (all official Guangxi rows extracted from paginated HTML tables)
- plan_count_sum_all_rows: 173 (sum of official Guangxi plan_count values across all visible rows)
- ordinary_physical_candidate_rows: 41 (本科普通批 + 物理类 + no detected special boundary)
- ordinary_physical_candidate_plan_sum: 150 (candidate plan-side evidence only)
- non_ordinary_or_special_rows: 9 (history/sport/other boundary rows kept for audit but excluded from ordinary physical candidate)
- subject_label_distribution: {'历史类': 8, '体育(物理类)': 1, '物理类': 41} ()
- batch_distribution: {'本科普通批': 49, '本科提前批体育类': 1} ()
- special_boundary_rows: 1 ({'none_detected': 49, 'sport_admission_boundary': 1})
- group_code_available_rows: 0 (Official source does not print Guangxi院校专业组 code.)
- score_rank_available_rows: 0 (Plan source only; no score/rank.)
- reference_trend_pool_eligible_rows: 0 (Group and score/rank mapping required.)
- calibration_eligible_rows: 0 (No group-year calibration opened.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
