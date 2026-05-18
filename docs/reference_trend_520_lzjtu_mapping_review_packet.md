# LZJTU Mapping Review Packet

Scope: 兰州交通大学 2024 official API score/plan rows with 101/102 group-candidate ambiguity.

- Packet rows: 52
- Score rows: 26
- Plan rows: 26

Status rollup:
- plan_major_mapping_candidate plan_ambiguous_candidate_from_exact_major_score_match: 20 rows, plan_count_sum=50
- plan_major_mapping_candidate plan_single_candidate_from_exact_major_score_match: 6 rows, plan_count_sum=14
- score_major_mapping_candidate score_ambiguous_two_group_threshold_candidate: 19 rows, plan_count_sum=0
- score_major_mapping_candidate score_floor_exact_but_still_two_group_candidate: 1 rows, plan_count_sum=0
- score_major_mapping_candidate score_floor_exact_single_candidate: 2 rows, plan_count_sum=0
- score_major_mapping_candidate score_single_threshold_candidate: 4 rows, plan_count_sum=0

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_lzjtu_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=52; source=52)
- score_and_plan_rows_classified: PASS (score=26; plan=26 expected)
- single_candidate_rows_carried: PASS (12)
- ambiguous_candidate_rows_carried: PASS (40)
- status_rollup_present: PASS (6 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
