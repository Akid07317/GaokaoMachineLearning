# P1 batch17 gated branch decision matrix

## Summary

This marker consolidates marker 140 action-board rows, marker 136 official score-rank approval packet, and marker 142 local checklist templates into a single gated-branch decision matrix. It does not fetch pages, use browser/OCR/WeChat state, select ranks, or open intake/calibration/canonical/ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gated_branch_decision_matrix.csv`
- `reports/reference_trend_520_p1_batch17_gated_branch_decision_matrix_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gated_branch_decision_matrix_qa.csv`
- `reports/reference_trend_520_p1_batch17_gated_branch_decision_matrix_exclusion_log.csv`

## Findings

- Input action-board rows: 25
- Decision families: 10
- Rows needing user action in marker 140: 17
- Unique official score-rank lookup scores waiting for official raw artifact: 382|461|462|490|527
- Local template rows in context: 15 across 3 source checklist rows
- Non-local-template rows kept blocked/excluded from automatic execution: 22

## Boundary

This is a decision-routing artifact only. Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
