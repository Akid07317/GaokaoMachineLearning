# Reference Trend 520 Batch 9 北方工业大学 Source Packet Parse

Generated: 2026-05-16

## Scope

This parse preview converts the batch9 T1 official plan source for 北方工业大学 into Guangxi-column major plan rows. It remains outside canonical/ML and outside the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_exclusion_log.csv`

## Parse Summary

- 北方工业大学: 37 parsed Guangxi-column major rows, plan total 57.
- Art/design rows marked for isolation: plan total 4.
- Sino-foreign cooperation rows marked for isolation: plan total 5.

## Boundary

The source does not print Guangxi院校专业组 codes or subject/selection requirements. `queue_group_code=304` is kept only as routing context; `source_group_code` remains blank. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: build a group/subject mapping workbench for 北方工业大学 or continue official-source discovery for the next P0 rows.
