# Reference Trend 520 Batch 8 T1 Source Packet Parse

Generated: 2026-05-16

## Scope

This parse preview converts the batch8 T1 official plan source for 中南林业科技大学 into major-level plan rows. It remains outside canonical/ML and outside the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch8_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_exclusion_log.csv`

## Parse Summary

- 中南林业科技大学: 41 parsed major rows, plan total 150.
- Selection requirement plan split: 不提科目要求: 5; 物理(1门科目考生必须选考方可报考): 19; 物理,化学(2门科目考生均须选考方可报考): 123; 生物(1门科目考生必须选考方可报考): 3.

## Boundary

The source does not print Guangxi院校专业组 codes. `queue_group_code=106` is kept only as routing context; `source_group_code` remains blank. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: build a group mapping workbench for 中南林业科技大学 or continue official-source discovery for the next P0 rows.
