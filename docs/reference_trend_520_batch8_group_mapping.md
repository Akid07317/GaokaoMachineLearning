# Reference Trend 520 Batch 8 Group Mapping Workbench

Generated: 2026-05-16

## Scope

This workbench joins the batch8 T1 official plan parse for 中南林业科技大学 with Guangxi exam-authority group lines. It records field-thickness evidence and group-mapping blockers only; it does not open reference_trend calibration, canonical, or ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch8_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch8_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch8_group_mapping_qa.csv`
- `reports/reference_trend_520_batch8_group_mapping_exclusion_log.csv`

## Summary

- Official 2025 physical ordinary plan total: 150 across 41 major rows.
- Selection split: 不提科目要求:5;物理(1门科目考生必须选考方可报考):19;物理,化学(2门科目考生均须选考方可报考):123;生物(1门科目考生必须选考方可报考):3.
- Guangxi exam-authority 2025 physical groups visible locally: 104、106、108.

## Decision Boundary

The official school plan source does not print Guangxi院校专业组 codes. The source total remains unassigned to group-year records: `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: obtain official group-code split/major-to-group mapping, or continue P0 official source discovery from the next uncovered row.
