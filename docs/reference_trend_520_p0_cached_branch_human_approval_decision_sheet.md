# Reference Trend 520 P0 Cached Branch Human Approval Decision Sheet

Date: 2026-05-17

Scope: human-fillable decision sheet for the P0 cached branch approval queue. Fill `selected_decision`, `reviewer`, `decision_time_iso`, and `decision_notes` here rather than editing the generated approval queue.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_decision_sheet.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_exclusion_log.csv`

## Coverage

- Decision sheet rows: 9
- QA status: PASS

## Approval Lanes

- `browser_form_replay_approval`: 1
- `cached_asset_capture_or_manual_upload`: 7
- `manual_pdf_table_layout_qa`: 1

## Current Decisions

- `__blank__`: 9

## Boundary

This sheet is a human decision surface only. It does not approve actions by itself, does not run browser/form replay, does not capture assets, does not OCR or parse source packets, and does not write reference trend intake, canonical, ML, or 32-school decision_pool rows.
