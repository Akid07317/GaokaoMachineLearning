# Reference Trend 520 Batch12 Asset/API Readiness

Generated: 2026-05-16

Purpose: record cached official image/API assets before any OCR, form replay, or source-packet parse.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch12_asset_api_readiness_preview.csv`
- `reports/reference_trend_520_batch12_asset_api_readiness_rollup.csv`
- `reports/reference_trend_520_batch12_asset_api_readiness_qa.csv`
- `reports/reference_trend_520_batch12_asset_api_readiness_exclusion_log.csv`

Key findings:
- 浙江海洋大学 (93|245|449): official_image_assets_cached_ocr_or_manual_parse_needed; next `audited_image_ocr_or_manual_transcription`.
- 温州医科大学 (95|316): tls_blocked_no_local_asset_hold; next `approved_browser_or_alternate_tls_route`.
- 重庆中医药学院 (106): official_portal_cached_endpoint_shape_found_api_404_hold; next `static_js_endpoint_review_or_approved_browser_form_replay`.
- 重庆工商大学 (107): no_parse_asset_hold; next `renewed_first_party_plan_source_discovery`.

Boundary:
- This is an asset/API readiness packet only.
- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` for every row.
- OCR, browser/form replay, header/cookie replay, alternate TLS route, or manual transcription remains approval-gated.

Rollup:
- asset_api_readiness_rows: 4 Batch12 cached/backoff assets assessed.
- cached_official_asset_rows: 2 Rows with at least one local official/cache file.
- image_asset_rows: 2 Rows requiring OCR/manual image parse.
- tls_blocked_rows: 1 Held for approval before retry.
- endpoint_shape_found_rows: 1 Portal/API route identified but not accepted.
- endpoint_data_rows: 0 The attempted 重庆中医药 API route returned 404 HTML, not data JSON.
- reference_trend_pool_eligible_rows: 0 Readiness only; no source-packet parse accepted.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false ML/canonical remains closed.
- requires_manual_approval_rows: 3 OCR/browser/form/TLS routes are approval-gated.
- status::no_parse_asset_hold: 1
- status::official_image_assets_cached_ocr_or_manual_parse_needed: 1
- status::official_portal_cached_endpoint_shape_found_api_404_hold: 1
- status::tls_blocked_no_local_asset_hold: 1
- route::approved_browser_or_alternate_tls_route: 1
- route::audited_image_ocr_or_manual_transcription: 1
- route::renewed_first_party_plan_source_discovery: 1
- route::static_js_endpoint_review_or_approved_browser_form_replay: 1
