# Reference trend 520 P1 batch16 static cache approval sheet

Generated: 2026-05-17

## Scope

This sheet lets a reviewer approve or hold future static-cache attempts row by row. It does not execute network/cache/parse work.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_approval_sheet.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_approval_sheet_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_approval_sheet_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_approval_sheet_exclusion_log.csv`

## Recommended decisions

- approve_static_GET_or_HEAD_probe_only: 2
- approve_static_cache_only: 3
- hold_for_exact_detail_url_or_static_discovery: 5

## Reviewer fields

Fill `selected_decision`, `reviewer`, `decision_notes`, and `approved_at` if static caching should proceed in a later run.

Allowed selected_decision values:

- `approve_static_cache_only`
- `approve_static_GET_or_HEAD_probe_only`
- `hold`
- `reject`
- `request_fix`

## Boundary

- This is an approval sheet only.
- Future execution must still stop on cookie/header/form/browser-state needs.
- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.
