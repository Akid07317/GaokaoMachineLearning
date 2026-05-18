# Reference Trend 520 P0 Official Source Discovery Batch 13

Generated: 2026-05-16

Scope: queue ranks 111-130 from the plan source packet queue.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch13_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch13_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch13_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch13_exclusion_log.csv`

Key findings:
- 陕西科技大学 (111): T4_third_party_context_rejected; no_first_party_plan_source_found_this_batch.
- 集美大学 (112|113|114|115): T2_official_plan_index_needs_detail_cache; official_plan_index_discovered_not_cached.
- 青岛理工大学 (116): T3_official_context_only_no_guangxi_plan_rows; official_context_found_no_structured_plan_rows.
- 青海大学 (117): T2_official_plan_image_candidate_not_cached; official_plan_image_candidate_discovered_not_cached.
- 上海应用技术大学 (118): T3_official_context_only_no_guangxi_plan_rows; official_context_found_no_structured_plan_rows.
- 华侨大学 (119): T1_official_plan_candidate_parse_ready_after_cache; official_plan_candidate_discovered_not_cached.
- 南京工程学院 (120|121): T4_third_party_context_rejected; no_first_party_plan_source_found_this_batch.
- 哈尔滨医科大学 (122): T1_official_plan_candidate_parse_ready_after_detail_cache; official_plan_detail_candidate_discovered_not_cached.
- 四川轻化工大学 (123): T1_official_plan_candidate_parse_ready_after_cache; official_plan_candidate_discovered_not_cached.
- 安徽工业大学 (124): T2_official_plan_image_candidate_not_cached; official_plan_image_candidate_discovered_not_cached.
- 广东海洋大学 (125): T2_existing_official_attachment_captcha_gated; existing_candidate_waiting_browser_or_manual_attachment.
- 成都大学 (126): T3_official_context_only_no_guangxi_plan_rows; official_context_found_no_structured_plan_rows.
- 无锡学院 (127): T4_third_party_plan_rows_rejected; no_first_party_plan_source_found_this_batch.
- 桂林理工大学 (128): T3_official_context_only_no_guangxi_group_rows; official_context_found_no_structured_plan_rows.
- 河南科技大学 (129): T1_official_plan_candidate_parse_ready_after_cache; official_plan_candidate_discovered_not_cached.
- 浙江传媒学院 (130): T2_existing_official_index_needs_asset_or_endpoint_drilldown; existing_official_index_cached_no_guangxi_rows.

Boundary:
- This is source discovery only.
- No remote asset cache, OCR, browser/form replay, source-packet parse, reference trend intake, canonical, or ML output is opened.
- Third-party summaries are retained only as rejected context until first-party sources are found.

Rollup:
- batch13_preview_rows: 16 Queue ranks 111-130 compressed by duplicate school groups where appropriate.
- queue_rank_coverage: 111-130 All listed queue ranks are represented.
- official_plan_candidate_rows: 7 Rows with first-party plan route candidates.
- existing_carry_forward_rows: 2 Prior noncanonical source state carried forward without refetch.
- third_party_rejected_rows: 3 Search hits retained only as rejected context.
- reference_trend_pool_eligible_rows: 0 Discovery only; no source-packet parse accepted.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false ML/canonical remains closed.
- requires_manual_approval_rows: 3 Image OCR/captcha routes are approval-gated.
- status::existing_candidate_waiting_browser_or_manual_attachment: 1
- status::existing_official_index_cached_no_guangxi_rows: 1
- status::no_first_party_plan_source_found_this_batch: 3
- status::official_context_found_no_structured_plan_rows: 4
- status::official_plan_candidate_discovered_not_cached: 3
- status::official_plan_detail_candidate_discovered_not_cached: 1
- status::official_plan_image_candidate_discovered_not_cached: 2
- status::official_plan_index_discovered_not_cached: 1
- confidence::T1_official_plan_candidate_parse_ready_after_cache: 3
- confidence::T1_official_plan_candidate_parse_ready_after_detail_cache: 1
- confidence::T2_existing_official_attachment_captcha_gated: 1
- confidence::T2_existing_official_index_needs_asset_or_endpoint_drilldown: 1
- confidence::T2_official_plan_image_candidate_not_cached: 2
- confidence::T2_official_plan_index_needs_detail_cache: 1
- confidence::T3_official_context_only_no_guangxi_group_rows: 1
- confidence::T3_official_context_only_no_guangxi_plan_rows: 3
- confidence::T4_third_party_context_rejected: 2
- confidence::T4_third_party_plan_rows_rejected: 1
