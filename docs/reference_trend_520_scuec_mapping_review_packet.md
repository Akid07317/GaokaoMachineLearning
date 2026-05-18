# SCUEC Mapping Review Packet

Scope: 中南民族大学 2025 official plan rows plus 2024 score-group evidence for 103/104/105.

- Packet rows: 35
- 2025 plan rows without group code: 32
- 2024 exact score-group evidence rows: 3
- Plan count sum: 492

Status rollup:
- plan_row_unmapped_no_group_code plan_count_row_unmapped_group_code_missing: 32 rows, plan_count_sum=492, groups=
- score_exact_single_exam_group_match score_exact_group_evidence_rank_delta_missing: 1 rows, plan_count_sum=0, groups=103
- score_exact_single_exam_group_match score_exact_group_evidence_with_rank_delta: 2 rows, plan_count_sum=0, groups=104|105

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_scuec_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=35; source=35)
- status_counts_match_source_rollup: PASS (plan_unmapped=32; score_exact=3)
- plan_count_sum_carried: PASS (492)
- score_group_codes_present: PASS (103|104|105)
- status_rollup_present: PASS (3 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
