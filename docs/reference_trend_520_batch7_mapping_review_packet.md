# Batch7 SHZU/FJUT Mapping Review Packet

Scope: 石河子大学 and 福建理工大学 2025 official plan-source evidence joined only to Guangxi exam-authority group-line context.

- Packet rows: 13
- Historical context rows: 5
- Regular plan-count available but group-mapping hold rows: 5
- School-level unassigned plan summaries: 2
- Special group isolated holds: 1

Official 2025 plan totals:
- 石河子大学: 100 (物理类:100)
- 福建理工大学: 205 (物理+不限:95;物理+化学:110)

Status rollup:
- historical_exam_line_context_only -> historical_context_only: 5 rows, schools=石河子大学|福建理工大学, groups=101|102|150|199|759
- multiple_exam_groups_source_no_group_code_hold -> plan_count_available_multi_group_mapping_hold: 5 rows, schools=石河子大学|福建理工大学, groups=101|102|104|150|199
- school_plan_total_unassigned_to_group -> school_plan_total_unassigned_summary: 2 rows, schools=石河子大学|福建理工大学, groups=unassigned
- special_type_exam_group_hold -> special_type_exam_group_isolated_hold: 1 rows, schools=福建理工大学, groups=759

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_batch7_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=13; source=13)
- university_counts_expected: PASS (石河子大学=6; 福建理工大学=7)
- historical_context_rows_expected: PASS (5)
- regular_group_mapping_hold_rows_expected: PASS (5)
- school_total_summary_rows_expected: PASS (2)
- special_type_hold_rows_expected: PASS (1)
- official_plan_totals_carried: PASS (石河子大学=100; 福建理工大学=205 expected)
- manual_decision_fields_blank: PASS (selected_decision/selected_group_code/reviewer/decision_notes checked)
- status_rollup_present: PASS (4 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
