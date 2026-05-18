# Reference trend 520 P1 official source discovery batch16

Generated: 2026-05-17

## Scope

This batch covers P1 plan source queue ranks 171-190. It records official source candidates only; it does not cache, parse, OCR, replay forms, or open intake/canonical/ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_official_source_discovery_batch16_preview.csv`
- `reports/reference_trend_520_p1_official_source_discovery_batch16_rollup.csv`
- `reports/reference_trend_520_p1_official_source_discovery_batch16_qa.csv`
- `reports/reference_trend_520_p1_official_source_discovery_batch16_exclusion_log.csv`

## Rollup

- Discovery rows: 17
- T1 exact official candidates: 3
- T2 official plan candidates: 7
- T3 context-only rows: 7
- Reference trend pool eligible rows: 0
- Calibration eligible rows: 0
- Canonical/ML entry rows: 0

## Status distribution

- official_context_found_no_structured_plan_rows: 2
- official_context_found_special_type_boundary_hold: 1
- official_exact_plan_candidate_found_not_cached: 2
- official_pdf_candidate_found_not_cached: 1
- official_plan_candidate_found_not_cached: 2
- official_plan_portal_discovered_not_cached: 3
- official_plan_query_candidate_found_not_cached: 2
- official_policy_context_found_no_plan_rows: 1
- official_portal_found_plan_detail_not_cached: 3

## Boundary

- All rows remain `reference_trend_source_packet_preview_only`.
- No row enters reference trend intake until official source packet cache/parse QA is complete.
- No row may be merged into the 32-school decision pool.
- Canonical/ML remains closed.
