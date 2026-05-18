# Reference Trend 520 P0 Official Source Discovery Batch 12

Generated: 2026-05-16

Scope: queue ranks 91-110. This is source discovery and carry-forward only, not reference trend intake.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch12_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch12_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch12_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch12_exclusion_log.csv`

Key source findings:
- 91 河南理工大学: existing_mapping_workbench_hold_for_group_acceptance (T1_existing_official_group_line_workbench).
- 92 浙江传媒学院: existing_official_index_cached_no_guangxi_rows (T2_existing_official_index_needs_asset_or_endpoint_drilldown).
- 93 浙江海洋大学: official_plan_score_candidate_discovered_not_cached (T2_official_homepage_guangxi_plan_score_candidate_not_cached).
- 94 浙江科技大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_guangxi_plan_rows).
- 95 温州医科大学: official_plan_page_candidate_discovered_not_cached (T2_official_plan_page_candidate_not_cached).
- 96 温州大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_guangxi_plan_rows).
- 97 湖北工业大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_guangxi_plan_rows).
- 98 湖南中医药大学: official_html_plan_table_parse_ready (T1_official_html_table_plan_candidate_parse_ready).
- 99 湘南学院: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 100 西南医科大学: existing_official_detail_cached_attachment_download_captcha_blocked (T2_existing_official_attachment_candidate_captcha_blocked).
- 101 西安财经大学: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 102 西藏大学: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 103 贵州财经大学: existing_official_pdf_candidate_reachability_blocked (T2_existing_official_pdf_candidate_reachability_blocked).
- 104 辽宁大学: official_score_reference_found_not_plan_source (T3_official_score_reference_not_plan_source).
- 105 郑州轻工业大学: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 106 重庆中医药学院: official_plan_page_candidate_discovered_not_cached (T2_official_plan_page_candidate_not_cached).
- 107 重庆工商大学: official_context_found_no_structured_plan_rows (T3_official_plan_context_no_guangxi_rows_confirmed).
- 108 重庆科技大学: official_plan_portal_discovered_endpoint_needed (T2_plan_query_portal_needs_endpoint_drilldown).
- 109 长春理工大学: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 110 长江大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_detailed_guangxi_plan_rows).

Boundary:
- This batch does not cache or parse any new PDF, endpoint, image, attachment, or HTML table.
- All rows remain `reference_trend_source_packet_preview_only` or existing noncanonical carry-forward status.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
- 32-school `decision_pool` remains isolated.

Next safe action:
- Prioritize 湖南中医药大学 official HTML plan table cache/parse because it is the only T1 parse-ready row in this batch.
- Continue source recovery for 浙江海洋大学、温州医科大学、重庆中医药学院 and endpoint drilldown for 重庆科技大学.
- Keep 西南医科大学 captcha route and 贵州财经大学 alternate PDF route approval-gated.

Rollup:
- discovery_rows: 20 Queue ranks 91-110.
- unique_universities: 20
- existing_candidate_carried_forward_rows: 4 Earlier noncanonical source artifacts/status carried forward only.
- official_plan_candidate_rows: 9 Requires cache/parse, endpoint drilldown, or existing-artifact review before intake.
- t1_parse_ready_rows: 1 湖南中医药大学 official HTML table is the only parse-ready candidate.
- first_party_context_or_score_only_rows: 6 Official context or score source, not a detailed plan packet.
- third_party_or_missing_rows: 5 No accepted first-party source packet.
- requires_manual_approval_rows: 3 Captcha/browser/alt-TLS/form routes.
- reference_trend_pool_eligible_rows: 0 Discovery preview only.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false
- status::existing_mapping_workbench_hold_for_group_acceptance: 1
- status::existing_official_detail_cached_attachment_download_captcha_blocked: 1
- status::existing_official_index_cached_no_guangxi_rows: 1
- status::existing_official_pdf_candidate_reachability_blocked: 1
- status::no_official_source_found_in_batch: 5
- status::official_context_found_no_structured_plan_rows: 5
- status::official_html_plan_table_parse_ready: 1
- status::official_plan_page_candidate_discovered_not_cached: 2
- status::official_plan_portal_discovered_endpoint_needed: 1
- status::official_plan_score_candidate_discovered_not_cached: 1
- status::official_score_reference_found_not_plan_source: 1
- confidence::T1_existing_official_group_line_workbench: 1
- confidence::T1_official_html_table_plan_candidate_parse_ready: 1
- confidence::T2_existing_official_attachment_candidate_captcha_blocked: 1
- confidence::T2_existing_official_index_needs_asset_or_endpoint_drilldown: 1
- confidence::T2_existing_official_pdf_candidate_reachability_blocked: 1
- confidence::T2_official_homepage_guangxi_plan_score_candidate_not_cached: 1
- confidence::T2_official_plan_page_candidate_not_cached: 2
- confidence::T2_plan_query_portal_needs_endpoint_drilldown: 1
- confidence::T3_official_context_only_no_detailed_guangxi_plan_rows: 1
- confidence::T3_official_context_only_no_guangxi_plan_rows: 3
- confidence::T3_official_plan_context_no_guangxi_rows_confirmed: 1
- confidence::T3_official_score_reference_not_plan_source: 1
- confidence::T4_no_first_party_guangxi_plan_source_found: 5
