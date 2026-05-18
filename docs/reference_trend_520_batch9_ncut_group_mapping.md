# Reference Trend 520 Batch 9 北方工业大学 Group Mapping Workbench

Generated: 2026-05-16

## Scope

This workbench joins the batch9 北方工业大学 official Guangxi-column plan parse with Guangxi exam-authority group lines. It records field-thickness evidence and group/subject mapping blockers only; it does not open reference_trend calibration, canonical, or ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_qa.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_exclusion_log.csv`

## Summary

- Official 2025 Guangxi-column plan total: 57 across 37 major rows.
- Unmarked ordinary-like plan total: 48.
- Special rows marked in source packet: art_design_boundary:4;sino_foreign_cooperation:5.
- Guangxi exam-authority 2025 physical groups visible locally: 102、103、304、500.

## Decision Boundary

The official school plan source does not print Guangxi院校专业组 codes or subject/selection labels. The source total remains unassigned to group-year records: `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.

Next step: obtain official group-code/subject split or manually accept a mapping rule; otherwise continue P0 official source discovery from the next uncovered row.
