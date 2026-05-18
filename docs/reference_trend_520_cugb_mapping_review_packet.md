# CUGB Mapping Review Packet

Scope: 中国地质大学(北京) 2024/2025 official major score and plan mapping candidates.

- Packet rows: 53
- Score-major rows: 9
- Plan-major rows: 44
- Special collision rows: 3

Status rollup:
- 2024 plan_major_mapping_candidate plan_matched_ambiguous_floor_candidate: 3 rows, plan_count_sum=7
- 2024 plan_major_mapping_candidate plan_matched_single_floor_candidate_unconfirmed: 1 rows, plan_count_sum=1
- 2024 plan_major_mapping_candidate plan_unmapped_no_score_match: 17 rows, plan_count_sum=39
- 2024 score_major_mapping_candidate score_ambiguous_multi_group_floor_candidate: 3 rows, plan_count_sum=0
- 2024 score_major_mapping_candidate score_single_group_floor_candidate_unconfirmed: 1 rows, plan_count_sum=0
- 2025 plan_major_mapping_candidate plan_matched_ambiguous_floor_candidate: 3 rows, plan_count_sum=5
- 2025 plan_major_mapping_candidate plan_matched_ambiguous_floor_candidate__special_collision_context: 2 rows, plan_count_sum=2
- 2025 plan_major_mapping_candidate plan_unmapped_no_score_match: 18 rows, plan_count_sum=45
- 2025 score_major_mapping_candidate score_ambiguous_multi_group_floor_candidate: 4 rows, plan_count_sum=0
- 2025 score_major_mapping_candidate score_ambiguous_multi_group_floor_candidate__special_collision_context: 1 rows, plan_count_sum=0

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_cugb_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=53; source=53)
- score_major_rows_classified: PASS (9)
- plan_major_rows_classified: PASS (44)
- special_collision_rows_carried: PASS (3)
- status_rollup_present: PASS (10 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
