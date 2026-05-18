# P1 batch17 user approval decision sheet

## Summary

This marker extracts the branches from marker 143 that require a user decision or an official raw artifact. It is a pending decision sheet only: no browser, fetch, OCR, WeChat capture, rank selection, intake, calibration, canonical, or ML action is performed.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_user_approval_decision_sheet.csv`
- `reports/reference_trend_520_p1_batch17_user_approval_decision_sheet_rollup.csv`
- `reports/reference_trend_520_p1_batch17_user_approval_decision_sheet_qa.csv`
- `reports/reference_trend_520_p1_batch17_user_approval_decision_sheet_exclusion_log.csv`

## Findings

- Input decision families: 10
- Approval option rows: 7
- Local/no-approval branches excluded from this sheet: 3
- Approval priorities: P0=3, P1=3, P2_optional=1
- Score-rank lookup scores preserved: 382|461|462|490|527

## Boundary

The sheet records only pending approval choices. Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
