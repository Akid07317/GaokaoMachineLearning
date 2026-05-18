# ZUCC Mapping Review Packet

Scope: 浙大城市学院 official image-plan evidence joined only to Guangxi exam-authority group-line context.

- Packet rows: 5
- Official image physics plan total: 80
- Official image history plan total: 10
- Official image major rows: 17
- Historical context rows: 2
- 2025 group plan-split missing holds: 1
- Explicit reject-full-plan-assignment rows: 1

Status rollup:
- candidate_2025_exam_group_without_school_plan_split -> exam_group_plan_split_missing_hold: 1 rows, groups=101, physics_total=80
- candidate_same_code_group_but_reject_full_80_plan_assignment -> reject_full_school_plan_assignment_same_code_context_hold: 1 rows, groups=102, physics_total=80
- historical_exam_line_context_only -> historical_context_only: 2 rows, groups=102|103, physics_total=0
- school_plan_total_unassigned_to_group -> school_plan_total_unassigned_summary: 1 rows, groups=unassigned, physics_total=80

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=5; source=5)
- multiple_2025_physics_groups_confirmed: PASS (101|102)
- physics_plan_total_carried: PASS (expected 80)
- history_plan_total_carried: PASS (expected 10)
- major_rows_carried: PASS (expected 17)
- reject_full_80_assignment_present: PASS (1)
- manual_decision_fields_blank: PASS (selected_decision/selected_group_code/reviewer/decision_notes checked)
- status_rollup_present: PASS (4 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
