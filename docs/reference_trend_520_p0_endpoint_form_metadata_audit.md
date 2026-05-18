# Reference Trend 520 P0 Endpoint/Form Metadata Audit

Date: 2026-05-17

Scope: local metadata audit of cached endpoint/form HTML for P0 endpoint routes. This audit identifies endpoint shapes only. It does not perform live replay, endpoint fetches, browser actions, source_packet parsing, or canonical/ML writes.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_endpoint_form_metadata_audit.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_rollup.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_qa.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_exclusion_log.csv`

## Coverage

- Endpoint audit rows: 9
- QA status: PASS

## Endpoint Shape Status

- `commonquery_iframe_shape_found_replay_approval_required`: 1
- `site_search_endpoint_not_plan_data`: 1
- `supporting_script_or_unknown_endpoint_shape`: 7

## Boundary

The cached page exposes a commonquery iframe shape that may be the招生计划 query surface, but live query replay requires browser/form approval. The site search endpoint is not plan data.
