# P1 batch17 local checklist review templates

## Summary

This marker expands the 3 approval-free local checklist rows from marker 141 into concrete review-template rows. It does not fetch pages, parse new artifacts, run OCR, open browser or WeChat state, infer ranks, or open intake/calibration/canonical/ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_local_checklist_review_templates.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_review_templates_rollup.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_review_templates_qa.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_review_templates_exclusion_log.csv`

## Findings

- Input marker 141 queue rows: 8
- Review template source rows: 3
- Review template rows: 15
- Excluded official-only backoff rows: 5
- Prior marker 141 blocked rows kept in context: 17
- Template rows by group: 10229-101=5, 10513-105=5, 10537-101=5

## Boundary

Every template row is initialized as `pending_local_or_approved_artifact` and keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
