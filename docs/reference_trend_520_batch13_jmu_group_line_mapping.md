# Reference Trend 520 Batch13 JMU Group-Line Mapping Workbench

Generated: 2026-05-16

Purpose: join the parsed 集美大学 official Guangxi plan source packet to the existing
520 rank-window queue as a candidate group-line mapping workbench. This is not
reference-trend pool intake, not canonical, and not ML input.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_group_line_mapping_workbench.csv`
- `reports/reference_trend_520_batch13_jmu_group_line_mapping_rollup.csv`
- `reports/reference_trend_520_batch13_jmu_group_line_mapping_qa.csv`
- `reports/reference_trend_520_batch13_jmu_group_line_mapping_exclusion_log.csv`

## Summary

- Official source groups: 8
- Candidate matched groups: 7
- Candidate matched plan sum: 155
- Held groups: 1
- Held plan sum: 5

Group 11 remains held because it is printed by the school source but was not in
the current top-batch 520 queue score/rank context. The other seven groups are
candidate mappings only and need human acceptance/source confirmation before
any reference-trend pool intake.

## Boundary

`reference_trend_pool_eligible=false_preview_only`,
`calibration_eligible=false_pending_human_acceptance_and_score_rank_source_confirmation`,
and `canonical_ml_entry_open=false` for all rows.
