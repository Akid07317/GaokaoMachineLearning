# Reference trend 520 P1 batch17 discovery workset

Generated: 2026-05-17

## Scope

Queue ranks 191-210 are prepared as an official-source discovery workset. This is a pre-network, pre-cache packet.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_discovery_workset.csv`
- `reports/reference_trend_520_p1_batch17_discovery_workset_rollup.csv`
- `reports/reference_trend_520_p1_batch17_discovery_workset_qa.csv`
- `reports/reference_trend_520_p1_batch17_discovery_workset_exclusion_log.csv`

## Route distribution

- ethnic_university_official_plan_discovery_with_special_type_isolation: 1
- local_guangxi_official_plan_discovery: 1
- medical_official_plan_discovery_with_special_type_isolation: 4
- merge_same_university_group_rows_then_official_plan_discovery: 2
- standard_official_plan_discovery: 12

## Boundary

- The workset records search strings, source fields, and exclusion constraints only.
- It does not claim official source URLs, cache files, parse rows, or intake eligibility.
- Canonical/ML and the 32-school decision pool remain closed.
