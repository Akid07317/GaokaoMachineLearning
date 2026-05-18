# Reference trend 520 P1 batch16 static cache run manifest

Generated: 2026-05-17

## Scope

This manifest reserves target cache paths and receipt IDs for a future approved static-cache run. It does not fetch, cache, parse, OCR, replay forms, or create intake rows.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_run_manifest.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_run_manifest_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_run_manifest_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_run_manifest_exclusion_log.csv`

## Route distribution

- detail_url_discovery_before_cache: 5
- static_html_page_cache_candidate: 2
- static_pdf_cache_candidate: 1
- static_query_probe_candidate: 2

## Boundary

- Future run may only use official URLs listed in the manifest.
- Static GET/HEAD only; no cookies, header replay, form submit, or browser state.
- Stop and request approval if the official site blocks static access or requires browser/form state.
- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.
