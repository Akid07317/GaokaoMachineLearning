# Reference Trend 520 P0 Source Discovery Next Actions

Generated: 2026-05-16

Purpose: route P0 plan-source queue rows after reconciliation so the project does not keep blind-searching schools that already have local candidates, parse previews, or group-mapping workbenches.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_source_discovery_next_actions.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_source_discovery_manual_approval_queue.csv`
- `reports/reference_trend_520_p0_source_discovery_next_actions_rollup.csv`
- `reports/reference_trend_520_p0_source_discovery_next_actions_qa.csv`
- `reports/reference_trend_520_p0_source_discovery_next_actions_exclusion_log.csv`

## Coverage

- P0 next-action rows: 117
- Manual/live approval rows: 71

## Action Lane Rollup

- blocked_existing_candidate_needs_approval_or_exact_url: 17
- existing_candidate_parse_or_endpoint_drilldown: 43
- group_mapping_human_acceptance_hold: 16
- live_official_source_discovery_approval: 36
- parse_gap_review_before_new_search: 3
- plan_count_available_group_mapping_hold: 2

## Approval Queue Rollup

- blocked_existing_candidate_needs_approval_or_exact_url: 17
- group_mapping_human_acceptance_hold: 16
- live_official_source_discovery_approval: 36
- plan_count_available_group_mapping_hold: 2

## Boundary

This artifact is non-baseline and non-canonical. Approval unlocks only a downstream `source_packet`, reachability preview, parse preview, or mapping review packet with QA. It does not open canonical/ML and does not merge anything into the 32-school decision_pool.
