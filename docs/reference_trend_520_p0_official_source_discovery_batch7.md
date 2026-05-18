# Reference Trend 520 P0 Official Source Discovery Batch 7

Generated: 2026-05-16

## Scope

This batch covers the next uncovered P0 plan-source queue rows, queue ranks 33-41. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch7_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_exclusion_log.csv`

## Key Findings

- Candidate rows: 9
- Universities covered: 9
- T1 extractable official candidates: 2 (石河子大学、福建理工大学)
- Manual approval / browser-replay boundaries: 2 (西南医科大学、贵州财经大学)

High-value rows:

1. 石河子大学: official plan page JS data cached. Guangxi 本科普通批 物理类 rows and plan counts are extractable, but no group code is printed.
2. 福建理工大学: official Guangxi HTML plan table cached and locally summarized, but no group code is printed.

Held rows:

- 西南医科大学: official attachment page cached; XLS download is captcha-gated.
- 贵州财经大学: official PDF candidate found, but terminal TLS fetch failed.
- 西安外国语大学: official-domain candidate URL returned 404.
- 福建中医药大学、西安石油大学、陕西中医药大学: no first-party plan source found in this pass.
- 青海大学: official page links an external poster; cached official page has no structured Guangxi rows.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next step should parse the T1 official plan sources into source-packet parse previews, then keep them held until group mapping/acceptance is explicit.
