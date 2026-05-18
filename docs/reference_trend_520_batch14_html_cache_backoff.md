# Reference Trend 520 Batch14 HTML Cache Backoff

Generated: 2026-05-16

Purpose: record official HTML caches that should not be retried blindly because
they did not expose static 2025 Guangxi physical ordinary plan rows.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_html_cache_backoff_preview.csv`
- `reports/reference_trend_520_batch14_html_cache_backoff_rollup.csv`
- `reports/reference_trend_520_batch14_html_cache_backoff_qa.csv`
- `reports/reference_trend_520_batch14_html_cache_backoff_exclusion_log.csv`

## Summary

- 苏州科技大学: official plan column cached, but no static 2025 Guangxi rows.
- 天津外国语大学: official index and plan column cached; plan column currently
  exposes 2024 and older plans, not 2025 Guangxi rows.

## Boundary

All rows remain `reference_trend_pool_eligible=false`,
`calibration_eligible=false`, and `canonical_ml_entry_open=false`.
