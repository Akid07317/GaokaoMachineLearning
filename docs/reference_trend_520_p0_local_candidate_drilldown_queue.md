# Reference Trend 520 P0 Local Candidate Drilldown Queue

Generated: 2026-05-16

Purpose: convert the P0 `existing_candidate_parse_or_endpoint_drilldown` lane into candidate-level parse/rejection/approval routes without doing any live fetch.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_local_candidate_drilldown_queue.csv`
- `reports/reference_trend_520_p0_local_candidate_drilldown_queue_rollup.csv`
- `reports/reference_trend_520_p0_local_candidate_drilldown_queue_qa.csv`
- `reports/reference_trend_520_p0_local_candidate_drilldown_queue_exclusion_log.csv`

## Coverage

- Candidate drilldown rows: 60

## Drilldown Lane Rollup

- context_or_no_rows_hold: 25
- endpoint_or_portal_drilldown: 10
- image_or_asset_ocr_candidate: 15
- metadata_drilldown_needed: 2
- no_local_candidate_found_in_prior_batch: 7
- reject_third_party_only_candidate: 1

## Boundary

This is a non-baseline parse-routing queue. It can only feed future source_packet parse previews, rejection notes, or manual approval queues with QA. It does not open reference_trend_pool, canonical, ML, or the 32-school decision_pool.
