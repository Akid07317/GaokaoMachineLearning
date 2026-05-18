# Reference trend 520 P1 batch17 gap pulse coverage update

Generated: 2026-05-17

## Scope

This consolidates marker 129-131 gap-search pulses into the marker 127 batch17 coverage ledger.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gap_pulse_coverage_update.csv`
- `reports/reference_trend_520_p1_batch17_gap_pulse_coverage_update_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gap_pulse_coverage_update_qa.csv`
- `reports/reference_trend_520_p1_batch17_gap_pulse_coverage_update_exclusion_log.csv`

## Summary

- Batch17 group targets: 20
- Gap pulse rows integrated: 12
- Rows with source-packet preview follow-up candidates: 15
- Official line-score rows retained: 6
- Official min-rank rows: 0
- Reference trend eligible rows: 0
- Canonical/ML rows opened: 0

## Consolidated States

- `existing_official_candidate_needs_parse_or_filter_QA`: 2
- `existing_official_candidate_plus_line_score_rank_missing`: 5
- `gap_pulse_official_candidate_needs_source_packet_preview`: 7
- `gap_pulse_reachability_backoff_no_preview`: 5
- `parsed_plan_preview_exists_but_rank_mapping_hold`: 1

## Boundary

This update performs no network fetch, cache, parse, OCR, browser/form replay, login-state review, WeChat capture, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update.
