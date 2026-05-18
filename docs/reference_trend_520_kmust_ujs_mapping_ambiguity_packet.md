# KMUST/UJS Mapping Ambiguity Packet

Scope: derived packet from the existing 昆明理工大学 / 江苏大学 mapping QA workbench.

- Packet rows: 86
- UJS single-regular score-reference rows with missing rank: 16
- KMUST exact floor candidate rows: 6
- KMUST ambiguous threshold rows: 46

Status rollup:
- 昆明理工大学 历史类 exclude_non_physics: 3 rows, admission_count_sum=0
- 昆明理工大学 物理类 ambiguous_threshold_multi_group: 46 rows, admission_count_sum=0
- 昆明理工大学 物理类 exact_floor_candidate_unconfirmed: 6 rows, admission_count_sum=0
- 江苏大学 历史类 exclude_non_physics: 11 rows, admission_count_sum=20
- 江苏大学 物理类 exclude_special_type: 4 rows, admission_count_sum=12
- 江苏大学 物理类 score_reference_single_regular_group_rank_missing: 16 rows, admission_count_sum=151

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_kmust_ujs_group_mapping_qa_workbench.csv)
- packet_rows_match_source: PASS (packet=86; source=86)
- ujs_single_regular_rows_classified: PASS (16)
- kmust_ambiguous_rows_classified: PASS (46)
- status_rollup_present: PASS (6 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
