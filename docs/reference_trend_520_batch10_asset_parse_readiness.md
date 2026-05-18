# Reference Trend 520 Batch10 Asset Parse Readiness

Generated: 2026-05-16

Purpose: assess batch10 cached/backoff official assets before any structured source-packet parse.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch10_asset_parse_readiness_preview.csv`
- `reports/reference_trend_520_batch10_asset_parse_readiness_rollup.csv`
- `reports/reference_trend_520_batch10_asset_parse_readiness_qa.csv`
- `reports/reference_trend_520_batch10_asset_parse_readiness_exclusion_log.csv`

Key findings:
- 宁夏医科大学 (70): cached_pdf_parser_unavailable_hold; next `pdf_text_parser_or_audited_pdf_render_ocr`.
- 山东政法学院 (75): guangxi_image_url_extracted_ocr_unavailable_hold; next `audited_image_download_plus_ocr_or_manual_transcription`.
- 宁夏大学 (71): parameterized_portal_cached_needs_api_or_form_drilldown; next `static_js_endpoint_inspection_or_approved_form_replay`.
- 天津外国语大学 (67|68): cached_context_no_structured_guangxi_rows_hold; next `find_official_province_plan_attachment_or_endpoint`.
- 大连医科大学中山学院 (65): tls_blocked_no_local_asset_hold; next `approved_browser_or_certificate_audited_retry`.
- 安徽理工大学 (74): no_parse_asset_hold; next `renewed_first_party_source_discovery`.

Boundary:
- This is a source readiness packet only.
- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` for every row.
- Remote image fetch, TLS retry, browser/form replay, or OCR route remains approval-gated.

Rollup:
- asset_readiness_rows: 6 Batch10 cached/backoff assets assessed.
- reference_trend_pool_eligible_rows: 0 Readiness only; no parse accepted.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false ML/canonical remains closed.
- requires_manual_approval_rows: 4 Routes involving remote image/browser/form/TLS need approval.
- status::cached_context_no_structured_guangxi_rows_hold: 1
- status::cached_pdf_parser_unavailable_hold: 1
- status::guangxi_image_url_extracted_ocr_unavailable_hold: 1
- status::no_parse_asset_hold: 1
- status::parameterized_portal_cached_needs_api_or_form_drilldown: 1
- status::tls_blocked_no_local_asset_hold: 1
- route::approved_browser_or_certificate_audited_retry: 1
- route::audited_image_download_plus_ocr_or_manual_transcription: 1
- route::find_official_province_plan_attachment_or_endpoint: 1
- route::pdf_text_parser_or_audited_pdf_render_ocr: 1
- route::renewed_first_party_source_discovery: 1
- route::static_js_endpoint_inspection_or_approved_form_replay: 1
