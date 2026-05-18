# NANHANG Mapping Review Packet

Scope: 南京航空航天大学 2024 official major-score rows, 2025 official plan rows, and overview boundary evidence.

- Packet rows: 44
- 2024 major-score rows: 19
- 2025 plan rows: 21
- 2024 overview rows: 4

Status rollup:
- official_major_score_2024_candidate score_floor_exact_rank_missing: 2 rows, plan_count_sum=0
- official_major_score_2024_candidate score_single_group_candidate_rank_missing: 17 rows, plan_count_sum=0
- official_plan_2025_cross_year_candidate plan_multiple_cross_year_matches_303_scope_unresolved: 2 rows, plan_count_sum=4
- official_plan_2025_cross_year_candidate plan_no_2024_score_match_303_scope_unresolved: 3 rows, plan_count_sum=7
- official_plan_2025_cross_year_candidate plan_single_cross_year_match_303_scope_unresolved: 16 rows, plan_count_sum=64
- official_score_overview_2024_boundary overview_ordinary_floor_boundary_only: 1 rows, plan_count_sum=0
- official_score_overview_2024_boundary overview_special_boundary_only: 3 rows, plan_count_sum=0

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_nanhang_group_boundary_workbench.csv)
- packet_rows_match_source: PASS (packet=44; source=44)
- row_kind_counts_match_rollup: PASS (score=19; plan=21; overview=4)
- single_candidate_rows_carried: PASS (38)
- unmapped_or_boundary_rows_carried: PASS (6)
- overview_boundary_split: PASS (ordinary=1; special=3)
- status_rollup_present: PASS (7 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
