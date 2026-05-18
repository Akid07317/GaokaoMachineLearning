# Reference Trend 520 Batch14 Manual Approval Queue

Generated: 2026-05-16

Purpose: consolidate source routes that should not advance automatically without
human approval. This file is outside the reference_trend_pool, canonical layer,
ML inputs, and the 32-school decision_pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_manual_approval_queue.csv`
- `reports/reference_trend_520_batch14_manual_approval_queue_rollup.csv`
- `reports/reference_trend_520_batch14_manual_approval_queue_qa.csv`
- `reports/reference_trend_520_batch14_manual_approval_queue_exclusion_log.csv`

## Included Approval Items

- 集美大学: aggregate reminder for the existing per-group mapping acceptance
  sheet; the per-group sheet remains authoritative.
- 上海政法学院: official embedded PNG plan images require OCR or manual
  transcription approval.
- 上海海洋大学: official PDF plan attachment requires reliable PDF table parser
  or manual transcription approval.
- 安徽工业大学: official image plan candidate requires OCR/manual transcription
  approval.
- 西华大学: official pages are visible through web index but terminal caching is
  blocked; continue only with exact URL or approved browser/header route.
- 苏州科技大学 / 天津外国语大学: static official pages are cached but no 2025
  Guangxi physical plan rows are visible; retry only with exact detail URL or
  approved dynamic/browser route.

## Boundary

All rows remain `reference_trend_pool_eligible_before_approval=false`,
`calibration_eligible_before_approval=false`, and
`canonical_ml_entry_open=false`. Approval only unlocks a downstream source-packet
or intake preview with QA; it does not open canonical/ML.
