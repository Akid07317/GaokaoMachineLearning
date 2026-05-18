# Reference trend 520 P1 batch16 static cache post-approval status

Generated: 2026-05-17

## Scope

This preview reads the static-cache approval sheet and routes rows for a future runner. It does not execute the runner.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_post_approval_status.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_post_approval_status_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_post_approval_status_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_post_approval_status_exclusion_log.csv`

## Status distribution

- waiting_human_decision: 10

## Boundary

- Rows only become future-runner eligible after human selected_decision is filled.
- Future runner must still stop on cookie/header/form/browser-state needs.
- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.
