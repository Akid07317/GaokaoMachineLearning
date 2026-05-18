# Reference Trend 520 Batch11 Parse Readiness

Generated: 2026-05-16

Scope: promote batch11 official source candidates from discovery to parse-readiness routing.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch11_parse_readiness_preview.csv`
- `reports/reference_trend_520_batch11_parse_readiness_rollup.csv`
- `reports/reference_trend_520_batch11_parse_readiness_qa.csv`
- `reports/reference_trend_520_batch11_parse_readiness_exclusion_log.csv`

Findings:
- 山东科技大学 (76): text_pdf_candidate_ready_for_local_cache_then_parse_preview; next `cache_pdf_then_table_parse_with_guangxi_column_validation`.
- 惠州学院 (85): text_pdf_candidate_ready_for_local_cache_then_parse_preview; next `cache_pdf_then_parse_subject_filtered_guangxi_rows`.
- 武汉轻工大学 (88): detail_page_candidate_cache_miss_hold; next `retry_normal_page_cache_or_browser_if_repeated_cache_miss`.
- 广东海洋大学 (79|80): captcha_gated_attachment_hold; next `manual_download_or_approved_browser_captcha_route`.

Boundary:
- This is readiness routing only; it does not parse plan rows into the trend pool.
- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` for every row.
- Any captcha/browser route remains approval-gated.

Rollup:
- parse_readiness_rows: 4 Batch11 official candidates only.
- text_pdf_candidates: 2 山东科技大学, 惠州学院.
- captcha_gated_rows: 1 广东海洋大学.
- detail_cache_miss_rows: 1 武汉轻工大学.
- requires_manual_approval_rows: 1
- reference_trend_pool_eligible_rows: 0 Readiness only.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false
- status::captcha_gated_attachment_hold: 1
- status::detail_page_candidate_cache_miss_hold: 1
- status::text_pdf_candidate_ready_for_local_cache_then_parse_preview: 2
- route::cache_pdf_then_parse_subject_filtered_guangxi_rows: 1
- route::cache_pdf_then_table_parse_with_guangxi_column_validation: 1
- route::manual_download_or_approved_browser_captcha_route: 1
- route::retry_normal_page_cache_or_browser_if_repeated_cache_miss: 1
