# Reference Trend 520 P0 Local Cache Inventory

Generated: 2026-05-16

Purpose: verify local cache availability for P0 local candidate drilldown rows and prevent parsing attempts against missing files.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_local_cache_inventory.csv`
- `reports/reference_trend_520_p0_local_cache_inventory_rollup.csv`
- `reports/reference_trend_520_p0_local_cache_inventory_qa.csv`
- `reports/reference_trend_520_p0_local_cache_inventory_exclusion_log.csv`

## Coverage

- Cache inventory rows: 67
- Existing cache files: 27
- Missing/no-cache rows: 40

## Feasibility Rollup

- cached_asset_or_page_ocr_preflight: 4
- cached_context_contains_guangxi_plan_terms_review: 3
- cached_context_no_structured_plan_hold: 19
- cached_endpoint_or_portal_page_review: 1
- metadata_only_no_cache_path: 40

## Boundary

This artifact is local-cache evidence only. It does not fetch the web, does not create source_packet parse rows, and does not open reference_trend_pool/canonical/ML or the 32-school decision_pool.
