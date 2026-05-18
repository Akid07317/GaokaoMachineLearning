# NCUT Mapping Review Packet

Scope: 北方工业大学 2025 official Guangxi-column plan evidence joined only to Guangxi exam-authority group-line context.

- Packet rows: 8
- Historical context rows: 3
- Regular plan-count available but group/subject-mapping hold rows: 3
- School-level unassigned plan summary rows: 1
- Special group isolated holds: 1
- Official 2025 Guangxi-column plan total: 57
- Ordinary unmarked plan total: 48
- Special plan breakdown: art_design_boundary:4;sino_foreign_cooperation:5

Status rollup:
- historical_exam_line_context_only -> historical_context_only: 3 rows, groups=102|304|505, source_rows=0
- multiple_exam_groups_source_no_group_or_subject_hold -> plan_count_available_multi_group_subject_mapping_hold: 3 rows, groups=102|103|304, source_rows=3
- school_plan_total_unassigned_to_group_and_subject -> school_plan_total_unassigned_group_subject_summary: 1 rows, groups=unassigned, source_rows=1
- special_type_exam_group_hold -> special_type_exam_group_isolated_hold: 1 rows, groups=500, source_rows=1

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=8; source=8)
- historical_context_rows_expected: PASS (3)
- regular_group_subject_mapping_hold_rows_expected: PASS (3)
- school_total_summary_rows_expected: PASS (1)
- special_type_hold_rows_expected: PASS (1)
- official_plan_total_carried: PASS (expected 57)
- ordinary_unmarked_plan_total_carried: PASS (expected 48)
- source_missing_group_and_subject_labels: PASS (official_source_contains_group_code/subject_label checked)
- manual_decision_fields_blank: PASS (selected_decision/selected_group_code/reviewer/decision_notes checked)
- status_rollup_present: PASS (4 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
