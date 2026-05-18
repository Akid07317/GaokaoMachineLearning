# HRBMU Mapping Review Packet

Scope: 哈尔滨医科大学 2025 Guangxi plan rows with physical ordinary group-code gaps, special-type isolation, and legacy non-physics holds.

- Packet rows: 22
- Ordinary physical plan rows: 19
- Ordinary physical plan count: 32
- National special hold rows: 1
- Non-physics hold rows: 2

Status rollup:
- national_special_hold national_special_isolated_hold: 1 rows, plan_count_sum=13, groups=555
- non_physics_legacy_wen_hold non_physics_legacy_hold: 2 rows, plan_count_sum=5, groups=
- ordinary_physics_plan_row_group_code_missing ordinary_physics_plan_group_code_missing: 19 rows, plan_count_sum=32, groups=151|152|153|154|156|157|158|159

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=22; source=22)
- status_counts_match_source_rollup: PASS (ordinary=19; special=1; nonphysics=2)
- ordinary_physics_plan_count_sum_carried: PASS (32)
- special_and_nonphysics_isolated: PASS (special=13; nonphysics=5)
- ordinary_candidate_group_count: PASS (151|152|153|154|156|157|158|159)
- status_rollup_present: PASS (3 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
