# HRBMU Group Mapping Workbench

Generated: 2026-05-16

This is a non-baseline, non-canonical, non-ML workbench for 哈尔滨医科大学 2025 广西 plan rows. It uses the parsed official HRBMU plan table and Guangxi exam-authority 2025 institution-group admission lines to expose the remaining group-code mapping gap.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv`
- `reports/reference_trend_hrbmu_group_mapping_rollup.csv`
- `reports/reference_trend_hrbmu_group_mapping_qa.csv`
- `reports/reference_trend_hrbmu_group_mapping_exclusion_log.csv`

## Coverage

- Workbench rows: 22
- Ordinary physical plan rows: 19
- Ordinary physical plan total: 32
- Legacy non-physics hold total: 5
- All Guangxi ordinary column total: 37
- National-special hold rows: 1
- National-special plan total: 13
- 2025 ordinary physical exam-authority groups: 151:562/19311|152:563/18857|153:496/58830|154:519/42974|156:450/96667|157:454/92968|158:453/93925|159:447/99362
- 2025 national-special exam-authority groups: 555:506/51696
- 520-window delta context: 10226-153:38102->58830(20728)|10226-154:38102->42974(4872)

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`. The HRBMU source has official plan counts but no Guangxi institution-major-group code, so rows remain in mapping QA until an official group structure or a manually accepted mapping rule is available.
