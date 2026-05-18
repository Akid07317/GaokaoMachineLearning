# CSUFT Mapping Review Packet

Scope: 中南林业科技大学 2025 official plan evidence joined only to Guangxi exam-authority group-line context.

- Packet rows: 7
- Historical context rows: 3
- Regular plan-count and selection available but group-mapping hold rows: 3
- School-level unassigned plan summary rows: 1
- Official 2025 plan total: 150
- Official major rows: 41
- Selection breakdown: 不提科目要求:5;物理(1门科目考生必须选考方可报考):19;物理,化学(2门科目考生均须选考方可报考):123;生物(1门科目考生必须选考方可报考):3

Status rollup:
- historical_exam_line_context_only -> historical_context_only: 3 rows, groups=104|106|108, source_rows=0
- multiple_exam_groups_source_no_group_code_hold -> plan_count_selection_available_group_mapping_hold: 3 rows, groups=104|106|108, source_rows=3
- school_plan_total_unassigned_to_group -> school_plan_total_unassigned_selection_summary: 1 rows, groups=unassigned, source_rows=1

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_batch8_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=7; source=7)
- historical_context_rows_expected: PASS (3)
- regular_group_mapping_hold_rows_expected: PASS (3)
- school_total_summary_rows_expected: PASS (1)
- official_plan_total_carried: PASS (expected 150)
- official_major_rows_carried: PASS (expected 41)
- source_missing_group_code: PASS (official_source_contains_group_code checked)
- selection_breakdown_present: PASS (selection plan breakdown checked)
- manual_decision_fields_blank: PASS (selected_decision/selected_group_code/reviewer/decision_notes checked)
- status_rollup_present: PASS (3 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
