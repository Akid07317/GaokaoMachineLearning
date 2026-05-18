# Reference Trend 520 Batch13 Cache Parse Preflight

Generated: 2026-05-16

Purpose: record the first cache/parse pass for selected batch13 official candidates.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_cache_parse_preflight_preview.csv`
- `reports/reference_trend_520_batch13_cache_parse_preflight_rollup.csv`
- `reports/reference_trend_520_batch13_cache_parse_preflight_qa.csv`
- `reports/reference_trend_520_batch13_cache_parse_preflight_exclusion_log.csv`

Key findings:
- 河南科技大学 and 哈尔滨医科大学 have official HTML tables that yield major-level Guangxi physical/proxy rows.
- 华侨大学 currently yields only province/subject aggregate counts for 广西, not major/group rows.
- 四川轻化工大学 is image-asset based and needs approved OCR/manual transcription.

Boundary:
- All rows remain source-packet parse preview or readiness only.
- No group code is printed in the parsed major rows, so `reference_trend_pool_eligible=false` and `calibration_eligible=false` remain closed.
- No canonical/ML output and no 32-school decision_pool merge.

Rollup:
- preview_rows: 33 Parsed rows plus aggregate/readiness rows.
- parsed_major_plan_preview_rows: 31 Major-level rows extracted from cached official HTML tables.
- parsed_major_plan_sum: 84 Normal Guangxi/physical-proxy plan count only; special columns not mixed.
- exclusion_rows: 13 Non-physical, summary, aggregate, or image-pending rows.
- reference_trend_pool_eligible_rows: 0 No group code / aggregate/image limitations keep pool closed.
- calibration_eligible_rows: 0 No score/rank and no group-year mapping opened.
- canonical_ml_entry_open: false ML/canonical remains closed.
- university::华侨大学: 1
- university::哈尔滨医科大学: 19
- university::四川轻化工大学: 1
- university::河南科技大学: 12
- status::official_aggregate_preview_not_major_or_group_level: 1
- status::official_image_assets_cached_ocr_or_manual_parse_needed: 1
- status::parsed_official_html_table_preview_hold_for_group_code_mapping: 31
