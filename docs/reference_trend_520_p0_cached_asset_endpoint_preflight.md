# Reference Trend 520 P0 Cached Asset/Endpoint Preflight

Date: 2026-05-16

Scope: locally cached files from `reference_trend_520_p0_local_cache_inventory.csv` whose feasibility is asset OCR preflight, endpoint/portal review, or context-with-Guangxi-plan terms. This is a local preflight only: no network, no browser replay, no source_packet parse rows, no reference_trend_pool intake, no canonical/ML, and no 32-school decision_pool changes.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_asset_endpoint_preflight.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_rollup.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_qa.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_exclusion_log.csv`

## Coverage

- Target cached preflight rows: 8
- QA status: PASS

## Route Counts

- `cached_context_keyword_only_hold`: 3
- `cached_endpoint_form_or_script_links_found`: 1
- `cached_html_asset_links_found`: 3
- `local_pdf_parse_needed`: 1

## Boundary

Rows remain in preflight/QA only. PDF binaries, image assets, endpoint scripts/forms, and keyword-only context require a later explicit parse/OCR or approval step before any source_packet preview can be created.
