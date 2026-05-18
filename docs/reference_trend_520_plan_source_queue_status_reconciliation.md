# Plan Source Queue Status Reconciliation

Generated: 2026-05-16

This non-baseline reconciliation joins `reference_trend_520_plan_source_packet_queue.csv` to existing discovery, source-packet parse, and group-mapping workbench artifacts. It is meant to prevent duplicate source searching and to route already-covered schools to mapping/QA resolution.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_plan_source_queue_status_reconciliation.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_rollup.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_qa.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_exclusion_log.csv`

## Coverage

- Queue rows reconciled: 457
- P0 rows: 117
- P0 rows with existing artifact: 81
- P0 rows still needing discovery: 36
- Universities with existing artifact: 61

## Status Rollup

- status::mapping_workbench_exists_hold_for_group_acceptance: 26
- status::needs_official_source_discovery: 322
- status::plan_count_source_packet_exists_hold_for_group_mapping: 4
- status::source_candidate_exists_not_structured: 98
- status::source_packet_parse_exists_but_field_gaps_remain: 7

## Boundary

This file is a queue-routing layer only. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.
