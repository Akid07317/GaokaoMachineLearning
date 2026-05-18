# P0 Official Source Discovery Batch 6

Generated: 2026-05-16

This batch records official-source discovery for the next P0/P1 plan-source queue segment after the HPU enrichment pass. It is a source-packet preview only.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch6_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_exclusion_log.csv`

## Coverage

- Candidate rows: 8
- Universities covered: 4
- T1 high-value official rows: 2
- Rows requiring manual approval/browser/form/TLS workaround: 2

## Source Notes

- ZUCC: official 2025 Guangxi plan page and embedded image asset were cached; image plan counts were parsed into a separate preview.
- CUZ: official information-disclosure page was cached, but it exposes viewer/PDF links rather than Guangxi physical ordinary rows.
- HNMU: official plan index was identified but terminal fetch is blocked by TLS/reachability; held for manual/browser approval.
- BZMC: official plan query page was cached; Guangxi rows require form/query replay or a static endpoint.

## Status Rollup

- collector_confidence::T1_official_image_extractable_plan_count_candidate: 1
- collector_confidence::T1_official_list_confirms_specific_guangxi_plan_asset: 1
- collector_confidence::T2_official_info_disclosure_needs_pdf_viewer_or_asset_drilldown: 1
- collector_confidence::T2_official_plan_query_form_needs_replay_or_browser: 1
- collector_confidence::T2_official_portal_js_endpoint_needed: 1
- collector_confidence::T3_official_context_not_structured_plan_rows: 1
- collector_confidence::T3_official_plan_index_reachability_blocked: 1
- collector_confidence::T4_official_context_not_target_province_rejected: 1
- source_packet_status::context_only_hold_out: 1
- source_packet_status::official_image_plan_cached_and_parsed_to_preview: 1
- source_packet_status::official_index_cached_no_guangxi_rows: 1
- source_packet_status::official_list_cached_asset_found: 1
- source_packet_status::official_plan_index_reachability_blocked: 1
- source_packet_status::official_portal_cached_no_structured_rows: 1
- source_packet_status::official_query_system_cached_no_rows: 1
- source_packet_status::rejected_official_context_no_guangxi_rows: 1

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Batch 6 does not write group-year records, does not open ML, and does not expand the 32-school decision pool.
