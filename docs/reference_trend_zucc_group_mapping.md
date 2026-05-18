# ZUCC Group Mapping Workbench

Generated: 2026-05-16

This workbench checks whether the official ZUCC 2025 Guangxi plan image can safely thicken the `13021-102` group-year trend row.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv`
- `reports/reference_trend_zucc_group_mapping_rollup.csv`
- `reports/reference_trend_zucc_group_mapping_qa.csv`
- `reports/reference_trend_zucc_group_mapping_exclusion_log.csv`

## Finding

Do **not** assign the official image's full 广西物 plan total of 80 to `13021-102`.

Local exam-authority intake rows show that ZUCC has two 2025 Guangxi physical groups: `101, 102`. The school official image only provides a combined 广西物 column and does not print group code boundaries. Therefore the official image can thicken school-level plan evidence, but it cannot yet thicken group-level plan count for `13021-102`.

## Trend Context

Existing exam-authority rows still keep `13021-102` as a valid score/rank trend pair:

- 2024 `13021-102`: 518 / rank 44178
- 2025 `13021-102`: 502 / rank 54559
- Rank delta: +10381, direction cooler/lower selectivity

This trend evidence remains score/rank-only because plan-count split is unresolved.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. This workbench does not alter the global intake preview, canonical/ML inputs, or the 32-school decision pool.
