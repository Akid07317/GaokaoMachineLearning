# Reference Trend 520 Batch 7 Group Mapping Workbench

Generated: 2026-05-16

## Scope

This workbench joins the batch7 T1 official plan parses with Guangxi exam-authority group lines. It records field-thickness evidence and group-mapping blockers only; it does not open reference_trend calibration, canonical, or ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch7_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch7_group_mapping_qa.csv`
- `reports/reference_trend_520_batch7_group_mapping_exclusion_log.csv`

## Summary

- 石河子大学: official 2025 physical plan total 100; breakdown 物理类:100; source group code absent.
- 福建理工大学: official 2025 physical plan total 205; breakdown 物理+不限:95;物理+化学:110; source group code absent.

## Decision Boundary

Both schools have multiple 2025 Guangxi physical exam-authority groups. The school plan sources do not print group codes. Therefore the plan totals remain unassigned to group-year records: `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: either obtain official group-code split/major-to-group mapping, or continue P0 official source discovery from rank 42.
