# P0 Official Source Discovery Batch 5

Generated: 2026-05-16

This batch records official-source discovery for P0 rows that the queue reconciliation still marked as needing source discovery. It is a source-packet preview only.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch5_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_exclusion_log.csv`

## Coverage

- Candidate rows: 8
- Universities covered: 6
- T1 high-value official rows: 2
- Rows needing endpoint/asset drilldown or retry: 5

## Status Rollup

- collector_confidence::T1_official_html_extractable_score_rank_candidate: 1
- collector_confidence::T1_official_pdf_extractable_plan_candidate: 1
- collector_confidence::T2_official_portal_needs_endpoint_or_asset: 3
- collector_confidence::T3_official_root_backoff_no_structured_plan_found: 1
- collector_confidence::T4_no_official_candidate_found_this_pass: 1
- collector_confidence::T4_official_domain_non_plan_context_rejected: 1
- source_packet_status::no_structured_official_plan_candidate_found_this_pass: 1
- source_packet_status::official_pdf_candidate_not_parsed: 1
- source_packet_status::official_portal_candidate_not_structured: 3
- source_packet_status::rejected_official_non_plan_context: 1
- source_packet_status::search_backoff_no_first_party_source: 1
- source_packet_status::web_verified_candidate_not_parsed: 1

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Batch 5 does not write parsed group-year records or expand the 32-school decision pool.
