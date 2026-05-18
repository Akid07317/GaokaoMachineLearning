# Reference Trend 520 P0 Official Source Discovery Batch 11

Generated: 2026-05-16

Scope: queue ranks 76-90. This is source discovery only, not intake.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch11_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch11_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch11_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch11_exclusion_log.csv`

Key source findings:
- 76 山东科技大学: official_pdf_plan_candidate_discovered_not_cached (T2_official_pdf_plan_candidate_not_cached).
- 77 山东财经大学: no_first_party_source_found_third_party_reference_only (T4_third_party_only_no_first_party_plan_source).
- 78 山东财经大学: no_first_party_source_found_third_party_reference_only (T4_third_party_only_no_first_party_plan_source).
- 79 广东海洋大学: official_plan_page_found_attachment_captcha_blocked (T2_official_attachment_captcha_blocked).
- 80 广东海洋大学: official_plan_page_found_attachment_captcha_blocked (T2_official_attachment_captcha_blocked).
- 81 广东石油化工学院: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 82 广东石油化工学院: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 83 延边大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_guangxi_plan_rows).
- 84 延边大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_guangxi_plan_rows).
- 85 惠州学院: official_pdf_plan_candidate_discovered_not_cached (T2_official_pdf_plan_candidate_not_cached).
- 86 成都中医药大学: official_context_found_no_structured_plan_rows (T3_official_context_only_no_guangxi_plan_rows).
- 87 成都师范学院: no_official_source_found_in_batch (T4_no_first_party_guangxi_plan_source_found).
- 88 武汉轻工大学: official_plan_page_candidate_discovered_not_cached (T2_official_plan_page_candidate_not_cached).
- 89 江苏师范大学: no_first_party_source_found_third_party_reference_only (T4_third_party_only_no_first_party_plan_source).
- 90 河北大学: no_first_party_source_found_third_party_reference_only (T4_third_party_only_no_first_party_plan_source).

Boundary:
- This batch does not parse any PDF, attachment, or HTML plan table.
- All rows remain `reference_trend_source_packet_preview_only`.
- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.

Rollup:
- discovery_rows: 15 Queue ranks 76-90, including duplicate-school group rows.
- unique_universities: 11
- official_plan_candidate_rows: 5 Needs cache/parse before intake.
- first_party_context_only_rows: 3 Official context but no plan rows.
- third_party_or_missing_rows: 7 Not accepted as source packets.
- requires_manual_approval_rows: 2 Captcha/browser-gated attachment routes.
- reference_trend_pool_eligible_rows: 0 Discovery preview only.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false
- status::no_first_party_source_found_third_party_reference_only: 4
- status::no_official_source_found_in_batch: 3
- status::official_context_found_no_structured_plan_rows: 3
- status::official_pdf_plan_candidate_discovered_not_cached: 2
- status::official_plan_page_candidate_discovered_not_cached: 1
- status::official_plan_page_found_attachment_captcha_blocked: 2
- confidence::T2_official_attachment_captcha_blocked: 2
- confidence::T2_official_pdf_plan_candidate_not_cached: 2
- confidence::T2_official_plan_page_candidate_not_cached: 1
- confidence::T3_official_context_only_no_guangxi_plan_rows: 3
- confidence::T4_no_first_party_guangxi_plan_source_found: 3
- confidence::T4_third_party_only_no_first_party_plan_source: 4
