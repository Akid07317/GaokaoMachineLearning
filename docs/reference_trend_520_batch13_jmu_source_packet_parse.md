# Reference Trend 520 Batch13 JMU Source Packet Parse

Generated: 2026-05-16

Purpose: parse 集美大学 official 2025 Guangxi plan detail page into a source-packet preview.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch13_jmu_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch13_jmu_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch13_jmu_source_packet_parse_exclusion_log.csv`

Key findings:
- The official Guangxi detail page prints batch, major, first subject, required subject, plan count, remarks, and professional-group code.
- 本科批 + 物理类 preview rows: 39; plan sum: 160.
- Groups printed in source: 04, 05, 06, 07, 08, 09, 10, 11.

Boundary:
- This is source-packet parse preview only.
- Group codes are printed, but score/rank group-line matching is not included in this source, so `reference_trend_pool_eligible` remains closed.
- No canonical/ML output and no 32-school decision_pool merge.

Rollup:
- cached_index_pages: 3 JMU plan index pages cached.
- source_major_rows: 51 All major rows before exclusions.
- source_total_plan_count: 230 Official total row.
- preview_physical_ordinary_rows: 39 本科批 + 物理类 rows.
- preview_physical_ordinary_plan_sum: 160 Sum of preview rows.
- excluded_plan_sum: 70 History/advance/summary plan count by difference.
- exclusion_rows: 13 Non-ordinary physical plus summary rows.
- reference_trend_pool_eligible_rows: 0 Needs score/rank or exam authority group-line match before pool intake.
- calibration_eligible_rows: 0 No score/rank in source packet.
- canonical_ml_entry_open: false ML/canonical remains closed.
- group_row_count::04: 10
- group_row_count::05: 4
- group_row_count::06: 4
- group_row_count::07: 9
- group_row_count::08: 5
- group_row_count::09: 4
- group_row_count::10: 1
- group_row_count::11: 2
- group_plan_sum::04: 31
- group_plan_sum::05: 18
- group_plan_sum::06: 19
- group_plan_sum::07: 40
- group_plan_sum::08: 23
- group_plan_sum::09: 20
- group_plan_sum::10: 4
- group_plan_sum::11: 5
