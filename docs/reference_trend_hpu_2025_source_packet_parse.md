# 河南理工大学 2025 广西 source packet parse

Generated: 2026-05-16T15:41:44

## Inputs

- Score HTML: `raw_sources/reference_trend/batch5_official/hpu_2025_guangxi_score.html`
- Plan page HTML: `raw_sources/reference_trend/batch5_official/hpu_2025_plan_page.html`
- Plan XLSX: `raw_sources/reference_trend/batch5_official/hpu_2025_plan_source.xlsx`
- Direct PDF attempt: `raw_sources/reference_trend/batch5_official/hpu_2025_plan_source.pdf` (blocked/404 hold)

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_hpu_2025_source_packet_parse_preview.csv`
- `reports/reference_trend_hpu_2025_source_packet_parse_rollup.csv`
- `reports/reference_trend_hpu_2025_source_packet_parse_qa.csv`
- `reports/reference_trend_hpu_2025_source_packet_parse_exclusion_log.csv`

## Result

- Major-level score/plan rows: 29
- Derived group summary candidates: 7
- Ordinary physical major rows: 25, plan total 50
- Score page total vs XLSX Guangxi total: 60 vs 60

## Boundary

This is a source-packet parse preview. Group summary rows are derived from official major rows and cannot replace Guangxi exam-authority group 投档线. `reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`.
