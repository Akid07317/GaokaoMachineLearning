# Group Mapping Review Closeout

Scope: closeout board for the 15 reference-trend group mapping action-board items.

- Action rows: 15
- Artifacts present: 15/15
- Artifact rows total: 424
- Pending human or batch-acceptance rows: 424
- Human-filled decision rows detected: 0

Pending queue:
- 1. 广西师范大学: 53 rows, fill_selected_group_code_selected_decision_reviewer_decision_notes (clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_mapping_review_packet.csv)
- 2. 昆明理工大学|江苏大学: 86 rows, review_mapping_ambiguity_and_select_group_or_hold (clean_data/engineering_guangxi_seed/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.csv)
- 3. 中国地质大学(北京): 53 rows, fill_mapping_decision_or_keep_multi_group_hold (clean_data/engineering_guangxi_seed/reference_trend_520_cugb_mapping_review_packet.csv)
- 4. 兰州交通大学: 52 rows, fill_mapping_decision_or_keep_multi_group_hold (clean_data/engineering_guangxi_seed/reference_trend_520_lzjtu_mapping_review_packet.csv)
- 5. 南京航空航天大学: 44 rows, review_boundary_and_rank_missing_holds (clean_data/engineering_guangxi_seed/reference_trend_520_nanhang_mapping_review_packet.csv)
- 6. 中南民族大学: 35 rows, assign_2025_plan_rows_to_group_or_hold_unassigned (clean_data/engineering_guangxi_seed/reference_trend_520_scuec_mapping_review_packet.csv)
- 7. 哈尔滨医科大学: 22 rows, review_physics_plan_group_missing_and_boundary_holds (clean_data/engineering_guangxi_seed/reference_trend_520_hrbmu_mapping_review_packet.csv)
- 8. 宁波诺丁汉大学: 17 rows, accept_or_hold_pdf_label_group303_mapping (clean_data/engineering_guangxi_seed/reference_trend_520_unnc_mapping_review_packet.csv)
- 9. 广西科技大学: 17 rows, review_plan_missing_and_group_line_evidence (clean_data/engineering_guangxi_seed/reference_trend_520_gxust_mapping_review_packet.csv)
- 10. 石河子大学|福建理工大学: 13 rows, review_shzu_fjut_group_mapping_or_keep_school_level_only (clean_data/engineering_guangxi_seed/reference_trend_520_batch7_mapping_review_packet.csv)
- 11. 集美大学: 7 rows, accept_hold_request_fix_or_reject_jmu_group_mapping (clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.csv)
- 12. 北方工业大学: 8 rows, review_ncut_group_subject_mapping_or_keep_school_level_only (clean_data/engineering_guangxi_seed/reference_trend_520_ncut_mapping_review_packet.csv)
- 13. 河南理工大学: 5 rows, batch_accept_hpu_enrichment_or_keep_preview_only (clean_data/engineering_guangxi_seed/reference_trend_hpu_group_line_intake_preview.csv)
- 14. 中南林业科技大学: 7 rows, review_csuft_group_mapping_or_keep_selection_summary_only (clean_data/engineering_guangxi_seed/reference_trend_520_csuft_mapping_review_packet.csv)
- 15. 浙大城市学院: 5 rows, find_group_split_or_keep_reject_full_80_assignment_hold (clean_data/engineering_guangxi_seed/reference_trend_520_zucc_mapping_review_packet.csv)

QA:
- action_board_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_action_board.csv)
- action_rows_expected: PASS (15)
- all_artifacts_present: PASS (15/15)
- manual_decision_rows_detected: PASS (0)
- todo_queue_nonempty: PASS (15)
- canonical_ml_still_closed: PASS (Closeout board only.)
- decision_pool_boundary: PASS (No 32-school decision_pool writes.)

Boundary: no row is promoted into reference_trend_pool, canonical, ML, or the 32-school decision pool.
