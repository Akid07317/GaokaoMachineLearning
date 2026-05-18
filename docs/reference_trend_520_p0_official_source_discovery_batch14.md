# Reference Trend 520 Official Source Discovery Batch14

Generated: 2026-05-16

Scope: queue ranks 131-150. This is source discovery only; no source asset
cache, OCR, form replay, source-packet parse, reference-trend intake, canonical,
or ML output is opened.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch14_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch14_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch14_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch14_exclusion_log.csv`

## Key candidates

- 苏州科技大学 (132|133): T2_official_plan_portal_needs_detail_cache; official_plan_portal_discovered_not_cached.
- 西华大学 (136): T2_official_plan_portal_needs_detail_cache; official_plan_portal_discovered_not_cached.
- 集美大学 (137): T1_existing_official_source_packet_with_mapping_sheet; existing_acceptance_sheet_pending_human_decision.
- 上海政法学院 (139): T2_official_plan_index_needs_detail_cache; official_plan_index_discovered_not_cached.
- 上海海洋大学 (140): T2_official_plan_index_needs_detail_cache; official_plan_index_discovered_not_cached.
- 天津外国语大学 (144): T2_official_plan_portal_needs_detail_cache; official_plan_portal_discovered_not_cached.
- 安徽工业大学 (147): T2_existing_official_plan_image_candidate; existing_image_candidate_hold_for_ocr_or_manual_transcription.

## Boundary

All rows remain `reference_trend_pool_eligible=false`,
`calibration_eligible=false`, and `canonical_ml_entry_open=false`.
