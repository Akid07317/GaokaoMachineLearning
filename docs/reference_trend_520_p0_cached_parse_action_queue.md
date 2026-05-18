# Reference Trend 520 P0 Cached Parse Action Queue

Date: 2026-05-16

Scope: local next-action queue derived from `reference_trend_520_p0_cached_asset_endpoint_preflight.csv`. This queue tells the next run whether to attempt local PDF text extraction, local asset/OCR review, endpoint metadata review, or keep keyword-only context on hold. It does not perform parsing/OCR, does not fetch remote pages, and does not create source_packet/intake/canonical rows.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_parse_action_queue.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_exclusion_log.csv`

## Coverage

- Parse action rows: 20
- QA status: PASS

## Route Counts

- `asset_link_needs_cached_capture_or_approval`: 11
- `decorative_or_site_asset_low_priority`: 4
- `endpoint_metadata_review_before_live_replay`: 1
- `keyword_context_hold_no_structured_plan_rows`: 3
- `local_pdf_text_extract_preview_queue`: 1

## Boundary

All rows remain outside reference_trend_pool intake and outside canonical/ML. Rows requiring live asset capture or form/browser replay remain approval-gated.
