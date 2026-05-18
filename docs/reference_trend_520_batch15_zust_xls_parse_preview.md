# Reference Trend 520 Batch15 Zhejiang University of Science and Technology XLS Parse Preview

Generated: 2026-05-16

Purpose: cache and parse 浙江科技大学 official 2025 plan page/XLS into a
non-canonical source-packet preview for later professional-group and subject
route mapping.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_zust_xls_parse_preview.csv`
- `reports/reference_trend_520_batch15_zust_xls_parse_rollup.csv`
- `reports/reference_trend_520_batch15_zust_xls_parse_qa.csv`
- `reports/reference_trend_520_batch15_zust_xls_parse_exclusion_log.csv`

## Summary

- Official page: `https://zsb.zust.edu.cn/wzxq/9163af354da64088986a66b6bc726358`
- Official XLS attachment: `https://job.zust.edu.cn/zjcFiles//ckimgs/1750238175796.xls`
- Cached page: `raw_sources/reference_trend/batch15_official/zust_2025_plan_page.html`
- Cached XLS: `raw_sources/reference_trend/batch15_official/zust_2025_plan_attachment.xls`
- XLS load status: `xlrd_sheet_loaded`; sheet: `2025年分省分专业方案`
- Guangxi rows extracted: 25
- Guangxi plan count sum: 165
- Physics-selection rows: 19
- Ambiguous 不限-selection rows: 6

The official XLS is useful plan-count evidence, but it is not a Guangxi
professional-group split and it contains several `不限` rows whose physical/history
route must be confirmed. All rows remain outside `reference_trend_pool`,
`canonical`, `ML`, and the 32-school decision_pool.

## Boundary

`eligible_for_intake_preview=true_source_packet_preview_only` marks a row as a
plan-side source-packet preview, not as calibration-ready data. Every row remains
`reference_trend_pool_eligible=false_until_group_code_and_subject_route_mapping`.
