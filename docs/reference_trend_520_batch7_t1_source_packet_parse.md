# Reference Trend 520 Batch 7 T1 Source Packet Parse

Generated: 2026-05-16

## Scope

This parse preview converts the two batch7 T1 official plan sources into major-level plan rows. It remains outside canonical/ML and outside the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_exclusion_log.csv`

## Parse Summary

- 石河子大学: 32 parsed major rows, plan total 100.
- 福建理工大学: 38 parsed major rows, plan total 205.

## Boundary

No source row prints Guangxi院校专业组 codes. `queue_group_code` is kept only as routing context; `source_group_code` remains blank. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: build a group mapping workbench for 石河子大学/福建理工大学 or continue official-source discovery for the next P0 rows.
