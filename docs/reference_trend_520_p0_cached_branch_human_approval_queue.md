# Reference Trend 520 P0 Cached Branch Human Approval Queue

Date: 2026-05-17

Scope: consolidated human approval/manual QA queue for P0 cached branch blockers. This package merges cached endpoint replay approvals, cached asset capture approvals, and PDF table-layout QA into one operator-facing queue.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_queue.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_exclusion_log.csv`

## Coverage

- Approval/manual QA rows: 9
- QA status: PASS

## Approval Lanes

- `browser_form_replay_approval`: 1
- `cached_asset_capture_or_manual_upload`: 7
- `manual_pdf_table_layout_qa`: 1

## Boundary

This queue is not a source_packet, reference trend intake, canonical, ML, or 32-school decision_pool artifact. Browser/form replay, asset capture, OCR, and manual PDF layout decisions remain gated until the user explicitly approves them.
