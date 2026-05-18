# GXUST Mapping Review Packet

Scope: 广西科技大学 official group-structure lines joined to 2024/2025 Guangxi exam-authority group lines.

- Packet rows: 17
- Regular physics joined line rows: 8
- Regular 520-window line rows: 3
- Exam-line-only holds: 5
- Excluded boundary rows: 4

Status rollup:
- exam_line_without_official_group_structure_hold exam_line_only_ethnic_class_hold: 2 rows, groups=751|761, both520=0
- exam_line_without_official_group_structure_hold exam_line_only_missing_official_group_structure_hold: 3 rows, groups=951|952|961, both520=0
- excluded_non_regular_or_special_group ethnic_preparatory_isolated_hold: 2 rows, groups=719|759, both520=0
- excluded_non_regular_or_special_group history_non_physics_isolated_hold: 1 rows, groups=111, both520=0
- excluded_non_regular_or_special_group sino_foreign_isolated_hold: 1 rows, groups=351, both520=0
- official_group_structure_joined_to_2025_exam_line_plan_count_missing regular_physics_group_line_520_window_plan_missing: 3 rows, groups=153|163|171, both520=3
- official_group_structure_joined_to_2025_exam_line_plan_count_missing regular_physics_group_line_outside_520_window_plan_missing: 5 rows, groups=151|152|154|161|162, both520=0

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_gxust_group_line_workbench.csv)
- packet_rows_match_source: PASS (packet=17; source=17)
- status_counts_match_source_rollup: PASS (joined=8; unmatched=5; excluded=4)
- regular_520_window_rows_carried: PASS (3)
- plan_count_still_missing: PASS (0)
- status_rollup_present: PASS (7 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
