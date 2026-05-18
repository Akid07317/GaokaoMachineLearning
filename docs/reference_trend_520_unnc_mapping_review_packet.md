# UNNC Mapping Review Packet

Scope: 宁波诺丁汉大学 2025 official PDF label/group303 mapping review packet.

- Packet rows: 17
- Ready positive-plan rows: 8
- Zero-plan or label-review hold rows: 9
- Provisional Guangxi physical plan sum: 20

Status rollup:
- ready_for_manual_accept_if_label_and_group303_are_confirmed ready_positive_plan_group303_t1_label: 4 rows, plan_sum=10, groups=303
- ready_for_manual_accept_if_label_and_group303_are_confirmed ready_positive_plan_group303_t2_label: 4 rows, plan_sum=10, groups=303
- zero_plan_or_label_review_hold zero_plan_hold_group303_label_context: 9 rows, plan_sum=0, groups=303

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv)
- packet_rows_match_source: PASS (packet=17; source=17)
- status_counts_match_source_rollup: PASS (ready=8; hold=9)
- guangxi_plan_checksum_carried: PASS (20)
- all_rows_group303_context: PASS (303)
- manual_decision_fields_blank: PASS (selected_decision/reviewer/decision_notes checked)
- status_rollup_present: PASS (3 rows)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
