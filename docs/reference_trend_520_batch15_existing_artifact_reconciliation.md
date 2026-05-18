# Reference Trend 520 Batch15 Existing Artifact Reconciliation

Generated: 2026-05-16

Purpose: deduplicate batch15 rediscovery of 中南林业科技大学 against existing
batch8 source-packet and group-mapping artifacts.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_existing_artifact_reconciliation.csv`
- `reports/reference_trend_520_batch15_existing_artifact_reconciliation_rollup.csv`
- `reports/reference_trend_520_batch15_existing_artifact_reconciliation_qa.csv`
- `reports/reference_trend_520_batch15_existing_artifact_reconciliation_exclusion_log.csv`

## Summary

Batch15 queue ranks 168/169 point to the same official 2025 Guangxi plan source
already handled in batch8. Existing artifacts contain 41 major rows and a plan
total of 150, but the official source does not print Guangxi professional-group
codes. The 2025 exam-authority context has groups 104|106|108; group-year
intake stays held until manual group mapping or an official group split is
accepted.

## Boundary

No new network fetch is needed for this exact source. All reconciled rows remain
`reference_trend_pool_eligible=false`, `calibration_eligible=false`, and
`canonical_ml_entry_open=false`.
