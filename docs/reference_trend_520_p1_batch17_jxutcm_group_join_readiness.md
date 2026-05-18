# Reference trend 520 P1 batch17 JXUTCM group join readiness

Generated: 2026-05-17

## Scope

This packet summarizes marker 122 JXUTCM official plan rows into source-group readiness rows and records the blockers for score/rank join and group mapping.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_group_join_readiness.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_group_join_readiness_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_group_join_readiness_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_group_join_readiness_exclusion_log.csv`

## Result

- Source-group readiness rows: 5
- Plan sum preserved from marker 122: 62
- Queue group context: `101`
- Suffix candidate mappings: 1
- Local official line/rank source found: 0

## Boundary

- `01 -> 101` is recorded only as a suffix candidate, not an accepted mapping.
- Source groups `02`, `04`, `06`, and `08` remain adjacent official source-packet context, not queue-target rows.
- No minimum score/rank was joined.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
