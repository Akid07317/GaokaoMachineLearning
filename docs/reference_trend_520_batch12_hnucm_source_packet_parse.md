# Reference Trend 520 Batch12 HNUCM Source Packet Parse

Generated: 2026-05-16

Scope: 湖南中医药大学 official 2025 province-by-major plan HTML table.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch12_hnucm_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch12_hnucm_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch12_hnucm_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch12_hnucm_source_packet_parse_exclusion_log.csv`

Result:
- Guangxi all-subject published total: 105
- Parsed Guangxi all-subject rows/sum: 39 / 105
- Parsed Guangxi physical rows/sum: 32 / 91
- Nonphysical excluded rows/sum: 7 / 14

Boundary:
- The source table does not print Guangxi院校专业组代码.
- `queue_group_code=105` is retained only as queue context, not accepted as source group mapping.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.

Rollup:
- source_file: raw_sources/reference_trend/batch12_official/hnucm_2025_plan.html
- source_url: https://zhaosheng.hnucm.edu.cn/info/1143/6051.htm
- published_guangxi_total_all_subjects: 105 Header total row for Guangxi.
- parsed_guangxi_all_subject_rows: 39
- parsed_guangxi_all_subject_plan_sum: 105
- parsed_guangxi_physical_rows: 32
- parsed_guangxi_physical_plan_sum: 91 Source subject contains 理科 or 物理.
- excluded_nonphysical_rows: 7
- excluded_nonphysical_plan_sum: 14
- special_type_flagged_rows: 4 Flagged, not deleted.
- reference_trend_pool_eligible_rows: 0 No group code printed by source.
- calibration_eligible_rows: 0 Group-year calibration closed pending mapping.
- canonical_ml_entry_open: false
- special::ordinary_unmarked: 28
- special::卓越;5+3: 4
