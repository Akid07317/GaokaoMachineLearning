# reference_trend_520 batch15 GZY PDF column parse preview

Generated: 2026-05-16

贵州中医药大学官方 2025 本科分省分专业招生计划 PDF 已缓存并解析为广西列 source-packet preview。本产物不进入 32 所 decision_pool。

## Result

- Official source URL: https://zs.gzy.edu.cn/info/1024/1853.htm
- Official PDF URL: https://zs.gzy.edu.cn/__local/5/DD/CD/C6E4AC695107FBBBFA9EC449395_1413CF88_18330.pdf
- Cached HTML: `raw_sources/reference_trend/batch15_official/gzy_2025_plan_page.html`
- Cached PDF: `raw_sources/reference_trend/batch15_official/gzy_2025_plan_pdf.pdf`
- Parsed Guangxi rows: 29
- Guangxi plan sum: 77
- Physical subject rows including boundaries: 21
- Physical subject plan sum including boundaries: 67
- Ordinary physical candidate rows: 20
- Ordinary physical candidate plan sum: 62
- Score/rank available: 0

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_gzy_pdf_column_parse_preview.csv`
- `reports/reference_trend_520_batch15_gzy_pdf_column_parse_rollup.csv`
- `reports/reference_trend_520_batch15_gzy_pdf_column_parse_qa.csv`
- `reports/reference_trend_520_batch15_gzy_pdf_column_parse_exclusion_log.csv`

## Gate Boundary

官方 PDF 可提取广西专业计划数，但没有院校专业组代码、最低分或最低位次。所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。后续需与广西考试院 group-line score/rank 和专业组上下文做 join workbench。

## QA

- official_page_cached: PASS - raw_sources/reference_trend/batch15_official/gzy_2025_plan_page.html
- official_pdf_cached: PASS - raw_sources/reference_trend/batch15_official/gzy_2025_plan_pdf.pdf
- pdf_column_table_extracted: PASS - rows=29
- guangxi_total_matches_pdf: PASS - parsed=77; pdf_total=77
- guangxi_physical_total_matches_pdf: PASS - parsed_all_physical=67; pdf_physical_total=67; ordinary_candidate_ex_special=62
- score_rank_hold: PASS - Official PDF is plan-only; no score or rank.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_page_cached_rows: 1 (raw_sources/reference_trend/batch15_official/gzy_2025_plan_page.html)
- official_pdf_cached_rows: 1 (raw_sources/reference_trend/batch15_official/gzy_2025_plan_pdf.pdf)
- parse_preview_rows_all_guangxi: 29 (rows with Guangxi plan count > 0)
- guangxi_plan_count_sum_all_rows: 77 (official total row=77)
- physical_subject_rows_all: 21 (all physical/理工 rows, including special boundaries)
- physical_subject_plan_sum_all: 67 (official physical total row=67)
- ordinary_physics_candidate_rows: 20 (physical/理工 rows excluding sport/cooperative boundaries)
- ordinary_physics_candidate_plan_sum: 62 (excludes cooperative/sport boundaries)
- source_group_code_available_rows: 0 (PDF does not print Guangxi professional-group codes)
- subject_distribution: {'历史': 5, '物理': 9, '理工/物理': 12, '文史/历史': 3} ()
- special_boundary_rows: 9 ({'history_subject_boundary': 8, 'none_detected': 20, 'cooperative_boundary': 1})
- score_rank_available_rows: 0 (Plan source only; no score/rank.)
- reference_trend_pool_eligible_rows: 0 (Score/rank and group join required before calibration.)
- calibration_eligible_rows: 0 (No group-year calibration opened.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
